
from .defs import defs
primitives = {"String": unicode, 
              "Bool": bool, 
              "Int": int, 
              "list": list, 
              "tuple": tuple}
types = {}
singletons = {}
typedefs = {} # name "aliases" instead
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
    def __init__(self, *args, **kwargs):
        if args:
            assert not kwargs
            self.args = args
            self.name = None
        else:
            assert "name" in kwargs
            self.name = kwargs["name"]
            self.args = None

    def __repr__(self):
        if self.args:
            typename = type(self).__name__
            args = ", ".join(repr(arg) for arg in self.args)
            return "{0}({1})".format(typename, args)
        else:
            return self.name

    __str__ = __repr__

class Record(Type):
    # Shit, we are losing the order of arguments here :(
    # Could be restored with the knowledge of the type decl however.
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __repr__(self):
        typename = type(self).__name__
        items = self.kwargs.items()
        kwargs = ", ".join("{0}={1!r}".format(k, v) for k, v in items)
        return "{0}({1})".format(typename, kwargs)

    __str__ = __repr__

class Typedef(Type):
    pass

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
                    print "***", base, decl
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
                    singletons[constructor_name] = base(name=constructor_name)
    if decl_type == "type":
        typedefs[type_name] = type(type_name, (Typedef,), {"_decl": decl[1][1]})
        
globals().update(primitives)
globals().update(types)
globals().update(singletons)
globals().update(typedefs)

