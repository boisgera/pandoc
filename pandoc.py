#!/usr/bin/env python

# Python 2.7 Standard Library
import json
import sys

# Third-Partly Libraries
import sh
try:
    pandoc = sh.pandoc
    magic, version = sh.pandoc("--version").splitlines()[0].split()
    assert magic == "pandoc"
    assert version.startswith("1.12")
except:
    raise ImportError("cannot find pandoc 1.12")

#
# Pandoc Document Model
# ------------------------------------------------------------------------------
#

def _tree_iter(item):
    "Tree iterator"
    yield item
    if not isinstance(item, basestring):
        try:
            it = iter(item)
            for subitem in it:
                for subsubitem in _tree_iter(subitem):
                    yield subsubitem
        except TypeError: # what kind of TypeError ? Why silence those ? 
            pass

class PandocType(object):
    """
    Pandoc types base class

    Refer to the original [Pandoc Types][] documentation for details.

    [Pandoc Types]: http://hackage.haskell.org/package/pandoc-types
    """
    def __init__(self, *args):
        self.args = list(args)
    def __iter__(self):
        "Child iterator"
        return iter(self.args)
    iter = _tree_iter
    def apply(self, transform): 
        apply(transform)(self)
    def __json__(self):
        """
        Convert the `PandocType instance` into a native Python structure that 
        may be encoded into text by `json.dumps`.
        """
        return {"t": type(self).__name__, "c": to_json(list(self.args))}
    def __repr__(self):
        typename = type(self).__name__
        args = ", ".join(repr(arg) for arg in self.args)
        return "{0}({1})".format(typename, args)

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
    def __json__(self):
        return {"unMeta": {}}

unMeta = Meta

class Block(PandocType):
    pass

class Header(Block):
    pass

class Table(Block):
    pass

class DefinitionList(Block):
    pass

class BulletList(Block):
    pass

class OrderedList(Block):
    pass

class Plain(Block):
    pass

class CodeBlock(Block):
    pass

class DisplayMath(Block):
    pass

class BlockQuote(Block):
    pass

class RawBlock(Block):
    pass

class Inline(PandocType):
    pass

class Emph(Inline):
    pass

class Para(Inline):
    pass

class Code(Inline):
    pass

class Link(Inline):
    pass

class Space(Inline):
    pass

class Str(Inline):
    def __init__(self, *args):
        self.args = [u"".join(args)]
    def __repr__(self):
        text = self.args[0]
        return "{0}({1!r})".format("Str", text)
    def __json__(self):
        return {"t": "Str", "c": self.args[0]}

class Strong(Inline):
    pass

class Math(Inline):
    pass

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
        return pandoc_type(*to_pandoc(contents))
    else:
        return json
    
def to_json(doc_item):
    if hasattr(doc_item, "__json__"):
        return doc_item.__json__()
    elif isinstance(doc_item, list):
        return [to_json(item) for item in doc_item]
    else:
        return doc_item

def read(text):
    """
    Read a markdown text as a Pandoc instance.
    """
    #print "***text:", text
    json_text = str(sh.pandoc(read="markdown", write="json", _in=text))
    json_ = json.loads(json_text)
    #import pprint
    #pp = pprint.PrettyPrinter(indent=2).pprint
    #print "***json:"
    #pp(json_)
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

# TODO: Pandoc json model to Python repr and back ? also with markdown text.

if __name__ == "__main__": # json pandoc output to Python, and back to json
    json_doc = json.loads(sys.stdin.read())
    #print repr(to_pandoc(json_doc))
    print json.dumps(to_json(to_pandoc(json_doc)))

