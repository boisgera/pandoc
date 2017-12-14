
# Python 2.7 Standard Library
from __future__ import absolute_import, print_function
try:
    import builtins
except ImportError:
    import __builtin__ as builtins
import collections

# Third-Party Libraries
import pkg_resources

# Pandoc
import pandoc.utils

# Metadata
# ------------------------------------------------------------------------------
version = "1.16"

# Typechecking & Error Reporting
# ------------------------------------------------------------------------------

# Typecheck method on Data stuff. Won't work with native typedefs or Typedefs.
# So we also offer a typecheck FUNCTION with the type as a first argument.
# Both the method and the function can be recursive or not (and this is no
# by default)?
# Nota: error message MATTERS here. And in recursive mode, 
# we should be smart and display some information in context of the 
# original call/check.
#
# Usage: 
#   - Automatic deep check before JSON write
#   - (shallow) check on instance creation, to get the errors asap
#   - Manual thorough check whenever the user feels like it

# NOTA: strings or signature type argument should stay internal/private.
#       That makes a smaller surface for errors (and error checking).

# TODO: error formatting. Use a stack for errors? Stack errors at
#       different levels? Does Python exception already do that?
#       or shall we replicate this stuff?

# NOTA: the constructor info is missing for a proper error message :(
# TODO: use a str repr of the types in error checking.
def check_args(args, type_signature, deep=True):
    kind, sub_types = type_signature
    if kind == "list": # classic type
        if len(args) != len(sub_types):
            error = "expected {0} argument(s) ({1} given)\n"
            error = error.format(len(sub_types), len(args))
            error += "arguments: {0!r}\n".format(args)
            error += "should be: {0!r}".format(sub_types)
            raise TypeError(error)
        for arg, sub_type in zip(args, sub_types):
            check(arg, sub_type, deep=deep)
    elif kind == "map": # record type
        key_value_types = sub_types
        sub_types = [key_value[1] for key_value in key_value_types]
        if len(args) != len(key_value_types):
            error = "expected {0} argument(s) ({1} given)\n"
            error = error.format(len(sub_types), len(args))
            error += "arguments: {0!r}\n".format(args)
            error += "should be: {0!r}".format(sub_types)
            raise TypeError(error)
            raise TypeError(error)
        for arg, sub_type in zip(args, sub_types):
            check(arg, sub_type, deep=deep)

def check(instance, type, deep=True): 

    # WRT the default: deep=True is simpler. The user could live without
    # deep=False, not without deep=True ...

    # 'recursive' or 'deep' ? Accept True/Number/False?
    # 'depth' instead? Use "total" (vs partial ?)

    # accept "no type" ? Would make SOME sense to check a pandoc type ...
    # But then maybe that's what the method would be for ? And then
    # what would be the interaction with deep? If the check is totally
    # shallow, this is stupid (equivalent to isinstance). So in this
    # case, shallow would be "one depth level" and deep the usual?
    # Beuah, dunno, then the difference of behavior between the function
    # and the method would be hard to explain. UNLESS we only advertise
    # the method?

    # TODO: type is either:
    #
    #  1. a Data type (abstract) 
    #  2. a Constructor type
    #  3. a TypeDef type
    #  4. a Primitive type 
    #  
    # To check 4, we rely on isinstance.
    # To check 1, we check that we have an instance
    # that is derived from the abstract data type, 
    # then we call typecheck again with the same instance 
    # but the constructor type.
    # To check 2, we check with instance, check every
    # argument vs the part of the signature for it.
    # The check for 3 is similar, we have a single argument
    # and a signature.
    # So the crux of this is to check and arguments vs
    # a signature made of lists, maps, tuples and names that
    # refer to types. For these names, we get the type
    # and perform a shallow (isinstance-based) check if not
    # recursive or ... nothing for typedefs? Or ... what?
    # Deep for typedefs? Dunno. Well it's probably easier
    # to recurse everything but Pandoc types.

    if isinstance(type, str): # simple type signature
        type_name = type
        type = _types_dict[type_name]
        check(instance, type)
    elif isinstance(type, list): # complex type signature
        type_signature = type
        decl_type = type_signature[0]
        if decl_type in ["data", "newtype"]:
           type_name, constructors = type_signature[1]
           abstract_type = _types_dict[type_name]
           if not isinstance(instance, abstract_type):
                error = "{0!r} is not an instance of {1!r}"
                error = error.format(instance, abstract_type.__name__)
                raise TypeError(error)
           concrete_type = builtins.type(instance)
           check(instance, concrete_type)
        elif decl_type == "type":
           decl = type_signature[1][1]
           check(instance, decl)
        elif decl_type == "list": 
            item_type = type_signature[1][0]
            if not isinstance(instance, list):
                error = "{0!r} is not a list".format(instance)
                raise TypeError(error)
            for item in instance:
                check(item, item_type)
        elif decl_type == "tuple":
            item_types = type_signature[1]
            if not isinstance(instance, list):
                error = "{0!r} is not a list".format(instance)
                raise TypeError(error)
            if not len(item_types) == len(instance):
                error  = "expecting a list of {0} items (found {1})\n"
                error  = error.format(len(item_type), len(instance)) 
                error += "expected: " + repr(item_types)
                error += "got:      " + repr(instance)
                raise TypeError(error)
            for item, item_type in zip(instance, item_types):
                check(item, item_types)
        elif decl_type == "map":
            key_type, value_type = type_signature[1]           
            if not isinstance(instance, dict):
                error = "expected a dict (got a {0!r})\n"
                error = error.format(builtins.type(instance))
                error += "got: " + repr(instance)
                raise TypeError(error)
            for key, value in instance.items():
                check(key, key_type)
                check(value, value_type)
        else: # constructor
            constructor_type = _types_dict[type_signature[0]]
            if not isinstance(instance, constructor_type):
                error = "{0!r} is not an instance of {1}"
                error = error.format(instance, constructor_type.__name__)
                raise TypeError(error)
            check_args(instance[:], type_signature[1], deep=deep)
    elif builtins.type(type) is builtins.type: # type, not type signature
        if issubclass(type, Type): # Pandoc type
            check(instance, type._def) # check against type signature
        else: # Primitive type
          if not isinstance(instance, type):
            error = "{0!r} is not an instance of {1}"
            error = error.format(instance, type.__name__)
            raise TypeError(error)

    else:
       pass
       # should not happen ... but do we raise a TypeError?
       # That would conflate a user mistake and a negative check ...
       # Or we can return ValueErrors for check (urk!) or a specific
       # pandoc.Typeerror derived stuff ...

