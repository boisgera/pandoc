#!/usr/bin/env python

# Python 2.7 Standard Library
import __builtin__
import abc
import argparse
import copy as _copy
import collections
import contextlib
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
    assert version.startswith("1.12") or version.startswith("1.13")
except:
    raise ImportError("cannot find pandoc 1.12 / 1.13")

# TODO: rethink the tuple thing. Tuple may yield a structure closer to the
#       original one, but also limit the mutability. Replace tuples with
#       list and update the typechecking accordingly ? (even in maps ?)

# TODO: analyze jQuery-like style to implement (mutable) transformations.
#       Selectors mutable transforms that apply on all elements of the list.
#       What would selector look like ? getattr magic to be applied to a
#       list-derived type ?

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

class Sequence(object):
    __metaclass__ = abc.ABCMeta
    @staticmethod
    def iter(sequence):
        if isinstance(sequence, dict):
            sequence = sequence.items()
        return __builtin__.iter(sequence)

Sequence.register(tuple)
Sequence.register(list)
Sequence.register(dict)

# TODO: migrate in a distinct module the transform part.
def transform(node, node_map=None, type_map=None, copy=True):
    if node_map is None:
        node_map = lambda node_: node_
    if type_map is None:
        type_map = lambda type_: type_
    if copy:
        node = _copy.deepcopy(node)
        copy = False

    new_type = type_map(type(node))
    if isinstance(node, (PandocType, Sequence)):
        if isinstance(node, Sequence):
            it = Sequence.iter(node)
        else:
            it = __builtin__.iter(node)
        new_args = [transform(arg, node_map, type_map, copy) for arg in it]
        if type(new_type) is type and issubclass(new_type, Sequence):
            new_instance = new_type(new_args)
        else:
            new_instance = new_type(*new_args)
        return node_map(new_instance)
    else: # atom
        return node_map(node)

# Rk: we don't know what's going on if the item gets muted during the iteration.
#     This iter is usable to extract data or for algorithms that create new
#     structures (and even then, copies should be made). At least add a copy
#     argument ? Default to true (as in transform) ?
def iter(node):
    "Return a tree iterator"
    if isinstance(node, PandocType):
        it = __builtin__.iter(item)
    elif isinstance(node, Sequence):
        it = Sequence.iter(node)
    else: # atom
        it = __builtin__.iter([])

    yield item
    for subitem in it:
        for subsubitem in iter(subitem):
            yield subsubitem

class Map(collections.OrderedDict):
    "Ordered Dictionary"

map = Map
list = list
tuple = tuple # arf. We store tuples as list to get mutability ... sort that out !
Int = int = int
Bool = bool = bool
String = unicode = unicode
Double = float = float

# TODO: refactor: reduce code duplication 
# TODO: consider: no newline for ",", no nesting for single items.
#       It would be more compact and probably more readable for most docs.
# TODO: consider several possible levels of expansion, invoked with -x, -xx, etc.
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

_typecheck = True

@contextlib.contextmanager
def enable_typecheck(status):
    global _typecheck
    _status = _typecheck
    _typecheck = status
    yield
    _typecheck = _status

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
        if _typecheck:
            self.typecheck()

    def typecheck(self, recursive=False):
        if len(self.args) != len(self.args_type):
            error = "invalid number of arguments, {0} instead of {1}"
            raise TypeError(error.format(len(self.args), len(self.args_type)))
        else:
            for arg, type in zip(self.args, self.args_type):
                typecheck(arg, type, recursive=recursive)

# ------------------------------------------------------------------------------
# The list-like methods can be handy, but that should not go too far: PandocType
# shall not inherit from list or tuple. Given our current designed, this is a
# typed/tagged structure that *wraps* (but is not) a inhomogeneous, fixed-length, 
# mutable sequence, hence a hybrid of tuple and list.

    def __iter__(self): # Maybe __iter__ should not be implemented ...
        "Return a child iterator"
        return __builtin__.iter(self.args)

    def __getitem__(self, i):
        return self.args[i]

    def __setitem__(self, i, value):
        self.args[i] = value

    def __len__(self): # I don't know about len either ...
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

# TODO: the typechecker does not grok derivation so far. So for example a type
#       spec may refer to "unMeta" but a Meta is actually used. The args_type
#       of Meta is irrelevant, None should be used, this is abstract

