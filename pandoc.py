#!/usr/bin/env python

# Python 2.7 Standard Library
import __builtin__
import collections
import json
import sys

# Third-Party Libraries
import sh

# Non-Python Dependencies
try:
    pandoc = sh.pandoc
    magic, version = sh.pandoc("--version").splitlines()[0].split()
    assert magic == "pandoc"
    assert version.startswith("1.12")
except:
    raise ImportError("cannot find pandoc 1.12")

#
# Metadata
# ------------------------------------------------------------------------------
#

from about_pandoc import *

#
# Pandoc Types
# ------------------------------------------------------------------------------
#

nothing = type("Nothing", (object,), {})()

# we want to support in-place algs & functional-style in a single scheme.
# have a look at the classic "fold" operation on trees of func. prog.
# (or rather, foldr).
# NB: the classic fold is fct first, node second, change signature.
# There is also the "initial value" in the sig, that explains how the 
# empty list because in tree-like structures based on list, an atom
# 5 may be represented as [5, []]. It's a way to distinguish the action
# that is to be applied to leafs somehow.
#
# Consider:
#
#     data Tree a = Leaf a | Branch (Tree a) (Tree a) deriving (Show)
#     data [a]    = []     | (:)    a [a]
#
#     treeFold :: (b -> b -> b) -> (a -> b) -> Tree a -> b
#     treeFold fbranch fleaf = g where
#       g (Leaf x) = fleaf x
#       g (Branch left right) = fbranch (g left) (g right)
#
# This fold specifies TWO functions, one to be used if the node is a leaf,
# the other one to use if the node is a branch (given that the subnodes
# have already been transformed). Here we don't care that much because the
# writer of the transformation can look the type of the object to see if
# it's primitive or not.
#
# Our structure is a bit more complex: our pandoc node is either a primitive
# object, or made of:
#   - a type
#   - a tuple of primitive / pandoc types / lists / dicts (k: string, v: anything)
#
# Ouch. "Tuple" here is meant to represent fixed-width, heterogeneous collection
# of stuff, it doesn't make sense to iterate on it automatically. The iteration
# that fold achieves can/shall be done on lists and dicts however, but how this
# thing translates into the management of the type arguments cannot be done
# automatically.
#
# OK, so the writer of transformations has to write rules to deal with:
#   1. atoms (Python primitive, non-container types). 
#   2. lists (unknown length, homogeneous type).
#   3. dicts (ordered, string key, node values).
#   4. pandoc nodes.
#
# The implementaion of a transformation would typically be:
# if pandoc doc stuff, if list do stuff, if dict do stuff, else, this is
# an atom, do stuff.
# 
# What do we do on lists and dicts ? Even list is not trivial, because it is
# not into the classic car-cons shape. And we cannot only apply the 
# transformation to each member of the list ... YES, we can do that in foldr,
# THEN give the result back to the transformation writer that may change
# the "type" of the list object accordingly.
#
# What is the responsibility of fold wtf dicts ? Apply the transformation
# to values only ? Consider that the structure is DICT [LIST-OF-PAIRS]
# and use the same mecanism as for pandoc types ? (the transf. writer then
# relies on the detection of tuples to know that a dict is iterated and
# the contract is that he is supposed to return the same kind of output ?
# (or instances of Nothing to get rid of stuff ? How to add stuff ? That
# has to be done at the dict level ? Mmmm that can probably be managed at
# the intermediate LIST level instead where sublists and nothings could
# be managed/consolidated (by the user)).
#
# Note that most of the time, it is useless to transform directly the
# primitive types. Only the context in which they are used is useful to
# determine what to do, so that's in the holder, a pandoc type instance,
# that we can do something. Example: don't transform str atoms, transform
# Str pandoc types.

def apply(item, action):
    # TODO: let the items override the default apply implementation.

    print "apply:", type(item), item

    # Interpretation of the action return value ? An object vs None vs Nothing ?
    # None means don't change anything, Nothing means get rid of it ?

    # Action is never called directly ?

    # Bug: tree iteration is borked ATM.

    if isinstance(item, PandocType):
        # "subitems" are args (cst number, heterogeneous), deal with it accordingly.
        # for example, Nothing is not applicable.
        subitems = [apply(subitem, action) for subitem in item]
        for i, subitem in enumerate(subitems):
            if subitem is not None:
                # TODO: raise an error if `nothing` is found here
                item.args[i] = subitem
                # in-place modification ? Is that really what we mean ? Nope.
    elif isinstance(item, list):
        subitems = [apply(subitem, action) for subitem in item]
        for i, subitem in enumerate(subitems):
            if subitem is not None:
                item[i] = subitem
        item[:] = [subitem for subitem in item if subitem is not nothing]
    elif isinstance(item, dict):
        subitems = []
        for subitem in item.items():
            new_subitem = apply(subitem, action)
            if new_subitem is None:
                subitems.append(subitem)
            elif new_subitem is nothing:
                pass
            else:
                subitems.append(new_subitem)
        item.clear()
        item.update(subitems)
    elif isinstance(item, tuple):
        pass
        # TODO: check that the action returns None.
    else:
        pass
        # TODO: check that the action returns None.
        
