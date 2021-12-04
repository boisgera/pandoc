
Pandoc – 🐍 Python Library
================================================================================

![Python](https://img.shields.io/pypi/pyversions/pandoc.svg)
[![PyPI version](https://img.shields.io/pypi/v/pandoc.svg)](https://pypi.python.org/pypi/pandoc)
[![Mkdocs](https://img.shields.io/badge/doc-mkdocs-845ed7.svg)](http://boisgera.github.io/pandoc)
[![GitHub discussions](https://img.shields.io/badge/discuss-online-845ef7)](https://github.com/boisgera/pandoc/discussions)
[![Downloads](https://pepy.tech/badge/pandoc)](https://pepy.tech/project/pandoc)
[![GitHub stars](https://img.shields.io/github/stars/boisgera/pandoc?style=flat)](https://github.com/boisgera/pandoc/stargazers)
[![build](https://github.com/boisgera/pandoc/actions/workflows/build.yml/badge.svg)](https://github.com/boisgera/pandoc/actions/workflows/build.yml)


🚀 Getting started
--------------------------------------------------------------------------------

[Pandoc] – the general markup converter (and Haskell library) written by 
[John MacFarlane] – needs to be available. 
You may follow [the official installation instructions](https://pandoc.org/installing.html) which are OS-dependent, or if you use [conda](https://www.google.com/search?client=firefox-b-d&q=conda+python), do

    $ conda install -c conda-forge pandoc

Then, install the latest stable version of the pandoc Python library with pip:

    $ pip install --upgrade pandoc


🌌 Overview 
--------------------------------------------------------------------------------

This project brings [Pandoc]'s data model for markdown documents to Python:

    $ echo "Hello world!" | python -m pandoc read 
    Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])

It can be used to analyze, create and transform documents, in Python :

    >>> import pandoc
    >>> text = "Hello world!"
    >>> doc = pandoc.read(text)
    >>> doc
    Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])

    >>> paragraph = doc[1][0]
    >>> paragraph
    Para([Str('Hello'), Space(), Str('world!')])
    >>> from pandoc.types import Str
    >>> paragraph[0][2] = Str('Python!')
    >>> text = pandoc.write(doc)
    >>> print(text)
    Hello Python!

For more information, refer to the  [📖 documentation](http://boisgera.github.io/pandoc).


[Pandoc]: http://pandoc.org/
[John MacFarlane]: http://johnmacfarlane.net/
[Haskell]: https://www.haskell.org/
[Python]: https://www.python.org/
[TPD]: https://hackage.haskell.org/package/pandoc-types-1.20/docs/Text-Pandoc-Definition.html
