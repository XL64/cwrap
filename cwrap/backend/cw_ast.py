# This largely mimics the AST of Python 2.7 with additional nodes 
# to support Cython specific constructs. 


#------------------------------------------------------------------------------
# AST validation
#------------------------------------------------------------------------------
def assert_mod(node, var_name):
    msg = '%s must be a mod node.' % var_name
    assert isinstance(node, mode), msg


def assert_stmt(node, var_name):
    msg = '%s must be a stmt node.' % var_name
    assert isinstance(node, stmt), msg


def assert_stmts(items, var_name):
    msg = '%s must be stmt nodes.' % var_name
    for item in items:
        assert isinstance(item, stmt), msg


def assert_expr(node, var_name):
    msg = '%s must be an expr node.' % var_name
    assert isinstance(node, expr), msg


def assert_exprs(items, var_name):
    msg = '%s must be expr nodes.' % var_name
    for item in items:
        assert isinstance(item, expr), msg


def assert_arguments(args, var_name):
    msg = '%s must be an arguments node.' % var_name
    assert isinstance(args, arguments), var_name


def assert_operator(op, var_name):
    msg = '%s must be an operator node.' % var_name
    assert isinstance(op, operator), msg


def assert_excepthandler(handler, var_name):
    msg = '%s must be an excepthandler node.' % var_name
    assert isinstance(handler, excepthandler), msg


def assert_excepthandlers(handlers, var_name):
    msg = '%s must be excepthandler nodes.' % var_name
    for handler in handlers:
        assert isinstance(handler, excepthandler), msg


def assert_alias(node, var_name):
    msg = '%s must be an alias node.' % var_name
    assert isinstance(node, alias), msg


def assert_aliases(items, var_name):
    msg = '%s must be alias nodes.' % var_name
    for item in items:
        assert isinstance(item, alias), msg


def assert_boolop(node, var_name):
    msg = '%s must be a boolop node.' % var_name
    assert isinstance(node, boolop), msg


def assert_unaryop(node, var_name):
    msg = '%s must be a unaryop node.' % var_name
    assert isinstance(node, unaryop), msg


def assert_cmpops(items, var_name):
    msg = '%s must be cmpop nodes.' % var_name
    for item in items:
        assert isinstance(item, cmpop), msg


def assert_keywords(items, var_name):
    msg = '%s must be keyword nodes.' % var_name
    for item in items:
        assert isinstance(item, keyword), msg


def assert_comprehension(node, var_name):
    msg = '%s must be a comprehension node.' % var_name
    assert isinstance(node, comprehension), msg


def assert_comprehensions(node, var_name):
    msg = '%s must be comprehension nodes.' % var_name
    for item in items:
        assert isinstance(item, comprehension), msg


def assert_expr_context(node, var_name):
    msg = '%s must be an expr_context node.' % var_name
    assert isinstance(node, expr_context)


def assert_slice(node, var_name):
    msg = '%s must be a slice node.' % var_name
    assert isinstance(node, slice), msg

   
def assert_slices(items, var_name):
    msg = '%s must be slice nodes.' % var_name
    for item in items:
        assert isinstance(item, slice), msg


def assert_str(node, var_name):
    msg = '%s must be a string.' % var_name
    assert isinstance(node, str), msg


def assert_strs(items, var_name):
    msg = '%s must be strings.' % var_name
    for item in items:
        assert isinstance(item, str), msg


def assert_bool(node, var_name):
    msg = '%s must be a boolean.' % var_name
    assert isinstance(node, bool), msg


def assert_int(node, var_name):
    msg = '%s must be an int.' % var_name
    assert isinstance(node, int), msg


def assert_num(node, var_name):
    msg = '%s must be a number.' % var_name
    assert isinstance(node, (int, float, long)), msg


def assert_basestring(node, var_name):
    msg = '%s must be a string.' % var_name
    assert isinstance(node, basestring), msg