def iter(item, delegate=True):
    "Return a tree iterator"
    if delegate:
        try: # try delegation first
            _iter = item.iter
        except AttributeError:
            _iter = lambda: iter(item, delegate=False)
        for subitem in _iter():
            yield subitem
    else:                
        yield item
        # do not iterate on strings
        if not isinstance(item, basestring):
            try:
                it = __builtin__.iter(item)
                for subitem in it:
                    for subsubitem in iter(subitem):
                        yield subsubitem
            except TypeError: # non-iterable
                pass

class Map(collections.OrderedDict):
    "Ordered Dictionary"
    def iter(self):
        "Return a tree iterator on key-value pairs"
        return iter(self.items())

# --- Not Ready Yet ------------------------------------------------------------
class _Map(object):
    "Fully Mutable Ordered Dictionary"

    # TODO: document the behavior. Basically, the last key wins.

    def __init__(self, items):
        self._items = []
        for k, v in items:
            self[k] = v

    def _compact(self):
        "Ensure key uniqueness"
        keys = set()
        items = []
        for k, v in reversed(self._items):
            if k not in keys:
                items.insert(0, [k, v])
                keys.add(k)
        self._items[:] = items

    def keys(self):
        return [item[0] for item in self.items()]

    def values(self):
        return [item[1] for item in self.items()]

    def items(self):
        self._compact()
        return self._items

    def __contains__(self, key):
        return key in [item[0] for item in self.items()]

    def __len__(self):
        return len(self.items())

    def __iter__(self):
        return iter(self.keys())

    def iter(self):
        "Return a tree iterator on key-value pairs"
        return iter(self.items())

    def __getitem__(self, key):
        for k, v in self.items():
            if k == key:
                return v
        else:
            raise KeyError(key)

    def __setitem__(self, key, value):
        for item in self.items():
            if item[0] == key:
                item[1] = value
                break
        else:
            self._items.append([key, value])
   
    def __delitem__(self, key):
        for i, k in enumerate(self.keys()):
           if k == key:
               self._items.pop(i)
               break

    def update(self, items, **kwargs):
        if hasattr(items, keys):
            for key in items.keys():
                self[key] = items[key]
        else:
            for key, value in items:
                self[key] = value
        for key, value in kwargs.items():
            self[key] = value

    def clear(self):
        self._items = []

    def __repr__(self):
       return "Map({0})".format(self.items())

    __str__ = __repr__
# ------------------------------------------------------------------------------

# TODO: implement all types.

# BUG: there are style some extra parenthesis: when I output some json,
#      i have a "when expecting a Object, encountered Array instead"
#      pandoc error. Make some before / after tree comparison to see
#      where we have this issue.


class PandocType(object):
    """
    Pandoc types base class

    Refer to the original [Pandoc Types][] documentation for details.

    [Pandoc Types]: http://hackage.haskell.org/package/pandoc-types
    """

    list_arg = False

    def __init__(self, *args):
        self.args = list(args) # ensure mutability

    def __iter__(self):
        "Return a child iterator"
        return iter(self.args)

    def __getitem__(self, i):
        return self.args[i]

    def __setitem__(self, i, value):
        self.args[i] = value

    def __delitem__(self, i):
        del self[i]

    def iter(self):
        "Return a tree iterator"
        # The module function `iter` shall really perform the tree iteration, 
        # not call this method back to do it, hence the `delegate=False`.
        return iter(self, delegate=False)        

    def __json__(self):
        """
        Convert the `PandocType instance` into a native Python structure that 
        may be encoded into text by `json.dumps`.
        """
        content = to_json(self.args)
        if len(content) == 1:
            content = content[0]
        k_v_pairs = [("t", type(self).__name__), ("c", content)] 
        return Map(k_v_pairs)

    def __repr__(self):
        typename = type(self).__name__
        args = ", ".join(repr(arg) for arg in self.args)
        return "{0}({1})".format(typename, args)

# TODO: the issue is not list_arg as much as it is single_arg that *may* be a list.
#       It may be a Map too ... Analyze the type decl to get this info, including
#       when Map arguments are used.

def declare_types(type_spec, bases=object, dct={}):
    if not isinstance(bases, (tuple, list)):
        bases = (bases,)
    else:
        bases = tuple(bases)
    for type_spec_ in type_spec.strip().splitlines():
       type_parts = [part.strip() for part in type_spec_.strip().split()] 
       type_name = type_parts[0]
       type_args = " ".join(type_parts[1:])
       list_arg = False
       if type_args.startswith("["):
           count = 0
           for i, char in enumerate(type_args):
               count += (char == "[") - (char == "]")
               if count == 0:
                   break
           list_arg = (i == len(type_args) - 1)
       dct["list_arg"] = list_arg
       globals()[type_name] = type(type_name, bases, dct)