# Haskell Type Constructs
# ------------------------------------------------------------------------------

# TODO: support position parameters for record types?
#       First have a look at the use cases: Meta (see deconstructor in Haskell
#       literature) and Citation. Also, drop the prefix when it's the
#       type name and go from CamelCase to kebab-case?

def _fail_init(self, *args, **kwargs):
    type_name = type(self).__name__
    error = "cannot instantiate abstract type {type}"
    raise NotImplementedError(error.format(type=type_name))

class Type(object):
    __init__ = _fail_init

class Data(Type):
    pass

class Constructor(Data):
    def __init__(self, *args):
        if type(self) is Constructor:
            _fail_init(self, *args)
        else:
            check_args(args, self._def[1])
            self._args = list(args)
    def __iter__(self):
        return iter(self._args)
    def __getitem__(self, key):
        return self._args[key]
    def __setitem__(self, key, value):
        self._args[key] = value
    def __len__(self):
        return len(self._args)
    def __eq__(self, other):
         return type(self) == type(other) and self[:] == other[:]
    def __neq__(self, other):
         return not (self == other)
    def __repr__(self):
        typename = type(self).__name__
        args = ", ".join(repr(arg) for arg in self)
        return "{0}({1})".format(typename, args)
    __str__ = __repr__

class TypeDef(Type):
    pass
    

# Pandoc Types
# ------------------------------------------------------------------------------

_types_dict = {}

def _make_builtin_types():
    "Create Builtin Types"
    td = _types_dict
    td["Bool"] = bool
    td["Double"] = float
    td["Int"] = int
    try:
        td["String"] = unicode
    except NameError:
        td["String"] = str
    td["list"] = list
    td["tuple"] = tuple
    td["map"] = type("map", (collections.OrderedDict,), {"__eq__": dict.__eq__})

def make_types(version=version):
    """Create Pandoc Types"""

    global _types_dict
    globs = globals()
    # Update the module version
    globs["version"] = version

    # Uninstall the types from the previous call
    for type_name in _types_dict:
      del globs[type_name]
    _types_dict = {}

    # Create builtin types
    _make_builtin_types()

    # Load & parse the types definition
    defs_path = "definitions/{0}.hs".format(version)
    defs_src = pkg_resources.resource_string("pandoc", defs_path)
    if not isinstance(defs_src, str): # resource loaded as bytes in Python 3
        defs_src = defs_src.decode("utf-8")
    defs = pandoc.utils.parse(defs_src)

    # Create the types
    for decl in defs:
        decl_type = decl[0]
        type_name = decl[1][0]
        _dict = {"_def": decl, "__doc__": pandoc.utils.docstring(decl)}
        if decl_type in ("data", "newtype"):
            data_type = type(type_name, (Data,), _dict)
            _types_dict[type_name] = data_type
            # Remark: when there is a constructor with the same name as its
            #         data type, the data type is shadowed. 
            #         This is intentional, but it's only consistent because 
            #         it happens when there is a single constructor. 
            #         That's merely a happy accident from the pandoc types
            #         definition, not something enforced by Haskell.
            # TODO: add an assert / check for this condition.
            for constructor in decl[1][1]:
                constructor_name = constructor[0]
                bases = (Constructor, data_type)
                _dict = {"_def": constructor, 
                         "__doc__": pandoc.utils.docstring(constructor)}
                type_ = type(constructor_name, bases, _dict)
                _types_dict[constructor_name] = type_
        elif decl_type == "type": 
            type_ = type(type_name, (TypeDef,), _dict)
            _types_dict[type_name] = type_

    # Install the types
    globs.update(_types_dict)
    
make_types()