def assert_cdefmodifiers(items, var_name):
    msg = '%s must be cdefmodifier nodes.' % var_name
    for item in items:
        assert isinstance(item, cdefmodifier), msg


def assert_ctype(node, var_name):
    msg = '%s must be a ctype node.' % var_name
    assert isinstance(node, ctype), msg


#------------------------------------------------------------------------------
# Base ast node
#------------------------------------------------------------------------------
class CWAN(object):
    """ The base class of all CWrap Ast Nodes. 

    """
    def __init__(self, *args, **kwargs):
        self.init(*args, **kwargs)

    def init(self, *args, **kwargs):
        pass


#------------------------------------------------------------------------------
# Python AST nodes (closely mimic the builtin ast module nodes)
#------------------------------------------------------------------------------
class mod(CWAN):
    pass


class Module(mod):
    """ A module node. Inherits mod.

    body : A list of stmt nodes.

    """
    def init(self, body):
        assert_stmts(body, 'body')
        self.body = body


class stmt(CWAN):
    pass


class FunctionDef(stmt):
    """ A function definition. Inherits stmt.

    name : The string name of the function.
    args : An arguments node.
    body : A list of stmt nodes.
    decorator_list : A list of expr nodes.

    """
    def init(self, name, args, body, decorator_list):
        assert_str(name, 'name')
        assert_stmts(body, 'body')
        assert_arguments(args, 'args')
        assert_exprs(decorator_list, 'decorator_list')
        self.name = name
        self.args = args
        self.body = body
        self.decorator_list = decorator_list


class ClassDef(stmt):
    """ A class definition. Inherits stmt.

    name : The string name of the class.
    bases : A list of expr nodes.
    body : A list of stmt nodes.
    decorator_list : A list of expr nodes.

    """
    def init(self, name, bases, body, decorator_list):
        assert_str(name, 'name')
        assert_exprs(bases, 'bases')
        assert_stmts(body, 'body')
        assert_exprs(decorator_list, 'decorator_list')
        self.name = name
        self.bases = bases
        self.body = body
        self.decorator_list = decorator_list


class Return(stmt):
    """ A return statement. Inherits stmt.

    value : An expr node. Can be None.

    """
    def init(self, value):
        if value:
            assert_expr(value, 'value')
        self.value = value


class Delete(stmt):
    """ A del statement. Inherits stmt.

    targets : A list of expr nodes.

    """
    def init(self, targets):
        assert_exprs(targets, 'targets')
        self.targets = targets


class Assign(stmt):
    """ An assignment. Inherits stmt.

    targets : a list of expr nodes
    value : an expr node

    """
    def init(self, targets, value):
        assert_exprs(targets, 'targets')
        assert_expr(value, 'value')
        self.targets = targets
        self.value = value


class AugAssign(stmt):
    """ Augmented (in-place) assignment. Inherits stmt.

    target : an expr node
    op : an operator node
    value : an expr node

    """
    def init(self, target, op, value):
        assert_expr(target, 'target')
        assert_operator(op, 'op')
        assert_expr(value, 'value')
        self.target = target
        self.op = op
        self.value = value


class Print(stmt):
    """ The print statement. Inherits stmt.

    dest : an expr node. Can be None.
    values : a list of expr nodes.
    nl : a boolean

    """
    def init(self, dest, values, nl):
        if dest:
            assert_expr(dest, 'dest')
        assert_exprs(values, 'values')
        assert_bool(nl, 'nl')
        self.dest = dest
        self.values = values
        self.nl = nl


class For(stmt):
    """ A For loop. Inherits stmt.

    target : an expr node.
    iter : an expr node.
    body : a list of stmt nodes.
    orelse : a list of stmt nodes.

    """
    def init(self, target, iter, body, orelse):
        assert_expr(target, 'target')
        assert_expr(iter, 'iter')
        assert_stmts(body, 'body')
        assert_stmts(orelse, 'orelse')
        self.target = target
        self.iter = iter
        self.body = body
        self.orelse = orelse


