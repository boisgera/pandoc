
Pandoc (Python Library)
================================================================================

[![PyPi](https://img.shields.io/pypi/v/pandoc.svg)](https://pypi.python.org/pypi/pandoc)
![Python](https://img.shields.io/pypi/pyversions/pandoc.svg)
![Status](https://img.shields.io/pypi/status/pandoc.svg)
 [![Build Status](https://travis-ci.org/boisgera/pandoc.svg?branch=master)](https://travis-ci.org/boisgera/pandoc)

A Pythonic Version of Pandoc
--------------------------------------------------------------------------------

[Pandoc] is the "document swiss army knife" made by [John MacFarlane]:

  - a (command-line) tool to convert from one format into another,

  - a (Haskell) library, used to analyze, create, transform documents,

  - a document (meta-)model: a formal specification of what a document *is*.

If you need to convert some documents from one format into another, 
the original command-line tool pandoc is probably what you need.
But if instead you need the more advanced features you may find this 
library useful (especially if you're proficient in Python but don't 
know Haskell).

[Pandoc]: http://pandoc.org/
[John MacFarlane]: http://johnmacfarlane.net/
[Haskell]: https://www.haskell.org/
[Python]: https://www.python.org/

 1. Create a document. For example, start read a markdown text

        >>> import pandoc
        >>> markdown = "Hello"
        >>> doc = pandoc.read(markdown)
        >>> doc
        Pandoc(Meta(map()), [Para([Str(u'Hello!')])])

 2. Analyze and/or transform the document as you like

        >>> from pandoc.types import *
        >>> para = doc[1][0]
        >>> para
        Para([Str(u'Hello')])
        >>> contents = para[0]
        >>> contents
        [Str(u'Hello')]
        >>> contents.extend([Space(), Str("World!")])
        >>> doc
        Pandoc(Meta(map()), [Para([Str(u'Hello'), Space(), Str('World')])])

 3. Write the resulting document to markdown

        >>> pandoc.write(doc)
        u'Hello World\n'

    and maybe, generate its HTML version:

        >>> pandoc.write(doc, file="doc.html")
        u'<p>Hello World</p>\n'