def typecheck(item, type, recursive=False):

    print "t args:", item, type, recursive

    # `type` can be for example: "Block", Block, ["list", ["Block"]], list

    # `recursive=False` means don't recurse on pandoc types, but we still
    # check the native Python objects, that do not typecheck in __init__.

    # TODO: handle tuples properly: tuples exist as lists in the json AND
    #       we also store them as lists (ex: Attr) to keep the mutability.
    #       Only maps have "real" tuples ? Check that. Rethink the mutability ?
    #       Mutability matters, but the ability to infer the "natural" Python
    #       type from the Haskell spec also matters ... Think about Attr and Map
    #       together wrt the use of tuples (these are the only occurences afaict)

    types = globals()
    if isinstance(type, str):
        root_type = type = types[type]
    if isinstance(type, __builtin__.type) and not issubclass(type, PandocType):
        assert type in (list, tuple, map, int, bool, unicode, float)
        return isinstance(item, type) # relax for tuples.

    if isinstance(type, list):
        root_type = types[type[0]] 

    if issubclass(root_type, PandocType):
        if not isinstance(item, root_type):
            error = "{0} is not of type {1}"
            raise TypeError(error.format(item, root_type))
        root_type = __builtin__.type(item)
        if recursive:
            if len(list(item)) != len(root_type.args_type):
                error = "invalid number of arguments, {0} instead of {1}"
                raise TypeError(error.format(len(list(item)), len(root_type.args_type)))
            else:
                for _type, child in zip(root_type.args_type, list(item)):
                    typecheck(child, _type, recursive=recursive)
    else:
        assert root_type in (list, tuple, map)
        if not isinstance(item, root_type): # relax for tuples.
            error = "{0} is not of type {1}"
            raise TypeError(error.format(item, root_type))
        if root_type is list:
            for child in list(item):
                child_type = type[1][0]
                typecheck(child, child_type, recursive=recursive)
        elif root_type is tuple:
            child_types = type[1]
            if len(child_types) !=  len(list(item)):
                error = "invalid number of arguments, {0} instead of {1}"
                raise TypeError(error.format(len(child_types), len(list(item))))
            else:
               for _type, child in zip(child_types, list(item)):
                   typecheck(child, _type, recursive=recursive)
        elif root_type is map:
            map_as_list = list(Sequence.iter(item))
            kv_type = type[1]
            _type = ["list", ["tuple", kv_type]]
            typecheck(map_as_list, _type, recursive=recursive)


# ------------------------------------------------------------------------------

def declare_types(type_spec, bases=object, inline={}, dct={}):
    for k, v in Map(inline).items():
        type_spec = re.sub(r"\b{0}\b".format(k), v, type_spec)
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
    args_type = None
    pass

class unMeta(Meta):
    args_type = [["map", ["String", "MetaValue"]]]

    # unMeta does not follow the json representation with 't' and 'k' keys.
    def __json__(self):
        dct = self.args[0]
        k_v_pairs = [(k, to_json(dct[k])) for k in dct]
        return {"unMeta": Map(k_v_pairs)}

class MetaValue(PandocType):
    pass

# BUG: MetaMap incorrectly parsed as tuple of stuff, solve that.
#      Then test typechecking with the sandbox/meta.txt example.
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

# TODO: manage ListAttributes and derived stuff.

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
""", 
Block, 
inline={
  "Attr": "(String, [String], [(String, String)])",
  "Format": "String", 
  "TableCell": "[Block]",
  "ListAttributes": "(Int, ListNumberStyle, ListNumberDelim)",
})

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
""",
ListNumberStyle)

class ListNumberDelim(PandocType):
    pass