class Pandoc(PandocType):
    def __json__(self):
        meta, blocks = self.args[0], self.args[1]
        return [to_json(meta), [to_json(block) for block in blocks]]
    @staticmethod 
    def read(text):
        return read(text)
    def write(self):
        return write(self)

class Meta(PandocType):
    pass

class unMeta(Meta):
    # unMeta does not follow the json representation with 't' and 'k' keys.
    def __json__(self):
        dct = self.args[0]
        k_v_pairs = [(k, to_json(dct[k])) for k in dct]
        return {"unMeta": Map(k_v_pairs)}

class MetaValue(PandocType):
    pass

declare_types(\
"""
MetaMap (Map String MetaValue)
MetaList [MetaValue]	 
MetaBool Bool	 
MetaString String	 
MetaInlines [Inline]	 
MetaBlocks [Block]
""", MetaValue)

class Block(PandocType):
    pass # TODO: make this type (and a buch of others) abstract ?
    # Mmmm but we could have to redefine the constructor in every 
    # derived class. Have a look at ABC ?

declare_types(\
"""
Plain [Inline]
Para [Inline]
CodeBlock Attr String
RawBlock Format String
BlockQuote [Block]
OrderedList ListAttributes [[Block]]
BulletList [[Block]]
DefinitionList [([Inline], [[Block]])]
Header Int Attr [Inline]
HorizontalRule
Table [Inline] [Alignment] [Double] [TableCell] [[TableCell]]
Div Attr [Block]
Null
""", Block)

class Alignment(PandocType):
    pass

declare_types(\
"""
AlignLeft
AlignRight
AlignCenter
AlignDefault
""", Alignment)

class ListNumberStyle(PandocType):
    pass

declare_types(\
"""
DefaultStyle	 
Example	 
Decimal	 
LowerRoman	 
UpperRoman	 
LowerAlpha	 
UpperAlpha
""", ListNumberStyle)

class ListNumberDelim(PandocType):
    pass

declare_types(\
"""
DefaultDelim	 
Period	 
OneParen	 
TwoParens
""", ListNumberDelim)

class Inline(PandocType):
    pass

declare_types(\
"""
Str String
Emph [Inline]	
Strong [Inline]	
Strikeout [Inline]	
Superscript [Inline]	
Subscript [Inline]	
SmallCaps [Inline]	
Quoted QuoteType [Inline]	
Cite [Citation] [Inline]	
Code Attr String	
Space	
LineBreak	
Math MathType String	
RawInline Format String	
Link [Inline] Target	
Image [Inline] Target	
Note [Block]	
Span Attr [Inline]	
""", Inline)

class MathType(PandocType):
    pass

class DisplayMath(MathType):
    pass

class InlineMath(MathType):
    pass

#
# Json to Pandoc and Pandoc to Json
# ------------------------------------------------------------------------------
#

def to_pandoc(json):
    def is_doc(item):
        return isinstance(item, list) and \
               len(item) == 2 and \
               isinstance(item[0], dict) and \
               "unMeta" in item[0].keys()
    if is_doc(json):
        return Pandoc(*[to_pandoc(item) for item in json])
    elif isinstance(json, list):
        return [to_pandoc(item) for item in json]
    elif isinstance(json, dict) and "t" in json:
        pandoc_type = eval(json["t"])
        contents = json["c"]
        pandoc_contents = to_pandoc(contents)
        if isinstance(pandoc_contents, list) and not getattr(pandoc_type, "list_arg", False):
            return pandoc_type(*pandoc_contents)
        else:
            return pandoc_type(pandoc_contents)
    elif isinstance(json, dict) and "unMeta" in json:
        dct = json["unMeta"]
        k_v_pairs = [(k, to_pandoc(dct[k])) for k in dct]
        return unMeta(Map(k_v_pairs))

    else:
        return json
    
def to_json(doc_item):
    if hasattr(doc_item, "__json__"):
        return doc_item.__json__()
    elif isinstance(doc_item, list):
        return [to_json(item) for item in doc_item]
    elif isinstance(doc_item, dict): # TODO: keep order
        return {key: to_json(doc_item[key]) for key in doc_item}
    else:
        return doc_item

#
# Markdown to Pandoc and Pandoc to Markdown
# ------------------------------------------------------------------------------
#

def read(text):
    """
    Read a markdown text as a Pandoc instance.
    """
    json_text = str(sh.pandoc(read="markdown", write="json", _in=text))
    json_ = json.loads(json_text, object_pairs_hook=Map) # still some stuff loaded as dict ???
    return to_pandoc(json_)

def write(doc):
    """
    Write a Pandoc instance as a markdown text.
    """
    json_text = json.dumps(to_json(doc))
    return str(sh.pandoc(read="json", write="markdown", _in=json_text))

#
# Command-Line Interface
# ------------------------------------------------------------------------------
#

if __name__ == "__main__":
    input = sys.stdin.read()
#    print
#    print input
#    print
    json_ = json.loads(input, object_pairs_hook=Map)
#    print json_
#    print
    pandoc = to_pandoc(json_)
#    print repr(pandoc)
#    print
    print json.dumps(to_json(pandoc))
#    print
