
# Python 2.7 Standard Library
import collections

# Local Modules
from .defs import defs

# ------------------------------------------------------------------------------

primitives = {"String": unicode, 
              "Bool": bool, 
              "Int": int, 
              "list": list, 
              "tuple": tuple}
types = {}
singletons = {}
typedefs = {} # name "aliases" instead ?
# TODO: typedefs = {} ? What would I put in there ? A kind of spec ?

# TODO: transfer to doc this paragraph.
# NOTA: the reboot of pandoc design includes ONLY:
#   - (unchecked wrt types) Python model
#   - back and forth JSON repr
# so pandoc (the Haskell lib/prg) is not required.

# List of features shared by pandoc types (eventually):
#   - repr / str / pprint ?
#   - ==
#   - type-checking / signature ----> target 2.0
#   - "pickable" ----> see later
#   - homogeneous iteration protocol (not sure about that one) ----> +inf
#
# Json repr (import / export) is EXTERNAL by design, we don't harcode the
# specific settings of Aeson ATM in the Python model.

# TODO: introduce abstract data types where applicable (PandocTypes, data types,
#       etc).

class Type(object):
    pass

class Data(Type):
    def __init__(self, *args):
        self.args = args

    def __repr__(self):
        if self.args:
            typename = type(self).__name__
            args = ", ".join(repr(arg) for arg in self.args)
            return "{0}({1})".format(typename, args)
        else:
            return self.__name__

    __str__ = __repr__

class NewType(Type):
    def __init__(self, *args):
        self.args = args

    def __repr__(self):
        if self.args:
            typename = type(self).__name__
            args = ", ".join(repr(arg) for arg in self.args)
            return "{0}({1})".format(typename, args)
        else:
            return self.__name__

    __str__ = __repr__


# Should records have all data behaviors ?
# ----------------------------------------
# Make a record support everything a data type does (init with args, etc.) ?
# That would be nice somehow ... but could pose problems down the line when
# /if we accept that those instances are mutable and we don't want to protect
# the data access with properties to keep the internal state. Pragmatically,
# it may be better NOT to supports args for records, only kwargs (note that
# records are serialized differently from non-record in JSON).

# Record field names
# ------------------
# Pragmatically, there are two schemes only that are used in Pandoc
#
#   - namespace protection: the Citation record prefixed all its fields with
#     "citation" to avoid a name clashe with the generated accessors.
#     We could maybe avoid that ... (this name clashes does not happen in Python)
#
#   - deconstructors: this is a feature used for records that are also newtypes: 
#     see <https://wiki.haskell.org/Type> for an explanation. Concretely, that
#     means that `Meta` has a single `unMeta` field (the generated function
#     does the unwrapping).
#
#     So in this case actually, AFAICT, the declaration of `Meta` as a record is 
#     merely a way to avoid the declaration of the accessor, not a true design
#     choice about the data structure ... In Haskell this is not a big deal,
#     because we can still use this object AS A DATA, pattern match on its
#     arguments, etc, without worrying about the fact that it's declared as 
#     a record ... That totally pleads in favor of having the records having 
#     the full data behaviors, but we know that we are going to run into
#     trouble if we allow such structures to be mutable ...
#
#   One semi-radical approach to records is NOT TO SUPPORT THEM: we still flag
#   then as records because it matters at the serialization level, but we don't
#   offer any support for field access. That's only semi-radical because `Meta`
#   is a "fake" record, and that means that there is only `Citation` left ...
#   Yeah, I kind of like this approach.

class Record(Type):
    def __init__(self, **kwargs):
        keys = [item[0] for item in self._decl]
        self.kwargs = collections.OrderedDict()
        for key in keys:
            self.kwargs[key] = kwargs.get(key)

    def __repr__(self):
        typename = type(self).__name__
        items = self.kwargs.items()
        kwargs = ", ".join("{0}={1!r}".format(k, v) for k, v in items)
        return "{0}({1})".format(typename, kwargs)

    __str__ = __repr__

class TypeDef(Type):
    pass

# TODO: note that there is no reason why the record is the single constructor
#       (hence the record nature should be attached to the constructor, not
#       the type itself), there is no reason why the record constructor name
#       is the same as the type name, etc. In other words: make sure that the
#       record / newtype (or merely single-constructor-with-same-name which is
#       mandatory for newtypes) treatments are orthogonal.
#
#       Question: as AESON seems to strip the type info from records,
#       what would happen if a type had declared several record constructors ?
#       The names of the fields *could* in principle be used to get rid of
#       the ambiguity, but (that would suck and) that wouldn't cover the case
#       of empty records:
#
#           data A = B {}
#                  | C {}
#
#       How could we know from the JSON if the `{}` refers to an `A` or a `B` ?
#       Is this actually "solved" in a ad hoc manner by the declaration in Pandoc
#       of a custom `FromJSON` function that explicits the unserialization
#       (actually there is no possible conflict in Pandoc structures, it can
#       always be resolved unambiguously) ? Grmph, no, for Meta and Citations,
#       Pandoc uses the same, generic AESON converter. Oh, this is funny:
#       Pandoc is using a generic JSON method, but AESON detects given the decl
#       of the structures that there is no ambiguity and gets rid of the type
#       info; if the records had siblings constructors, the maps would inherit
#       a `"t"` field with the name of the constructor. So AESON recognize the
#       most common use of records (single constructor) and "optimize" the
#       representation for this scheme.

for decl in defs:
    decl_type = decl[0]
    type_name = decl[1][0]

    if decl_type in ("data", "newtype"):
        constructors = decl[1][1]

        if len(constructors) == 1:
            constructor = constructors[0]
            constructor_name = constructor[0]
            constructor_args = constructor[1]
            if constructor_name == type_name:
                # There is a single constructor whose name is the type name; 
                # we create a single type instead of two.
                if constructor[1][0] == "record":
                    base = Record
                    decl = constructor_args[1]
                else:
                    base = Data
                    decl = constructor_args
                types[type_name] = type(type_name, (base,), {"_decl": decl})
        else:
            types[type_name] = base = type(type_name, (Data,), {"_decl": constructors})
            for constructor in constructors:
                constructor_name = constructor[0]
                constructor_args = constructor[1]
                if constructor_args:
                    types[constructor_name] = \
                      type(constructor_name, (base,), {"_decl": constructor_args})
                else:
                    singletons[constructor_name] = base(__name__=constructor_name)
    if decl_type == "type":
        typedefs[type_name] = type(type_name, (TypeDef,), {"_decl": decl[1][1]})
        
globals().update(primitives)
globals().update(types)
globals().update(singletons)
globals().update(typedefs)

