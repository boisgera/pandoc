#!/usr/bin/env python

# Python 2.7 Standard Library
import __builtin__
import argparse
import copy as _copy
import collections
import json
import re
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

__main__ = (__name__ == "__main__")

from about_pandoc import *

#
# Pandoc Types
# ------------------------------------------------------------------------------
#

nothing = type("Nothing", (object,), {})()

# Consider map, not only fold ? What is the main pattern ?
#
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
# be managed/consolidated (by the user)). But at the list-level, we do
# have the context that this is a dict ... that's tricky. AH ! We could
# advocated a coding ? Like, replace "a": 56 with "a": None or "a": [1,2,3]
# and consolidate at the dict level (by the user) ? This is not totally
# stupid and somehow similar to how lists and handled (dispatch + consolid.
# at the type level)
#
# Note that most of the time, it is useless to transform directly the
# primitive types. Only the context in which they are used is useful to
# determine what to do, so that's in the holder, a pandoc type instance,
# that we can do something. Example: don't transform str atoms, transform
# Str pandoc types.

# TODO: review iteration to make it consistent with fold.

# TODO: dude, we deal with MUTABLE structures here, make sure we copy stuff
#       by default ? We wouldn't want our result to get entangled with the
#       input data structure.
def fold(f, node, copy=True):
    # rk: if all types where iterable *in the right way*, we could collapse
    #     most of this implementation. But is it wise ? Iteration on Pandoc
    #     types constructor argument is kind of weird and for Map, that would
    #     conflict with the standard behavior of the parent class.
    if copy:
        node = _copy.deepcopy(node)
        copy = False 
    if isinstance(node, PandocType):
        type_ = type(node) 
        args = [fold(f, arg, copy) for arg in node.args]
        return f(type_(*args))
    elif isinstance(node, (tuple, list)):
        type_ = type(node)
        return f(type_([fold(f, item, copy) for item in node]))
    elif isinstance(node, Map):
        return f(Map([fold(f, item, copy) for item in node.items()]))
    else: # Python atomic type 
        return f(node)

def apply(item, action):
    # TODO: let the items override the default apply implementation.

    print "apply:", type(item), item

    # Interpretation of the action return value ? An object vs None vs Nothing ?
    # None means don't change anything, Nothing means get rid of it ?

    # Action is never called directly ?

    # Bug: tree iteration is totally borked ATM.

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
        
# TODO: externalize all the code in iter and remove from the classes.
#       Get rid of delegation, it is complex for little (or no) benefit.

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


# TODO: implement all types.

# BUG: there are style some extra parenthesis: when I output some json,
#      i have a "when expecting a Object, encountered Array instead"
#      pandoc error. Make some before / after tree comparison to see
#      where we have this issue.


# TODO: need to manage dicts properly (see map stuff, that's not ok).
# TODO: also need to manage lists ; in both cases, do it directly in
#       tree_str global, don't dispatch the implementation (can't do it
#       for lists anyway).

def tree_str(item, depth=0):
    method = getattr(item, "__tree_str__", None)
    tab = 2 * u" " * depth
    if method:
        return method(depth)
    elif isinstance(item, list):
        output = u""
        for child in item:
            child_str = tree_str(child, depth + 1)
            child_str = tab + u"- " + child_str[2*(depth+1):]
            output += child_str + u"\n"
        return output[:-1]
    elif isinstance(item, dict):
        output = ""
        for key, value in item.items():
            output += tab + unicode(key) + u":\n" + tree_str(value, depth + 1) + u"\n"
        return output[:-1]
    else: # TODO: smarter behavior for multiline objects.
        try:
            string = unicode(item)
        except (UnicodeEncodeError, UnicodeDecodeError):
            string = item.decode("utf-8")
        lines = string.split(u"\n")
        return u"\n".join([tab + line for line in lines]) 


class PandocType(object):
    """
    Pandoc types base class

    Refer to the original [Pandoc Types][] documentation for details.

    [Pandoc Types]: http://hackage.haskell.org/package/pandoc-types
    """

    args_type = [] # TODO: define properly args_type for every manually defined 
                   #       pandoc type.

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

    def __tree_str__(self, depth=0):
        tab = 2 * depth * u" "
        out = tab + unicode(type(self).__name__) + u"\n"
        for arg in self.args:
            out += tree_str(arg, depth+1) + u"\n"
        return out[:-1]

    __unicode__ = __tree_str__            

    def __str__(self):
        return unicode(self).encode("utf-8")