class While(stmt):
    """ A While loop. Inherits stmt.

    test : an expr node.
    body : a list of stmt nodes.
    orelse : a list of stmt nodes.

    """
    def init(self, test, body, orelse):
        assert_expr(test, 'test')
        assert_stmts(body, 'body')
        assert_stmts(orelse, 'orelse')
        self.test = test
        self.body = body
        self.orelse = orelse


class If(stmt):
    """ An If statment. Inherits stmt.

    test : an expr node.
    body : a list of stmt nodes.
    orelse : a list of stmt nodes.

    """
    def init(self, test, body, orelse):
        assert_expr(test, 'test')
        assert_stmts(body, 'body')
        assert_stmts(orelse, 'orelse')
        self.test = test
        self.body = body
        self.orelse = orelse


class With(stmt):
    """ A with statement. Inherits stmt.

    context_expr : an expr node
    optional_vars : an expr node. Can be None.
    body : a list of stmt nodes.

    """
    def init(self, context_expr, optional_vars, body):
        assert_expr(context_expr, 'context_expr')
        if optional_vars:
            assert_expr(optional_vars, 'optional_vars')
        assert_stmts(body, 'body')
        self.context_expr = context_expr
        self.optional_vars = optional_vars
        self.body = body


class Raise(stmt):
    """ A raise statment. Inherits stmt.

    type : an expr node. Can be None.
    inst : an expr node. Can be None.
    tback : an expr node. Can be None.

    """
    def init(self, type, inst, tback):
        if type:
            assert_expr(type, 'type')
        if inst:
            assert_expr(inst, 'inst')
        if tback:
            assert_expr(tback, 'tback')
        self.type = type
        self.inst = inst
        self.tback = tback


class TryExcept(stmt):
    """ A try except block. Inherits stmt.

    body : a list of stmt nodes.
    handlers : a list of excepthandler nodes.
    orelse : a list of stmt nodes.

    """
    def init(self, body, handlers, orelse):
        assert_stmts(body, 'body')
        assert_excepthandlers(handlers, 'handlers')
        assert_stmts(orelse, 'orelse')
        self.body = body
        self.handlers = handlers
        self.orelse = orelse


class TryFinally(stmt):
    """ A try finally block. Inherits stmt.

    body : a list of stmt nodes.
    finalbody : a list of stmt nodes.

    """
    def init(self, body, finalbody):
        assert_stmts(body, 'body')
        assert_stmts(finalbody, 'finalbody')
        self.body = body
        self.finalbody = finalbody


class Assert(stmt):
    """ Assert statement. Inherits stmt.

    test : an expr node.
    msg : an expr node. Can be None.

    """
    def init(self, test, msg):
        assert_expr(test, 'test')
        if msg:
            assert_expr(msg, 'msg')
        self.test = test
        self.msg = msg


class Import(stmt):
    """ Import statement. Inherits stmt.

    names : a list of alias nodes.

    """
    def init(self, names):
        assert_aliases(names, 'names')
        self.names = names


class ImportFrom(stmt):
    """ Import from statement. Inherits stmt.

    module : a string. Can be None.
    names : a list of alias nodes.
    level : an integer. Can be None.

    """
    def init(self, module, names, level):
        if module:
            assert_str(module, 'module')
        assert_aliases(names, 'names')
        if level:
            assert_int(level, 'level')
        self.module = module
        self.names = names
        self.level = level


class Exec(stmt):
    """ The exec statement. Inherits stmt.

    body : an expr node
    globals : an expr node. Can be None.
    locals : an expr node. Can be None.

    """
    def init(self, body, globals, locals):
        assert_expr(body, 'body')
        if globals:
            assert_expr(globals, 'globals')
        if locals:
            assert_expr(locals, 'locals')
        self.body = body
        self.globals = globals
        self.locals = locals