declare_types(\
"""
DefaultDelim	 
Period	 
OneParen	 
TwoParens
"""
)

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
Code Attr String	
Space	
LineBreak	
Math MathType String	
RawInline Format String	
Link [Inline] Target	
Image [Inline] Target	
Note [Block]	
Span Attr [Inline]	
""", 
Inline,
inline={"Attr": "(String, [String], [(String, String)])", 
        "Format": "String", 
        "Target": "(String, String)"})

class MathType(PandocType):
    pass

declare_types(\
"""
DisplayMath
InlineMath
""", MathType)

#
# Citations
# ------------------------------------------------------------------------------
#

# Oo, this is messy. When the --bibliography option is not given to pandoc
# citations are available as the following 'Cite' inline:
#
#     [{"t":"Cite","c":[
#       [
#         {"citationSuffix":[],
#          "citationNoteNum":0,
#          "citationMode":{"t":"NormalCitation","c":[]},
#          "citationPrefix":[],
#          "citationId":"Rud87",
#          "citationHash":0}
#       ],
#       [
#         {"t":"Str","c":"[@Rud87]"}
#       ]
#     ]}]}]]
#
# and when the bibliography is resolved, the second part ([@Rud87]) is 
# substituted with a list of inlines (the citation content):
#
#
#     [{"t":"Cite","c":[
#       [
#         {"citationSuffix":[],
#          "citationNoteNum":0,
#          "citationMode":{"t":"NormalCitation","c":[]},
#          "citationPrefix":[],
#          "citationId":"Rud87",
#          "citationHash":1
#         }
#       ],
#       LIST_OF_INLINES (the citation content) 
#     ]}]
#
# AND, there is some reference to the bibliography file in the metadata.
# (but the 'content' of the citation is NOT printed with the markdown output
# anyway ... that's kinda weird if you ask me (and not a behavior shared by
# all backends). Well anyway: json format can embed the citation data
# but the markdown output won't. 

# Concretely, if I keep on opening the markdown files myself (without any
# reference to a bibliography file), I am gonna miss the citations content.


class Cite(Inline):
    args_type = [["list", ["Citation"]], ["list", ["Inline"]]]

    
class Citation(object):
    pass

class CitationMode(PandocType):
    pass

declare_types(\
"""
AuthorInText	 
SuppressAuthor	 
NormalCitation
""", CitationMode)




# This is a mistake: Citation is not a collection of possible constructors here,
# but a "struct" with several fields. Define accordingly ! And update the
# typechecker for "structs". Here "Citation" does not wrap but "is" a struct,
# there is no type info with "citation".

declare_types(\
"""
citationId :: String
citationPrefix :: [Inline]
citationSuffix :: [Inline]
citationMode :: CitationMode
citationNoteNum :: Int
citationHash :: Int
""", Citation)



declare_types(\
"""
Constructors
AuthorInText
SuppressAuthor
NormalCitation
""", CitationMode)

#
# Json to Pandoc and Pandoc to Json
# ------------------------------------------------------------------------------
#

# TODO: the parsing of Attr has issues : as in the json, they are represented as
#       lists instead of tuples. The issue is that we cannot infer the correct
#       type (and coerce to it), unless we take into account the (type) context.
#       Short-term: hack something.
#       Long-term: drive the reco by the type info.

def _Attrify(type, args):
    """\
Turn list-based descriptions of Attr into:
    
    (String, [String], [(String, String)])
"""
    _Attr_holders = Map([(Code, 0), (CodeBlock, 0), (Div, 0), (Header, 1), (Span, 0)])
    if type in _Attr_holders.keys():
        index = _Attr_holders[type]
        attr = args[index]
        first, second, third = attr
        third = [tuple(child) for child in third]
        args[index] = tuple([first, second, third])

def _Targetify(type, args):
    """\
Turn list-based descriptions of Target into:

    (String, String)
"""
    _Target_holders = Map([(Link, 1), (Image, 1)])
    if type in _Target_holders.keys():
        index = _Target_holders[type]
        args[index] = tuple(args[index])

def _DefinitionListify(type, args):
    """
    --> [([Inline], [[Block]])]
"""

    if type is DefinitionList:
        args[:] = [tuple(item) for item in args]

def _ListAttributesify(type, args):
    """
    """
    if type is OrderedList:
        args[0] = tuple(args[0])

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
        _Attrify(pandoc_type, pandoc_contents)
        _Targetify(pandoc_type, pandoc_contents)
        _DefinitionListify(pandoc_type, pandoc_contents)
        _ListAttributesify(pandoc_type, pandoc_contents)
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
    elif isinstance(json, dict):
        k_v_pairs = [(k, from_json(json[k])) for k in json]
        return Map(k_v_pairs)
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
    return str(sh.pandoc("-s", read="json", write="markdown", _in=json_str))

#
# Command-Line Interface
# ------------------------------------------------------------------------------
#

# TODO: accept inlines(s) and block(s) fragement as valid data ; 
#       expose the function that wraps them in a doc.  

def main():
    "CLI entry point, invoked as `python -m pandoc`"

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
    parser.add_argument("-n", "--no-typecheck", 
                        dest = "typecheck_status",
                        action = "store_false",
                        help = "disable pandoc type checker")
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

    with enable_typecheck(args.typecheck_status):
        output = writer(reader(input))

    if output and output[-1] != "\n":
        output += "\n"
    args.output.write(output)
    sys.exit(0)

if __main__:
    main()



