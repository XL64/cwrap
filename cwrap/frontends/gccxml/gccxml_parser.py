#------------------------------------------------------------------------------
# This file is adapted from ctypeslib.codegen.gccxmlparser
#------------------------------------------------------------------------------
from xml.etree import cElementTree
import os
import sys
import re

from . import c_ast


def MAKE_NAME(name):
    """ Converts a mangled C++ name to a valid python identifier.

    """
    name = name.replace('$', 'DOLLAR')
    name = name.replace('.', 'DOT')
    if name.startswith('__'):
        return '_X' + name
    elif name[0] in '01234567879':
        return '_' + name
    return name


WORDPAT = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')


def CHECK_NAME(name):
    """ Checks if `name` is a valid Python identifier. Returns
    `name` on success, None on failure.

    """
    if WORDPAT.match(name):
        return name
    return None


class GCCXMLParser(object):
    """ Parses a gccxml file into a list of file-level c_ast nodes.

    """
    # xml element types that have xml subelements. For example, 
    # function arguments are subelements of a function, but struct 
    # fields are their own toplevel xml elements
    has_subelements = set(['Enumeration', 'Function', 'FunctionType',
                           'OperatorFunction', 'Method', 'Constructor',
                           'Destructor', 'OperatorMethod'])

    def __init__(self, *args):
        # `context` acts like stack where parent nodes are pushed
        # before visiting children
        self.context = []

        # `all` maps the unique ids from the xml to the c_ast
        # node that was generated by the element. This is used
        # after all nodes have been generated to go back and
        # hook up dependent nodes.
        self.all = {}

        # XXX - what does this do?
        self.cpp_data = {}

        # `cdata` is used as temporary storage while elements
        # are being processed.
        self.cdata = None

        # `cvs_revision` stores the gccxml version in use.
        self.cvs_revision = None

    #--------------------------------------------------------------------------
    # Parsing entry points
    #--------------------------------------------------------------------------
    def parse(self, xmlfile):
        """ Parsing entry point. `xmlfile` is a filename or a file
        object.

        """
        for event, node in cElementTree.iterparse(xmlfile, events=('start', 'end')):
            if event == 'start':
                self.start_element(node.tag, dict(node.items()))
            else:
                if node.text:
                    self.visit_Characters(node.text)
                self.end_element(node.tag)
                node.clear()

    def start_element(self, name, attrs):
        """ XML start element handler. Generates and calls the visitor 
        method name, registers the resulting node's id, and 
        sets the location on the node.

        """
        # find and call the handler for this element
        mth = getattr(self, 'visit_' + name, None)
        if mth is None:
            result = self.unhandled_element(name, attrs)
        else:
            result = mth(attrs)

        # Record the result and register the the id, which is
        # used in the _fixup_* methods. Some elements don't have
        # an id, so we create our own.
        if result is not None:
            location = attrs.get('location', None)
            if location is not None:
                result.location = location
            _id = attrs.get('id', None)
            if _id is not None:
                self.all[_id] = result
            else:
                self.all[id(result)] = result

        # if this element has subelements, push it onto the context
        # since the next elements will be it's children.
        if name in self.has_subelements:
            self.context.append(result)

    def end_element(self, name):
        """ XML end element handler.

        """
        # if this element has subelements, then it will have
        # been push onto the stack and needs to be removed.
        if name in self.has_subelements:
            self.context.pop()
        self.cdata = None

    def unhandled_element(self, name, attrs):
        """ Handler for element nodes where a real handler is not
        found.

        """
        print 'Unhandled element `%s`.' % name

    #--------------------------------------------------------------------------
    # Ignored elements and do-nothing handlers
    #--------------------------------------------------------------------------
    def visit_Ignored(self, attrs):
        """ Ignored elements are those which we don't care about,
        but need to keep in place because we care about their 
        children.

        """
        name = attrs.get('name', None)
        if name is None:
            name = attrs.get('mangled', None)
            if name is None:
                name = 'UNDEFINED'
            else:
                name = MAKE_NAME(name)
        return c_ast.Ignored(name)

    visit_Method =  visit_Ignored
    visit_Constructor = visit_Ignored
    visit_Destructor = visit_Ignored
    visit_OperatorMethod  =  visit_Ignored
    #visit_Class = visit_Ignored
    visit_Base = visit_Ignored
    visit_Converter = visit_Ignored
    visit_MethodType = visit_Ignored

    # These node types are ignored becuase we don't need anything
    # at all from them.
    #visit_Class = lambda *args: None
    #visit_Base =  lambda *args: None
    visit_Ellipsis =  lambda *args: None

    visit_OffsetType = visit_Ignored

    #--------------------------------------------------------------------------
    # Revision Handler
    #--------------------------------------------------------------------------
    def visit_GCC_XML(self, attrs):
        """ Handles the versioning info from the gccxml version.

        """
        rev = attrs['cvs_revision']
        self.cvs_revision = tuple(map(int, rev.split('.')))
    
    #--------------------------------------------------------------------------
    # Text handlers
    #--------------------------------------------------------------------------
    def visit_Characters(self, content):
        """ The character handler which is called after each xml 
        element has been processed.

        """
        if self.cdata is not None:
            self.cdata.append(content)
    
    def visit_CPP_DUMP(self, attrs):
        """ Gathers preprocessor elements like macros and defines.

        """
        # Insert a new list for each named section into self.cpp_data,
        # and point self.cdata to it.  self.cdata will be set to None
        # again at the end of each section.
        name = attrs['name']
        self.cpp_data[name] = self.cdata = []
 
    #--------------------------------------------------------------------------
    # Node element handlers
    #--------------------------------------------------------------------------
    def visit_Namespace(self, attrs):
        name = attrs['name']
        members = attrs['members'].split()
        return c_ast.Namespace(name, members)
    
    def visit_File(self, attrs):
        name = attrs['name']
        return c_ast.File(name)

    def visit_Variable(self, attrs):
        name = attrs['name']
        typ = attrs['type']
        context = attrs['context']
        init = attrs.get('init', None)
        return c_ast.Variable(name, typ, context, init)

    def visit_Typedef(self, attrs):
        name = attrs['name']
        typ = attrs['type']
        context = attrs['context']
        return c_ast.Typedef(name, typ, context)
   
    def visit_FundamentalType(self, attrs):
        name = attrs['name']
        if name == 'void':
            size = ''
        else:
            size = attrs['size']
        align = attrs['align']
        return c_ast.FundamentalType(name, size, align)

    def visit_PointerType(self, attrs):
        typ = attrs['type']
        size = attrs['size']
        align = attrs['align']
        return c_ast.PointerType(typ, size, align)

    visit_ReferenceType = visit_PointerType
   
    def visit_ArrayType(self, attrs):
        # min, max are the min and max array indices
        typ = attrs['type']
        min = attrs['min']
        max = attrs['max']
        if max == 'ffffffffffffffff':
            max = '-1'
        if max == '': #ADDED gregor
            max = '-1'
        min = int(min.rstrip('lu'))
        max = int(max.rstrip('lu'))
        return c_ast.ArrayType(typ, min, max)

    def visit_CvQualifiedType(self, attrs):
        typ = attrs['type']
        const = attrs.get('const', None)
        volatile = attrs.get('volatile', None)
        return c_ast.CvQualifiedType(typ, const, volatile)
 
    def visit_Function(self, attrs):
        name = attrs['name']
        returns = attrs['returns']
        context = attrs['context']
        attributes = attrs.get('attributes', '').split()
        extern = attrs.get('extern')
        return c_ast.Function(name, returns, context, attributes, extern)

    def visit_FunctionType(self, attrs):
        returns = attrs['returns']
        attributes = attrs.get('attributes', '').split()
        return c_ast.FunctionType(returns, attributes)
  
    def visit_OperatorFunction(self, attrs):
        name = attrs['name']
        returns = attrs['returns']
        context = attrs['context']
        attributes = attrs.get('attributes', '').split()
        extern = attrs.get('extern')
        #return c_ast.OperatorFunction(name, returns)
        return c_ast.OperatorFunction(name, returns, context, attributes, extern)

    def visit_Argument(self, attrs):
        parent = self.context[-1]
        if parent is not None:
            typ = attrs['type']
            name = attrs.get('name')
            arg = c_ast.Argument(typ, name)
            parent.add_argument(arg)

    def visit_Enumeration(self, attrs):
        # If the name isn't a valid Python identifier, 
        # create an unnamed enum
        name = CHECK_NAME(attrs['name'])
        size = attrs['size']
        align = attrs['align']
        return c_ast.Enumeration(name, size, align)
    
    def visit_EnumValue(self, attrs):
        parent = self.context[-1]
        if parent is not None:
            name = attrs['name']
            value = attrs['init']
            val = c_ast.EnumValue(name, value)
            parent.add_value(val)

    def visit_Struct(self, attrs):
        name = attrs.get('name')
        if name is None:
            name = MAKE_NAME(attrs['mangled'])
        bases = attrs.get('bases', '').split()
        members = attrs.get('members', '').split()
        context = attrs['context']
        align = attrs['align']
        size = attrs.get('size')
        return c_ast.Struct(name, align, members, context, bases, size)

    def visit_Class(self, attrs):
        name = attrs.get('name')
        if name is None:
            name = MAKE_NAME(attrs['mangled'])
        bases = attrs.get('bases', '').split()
        #fix 'protected:_12345'
        bases = [b.replace('protected:','') for b in bases]
        members = attrs.get('members', '').split()
        context = attrs['context']
        align = attrs['align']
        size = attrs.get('size')
        return c_ast.Struct(name, align, members, context, bases, size) #TODO: Class

    
    def visit_Union(self, attrs):
        name = attrs.get('name')
        if name is None:
            name = MAKE_NAME(attrs['mangled'])
        bases = attrs.get('bases', '').split()
        members = attrs.get('members', '').split()
        context = attrs['context']
        align = attrs['align']
        size = attrs.get('size')
        return c_ast.Union(name, align, members, context, bases, size)

    def visit_Field(self, attrs):
        name = attrs['name']
        typ = attrs['type']
        context = attrs['context']
        bits = attrs.get('bits', None)
        offset = attrs.get('offset')
        return c_ast.Field(name, typ, context, bits, offset)


    #visit_Class = visit_Struct
    #visit_Class = visit_Ignored


    #--------------------------------------------------------------------------
    # Fixup handlers
    #--------------------------------------------------------------------------

    # The fixup handlers use the ids save on the node attrs to lookup 
    # the replacement node from the storage, then do the swapout. There
    # must be a fixup handler (even if its pass-thru) for each node
    # handler that returns a node object.
    
    def _fixup_Namespace(self, ns):
        for i, mbr in enumerate(ns.members):
            ns.members[i] = self.all[mbr]

    def _fixup_File(self, f): 
        pass
    
    def _fixup_Variable(self, t):
        t.typ = self.all[t.typ]
        t.context = self.all[t.context]

    def _fixup_Typedef(self, t):
        t.typ = self.all[t.typ]
        t.context = self.all[t.context]

    def _fixup_FundamentalType(self, t): 
        pass

    def _fixup_PointerType(self, p):
        p.typ = self.all[p.typ]

    _fixup_ReferenceType = _fixup_PointerType

    def _fixup_ArrayType(self, a):
        a.typ = self.all[a.typ]

    def _fixup_CvQualifiedType(self, c):
        c.typ = self.all[c.typ]

    def _fixup_Function(self, func):
        func.returns = self.all[func.returns]
        func.context = self.all[func.context]
        func.fixup_argtypes(self.all)
        
    def _fixup_FunctionType(self, func):
        func.returns = self.all[func.returns]
        func.fixup_argtypes(self.all)
        
    def _fixup_OperatorFunction(self, func):
        func.returns = self.all[func.returns]
        func.context = self.all[func.context]
        func.fixup_argtypes(self.all)

    def _fixup_Enumeration(self, e): 
        pass

    def _fixup_EnumValue(self, e): 
        pass
    
    def _fixup_Struct(self, s):
        s.members = [self.all[m] for m in s.members]
        s.bases = [self.all[b] for b in s.bases]
        s.context = self.all[s.context]

    def _fixup_Union(self, u):
        u.members = [self.all[m] for m in u.members]
        u.bases = [self.all[b] for b in u.bases]
        u.context = self.all[u.context]

    def _fixup_Field(self, f):
        f.typ = self.all[f.typ]
        f.context = self.all[f.context]

    def _fixup_Macro(self, m):
        pass
    
    def _fixup_Ignored(self, const): 
        pass

    _fixup_Method = _fixup_Ignored
    _fixup_Constructor = _fixup_Ignored
    _fixup_Destructor = _fixup_Ignored
    _fixup_OperatorMethod = _fixup_Ignored
   
    #--------------------------------------------------------------------------
    # Post parsing helpers
    #--------------------------------------------------------------------------
    def get_macros(self, text):
        """ Attempts to extract the macros from a piece of text
        and converts it to a Macro node containing the name,
        args, and body.  

        """
        if text is None:
            return
        
        # join and split so we can accept a list or  string. 
        text = ''.join(text)
        for m in text.splitlines():
            name, body = m.split(None, 1)
            name, args = name.split('(', 1)
            args = '(%s' % args
            self.all[name] = c_ast.Macro(name, args, body)

    def get_aliases(self, text, namespace):
        """ Attemps to extract defined aliases of the form
        #define A B and store them in an Alias node.

        """
        if text is None:
            return
        
        aliases = {}
        text = ''.join(text)
        for a in text.splitlines():
            name, value = a.split(None, 1)
            a = c_ast.Alias(name, value)
            aliases[name] = a
            self.all[name] = a

        # The alias value will be located in the namespace,
        # or the aliases. Otherwise, it's unfound.
        for name, a in aliases.items():
            value = a.value
            if value in namespace:
                a.typ = namespace[value]
            elif value in aliases:
                a.typ = aliases[value]
            else:
                pass

    def get_result(self):
        """ After parsing, call this method to retrieve the results
        as a list of AST nodes. This list will contain *all* nodes
        in the xml file which will include a bunch of builtin and 
        internal stuff that you wont want.

        """
        # Drop some warnings for early gccxml versions
        import warnings
        if self.cvs_revision is None:
            warnings.warn('Could not determine CVS revision of GCCXML')
        elif self.cvs_revision < (1, 114):
            warnings.warn('CVS Revision of GCCXML is %d.%d' % self.cvs_revision)

        # Gather any macros.
        self.get_macros(self.cpp_data.get('functions'))

        # Walk through all the items, hooking up the appropriate 
        # links by replacing the id tags with the actual objects
        remove = []
        for name, node in self.all.items():
            location = getattr(node, 'location', None)
            if location is not None:
                fil, line = location.split(':')
                node.location = (self.all[fil].name, int(line))
            method_name = '_fixup_' + node.__class__.__name__
            fixup_method = getattr(self, method_name, None)
            if fixup_method is not None:
                fixup_method(node)
            else:
                remove.append(node)
        
        # remove any nodes don't have handler methods
        for n in remove:
            del self.all[n]
               
        # sub out any #define'd aliases and collect all the nodes 
        # we're interested in. The interesting nodes are not necessarily
        # all nodes, but rather the ones that may need to be modified
        # by the transformations applied later on.
        interesting = (c_ast.Typedef, c_ast.Struct, c_ast.Enumeration, 
                       c_ast.Union, c_ast.Function, c_ast.Variable, 
                       c_ast.Namespace, c_ast.File)

        result = []
        namespace = {}
        for node in self.all.values():
            if not isinstance(node, interesting):
                continue
            name = getattr(node, 'name', None)
            if name is not None:
                namespace[name] = node
            result.append(node)
        self.get_aliases(self.cpp_data.get('aliases'), namespace)
        
        return result


def parse(xmlfile):
    # parse an XML file into a sequence of type descriptions
    parser = GCCXMLParser()
    parser.parse(xmlfile)
    items = parser.get_result()
    return items
