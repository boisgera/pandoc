# coding: utf-8

# Python 3 Standard Library
import builtins
import collections
import inspect
import pydoc
import sys

# Third-Party Libraries
import pkg_resources

# Pandoc
import pandoc
import pandoc.utils


# Haskell Type Constructs
# ------------------------------------------------------------------------------
def _fail_init(self, *args, **kwargs):
    type_name = type(self).__name__
    error = "cannot instantiate abstract type {type}"
    raise NotImplementedError(error.format(type=type_name))


class MetaType(type):
    def __repr__(cls):
        doc = getattr(cls, "__doc__", None)
        if doc is not None:
            return doc
        else:
            return type.__repr__(cls)


Type = MetaType("Type", (object,), {"__init__": _fail_init})


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
    td["String"] = str
    td["Text"] = str
    td["list"] = list
    td["tuple"] = tuple
    td["map"] = dict


def clear_types():
    """Uninstall Pandoc Types"""
    global _types_dict
    globs = globals()

    # Uninstall registered types
    for type_name in _types_dict:
        del globs[type_name]
    _types_dict = {}


def make_types():
    """Create Pandoc Types"""

    global _types_dict
    globs = globals()

    # Uninstall existing types (if any)
    clear_types()

    # Get the pandoc types version
    version = pandoc._configuration["pandoc_types_version"]

    # Create builtin types
    _make_builtin_types()

    # Load & parse the types definition
    defs_src = pandoc.utils.definitions[version]
    if not isinstance(defs_src, str):  # resource loaded as bytes in Python 3
        defs_src = defs_src.decode("utf-8")

    #print(defs_src) # Issue with Caption that uses a Maybe. Shall I just add
    # the definition to defs_src ? 
    #     # data Maybe a = Just a | Nothing
    # Would it make it work ? Arf, fuck, not a chance, we have generics, 
    # my parser AND type factory would choke on this.
    # 
    # There is another issue that the Maybe pattern is extremely unpythonic ...
    # Shall I map (Maybe Stuff) to just Stuff ? Arf we would break the Haskell
    # types that we have followed to the letter so far. Or define Maybe manually
    # (as a builtin) ? But then we have a generic type ? How do we deal with
    # this in Python. Issues here, on the principles, that should be solved
    # before the implementation issue.
    # 
    # May advice so far would be to adapt the type like I have been doing
    # for MetaMap where
    #     MetaMap (Map Text MetaValue)
    # has been replaced with
    #     MetaValue = MetaMap({Text: MetaValue})
    # 
    # Here, add a notation in the parsed defs that says optional and render it
    # like "Stuff?" or "Stuff or None", whatever. But now this "optional" stuff
    # also has to be taken care of in the types generation, like the map stuff
    # is. OK, study what i have been doing for MetaMap first then. 
    #
    # OK, ATM I have use the "Type?" syntax.
    #
    # Caption is the new type that uses that.
    # --------------------------------------------------------------------------
    # TODO: Now, I still have to adapt the serialization.
    # Nota: experiments show that Maybe Stuff is serialiazed in JSON as
    # `null` or an instance of stuff. I guess that's how it is since I
    # don't see a support for it in the markdown reader doc (yet ?).
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
            # TODO: add an assert / check for this condition.
            for constructor in decl[1][1]:
                constructor_name = constructor[0]
                bases = (Constructor, data_type)
                _dict = {
                    "_def": constructor,
                    "__doc__": pandoc.utils.docstring(constructor),
                }
                type_ = type(constructor_name, bases, _dict)
                _types_dict[constructor_name] = type_
        elif decl_type == "type":
            type_ = type(type_name, (TypeDef,), _dict)
            _types_dict[type_name] = type_

    # Install the types
    globs.update(_types_dict)


# Create Types
# ------------------------------------------------------------------------------
_configuration = pandoc.configure(read=True)
if _configuration is None:
    pandoc.configure(auto=True)
else:
    pandoc.configure(**_configuration)
