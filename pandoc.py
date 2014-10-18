#!/usr/bin/env python

# Python 2.7 Standard Library
import abc
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
#     structures (and even then, copies should be made).
def iter(node):
    "Return a tree iterator"
    if isinstance(node, PandocType):
        it = __builtin__.iter(item)
    elif isinstance(node, Sequence):
        it = Sequence.iter(node)
    else: # atom
        it = None

    yield item
    if it is not None:
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
        return __builtin__.iter(self.args)

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



