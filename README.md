

Pandoc (Python Library)
================================================================================

![Python](https://img.shields.io/pypi/pyversions/pandoc.svg)
[![PyPi](https://img.shields.io/pypi/v/pandoc.svg)](https://pypi.python.org/pypi/pandoc)
![Status](https://img.shields.io/pypi/status/pandoc.svg)
 [![Build Status](https://travis-ci.org/boisgera/pandoc.svg?branch=master)](https://travis-ci.org/boisgera/pandoc)

**Warning.**
This project is *not* a Python binding for [pandoc], the command-line tool. 
If this is what you need, you can either use [pypandoc], [pyandoc], etc.,
or create you own wrapper with [subprocess] or [sh].

[pandoc]: http://pandoc.org/
[pypandoc]: https://pypi.python.org/pypi/pypandoc/
[pyandoc]: https://github.com/kennethreitz/pyandoc
[sh]: https://amoffat.github.io/sh/
[subprocess]: https://docs.python.org/2/library/subprocess.html

-----

This library provides a Pythonic way to analyze, create and 
transform documents.
It targets the pandoc power users which are more productive
in Python than in Haskell (the native language of the pandoc library).

The pandoc Python library translates documents between the native 
pandoc JSON format and a Python document model. 
If you need to manage other formats (html, latex, etc.) use the 
pandoc command-line tool to convert to/from the JSON format.

This library is still in the alpha stage and not documented.
To get a better feel of the Python document model
(an automated translation of [the Haskell one][Text.Pandoc.Definition]),
have a look at the [test suite][].
The typical workflow is the following:

 1. Get a document in the JSON format:

        >>> json_input = [{"unMeta":{}},[{"t":"Para","c":[{"t":"Str","c":"Hello"}]}]]

    To be honest, I got this one with the commands:

        >>> import json, os
        >>> file = os.popen('echo "Hello" | pandoc -t json')
        >>> json_input = json.load(file)

 2. Read it as a Python document

        >>> import pandoc
        >>> doc = pandoc.read(json_input)
        >>> doc
        Pandoc(Meta(map()), [Para([Str(u'Hello!')])])

 3. Analyze and/or transform the document

        >>> from pandoc.types import Space, Str
        >>> doc[1][0][0].extend([Space(), Str(u"World!")])
        >>> doc
        Pandoc(Meta(map()), [Para([Str(u'Hello'), Space(), Str(u'World!')])])

 4. Export the resulting document to JSON

        >>> json_output = pandoc.write(doc)

    and maybe, generate its HTML version:

        >>> import json, os     
        >>> json.dump(json_output, open("doc.json", "w"))
        >>> os.system("pandoc doc.json")
        <p>Hello World!</p>
        0

[Text.Pandoc.Definition]: https://hackage.haskell.org/package/pandoc-types-1.16.1/docs/Text-Pandoc-Definition.html 
[test suite]: https://github.com/boisgera/pandoc/blob/master/pandoc/tests.md
 
<!--

Common Code
--------------------------------------------------------------------------------

For all examples, we use the following imports

    import json
    import sys
    import pandoc
    from pandoc.types import *

and the following depth-first document iterator: 

    def iter(elt, enter=None, exit=None):
        yield elt
        if enter is not None:
            enter(elt)
        if isinstance(elt, dict):
            elt = elt.items()
        if hasattr(elt, "__iter__"): # exclude strings
            for child in elt:
                 for subelt in iter(child, enter, exit):
                     yield subelt
        if exit is not None:
            exit(elt)


Mathematics
--------------------------------------------------------------------------------

Define the file `math.py` to count the number of math items in documents:

    def find_math(doc):
        return [elt for elt in iter(doc) if type(elt) is Math]
        
    if __name__ == "__main__":
        doc = pandoc.read(json.load(sys.stdin))
        print "math:", len(find_math(doc)), "items."

Then, use it on the (markdown) document `doc.txt`:

    $ pandoc -t json doc.txt | python math.py


Implicit Sections
--------------------------------------------------------------------------------

I like to use bold text at the beginning of a paragraph to denote the existence 
of a low-level section. 
This pattern can be detected and the sections automatically explicited.

Define a `sections.py` file ; then, use the hooks defined in the depth-first
iterator factory to provide the full path from the root to the element at 
each step:

    def iter_path(elt):
        parents = []
        def enter(elt_):
            parents.append(elt_)
        def exit(elt_):
            parents.pop()
        for elt_ in iter(elt, enter, exit):
            yield parents + [elt_]

Leverage this new iterator to find the parent of an element:

    def find_parent(doc, elt):
        for path in iter_path(doc):
            elt_ = path[-1]
            parent = path[-2] if len(path) >= 2 else None
            if elt is elt_:
                 return parent

To detect a paragraph that is an implicit section, define:

    def match_implicit_section(elt):
        if type(elt) is Para:
            content = elt[0]
            if len(content) >= 1 and type(content[0]) is Strong:
                return True
        return False

The transformation itself:

    def explicit_sections(doc, level=6):
        for para in filter(match_implicit_section, iter(doc)):
            blocks = find_parent(doc, para)
            content = para[0].pop(0)[0]
            if len(para[0]) >= 1 and para[0][0] == Space():
                para[0].pop(0)
            index = blocks.index(para)
            header = Header(level, ("", [], []), content)
            blocks.insert(index, header)
        return doc

Finally, provide the command-line API with

    if __name__ == "__main__":
        doc = pandoc.read(json.load(sys.stdin))
        doc = explicit_sections(doc)
        print json.dumps(pandoc.write(doc))

and use it like that:

    $ pandoc -t json doc.txt | \
    > python sections.py | \
    > pandoc -f json -o doc2.txt

-->

