
Overview
================================================================================

*This documentation is about the 2.x branch of the library (alpha stage!).*


This project brings [Pandoc]'s data model for markdown documents to Python:

    $ echo "Hello world!" | python -m pandoc read 
    Pandoc(Meta(map()), [Para([Str('Hello'), Space(), Str('world!')])])

It can be used to analyze, create and transform documents, in Python :

    >>> import pandoc
    >>> text = "Hello world!"
    >>> doc = pandoc.read(text)
    >>> doc
    Pandoc(Meta(map()), [Para([Str('Hello'), Space(), Str('world!')])])

    >>> paragraph = doc[1][0]
    >>> paragraph
    Para([Str('Hello'), Space(), Str('world!')])
    >>> from pandoc.types import Str
    >>> paragraph[0][2] = Str('Python!')
    >>> text = pandoc.write(doc)
    >>> print(text) # doctest: +NORMALIZE_WHITESPACE
    Hello Python!

[Pandoc] is the general markup converter (and Haskell library) written by [John MacFarlane].


[Pandoc]: http://pandoc.org/
[John MacFarlane]: http://johnmacfarlane.net/
[Haskell]: https://www.haskell.org/
[Python]: https://www.python.org/
[TPD]: https://hackage.haskell.org/package/pandoc-types-1.20/docs/Text-Pandoc-Definition.html