class Global(stmt):
    """ The global statement. Inherits stmt.

    names : a list of strings.

    """
    def init(self, names):
        assert_strs(names, 'names')
        self.names = names


class Expr(stmt):
    """ An expression node. Inherits stmt.
    
    value : an expr node. 
    
    """
    def init(self, value):
        assert_expr(value, 'value')
        self.value = value

class EnumValue(stmt):
    """ An expression node. Inherits stmt.

    value : an expr node.

    """
    def init(self, name, value, islast=0):
        assert_int(value, 'value')
        self.value = value
        assert_expr(name, 'name')
        self.name = name.id
        self.islast = islast


class Pass(stmt):
    """ The pass statement. Inherits stmt. Singleton.

    """
    pass
Pass = Pass()


class Break(stmt):
    """ The break statement. Inherits stmt. Singleton.

    """
    pass
Break = Break()


class Continue(stmt):
    """ The continue statement. Inherits stmt. Singleton.

    """
    pass
Continue = Continue()


class expr(CWAN):
    pass


class BoolOp(expr):
    """ A boolean operation. Inherits expr.

    op : a boolop node
    values : a list of expr nodes.

    """
    def init(self, op, values):
        assert_boolop(op, 'op')
        assert_exprs(values, 'values')
        self.op = op
        self.values = values


class BinOp(expr):
    """ A binary operation. Inherits expr.

    left : an expr node.
    op : an operator node.
    right : an expr node.

    """
    def init(self, left, op, right):
        assert_expr(left, 'left')
        assert_operator(op, 'op')
        assert_expr(right, 'right')
        self.left = left
        self.op = op
        self.right = right


class UnaryOp(expr):
    """ A unary operation. Inherits expr.

    op : a unaryop node.
    operand : an expr node.

    """
    def init(self, op, operand):
        assert_unaryop(op, 'op')
        assert_expr(operand, 'operand')
        self.op = op
        self.operand = operand


class Lambda(expr):
    """ A lambda expression. Inherits expr.

    args : an arguments node.
    body : and expr node.

    """
    def init(self, args, body):
        assert_arguments(args, 'args')
        assert_expr(body, 'body')
        self.args = args
        self.body = body


class IfExp(expr):
    """ An If expression. Inherits expr.

    test : an expr node.
    body : an expr node.
    orelse : an expr node

    """
    def init(self, test, body, orelse):
        assert_expr(test, 'test')
        assert_expr(body, 'body')
        assert_expr(orelse, 'orelse')
        self.test = test
        self.body = body
        self.orelse = orelse


class Dict(expr):
    """ A dictionary literal. Inherits expr.

    keys : a list of expr nodes.
    values : a list of expr nodes.

    """
    def init(self, keys, values):
        assert_exprs(keys, 'keys')
        assert_exprs(values, 'values')
        msg = 'keys and values not same lenght'
        assert len(keys) == len(values), msg
        self.keys = keys
        self.values = values


class Set(expr):
    """ A set literal. Inherits expr.
    
    elts : A list of expr nodes.

    """
    def init(self, elts):
        assert_exprs(elts, 'elts')
        assert elts, 'Set literal cannot be empty.'
        self.elts = elts


class ListComp(expr):
    """ A list comprehension. Inherits expr.

    elt : an expr node.
    generators : a list of comprehension nodes.

    """
    def init(self, elt, generators):
        assert_expr(elt, 'elt')
        assert_comprehensions(generators, 'generators')
        self.elt = elt
        self.generators = generators


class SetComp(expr):
    """ A set comprehension. Inherits expr.

    elt : an expr node.
    generators : a list of comprehension nodes.

    """
    def init(self, elt, generators):
        assert_expr(elt, 'elt')
        assert_comprehensions(generators, 'generators')
        self.elt = elt
        self.generators = generators


