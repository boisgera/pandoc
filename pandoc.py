#!/usr/bin/env python

# Python 2.7 Standard Library
import __builtin__
import argparse
import copy as _copy
import collections
import json
import os.path
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

# Q: make pandoc optional and remove the markdown input/output from the CLI 
#    and Python API ? Is is too smart/complex ?

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

# TODO: we need to support object replacement, do-not-change, object replacement
#       by a collection of objects and object deletion, either in this fold fct,
#       or by patterns in client code that are compatible with fold. Another
#       possibility would be for the user to install filters applied in
#       each clause. Would it make the job ? MMmmm maybe at the right level.
#       applied on the [fold(sub) for sub in ...] list to get a new list.
#       rk: everything is easy to support (at least for lists), but the 
#       insertion of a collection. The pandocfilters trick to use a list has
#       issues: it is ambiguous when the child *already* are lists. 
# UP:   We could use an extra level of list and detect that. That would
#       not be ambiguous. ... EXCEPT IF WE HAVE SOME EMPTY LISTS ? Think of it ...
#       Consider BulletList for example that contains a [[Block]]
# TODO: adaptation for types that are not lists ?
def fold(f, node, copy=True):
    if copy:
        node = _copy.deepcopy(node)
        copy = False 
    if isinstance(node, PandocType):
        type_ = type(node) 
        args = [fold(f, arg, copy) for arg in node.args]
        return f(type_(*args))
    elif isinstance(node, (list, tuple)):
        type_ = type(node)
        items = []
        items_ = [fold(f, item, copy) for item in node]
        for i, item in enumerate(items_):
            if item is None:
                pass
            elif isinstance(item, list) and not isinstance(node[i], list):
                items.extend(item)
            # The clause below works because in the pandoc model, we have no 
            # more than two levels of lists, so a list of lists in a list node
            # has to be an extra level added by the user to return multiple
            # values. Note that for tuples, that appear only in maps, as pairs, 
            # neither the key not the value may be a list so the clause above
            # applies.
            elif isinstance(item, list) and len(item) != 0 and isinstance(item[0], list):
                items.extend(item)
            else:
                items.append(item)
        return f(type_(items))
    elif isinstance(node, Map): # child of unMeta or MetaMap, str keys.
        return f(Map([fold(f, item, copy) for item in node.items()]))
    else: # Python atomic type 
        return f(node)

def iter(item, delegate=True):
    "Return a tree iterator"
    if isinstance(item, (PandocType, list, tuple)):
        it = __builtin__.iter(item)
    elif isinstance(item, dict):
        it = item.items()
    else: # atom
        it = []

    yield item
    for subitem in it:
        for subsubitem in iter(subitem):
            yield subsubitem

class Map(collections.OrderedDict):
    "Ordered Dictionary"

# TODO: refactor: reduce code duplication 
# TODO: consider: no newline for ",", no nesting for single items.
#       It would be more compact and probably more readable for most docs.
def alt_repr(item, depth=0):
    pad = 2 * u" "
    tab = depth * pad
    if isinstance(item, PandocType):
        out = [tab, unicode(type(item).__name__), u"("]
        for arg in item.args:
            out += [u"\n", alt_repr(arg, depth + 1), u"\n", tab, pad, u","]
        if len(item.args):
            out = out[:-2] + [")"]
        else:
            out = out + [")"]
    elif isinstance(item, list):
        out = [tab, u"["]
        for child in item:
            out += [u"\n", alt_repr(child, depth + 1), u"\n", tab, pad, u","]
        if len(item):
            out = out[:-2] + ["]"]
        else:
            out += ["]"] 
    elif isinstance(item, tuple):
        out = [tab, u"("]
        for child in item:
            out += [u"\n", alt_repr(child, depth + 1), u"\n", tab, pad, u","]
        if len(item):
            out = out[:-2] + [")"]
        else:
            out += [")"] 
    elif isinstance(item, Map):
        out = [tab, u"Map("]
        if len(item):
            out += [u"\n", alt_repr(list(item.items()), depth + 1), u"\n"]
        out += [u")"]
    else:
        try:
            string = unicode(item)
        except (UnicodeEncodeError, UnicodeDecodeError):
            string = item.decode("utf-8")
        out = [tab, repr(string)]
    return u"".join(out) 


