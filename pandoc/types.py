
# Python 2.7 Standard Library
from __future__ import absolute_import, print_function
try:
    import builtins
except ImportError:
    import __builtin__ as builtins
import collections
import inspect
import pydoc

# Third-Party Libraries
import pkg_resources

# Pandoc
import pandoc.utils
from pandoc.utils import signature

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
#   - Automatic full check before JSON write
#   - (shallow) check on instance creation, to get the errors asap
#   - Manual thorough check whenever the user feels like it

# NOTA: strings or signature type argument should stay internal/private.
#       That makes a smaller surface for errors (and error checking).

# TODO: error formatting. Use a stack for errors? Stack errors at
#       different levels? Does Python exception already do that?
#       or shall we replicate this stuff?

# NOTA: the constructor info is missing for a proper error message :(
# TODO: use a str repr of the types in error checking.

def annotate(exception, message):
    exception_type = type(exception)
    args = list(exception.args)
    if not message.endswith("\n"):
        message += "\n"
    args[0] = message + args[0]
    return exception_type(*args)     

# TODO: recognize summary / details in messages & format accordingly?
#       Like, i don't know, *indent* the details?
#       recognize them like pydoc would do it? 
class TypeError(builtins.TypeError):
    def __init__(self, message):
        self.messages = []
        self.log(message)
    def log(self, message):
        message = inspect.cleandoc(message)
        summary, details = pydoc.splitdoc(message)
        message = summary.strip() + "\n" + \
                  "\n".join(4*" " +  line for line in details.splitlines())
        self.messages = [message] + self.messages
        self.args = ("\n".join(self.messages),)

sr = lambda decl: str(pandoc.utils.signature(decl))

def place(i):
    special = {1: "1st", 2: "2nd", 3: "3rd"}
    if 1 <= i + 1 <=3:
        return special[i + 1]
    else:
        return "{0}th".format(i + 1)

def invalid_argument(type_decl, i):
    sig = signature(type_decl)
    start, end = sig.locate(i)
    return str(sig) + "\n" + " " * start + "^" * (end - start) 

def check_args(args, type, full=True):
    type_signature = type._def
    type_signature_repr = sr(type_signature)
    type_name = type_signature[0]
    kind, type_args = type_signature[1]
    if kind == "map": # record type, get rid of the type arguments name
        type_args = [type_arg for key, type_arg in type_args]

    # Check the number of arguments
    if len(args) != len(type_args):
        if len(type_args) == 0:
            summary = "{type_name}(...) takes no argument"
            summary = summary.format(type_name=type_name)
        elif len(type_args) == 1:
            summary = "{type_name}(...) takes exactly 1 argument"
            summary = summary.format(type_name=type_name)
        else:
            summary = "{type_name}(...) takes exactly {0} arguments"
            summary = summary.format(len(type_args), type_name=type_name)
        summary += " ({0} given).".format(len(args))
        details = "signature: " + type_signature_repr
        message = summary + "\n\n" + details
        raise TypeError(message)

    # Check the arguments type
    for i, (arg, type_arg) in enumerate(zip(args, type_args)):
        try:
            check(arg, type_arg, full=full)
        except TypeError as error:
            summary = "invalid argument in {type_name}(...) ({0} place)."
            summary = summary.format(place(i), type_name=type_name)
            details = invalid_argument(type_signature, i)
            message = summary + "\n\n" + details               
            error.log(message)                
            raise

def check(instance, type, full=True):
    # TODO: for all recursive check, try/catch & augment the error message
    if isinstance(type, str): # simple type signature
        type_name = type
        type = _types_dict[type_name]
        try:
            check(instance, type)
        except TypeError as error:
            message = "{0!r} is not an instance of {1}"
            message = message.format(instance, type_name)
            if type_name != type.__name__:
              details = "Pandoc {0!r} type is Python {1!r} type"
              details = details.format(type_name, type.__name__)
              message += "\n\n" + details
            error.log(message)
            raise
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
            if not isinstance(instance, tuple):
                error = "{0!r} is not a tuple".format(instance)
                raise TypeError(error)
            if not len(item_types) == len(instance):
                summary = "expecting a tuple of {0} items (found {1})"
                summary = summary.format(len(item_types), len(instance)) 
                details = "expected: {0!r}\n".format(item_types)
                details += "got:      {0!r}".format(instance)
                raise TypeError(summary + "\n\n" + details)
            for item, item_type in zip(instance, item_types):
                check(item, item_type)
        elif decl_type == "map":
            key_type, value_type = type_signature[1]           
            if not isinstance(instance, dict):
                summary = "expected a dict (got a {0!r})"
                summary = summary.format(builtins.type(instance).__name__)
                details = "got: " + repr(instance)
                raise TypeError(summary + "\n\n" + details)
            for i, (key, value) in enumerate(instance.items()):
                try:
                    check(key, key_type)
                except TypeError as error:
                  summary = "invalid key in {map} ({0} place)."
                  summary = summary.format(place(i), map=signature(type_signature))
                  error.log(summary)
                  raise
                try:
                    check(value, value_type)
                except TypeError as error:
                  summary = "invalid value in {map} ({0} place)."
                  summary = summary.format(place(i), map=signature(type_signature))
                  error.log(summary)
                  raise
        else: # constructor 
            constructor_type = _types_dict[type_signature[0]]
            if not isinstance(instance, constructor_type):
                error = "{0!r} is not an instance of {1}"
                error = error.format(instance, constructor_type.__name__)
                raise TypeError(error)
            check_args(instance[:], constructor_type, full=full)
    elif builtins.type(type) is builtins.type: # type, not type decl
        if issubclass(type, Type): # Pandoc type
            check(instance, type._def) # check against type decl
        else: # Primitive type
          if not isinstance(instance, type):
            error = "{0!r} is not an instance of {1}"
            error = error.format(instance, type.__name__)
            raise TypeError(error)
    else:
       raise builtins.TypeError() # TODO: details here.

# Haskell Type Constructs
# ------------------------------------------------------------------------------

# TODO: support position parameters for record types?
#       First have a look at the use cases: Meta (see deconstructor in Haskell
#       literature) and Citation. Also, drop the prefix when it's the
#       type name and go from CamelCase to kebab-case?

# TODO: details in the error ? Give the constructors or send to help() ?
# TODO: upgrade to manage the attempt to instantiate a typedef
def _fail_init(self, *args, **kwargs):
    type_name = type(self).__name__
    error = "cannot instantiate abstract type {type_name}."
    raise NotImplementedError(error.format(type_name=type_name))

class Type(object):
    __init__ = _fail_init

class Data(Type):
    pass

# TODO: custom repr to see the signatures? Arf would mean metaclass hacking :(

class Constructor(Data):
    def __init__(self, *args):
        if type(self) is Constructor:
            _fail_init(self, *args)
        else:
            check_args(args, type(self))
            self._args = list(args)
    def check(self, full=True):
        check(self, type(self))
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

# TODO: get a custom "_fail_init" for typedefs?
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
        _dict = {"_def": decl, "__doc__": str(pandoc.utils.signature(decl))}
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
                         "__doc__": str(pandoc.utils.signature(constructor))}
                type_ = type(constructor_name, bases, _dict)
                _types_dict[constructor_name] = type_
        elif decl_type == "type": 
            type_ = type(type_name, (TypeDef,), _dict)
            _types_dict[type_name] = type_

    # Install the types
    globs.update(_types_dict)
    
make_types()