class DictComp(expr):
    """ A dictionary comprehension. Inherits expr.

    key : an expr node.
    value : an expr node.
    generators : a list of comprehension nodes.

    """
    def init(self, key, value, generators):
        assert_expr(key, 'key')
        assert_expr(value, 'value')
        assert_comprehensions(generators, 'generators')
        self.key = key
        self.value = value
        self.generators = generators


class GeneratorExp(expr):
    """ A generator expression. Inherits expr.

    elt : an expr node.
    generators : a list of comprehension nodes.

    """
    def init(self, elt, generators):
        assert_expr(elt, 'elt')
        assert_comprehensions(generators, 'generators')
        self.elt = elt
        self.generators = generators


class Yield(expr):
    """ A yield expression. Inherits expr.

    value : an expr node. Can be None.

    """
    def init(self, value):
        if value:
            assert_expr(value, 'value')
        self.value = value


class Compare(expr):
    """ A compare expression. Inherits expr.

    left : an expr node.
    ops : a list of cmpop nodes.
    comparators : a list of expr node.

    """
    def init(self, left, ops, comparators):
        assert_expr(left, 'left')
        assert_cmpops(ops, 'op')
        assert_exprs(comparators, 'comparators')
        msg = 'ops and comparators must have same length'
        assert len(ops) == len(comparators), msg
        self.left = left
        self.ops = ops
        self.comparators = comparators


class Call(expr):
    """ A call node. Inherits expr.

    func : an expr node.
    args : a list of expr nodes.
    keywords : a list keyword nodes.
    starargs : an expr node. Can be None.
    kwargs : an expr node. Can be None.

    """
    def init(self, func, args, keywords, starargs, kwargs):
        assert_expr(func, 'func')
        assert_exprs(args, 'args')
        assert_keywords(keywords, 'keywords')
        if starargs:
            assert_expr(starargs, 'starargs')
        if kwargs:
            assert_expr(kwargs, 'kwargs')
        self.func = func
        self.args = args
        self.keywords = keywords
        self.starargs = starargs
        self.kwargs = kwargs


class Repr(expr):
    """ A repr node (backquotes). Inherits expr.

    value : an expr node.

    """
    def init(self, value):
        assert_expr(value, 'value')
        self.value = value


class Num(expr):
    """ A number node. Inherits expr.

    n : A Python number.

    """
    def init(self, n):
        assert_num(n, 'n')
        self.n = n


class Str(expr):
    """ A string node. Inherits expr.

    s : A Python string.

    """
    def init(self, s):
        assert_basestring(s, 's')
        self.s = s


class Attribute(expr):
    """ Attribute access node. Inherits expr.

    value : an expr node.
    attr : a string.
    ctx : an expr_context node.

    """
    def init(self, value, attr, ctx):
        assert_expr(value, 'value')
        assert_str(attr, 'attr')
        assert_expr_context(ctx, 'ctx')
        self.value = value
        self.attr = attr
        self.ctx = ctx


class Subscript(expr):
    """ Subsript access node. Inherits expr.

    value : an expr node.
    slice : a slice node.
    ctx : an expr_context node.

    """
    def init(self, value, slice, ctx):
        assert_expr(value, 'value')
        assert_slice(slice, 'slice')
        assert_expr_context(ctx, 'ctx')
        self.value = value
        self.slice = slice
        self.ctx = ctx


class Name(expr):
    """ A name node. Inherits expr.

    id : a string.
    ctx : an expr_context node.

    """
    def init(self, id, ctx):
        assert_str(id, 'id')
        assert_expr_context(ctx, 'ctx')
        self.id = id
        self.ctx = ctx


class List(expr):
    """ A list listeral. Inherits expr.

    elts : a list of expr nodes.
    ctx : an expr_context node.

    """
    def init(self, elts, ctx):
        assert_exprs(elts, 'elts')
        assert_expr_context(ctx, 'ctx')
        self.elts = elts
        self.ctx = ctx


