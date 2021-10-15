
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
    by default; the format can also be specified explicitly.
    Extra options can be passed to the pandoc command-line tool.


    <h5>Arguments</h5>


      - `source`: the document content, as a string or as utf-8 encoded bytes.
      
      - `file`: the document, provided as a file or filename.

    [^heuristics]: refer to [Pandoc's heuristics](https://github.com/jgm/pandoc/blob/master/src/Text/Pandoc/App/FormatHeuristics.hs) for the gory details of this inference.

      - `format`: the document format (such as `"markdown"`, `"odt"`, `"docx"`, `"html"`, etc.)

        Refer to [Pandoc's README](https://github.com/jgm/pandoc#pandoc) for
        the list of supported input formats.

      - `options`: additional pandoc options (a list of strings).

        Refer to [Pandoc's user guide](https://pandoc.org/MANUAL.html) for a
        complete list of options.

    <h5>Returns</h5>

      - `doc`: the document, as an instance of `pandoc.types.Pandoc`.

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

    Use pandoc options:
    ``` python
    >>> pandoc.read(markdown, options=["-M", "id=hello"]) # add metadata
    Pandoc(Meta({'id': MetaString('hello')}), [Para([Str('Hello'), Space(), Str('world!')])])
    ```

???+ note "`pandoc.write(doc, file=None, format=None, options=None)`"
    
