
Overview
================================================================================

[Pandoc] is the awesome open-source command-line tool that converts documents
from one format to another. The project was initiated by [John MacFarlane];
under the hood, it's a [Haskell] library.

The Pandoc Python Library brings [Pandoc]'s document model to Python:

    $ echo "Hello world!" | python -m pandoc read 
    Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])

It can be used to analyze, create and transform documents, in Python.

-----

Let's transform `"Hello world!"` into `"Hello Python!"` to get a flavor
of the typical workflow:

1. First, we convert the original Markdown text into a `Pandoc` document

    ``` pycon
    >>> import pandoc
    >>> text = "Hello world!"  # markdown text
    >>> doc = pandoc.read(text)
    >>> doc
    Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])
    ```

2. Then we explore the document tree to locate the `"world!"` string. 
   We use branch indices to select the appropriate child of a document fragment;
   we display here the selected fragment at each step for more clarity.

    ```python
    >>> blocks = doc[1]
    >>> blocks
    [Para([Str('Hello'), Space(), Str('world!')])]
    >>> paragraph = blocks[0]
    >>> paragraph
    Para([Str('Hello'), Space(), Str('world!')])
    >>> content = paragraph[0]
    >>> content
    [Str('Hello'), Space(), Str('world!')]
    >>> string = content[2]
    >>> string
    Str('world!')
    >>> string[0]
    'world!'
    ```

2. Equivalently, using attributes instead of indices, we may use the more explicit code

    ```python
    >>> paragraph = doc.blocks[0]
    >>> string = paragraph.content[2]
    >>> string.text
    'world!'
    ```

3. Then we transform the document

    ```python
    >>> string[0] = "Python!"  # or instead: string.text = "Python!"
    ```

4. and finally we output the modified text.

    ```python
    >>> doc
    Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('Python!')])])
    >>> text = pandoc.write(doc)  # the output format is markdown by default
    >>> print(text) # doctest: +NORMALIZE_WHITESPACE
    Hello Python!
    ```


[Pandoc]: http://pandoc.org/
[John MacFarlane]: http://johnmacfarlane.net/
[Haskell]: https://www.haskell.org/

!!! warning
    This documentation is dedicated to the [latest version of the project
    available on github](https://github.com/boisgera/pandoc).
    It is automatically tested with Python 3.12.5 against pandoc 3.3.
    At the moment I am writing this,
    [the latest release of pandoc on conda-forge](https://anaconda.org/conda-forge/pandoc)
    is pandoc 3.3.
