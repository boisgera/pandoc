
from declarations import type_declarations

hs = {}
for decl in type_declarations:
    name = decl[1][0]
    hs[name] = decl

# distinguish python symbols available to the user (mix of types and instances)
# and the factories that given the args already converted to python returns the
# python instance ? Probably no need, we can check if the Python object is a 
# type and act accordingly.
hs_to_py = {}

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

class PandocType(object): # TODO: abstract type
    def __init__(self, *args):
        self.args = args
    
for type_name, decl in hs.items():
    print decl[0]
    if decl[0] == "data":
        hs_to_py[type_name] = parent = type(type_name, (PandocType,), {})
        constructors = decl[1][1]
        for constructor in constructors:
            constructor_name = constructor[0]
            hs_to_py[constructor_name] = type(constructor_name, (parent,), {})

globs = globals()
for type_name, type in hs_to_py.items():
    globs[type_name] = type

# for "data" types (or "newtype", look at the constructors ; if all of them have 
# arguments, create an abstract base type, otherwise a normal one. (First step:
# make the easiest think that works: don't bother with abstract data types) 
# For every constructor
# without arguments, create a named singleton instance. For the other ones,
# create a derived types with *args constructor sign. (for now, no typechecking
# at all, not even the number of args), and store the result in args attribute.
# The other option for singletons / enums is to design a type that has a 
# single instance, say AlignedLeftType that would derive from Alignment and
# has a single AlignedLeft instance ... yes, I kind of like that better somehow.

# NOTA: the many args vs single list arg info is needed by the JSON parser
# given the current JSON representation but we couldn't care less, the parser
# will handle it, the Python repr is not supposed to know this.

# EXCEPT that record types should be treated differently: we create a unique
# concrete type with kwargs (not checked for now). We could create an 
# intermediate type "Record" or "RecordType" that would derive from PandocType 
# to simplify pattern matching.

# for type declaration, we do nothing for now (they are "inlined").

