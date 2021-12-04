
Pandoc (Python Library)
================================================================================

[![build](https://github.com/boisgera/pandoc/actions/workflows/build.yml/badge.svg)](https://github.com/boisgera/pandoc/actions/workflows/build.yml)
[![Mkdocs](https://img.shields.io/badge/doc-mkdocs-blue.svg)](http://boisgera.github.io/pandoc)
[![Downloads](https://pepy.tech/badge/pandoc)](https://pepy.tech/project/pandoc)
[![GitHub stars](https://img.shields.io/github/stars/boisgera/pandoc?style=flat)](https://github.com/boisgera/pandoc/stargazers)
[![Gitter chat](https://badges.gitter.im/boisgera/python-pandoc.svg)](https://gitter.im/python-pandoc/community#) 

*This README is about the 2.x branch of the library (alpha stage!). Only the 1.x branch is available on PyPi at the moment.*

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