class Tuple(expr):
    """ A tuple literal. Inherits expr.

    elts : a list of expr nodes.
    ctx : an expr_context node.

    """
    def init(self, elts, ctx):
        assert_exprs(elts, 'elts')
        assert_expr_context(ctx, 'ctx')
        self.elts = elts
        self.ctx = ctx


class expr_context(CWAN):
    pass


class Load(expr_context):
    pass
Load = Load()


class Store(expr_context):
    pass
Store = Store()


class Del(expr_context):
    pass
Del = Del()


class AugLoad(expr_context):
    pass
AugLoad = AugLoad()


class AugStore(expr_context):
    pass
AugStore = AugStore()


class Param(expr_context):
    pass
Param = Param()


class slice(CWAN):
    pass


class Ellipsis(slice):
    """ The Ellipsis object. Inherits slice. Singleton.

    """
    pass
Ellipsis = Ellipsis()


class Slice(slice):
    """ A slice node. Inherits slice.

    lower : an expr node. Can be None.
    upper : an expr node. Can be None.
    step : an expr node. Can be None.

    """
    def init(self, lower, upper, step):
        if lower:
            assert_expr(lower, 'lower')
        if upper:
            assert_expr(upper, 'upper')
        if step:
            assert_expr(step, 'step')
        self.lower = lower
        self.upper = upper
        self.step = step


class ExtSlice(slice):
    """ An extended slice node. Inherits slice.

    dims : a list of slice nodes.

    """
    def init(self, dims):
        assert_slices(dims, 'dims')
        self.dims = dims


class Index(slice):
    """ An index node. Inherits slice.

    value : an expr node.

    """
    def init(self, value):
        assert_expr(value)
        self.value = value


class boolop(CWAN):
    pass


class And(boolop):
    pass
And = And()


class Or(boolop):
    pass
Or = Or()


class operator(CWAN):
    pass


class Add(operator):
    pass
Add = Add()


class Sub(operator):
    pass
Sub = Sub()


class Mult(operator):
    pass
Mult = Mult()


class Div(operator):
    pass
Div = Div()


class Mod(operator):
    pass
Mod = Mod()


class Pow(operator):
    pass
Pow = Pow()


class LShift(operator):
    pass
LShift = LShift()


class RShift(operator):
    pass
RShift = RShift()


class BitOr(operator):
    pass
BitOr = BitOr()


class BitXor(operator):
    pass
BitXor = BitXor()


class BitAnd(operator):
    pass
BitAnd = BitAnd()


class FloorDiv(operator):
    pass
FloorDiv = FloorDiv()


class unaryop(CWAN):
    pass


class Invert(unaryop):
    pass
Invert = Invert()


class Not(unaryop):
    pass
Not = Not()


class UAdd(unaryop):
    pass
UAdd = UAdd()


class USub(unaryop):
    pass
USub = USub()


class cmpop(CWAN):
    pass


class Eq(cmpop):
    pass
Eq = Eq()


class NotEq(cmpop):
    pass
NotEq = NotEq()


class Lt(cmpop):
    pass
Lt = Lt()


class LtE(cmpop):
    pass
LtE = LtE()


class Gt(cmpop):
    pass
Gt = Gt()


class GtE(cmpop):
    pass
GtE = GtE()


class Is(cmpop):
    pass
Is = Is()


class IsNot(cmpop):
    pass
IsNot = IsNot()


class In(cmpop):
    pass
In = In()


class NotIn(cmpop):
    pass
NotIn = NotIn()


class comprehension(CWAN):
    """ A comprehension node. 

    target : an expr node.
    iter : an expr node.
    ifs : a list of expr nodes.

    """
    def init(self, target, iter, ifs):
        assert_expr(target)
        assert_expr(iter)
        assert_exprs(ifs)
        self.target = target
        self.iter = iter
        self.ifs = ifs


class excepthandler(CWAN):
    pass


