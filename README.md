
Pandoc (Python Library)
================================================================================

<!--
[![PyPi](https://img.shields.io/pypi/v/pandoc.svg)](https://pypi.python.org/pypi/pandoc)
![Python](https://img.shields.io/pypi/pyversions/pandoc.svg)
![Status](https://img.shields.io/pypi/status/pandoc.svg)
-->
[![Travis CI Build Status](https://travis-ci.org/boisgera/pandoc.svg?branch=master)](https://travis-ci.org/boisgera/pandoc)
[![AppVeyor Build status](https://ci.appveyor.com/api/projects/status/usube01hmjcl1m0t?svg=true)](https://ci.appveyor.com/project/boisgera/pandoc)

*This README is about the 2.x branch of the library (alpha stage!).*

Getting started
--------------------------------------------------------------------------------

Install the latest version with:

    $ pip install --upgrade git+https://github.com/boisgera/pandoc.git

The [Pandoc] command-line tool is a also required dependency ;
you may install it with :

    $ conda install -c conda-forge pandoc 

Overview
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

[Pandoc] is the general markup converter (and Haskell library) written by [John MacFarlane].


[Pandoc]: http://pandoc.org/
[John MacFarlane]: http://johnmacfarlane.net/
[Haskell]: https://www.haskell.org/
[Python]: https://www.python.org/
[TPD]: https://hackage.haskell.org/package/pandoc-types-1.20/docs/Text-Pandoc-Definition.html
