
!!! warning
    This documentation is dedicated to the [latest version of the project
    available on github](https://github.com/boisgera/pandoc). 
    It is automatically tested against pandoc 2.14.2,
    [the latest release of pandoc](https://pandoc.org/releases.html) so far.

API Reference
================================================================================

``` python
import pandoc
from pandoc.types import *
```


???+ note "`pandoc.read(source=None, file=None, format=None, options=None)`"
    Read a source document.

    The source document must be specified by either `source` or `file`.
    Implicitly, the document format is inferred from the filename extension
    when possible[^heuristics], otherwise the markdown format is assumed
    by default; the input format can also be specified explicitly.
    Extra options can be passed to the pandoc command-line tool.


    [^heuristics]: refer to [Pandoc's heuristics](https://github.com/jgm/pandoc/blob/master/src/Text/Pandoc/App/FormatHeuristics.hs) for the gory details of this inference.

    <h5>Arguments</h5>


      - `source`: the document content, as a string or as utf-8 encoded bytes.
      
      - `file`: the document, provided as a file or filename.

      - `format`: the document format (such as `"markdown"`, `"odt"`, `"docx"`, `"html"`, etc.)

        Refer to [Pandoc's README](https://github.com/jgm/pandoc#pandoc) for
        the list of supported input formats.

      - `options`: additional pandoc options (a list of strings).

        Refer to [Pandoc's user guide](https://pandoc.org/MANUAL.html) for a
        complete list of options.

    <h5>Returns</h5>

      - `doc`: the document, as a `Pandoc` object.

    <h5>Usage</h5>


    Read documents from strings:

    ``` pycon
    >>> markdown = "Hello world!"
    >>> pandoc.read(markdown)
    Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])
    >>> html = "<p>Hello world!</p>"
    >>> pandoc.read(html, format="html")
    Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])
    ```

    Read documents from files:

    ``` pycon
    >>> filename = "doc.html"
    >>> with open(filename, "w", encoding="utf-8") as file:
    ...     _ = file.write(html)
    >>> pandoc.read(file=filename) # html format inferred from filename
    Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])
    >>> file = open(filename, encoding="utf-8")
    >>> pandoc.read(file=file, format="html") # but here it must be explicit
    Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])
    ```

    Use extra pandoc options:

    ``` pycon
    >>> pandoc.read(markdown, options=["-M", "id=hello"]) # add metadata
    Pandoc(Meta({'id': MetaString('hello')}), [Para([Str('Hello'), Space(), Str('world!')])])
    ```
    

???+ note "`pandoc.write(doc, file=None, format=None, options=None)`"
    Write a pandoc document or document fragment to a file.

    The function always returns the file contents.
    The output for document fragment has empty metadata; 
    inlines are automatically wrapped into a `Plain` block before the write.
    Implicitly, the document format is inferred from the filename extension
    when possible[^heuristics], otherwise the markdown format is assumed
    by default; the output format can also be specified explicitly.
    Extra options can be passed to the pandoc command-line tool.


    <h5>Arguments</h5>

      - `doc`: the document, as a `Pandoc` object, or document fragment 
        (single inline or block or lists of such objects)

      - `file`: a file, filename or `None`.

      - `format`: the document format (such as `"markdown"`, `"odt"`, `"docx"`, `"html"`, etc.)

        Refer to [Pandoc's README](https://github.com/jgm/pandoc#pandoc) for
        the list of supported output formats.

      - `options`: additional pandoc options (a list of strings).

        Refer to [Pandoc's user guide](https://pandoc.org/MANUAL.html) for a
        complete list of options.

    <h5>Returns</h5>

      - `output`: the output document, as a string or as a byte sequence.

        Bytes are only used for binary output formats (doc, ppt, etc.).

    <h5>Usage</h5>

    Write documents to markdown strings:

    ``` pycon
    >>> doc = pandoc.read("Hello world!")
    >>> doc
    Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])
    >>> pandoc.write(doc) # markdown output
    'Hello world!\n'
    ```

    Write document fragments to markdown strings:

    ``` pycon
    >>> pandoc.write(Str("Hello!"))
    'Hello!\n'
    >>> pandoc.write([Str('Hello'), Space(), Str('world!')])
    'Hello world!\n'
    >>> pandoc.write(Para([Str('Hello'), Space(), Str('world!')]))
    'Hello world!\n'
    >>> pandoc.write([
    ...     Para([Str('Hello'), Space(), Str('world!')]),
    ...     Para([Str('Hello'), Space(), Str('world!')])
    ... ])
    'Hello world!\n\nHello world!\n'
    ```

    Use alternate (text or binary) output formats:

    ``` pycon
    >>> pandoc.write(doc, format="html") # html output
    '<p>Hello world!</p>\n'
    >>> pandoc.write(doc, format="odt") # doctest: +ELLIPSIS
    b'PK...'
    ```


    Write documents to files:

    ``` pycon
    >>> _ = pandoc.write(doc, file="doc.md")
    >>> open("doc.md", encoding="utf-8").read()
    'Hello world!\n'
    >>> _ = pandoc.write(doc, file="doc.html")
    >>> open("doc.html", encoding="utf-8").read()
    '<p>Hello world!</p>\n'
    ```

    Use extra pandoc options:

    ``` pycon
    >>> output = pandoc.write(
    ...     doc, 
    ...     format="html", 
    ...     options=["--standalone", "-V", "lang=en"]
    ... )
    >>> print(output) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    <!DOCTYPE html>
    <html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
    ...
    <body>
    <p>Hello world!</p>
    </body>
    </html>
    ```