class ExceptHandler(excepthandler):
    """ Exception Handlers. Inherits excepthandler.

    type : an expr node. Can be None.
    name : an expr node. Can be None.
    body : a list of stmt nodes.

    """
    def init(self, type, name, body):
        if type:
            assert_expr(type, 'type')
        if name:
            assert_expr(name, 'name')
            assert type, 'Cannot have exception name and not type.'
        assert_stmts(body, 'body')
        self.type = type
        self.name = name
        self.body = body


class arguments(CWAN):
    """ Arguments node.

    args : a list of expr nodes.
    vararg : a string. Can be None.
    kwarg : a string. Can be None.
    defaults : a list of expr nodes.

    """
    def init(self, args, vararg, kwarg, defaults):
        assert_exprs(args, 'args')
        if vararg:
            assert_str(vararg, 'vararg')
        if kwarg:
            assert_str(kwarg, 'kwarg')
        assert_exprs(defaults, 'defaults')
        self.args = args
        self.vararg = vararg
        self.kwarg = kwarg
        self.defaults = defaults


class keyword(CWAN):
    """ A keyword node. 

    arg : a string.
    value : an expr node.

    """
    def init(self, arg, value):
        assert_str(arg, 'arg')
        assert_expr(value, 'value')
        self.arg = arg
        self.value = value


class alias(CWAN):
    """ An alias node for 'as' import.

    name : a string.
    asname : a string. Can be None.

    """
    def init(self, name, asname):
        assert_str(name)
        if asname:
            assert_str(asname)
        self.name = name
        self.asname = asname


#------------------------------------------------------------------------------
# Cython AST nodes
#------------------------------------------------------------------------------
class cdefmodifier(CWAN):
    pass


class Extern(cdefmodifier):
    pass
Extern = Extern()


class Inline(cdefmodifier):
    pass
Inline = Inline()


class Public(cdefmodifier):
    pass
Public = Public()


class Api(cdefmodifier):
    pass
Api = Api()


class CdefDecl(stmt):
    """ A cdef declaration. Inherits stmt.

    modifiers : A list of cdefmodifier nodes.
    value : A stmt node.

    """
    def init(self, modifiers, value):
        assert_cdefmodifiers(modifiers, 'modifiers')
        assert_stmt(value, 'value')
        self.modifiers = modifiers
        self.value = value


class CpdefDecl(stmt):
    """ A cpdef declaration. Inherits stmt.

    value : A stmt node.

    """
    def init(self, value):
        assert_stmt(value, 'value')
        self.value = value


class CFunctionDecl(stmt):
    """ A C function declaration. Inherits stmt.

    name : The string name of the function.
    args : An arguments node.
    returns : A ctype node. Can be None.
    excepts : An expr node. Can be None.

    """
    def init(self, name, args, returns, excepts):
        assert_str(name, 'name')
        assert_arguments(args, 'args')
        if returns:
            assert_ctype(returns, 'returns')
        if excepts:
            assert_expr(excepts, 'excepts')
        self.name = name
        self.args = args
        self.returns = returns
        self.excepts = excepts


class CFunctionDef(stmt):
    """ A C function definition. Inherits stmt.

    name : The string name of the function.
    args : An arguments node.
    body : A list of stmt nodes.
    decorator_list : A list of expr nodes.
    returns : A ctype node. Can be None.
    excepts : An expr node. Can be None.

    """
    def init(self, name, args, body, decorator_list, returns, excepts):
        assert_str(name, 'name')
        assert_stmts(body, 'body')
        assert_arguments(args, 'args')
        assert_exprs(decorator_list, 'decorator_list')
        if returns:
            assert_ctype(returns, 'returns')
        if excepts:
            assert_expr(excepts, 'excepts')
        self.name = name
        self.args = args
        self.body = body
        self.decorator_list = decorator_list
        self.returns = returns
        self.excepts = excepts


class CImport(stmt):
    """ Import statement. Inherits stmt.

    names : a list of alias nodes.

    """
    def init(self, names):
        assert_aliases(names, 'names')
        self.names = names