class PandocType(object):
    """
    Pandoc types base class

    Refer to the original [Pandoc Types][] documentation for details.

    [Pandoc Types]: http://hackage.haskell.org/package/pandoc-types
    """

    args_type = None # TODO: define properly args_type for every manually defined 
                     #       pandoc type. "None" should be a marker for abstract
                     #       types.

    # TODO: perform some type_checking of args based on args_type ? That would
    #       force us to have a well-defined args_type for every PandocType
    #       that is ever instantiated and currently, this is not the cases for
    #       the ones that are manually built. Pure Pandoc types (that are never
    #       instantiated) should probably have a None args_type.

    def __init__(self, *args):
        self.args = list(args) # ensure mutability

# ------------------------------------------------------------------------------
# The list-like methods can be handy, but that should not go too far: PandocType
# shall not inherit from list or tuple. Given our current designed, this is a
# typed/tagged structure that *wraps* (but is not) a inhomogeneous, fixed-length, 
# mutable sequence, hence a hybrid of tuple and list.

    def __iter__(self):
        "Return a child iterator"
        return iter(self.args)

    def __getitem__(self, i):
        return self.args[i]

    def __setitem__(self, i, value):
        self.args[i] = value

    def __len__(self):
        return len(self.args)

    def iter(self):
        "Return a tree iterator"
        return iter(self)        
# ------------------------------------------------------------------------------

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

    __str__ = __repr__

    def __unicode__(self):
        return str(self).decode("utf-8")

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

    args_type = ["Meta", ["list", ["Block"]]]

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
    args_type = ["MetaValue"]

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

declare_types(\
"""
DisplayMath
InlineMath
""", MathType)

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

def to_json_str(doc, indent=None):
    return json.dumps(to_json(doc), indent=indent)

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

def main():
    "CLI entry point, exposed as pandoc-convert"

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
    parser.add_argument("-f", "--from", 
                        type = str, choices = ["auto", "markdown", "json", "python"],
                        default = "auto",
                        help = "input representation format (default: auto)")
    parser.add_argument("-t", "--to", 
                        type = str, choices = ["auto", "markdown", "json", "python"],
                        default = "auto",
                        help = "output representation format (default: python)")
    parser.add_argument("-x", "--expand", 
                        dest = "alt",
                        action = "store_true",
                        help = "expand the representation")
    args = parser.parse_args()

    readers = dict(markdown=from_markdown, json=from_json_str, python=eval)
    writers = dict(markdown   = to_markdown, 
                   json       = to_json_str, 
                   python     = repr       ,
                   alt_python = alt_repr   , 
                   alt_json   = lambda doc: to_json_str(doc, indent=2),
                  )

    from_ = args.__dict__.get("from")
    if from_ == "auto":
        _, ext = os.path.splitext(args.input.name)
        if ext == ".py":
            from_ = "python"
        elif ext in [".js", ".json"]:
            from_ = "json"
        elif ext in [".md", ".txt"]:
            from_ = "markdown"
        else:
            sys.exit("error: unknown input format")

    # TODO: reduce code duplication
    to = args.to
    if to == "auto":
        _, ext = os.path.splitext(args.output.name)
        if ext == ".py":
            to = "python"
        elif ext in [".js", ".json"]:
            to = "json"
        elif ext in [".md", ".txt"]:
            to = "markdown"
        else:
            sys.exit("error: unknown output format")

    if to == "python" and args.alt is True:
        to = "alt_python"
    if to == "json" and args.alt is True:
        to = "alt_json"

    reader = readers[from_]
    writer = writers[to]
 
    input = args.input.read()
    try:
        args.input.close()
    except AttributeError:
        pass
    output = writer(reader(input))
    if output and output[-1] != "\n":
        output += "\n"
    args.output.write(output)
    sys.exit(0)

if __main__:
    main()



