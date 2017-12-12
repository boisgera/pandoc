
# Python 2.7 Standard Library
from __future__ import absolute_import, print_function
import builtins
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

def check(instance, type, deep=True): 

    # WRT the default: deep=True is simpler. The user could live without
    # deep=False, not without deep=True ...

    # 'recursive' or 'deep' ? Accept True/Number/False?
    # 'depth' instead?

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
        type = _types_dict[type]
        check(instance, type)
    elif isinstance(type, list): # complex type signature
        decl_type = type[0]
        if decl_type in ["data", "newtype"]:
           type_name = type[1][0]
           constructors = type[1][1]
           if not isinstance(instance, _types_dict[type_name]):
               raise TypeError()
           actual_type = builtins.type(instance)
           check(instance, actual_type)
        elif decl_type == "typedef":
           decl = type[1][1]
           check(instance, decl)
        elif decl_type == "list": 
            item_type = type[1][0]
            if not isinstance(instance, list):
                raise TypeError()
            for item in instance:
                check(item, item_type)
        elif decl_type == "tuple":
            item_types = type[1]
            if not isinstance(instance, list):
                raise TypeError()
            if not len(item_type) == len(instance):
                raise TypeError()
            for item, item_type in zip(instance, item_types):
                check(item, item_types)
        elif decl_type == "map":
            key_type, value_type = type[1][0], type[1][1]            
            if not isinstance(instance, dict):
                raise TypeError()
            for key, value in instance.items():
                check(key, key_type)
                check(value, value_type)
        else: # constructor
            constructor_type = _types_dict[type[0]]
            if builtins.type(instance) != constructor_type:
                 raise TypeError
            if deep:
                if type[1][0] == "list": # classic type
                    sub_types = type[1][1]
                    if len(instance) != len(sub_types):
                        raise TypeError()
                    for item, sub_type in zip(instance, sub_types):
                        check(item, sub_type)
                elif type[1][0] == "map": # record type
                    key_value_types = type[1][1]
                    if len(instance) != len(key_value_types):
                        error = "** {0} {1}".format(instance, key_value_types) 
                        raise TypeError(error)
                    sub_types = [key_value[1] for key_value in key_value_types]
                    for item, sub_type in zip(instance, sub_types):
                        check(item, sub_type)
    else: # check vs actual type, not signature.
        if builtins.type(type) is builtins.type and issubclass(type, Type):
            # Pandoc types, use signature
            check(instance, type._def)
        elif not isinstance(instance, type):
            # Primitive types
            raise TypeError()


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