class CImportFrom(stmt):
    """ Cimport from statement. Inherits stmt.

    module : a string. Can be None.
    names : a list of alias nodes.
    level : an integer. Can be None.

    """
    def init(self, module, names, level):
        if module:
            assert_str(module, 'module')
        assert_aliases(names, 'names')
        if level:
            assert_int(level, 'level')
        self.module = module
        self.names = names
        self.level = level


class CTypedefDecl(stmt):
    """ A ctypedef declarations. Inherits stmt.

    value : a stmt node.

    """
    def init(self, value):
        assert_stmt(value, 'value')
        self.value = value


class StructDef(stmt):
    """ A struct definition. Inherits stmt.

    name : a string.
    body : a list of stmt nodes.

    """
    def init(self, name, body):
        assert_str(name, 'name')
        assert_stmts(body, 'body')
        self.name = name
        self.body = body


class UnionDef(stmt):
    """ A union definition. Inherits stmt.

    name : a string.
    body : a list of stmt nodes.

    """
    def init(self, name, body):
        assert_str(name, 'name')
        assert_stmts(body, 'body')
        self.name = name
        self.body = body


class EnumDef(stmt):
    """ An enum definition. Inherits stmt.

    name : a string. Can be None.
    body : A list of stmt nodes.

    """
    def init(self, name, body):
        if name:
            assert_str(name, 'name')
        assert_stmts(body, 'body')
        self.name = name
        self.body = body


class Property(stmt):
    """ A cdef property. Inherits stmt.

    name : a string.
    body : a list of stmt nodes.

    """
    def init(self, name, body):
        assert_str(name, 'name')
        assert_stmts(body, 'body')
        self.name = name
        self.body = body


class ExternFrom(stmt):
    """ An extern from declaration. Inherits stmt.

    name : a string
    body : a list of stmt nodes.

    """
    def init(self, name, body):
        assert_str(name, 'name')
        assert_stmts(body, 'body')
        self.name = name
        self.body = body


class CName(expr):
    """ A C name with a type. Inherits expr.

    ctype : a ctype node.
    name : a string

    """
    def init(self, ctype, name):
        assert_ctype(ctype, 'ctype')
        assert_str(name, 'name')
        self.ctype = ctype
        self.name = name


class ctype(CWAN):
    pass


class TypeName(ctype):
    """ A C type name. Inherits ctype.

    name : an expr node.

    """
    def init(self, name, const=False, volatile=False):
        assert_expr(name, 'name')
        self.name = name
        self.const = const
        self.volatile = volatile


class CFunctionType(ctype):
    """ A C function type. Inherits ctype.
    
    args : an arguments node.
    returns : a ctype node. Can be None.
    
    """
    def init(self, args, returns):
        assert_arguments(args, 'args')
        if returns:
            assert_ctype(returns, 'returns')
        self.args = args
        self.returns = returns


class Pointer(ctype):
    """ A pointer node. Inherits ctype.

    value : a ctype node.

    """
    def init(self, value, const=False, volatile=False):
        assert_ctype(value, 'value')
        self.value = value
        self.const = const
        self.volatile = volatile


class Array(ctype):
    """ An array node. Inherits ctype.

    value : a ctype node.
    dim : an integer

    """
    def init(self, value, dim):
        assert_ctype(value, 'value')
        assert_int(dim, 'dim')
        self.value = value
        self.dim = dim

class CppClassDef(stmt):
    """ A cppclass definition. Inherits stmt.

    name : The string name of the class.
    body : A list of stmt nodes.
    #TODO: add template arguments

    """
    def init(self, name, body):
        assert_str(name, 'name')
        assert_stmts(body, 'body')
        self.name = name
        self.body = body

class Reference(ctype):
    """ A C++ reference node. Inherits ctype.

    value : a ctype node.

    """
    def init(self, value):
        assert_ctype(value, 'value')
        self.value = value




