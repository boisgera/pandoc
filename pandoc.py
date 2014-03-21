#!/bin/env python

# Python 2.7 Standard Library
pass

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
        return {type(self).__name__: to_json(list(self.args))}
    def __repr__(self):
        typename = type(self).__name__
        args = ", ".join(repr(arg) for arg in self.args)
        return "{0}({1})".format(typename, args)

class Pandoc(PandocType):
    def __json__(self):
        meta, blocks = self.args[0], self.args[1]
        return [meta, [to_json(block) for block in blocks]]
    @staticmethod 
    def read(text):
        return read(text)
    def write(self):
        return write(self)

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

class Str(Inline):
    def __init__(self, *args):
        self.args = [u"".join(args)]
    def __repr__(self):
        text = self.args[0]
        return "{0}({1!r})".format("Str", text)
    def __json__(self):
        return {"Str": self.args[0]}

#
# **Remark:** `Space` is encoded as a string in the json exported by pandoc.
# That's kind of a problem because we won't typematch it like the other
# instances and searching for the string "Space" may lead to false positive.
# The only way to deal with it is to be aware of the context where the Space
# atom (inline) may appear but here we typically are not aware of that.
#

class Strong(Inline):
    pass

class Math(Inline):
    pass


# TODO: check Pandoc version: in 1.12(.1 ?), change in the json output 
#       structure ... Need to handle both kind of outputs ... selection
#       of the format as a new argument to __json__ ? The Text.Pandoc.Definition
#       has been moved to pandoc-types <http://hackage.haskell.org/package/pandoc-types>.
#       Detect the format used by the conversion of a simple document ? Fuck, 
#       In need to be able to access an "old" version of pandoc (the one packaged
#       for ubuntu 12.04 ?). Ah, fuck, all this is a moving target. In 12.1,
#       that's "tag" and "contents", but changelog of 12.1 stated that it is
#       "t" and "c" ... I don't even know what version I am really using.
#       What is supposed to be stable ? There is probably 3 target: the packaged
#       ubuntu 12.04, the 1.12 installed as latest by cabal ... and the current
#       git version ... 1.12.3 ouch. What's in Ubuntu 13.04 ? 13.10 ? The 1.11.1
#       Errr ... Try to build from git the git version and see if there is
#       really a change in the JSON format ?

def to_pandoc(json):
    def is_doc(item):
        return isinstance(item, list) and \
               len(item) == 2 and \
               isinstance(item[0], dict) and \
               "docTitle" in item[0].keys()
    if is_doc(json):
        return Pandoc(*[to_pandoc(item) for item in json])
    elif isinstance(json, list):
        return [to_pandoc(item) for item in json]
    elif isinstance(json, dict) and len(json) == 1:
        key, args = json.items()[0]
        pandoc_type = eval(key)
        return pandoc_type(*to_pandoc(args))
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
# Pandoc Transforms
# ------------------------------------------------------------------------------
#
def apply(transform):
    def doc_transform(doc_item):
        for elt in doc_item.iter():
            transform(elt)
    return doc_transform


def increase_header_level(doc, delta=1):
    def _increase_header_level(delta):
        def _increase(doc_item):
            if isinstance(doc_item, Header):
                doc_item.args[0] = doc_item.args[0] + delta
        return _increase
    return doc.apply(_increase_header_level(delta))

def set_min_header_level(doc, minimum=1):
    levels = [item.args[0] for item in doc.iter() if isinstance(item, Header)]
    if not levels:
        return
    else:
        min_ = min(levels)
        if minimum > min_:
            delta = minimum - min_
            increase_header_level(doc, delta)


#
# Command-Line Interface
# ------------------------------------------------------------------------------
#

# TODO: Pandoc json model to Python repr and back.

if __name__ == "__main__":
    pass


