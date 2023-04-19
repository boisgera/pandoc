
Overview
================================================================================

[Pandoc] is the awesome open-source command-line tool that converts documents 
from one format to another. The project was initiated by [John MacFarlane]; 
under the hood, it's a [Haskell] library.

The Pandoc Python Library (PPL) brings [Pandoc]'s document model to Python:

    $ echo "Hello world!" | python -m pandoc read 
    Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])

It can be used to analyze, create and transform documents, in Python :

``` pycon
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
>>> print(text) # doctest: +NORMALIZE_WHITESPACE
Hello Python!
```



[Pandoc]: http://pandoc.org/
[John MacFarlane]: http://johnmacfarlane.net/
[Haskell]: https://www.haskell.org/
[Python]: https://www.python.org/
[TPD]: https://hackage.haskell.org/package/pandoc-types-1.23/docs/Text-Pandoc-Definition.html

!!! warning
    This documentation is dedicated to the [latest version of the project
    available on github](https://github.com/boisgera/pandoc). 
    It is automatically tested with Python 3.10 against pandoc 2.1.1.
    At the moment I am writing this,
    [the latest release of pandoc for conda](https://anaconda.org/conda-forge/pandoc) 
    is pandoc 3.1.1.