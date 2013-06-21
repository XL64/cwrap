# Stdlib imports
import os
import subprocess
import tempfile

# Local package imports
from . import ast_transforms as transforms
from . import gccxml_parser
from . import c_ast


def gen_c_ast(header_path, include_dirs):
    """ Parse the given header file into a C style ast which can be
    transformed into a CWrap ast. The include dirs are passed along to 
    gccxml.

    """
    # A temporary file to store the xml generated by gccxml
    xml_file = tempfile.NamedTemporaryFile(suffix='.xml', delete=False)
    xml_file.close()

    # buildup the gccxml command
    cmds = ['gccxml']
    for inc_dir in include_dirs:
        cmds.append('-I' + inc_dir)
    cmds.append(header_path)
    cmds.append('-fxml=%s' % xml_file.name)
   
    # we pipe stdout so the preprocessing doesn't dump to the 
    # shell. We really don't care about it.
    p = subprocess.Popen(cmds, stdout=subprocess.PIPE)
    cpp, _ = p.communicate()
    
    # Parse the xml into the ast then delete the temp file
    c_ast = gccxml_parser.parse(xml_file.name)
    os.remove(xml_file.name)

    return c_ast


def print_item(item, caption = '', level=0):
    if not item:
        return
    print '   '*level, item.__class__.__name__, repr(getattr(item, 'name', ''))
    #print '   '*level, item
    print '   '*level, 'context:', getattr(getattr(item, 'context', None), 'name', 'no context')
    print '   '*level, 'bases', getattr(item, 'bases', None)
    print
    for i in getattr(item, 'members', []):
        print_item(i, '', level+1)
    #print

def generate_asts(config):
    """ Returns an iterable of ASTContainer objects.

    """
    c_ast_containers = []
    for header_file in config.files:
        # read the header info and create the extern and implemenation
        # module names
        path = header_file.path
        header_name = os.path.split(path)[-1]
        extern_name = header_file.metadata.get('extern_name')
        implementation_name = header_file.metadata.get('implementation_name')
        if extern_name is None:
            extern_name = '_' + os.path.splitext(header_name)[0]
        if implementation_name is None:
            implementation_name = os.path.splitext(header_name)[0]

        # generate the c_ast for the header 
        include_dirs = config.metadata.get('include_dirs', [])
        print 'Parsing %s' % path
        ast_items = gen_c_ast(path, include_dirs) 

        print 'file parsed'
        print 'AST:'
        for item in ast_items:
            if isinstance(item, c_ast.Namespace):
                for i in item.members:
                    
                    if i.location is not None and 'gccxml_builtins' in i.location[0]:
                        #print 'skipped'
                        pass
                    else:
                        print_item(i)


        # Apply the transformations to the ast items 
        trans_items = transforms.apply_c_ast_transformations(ast_items)
        
        # Create the CAstContainer for these items
        container = transforms.CAstContainer(trans_items, header_name, 
                                             extern_name, implementation_name)

        # Add the container to the list
        c_ast_containers.append(container)

    # Now we can create an ast transformer and transform the list 
    # of containers into a generator that can be rendered into code
    ast_transformer = transforms.CAstTransformer(c_ast_containers)
    return ast_transformer.transform()