# ------------------------------------------------------------------------------

# TODO: the issue is not list_arg as much as it is single_arg that *may* be a list.
#       It may be a Map too ... Analyze the type decl to get this info, including
#       when Map arguments are used.

# TODO: control the number of arguments in the constructor
# TODO: control the type of the arguments in the constructor (worth the effort ?)
# TODO: deal with Haskell Maps in constructors. What should accept the constructor ?
#       (keyword arguments ? a single dict-like argument ? list of pairs, several
#       pair arguments ? Does the args attribute still "works" ? We also have
#       a problem when we deal with the Pythonification of the json maps, because
#       they are dicts WITHOUT the "t" and "c" keys, or if the keys are here,
#       they should not be interpreted as type info. Hence the classic
#       pythonization of the args before the constructor call cannot take place. 
#       Hence 'from_json' should be adapted. Need some extra "map_arg" flag in
#       the type to deal with the recursive structure adequaltly. BUT, it 
#       doesn't solve the constructor / arg pb. If we mimick dict, we should
#       accept dict, sequence of pairs AND keyword arguments. And we store the
#       stuff in args[0]
# TODO: wrapper around single Map or List should inherit from the python type
#       (list or Map). Buuuut ... the delegation of the behavior to the content
#       of args[0] may be a bit nasty ... via getattr ?
#       Grpmh dunno ... doin so would make some sense BUT it may also scramble
#       the way fold is applied as we are going to "lose" the type tag on
#       top of the object. So, well, too bad, such objects have to be unwrapped
#       before their list or map interface can be used.
#
#       The type declaration are lists of types / tuples of types / lists
#       (homogeneous, based on a single type) / maps (based on homogeneous
#       key type and homogeneou value type). [] are used for lists, (,) for
#       tuples, () for priority and Map for maps.
#
# TODO: lexer of (constructor) type decl: first, split on '(', ')', '[', ']'
#       and whitespace (normalize to one space).

def split(strings, symbol, pattern=None):
    if isinstance(strings, str):
        strings = [strings]
    if pattern is None:
        pattern = re.escape(symbol)
    output = []
    for string in strings:
        splitted = re.split(pattern, string)
        parts = []
        for item in splitted:
            parts.extend([item, symbol])
        output.extend(parts[:-1])
    return [item for item in output if item != ""]
  
def tokenize(string):
    tokens = [string]
    for sep in "( ) [ ] ,".split():
        tokens = split(tokens, sep)
    tokens = split(tokens, "", "\s+")
    return tokens

def parse(tokens):
    if isinstance(tokens, str):
        tokens = tokenize(tokens)

    stack = [[None, []]]

    def insert(tag):
        stack.append([tag, []])

    def push(item):
        tag = stack[-1][0]
        stack[-1][1].append(item)
        if tag == "map" and len(stack[-1][1]) == 2:
            fold()

    def fold():
        item = stack.pop() 
        stack[-1][1].append(item)

    for token in tokens:
        if token == "[":
            insert("list")
        elif token == "(":
            insert("tuple")
        elif token == "Map":
            insert("map")
        elif token == "]" or token == ")":
            fold()
        elif token == ",":
            pass
        else:
            push(token)

    if len(stack) != 1:
        raise SyntaxError("invalid type definition syntax: {0}".format(stack))
    
    ast = stack[0][1]
    
    def filter(node, _root=True):
        if _root is True:
            return [filter(item, _root=False) for item in node]
        elif isinstance(node, list):
            if node[0] == "tuple" and len(node[1]) == 1:
                return filter(node[1][0], _root=False)
            else:
                return [node[0]] + [filter(item, _root=False) for item in node[1:]]
        else:
            return node

    filter(ast)

    return ast


# ------------------------------------------------------------------------------

def declare_types(type_spec, bases=object, dct={}):
    if not isinstance(bases, (tuple, list)):
        bases = (bases,)
    else:
        bases = tuple(bases)
    for type_spec_ in type_spec.strip().splitlines():
        type_spec_ = parse(type_spec_)
        type_name, args_type = type_spec_[0], type_spec_[1:]
        type_ = globals()[type_name] = type(type_name, bases, dct)
        type_.args_type = args_type

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

