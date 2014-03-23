#!/usr/bin/env python

# Python 2.7 Standard Library
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

# TODO: support kwargs at this level (for MetaValues).
#       Arf actually, the constructor arguments could be a list/tuple of
#       stuff, a dictionary of stuff or a single string. Here for the moment
#       we support only list/tuple stuff in the constructor, this is why
#       MetaMap and Str are implemented manually. Rk: that could even be
#       a bool, see MetaBool ! The *args, **kwargs stuff is an issue because
#       we cannot distinguish a single argument and a list of one argument
#       if the list / dict are expanded prior to the constructor call.
#       Also, tuples/list args could/should be distinguished ? Tuples are
#       heterogeneous sequences of fixed size, lists are homogeneous sequences
#       of variable size ...

# Q: how do we support iteration if the constructor has keyword arguments ?

class PandocType(object):
    """
    Pandoc types base class

    Refer to the original [Pandoc Types][] documentation for details.

    [Pandoc Types]: http://hackage.haskell.org/package/pandoc-types
    """
    def __init__(self, *args, **kwargs):
        self.args = list(args)

    @staticmethod
    def _tree_iter(item):
        "Tree iterator"
        yield item
        if not isinstance(item, basestring):
            try:
                it = iter(item)
                for subitem in it:
                    for subsubitem in PandocType._tree_iter(subitem):
                        yield subsubitem
            except TypeError: # non-iterable. Is this check necessary ? 
                pass

    def __iter__(self):
        "Child iterator"
        return iter(self.args)

    iter = _tree_iter.__func__

    def __json__(self):
        """
        Convert the `PandocType instance` into a native Python structure that 
        may be encoded into text by `json.dumps`.
        """
        return {"t": type(self).__name__, "c": to_json(self.args)}

    def __repr__(self):
        typename = type(self).__name__
        args = ", ".join(repr(arg) for arg in self.args)
        return "{0}({1})".format(typename, args)

def declare_types(type_spec, bases=[object], dct={}):
    for type_spec_ in type_spec.strip().splitlines():
       type_name = type_spec_.strip().split()[0]
       globals()[type_name] = type(type_name, tuple(bases), dct)

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
    def __json__(self):
        return {"unMeta": {}}

class MetaValue(PandocType):
    pass

declare_types(\
"""
MetaList [MetaValue]	 
MetaBool Bool	 
MetaString String	 
MetaInlines [Inline]	 
MetaBlocks [Block]
""", [MetaValue])

# "MetaMap (Map String MetaValue)" has to be handled manually.
class MetaMap(MetaValue):
    def __init__(self, *kwargs):
        self.kwargs = dict(kwargs)
    def __repr__(self):
        typename = type(self).__name__
        kwargs = ", ".join("{0}={1!r}".format(k, v) for k, v in self.kwargs.items())
        return "{0}({1})".format(typename, args)
    def __json__(self):
        """
        Convert the `PandocType instance` into a native Python structure that 
        may be encoded into text by `json.dumps`.
        """
        return {"t": type(self).__name__, "c": to_json(dict(self.kwargs))}

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
""", [Block])

class Inline(PandocType):
    pass

# TODO: document why this class is special.
class Str(Inline):
    def __init__(self, *args):
        self.args = [u"".join(args)]
    def __json__(self):
        return {"t": "Str", "c": self.args[0]}
    def __repr__(self):
        text = self.args[0]
        return "{0}({1!r})".format("Str", text)

declare_types(\
"""
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
""", [Inline])

class MathType(PandocType):
    pass

class DisplayMath(MathType):
    pass

class MathInline(MathType):
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
        if isinstance(pandoc_contents, list):
            return pandoc_type(*pandoc_contents)
        elif isinstance(pandoc_contents, dict):
            return pandoc_type(**pandoc_contents)
        else:
            return pandoc_type(pandoc_contents)
    elif isinstance(json, dict) and "unMeta" in json:
        dct = json["unMeta"]
        return unMeta({key: to_pandoc(dct[key]) for key in dct})
    elif isinstance(json, dict):
        return {key: to_pandoc(json[key]) for key in json}
    else:
        return json
    
def to_json(doc_item):
    if hasattr(doc_item, "__json__"):
        return doc_item.__json__()
    elif isinstance(doc_item, list):
        return [to_json(item) for item in doc_item]
    elif isinstance(doc_item, dict):
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
    json_ = json.loads(json_text)
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
    json_ = json.loads(sys.stdin.read())
    print repr(to_pandoc(json_))