# TODO: consider the example of YAML metadat given in the pandoc doc.
#       here, when we parse it, we shouldn't have any dict with 
#       "t" and "c" keys anymore, those dicts should be abstracted 
#       away. Currently some of them are, some aren't.
#       
#       Hey OBVIOUSLY. `declare_types` knows nothing of the 
#       "Map String Metavalue" construct used in MetaMap, this
#       is interpreted as a sequence of three arguments.      

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

def from_json(json):
    def is_doc(item):
        return isinstance(item, list) and \
               len(item) == 2 and \
               isinstance(item[0], dict) and \
               "unMeta" in item[0].keys()
    if is_doc(json):
        return Pandoc(*[from_json(item) for item in json])
    elif isinstance(json, list):
        return [from_json(item) for item in json]
    elif isinstance(json, dict) and "t" in json: # that's a bit weak ...
        pandoc_type = eval(json["t"])
        contents = json["c"]
        pandoc_contents = from_json(contents)
        args_type = pandoc_type.args_type
        if len(args_type) == 1 and args_type[0][0] == "list" or\
           not isinstance(pandoc_contents, list):
            return pandoc_type(pandoc_contents)
        else: # list of arguments, to be interpreted as several arguments
            return pandoc_type(*pandoc_contents)
        # TODO: is map correctly handled ?
    elif isinstance(json, dict) and "unMeta" in json:
        dct = json["unMeta"]
        k_v_pairs = [(k, from_json(dct[k])) for k in dct]
        return unMeta(Map(k_v_pairs))
    else:
        return json

def from_json_str(json_str):
    return from_json(json.loads(json_str, object_pairs_hook=Map))

    
def to_json(doc):
    if hasattr(doc, "__json__"):
        return doc.__json__()
    elif isinstance(doc, list):
        return [to_json(item) for item in doc]
    elif isinstance(doc, dict): # TODO: keep order
        return {key: to_json(doc[key]) for key in doc}
    else:
        return doc

def to_json_str(doc):
    return json.dumps(to_json(doc))

#
# Markdown to Pandoc and Pandoc to Markdown
# ------------------------------------------------------------------------------
#

def from_markdown(string):
    """
    Read a markdown text as a Pandoc instance.
    """
    json_str = str(sh.pandoc(read="markdown", write="json", _in=string))
    json_ = json.loads(json_str, object_pairs_hook=Map)
    return from_json(json_)

def to_markdown(doc):
    """
    Write a Pandoc instance as a markdown text.
    """
    json_str = json.dumps(to_json(doc))
    return str(sh.pandoc(read="json", write="markdown", _in=json_str))

#
# Command-Line Interface
# ------------------------------------------------------------------------------
#

# TODO: deliver the CLI as a setuptools console script.

if __main__:
    description = "Convert pandoc formats."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("input", nargs='?', 
                         type = argparse.FileType("r"),
                         default = sys.stdin,
                         help = "input file (default: standard input)")
    parser.add_argument("-o", "--output", 
                        type = argparse.FileType("w"),
                        default = sys.stdout,
                        help = "output file (default: standard output)")
    # TODO: add automatic detection of input formats based on file extension ?
    #       Mmmm not sure we can do this if we rely on argparse.FileType.
    #       Aaah, yes we can, with the 'name' attribute.
    parser.add_argument("-f", "--from", 
                        type = str, choices = ["markdown", "json", "python"],
                        default = "markdown",
                        help = "input representation format (default: markdown)")
    parser.add_argument("-t", "--to", 
                        type = str, choices = ["markdown", "json", "python"],
                        default = "python",
                        help = "output representation format (default: python)")
    args = parser.parse_args()

    readers = dict(markdown=from_markdown, json=from_json_str, python=eval)
    writers = dict(markdown=to_markdown  , json=to_json_str  , python=repr)

    reader = readers[args.__dict__.get("from")]
    writer = writers[args.to]

    print args.input.name

    output = writer(reader(args.input.read()))
    if output and output[-1] != "\n":
        output += "\n"
    args.output.write(output)
    sys.exit(0)

