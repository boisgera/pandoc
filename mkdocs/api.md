API Reference
================================================================================

``` python
import pandoc
from pandoc.types import *
```

`pandoc`
--------------------------------------------------------------------------------


??? note "`read(source=None, file=None, format=None, options=None)`"
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
    

??? note "`write(doc, file=None, format=None, options=None)`"
    Write a pandoc document (or document fragment) to a file and return its contents.


    Inline document fragments are automatically wrapped into a `Plain` 
    blocks; block document fragments are automatically wrapped into
    a `Pandoc` element with no metadata. 

    Implicitly, the document format is inferred from the filename extension
    when possible[^heuristics], otherwise the markdown format is assumed
    by default; the output format can also be specified explicitly.
    Extra options can be passed to the pandoc command-line tool.


    <h5>Arguments</h5>

      - `doc`: a `Pandoc` object or a document fragment 
        (`Inline`, `[Inline]`, `MetaInlines`, 
         `Block`, `[Block]` or `MetaBlocks`).

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
    >>> print(pandoc.write(doc))  # doctest: +NORMALIZE_WHITESPACE
    Hello world!
    ```

    Write document fragments to markdown strings:

    ``` pycon
    >>> md = lambda elt: print(pandoc.write(elt))
    >>> md(Str("Hello!")) # doctest: +NORMALIZE_WHITESPACE
    Hello!
    >>> md([Str('Hello'), Space(), Str('world!')]) # doctest: +NORMALIZE_WHITESPACE
    Hello world!
    >>> md(Para([Str('Hello'), Space(), Str('world!')])) # doctest: +NORMALIZE_WHITESPACE
    Hello world!
    >>> md([ # doctest: +NORMALIZE_WHITESPACE
    ...     Para([Str('Hello'), Space(), Str('world!')]),
    ...     Para([Str('Hello'), Space(), Str('world!')])
    ... ])
    Hello world!
    <BLANKLINE>
    Hello world!
    >>> md(MetaInlines([Str('Hello'), Space(), Str('world!')])) # doctest: +NORMALIZE_WHITESPACE
    Hello world!
    >>> md(MetaBlocks([ # doctest: +NORMALIZE_WHITESPACE
    ...     Para([Str('Hello'), Space(), Str('world!')]),
    ...     Para([Str('Hello'), Space(), Str('world!')])
    ... ]))
    Hello world!
    <BLANKLINE>
    Hello world!
    ```

    Use alternate (text or binary) output formats:

    ``` pycon
    >>> output = pandoc.write(doc, format="html") # html output
    >>> type(output)
    <class 'str'>
    >>> print(output)
    <p>Hello world!</p>
    <BLANKLINE>
    >>> output = pandoc.write(doc, format="odt")
    >>> type(output)
    <class 'bytes'>
    >>> output # doctest: +ELLIPSIS
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
    >>> _ = pandoc.write(doc, file="doc.pdf")
    >>> open("doc.pdf", "rb").read() # doctest: +ELLIPSIS
    b'%PDF...'
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

??? note "`iter(elt, path=False)`"

    Iterate on document elements in document order.
    
    <h5>Arguments</h5>

      - `elt`: a pandoc item (or more generally any Python object),

      - `path`: a boolean; defaults to `False`.

    <h5>Returns</h5>

      - `iterator`: a depth-first tree iterator.

      - `elt_path` (when `path==True`): a list of `(elt, index)` pairs. 
      
    <h5>Usage</h5>

    This iterator may be used as a general-purpose tree iterator

    ``` pycon
    >>> tree = [1, [2, [3]]]
    >>> for elt in pandoc.iter(tree):
    ...     print(elt)
    [1, [2, [3]]]
    1
    [2, [3]]
    2
    [3]
    3
    ```

    Non-iterable objects yield themselves:

    ``` pycon
    >>> root = 1
    >>> for elt in pandoc.iter(root):
    ...     print(elt)
    1
    ```

    But it is really meant to be used with pandoc objects:

    ``` pycon
    >>> doc = Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])
    >>> for elt in pandoc.iter(doc):
    ...     print(elt)
    Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])
    Meta({})
    {}
    [Para([Str('Hello'), Space(), Str('world!')])]
    Para([Str('Hello'), Space(), Str('world!')])
    [Str('Hello'), Space(), Str('world!')]
    Str('Hello')
    Hello
    Space()
    Str('world!')
    world!
    ```

    Two gotchas: characters in strings are not iterated (strings are considered
    "atomic")

    ``` pycon
    >>> root = "Hello world!"
    >>> for elt in pandoc.iter(root):
    ...     print(elt)
    Hello world!
    ```

    and dicts yield their key-value pairs (and not only their keys):

    ``` pycon
    >>> root = {"a": 1, "b": 2}
    >>> for elt in pandoc.iter(root):
    ...      print(elt)
    {'a': 1, 'b': 2}
    ('a', 1)
    a
    1
    ('b', 2)
    b
    2
    ```

    Use `path=True` when you need to locate the element in the document.
    You can get the element parent and index within this parent as `path[-1]`,
    the grand-parent and the index of the parent within the grand-parent 
    as `path[-2]`, etc. up to the document root.

    ``` pycon
    >>> doc = Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])
    >>> world = Str("world!")
    >>> for elt, path in pandoc.iter(doc, path=True): # find the path to Str("world!")
    ...     if elt == world:
    ...         break
    >>> for elt, index in path:
    ...     print(f"At index {index} in {elt}:")
    ... else:
    ...     print(world)
    At index 1 in Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])]):
    At index 0 in [Para([Str('Hello'), Space(), Str('world!')])]:
    At index 0 in Para([Str('Hello'), Space(), Str('world!')]):
    At index 2 in [Str('Hello'), Space(), Str('world!')]:
    Str('world!')
    ```

    <h5>See also</h5>

    Refer to the [Tree iteration section](#tree-iteration).


??? note "`configure(auto=False, path=None, version=None, pandoc_types_version=None, read=False, reset=False)`"

    <h5>Arguments</h5>

      - `auto`: a boolean; defaults to `False`; set to `True` to
        infer the configuration from the `pandoc` in your path.

      - `path`: the path to the pandoc executable, such as `"/usr/bin/pandoc"`.

      - `version`: the `pandoc` command-line tool version, such as `"2.14.2"`.

      - `pandoc_types_version`: the [`pandoc-types`](https://hackage.haskell.org/package/pandoc-types)
         version, such as `"1.22.1"`.

      - `read`: a boolean; defaults to `False`. Return the configuration dictionary.

      - `reset`: a boolean; defaults to `False`. Delete the current configuration.

    <h5>Returns</h5>

      - `configuration` (if `read==True`): the configuration dictionary,
        with entries `"auto"`, `"path"`, `"version"` and "`pandoc_types_version`".

    <h5>Usage</h5>

    The configuration step is triggered when you import `pandoc.types` or
    call `pandoc.read` or `pandoc.write` and will automatically infer the
    configuration from the `pandoc` executable found in the path (or fails).

    ``` pycon
    >>> config = pandoc.configure(read=True)
    >>> config # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    {'auto': True, 
     'path': ..., 
     'version': '2.19.2', 
     'pandoc_types_version': '1.22.2.1'}
    ```
    To avoid this, call `pandoc.configure(...)` yourself beforehand.
    Alternatively, select manually your pandoc executable afterwards:

    ``` pycon
    >>> pandoc.configure(reset=True)
    >>> pandoc.configure(read=True) is None
    True
    >>> config["auto"] = False
    >>> pandoc.configure(**config)
    >>> pandoc.configure(read=True) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    {'auto': False, 
     'path': ..., 
     'version': '2.19.2', 
     'pandoc_types_version': '1.22.2.1'}    
    ```

    <h5>See also</h5>

    Refer to the [Configuration section](#configuration).


`pandoc.types`
--------------------------------------------------------------------------------


<div id="AlignCenter"></div>

??? note "`AlignCenter`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    AlignCenter()
    ```



<div id="AlignDefault"></div>

??? note "`AlignDefault`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    AlignDefault()
    ```



<div id="AlignLeft"></div>

??? note "`AlignLeft`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    AlignLeft()
    ```



<div id="AlignRight"></div>

??? note "`AlignRight`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    AlignRight()
    ```



<div id="Alignment"></div>

??? note "`Alignment`"

    Abstract data type

    <h5>Signature</h5>

    ``` skip
    Alignment = AlignLeft()
              | AlignRight()
              | AlignCenter()
              | AlignDefault()
    ```

    <h5>See also</h5>
    
    <a href="#AlignCenter"><code>AlignCenter</code></a>, <a href="#AlignDefault"><code>AlignDefault</code></a>, <a href="#AlignLeft"><code>AlignLeft</code></a>, <a href="#AlignRight"><code>AlignRight</code></a>.

<div id="Attr"></div>

??? note "`Attr`"

    Typedef

    <h5>Signature</h5>

    ``` skip
    Attr = (Text, [Text], [(Text, Text)])
    ```

    <h5>See also</h5>
    
    <a href="#Text"><code>Text</code></a>.

<div id="AuthorInText"></div>

??? note "`AuthorInText`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    AuthorInText()
    ```



<div id="Block"></div>

??? note "`Block`"

    Abstract data type

    <h5>Signature</h5>

    ``` skip
    Block = Plain([Inline])
          | Para([Inline])
          | LineBlock([[Inline]])
          | CodeBlock(Attr, Text)
          | RawBlock(Format, Text)
          | BlockQuote([Block])
          | OrderedList(ListAttributes, [[Block]])
          | BulletList([[Block]])
          | DefinitionList([([Inline], [[Block]])])
          | Header(Int, Attr, [Inline])
          | HorizontalRule()
          | Table(Attr, Caption, [ColSpec], TableHead, [TableBody], TableFoot)
          | Div(Attr, [Block])
          | Null()
    ```

    <h5>See also</h5>
    
    <a href="#Attr"><code>Attr</code></a>, <a href="#BlockQuote"><code>BlockQuote</code></a>, <a href="#BulletList"><code>BulletList</code></a>, <a href="#Caption"><code>Caption</code></a>, <a href="#CodeBlock"><code>CodeBlock</code></a>, <a href="#ColSpec"><code>ColSpec</code></a>, <a href="#DefinitionList"><code>DefinitionList</code></a>, <a href="#Div"><code>Div</code></a>, <a href="#Format"><code>Format</code></a>, <a href="#Header"><code>Header</code></a>, <a href="#HorizontalRule"><code>HorizontalRule</code></a>, <a href="#Inline"><code>Inline</code></a>, <a href="#Int"><code>Int</code></a>, <a href="#LineBlock"><code>LineBlock</code></a>, <a href="#ListAttributes"><code>ListAttributes</code></a>, <a href="#Null"><code>Null</code></a>, <a href="#OrderedList"><code>OrderedList</code></a>, <a href="#Para"><code>Para</code></a>, <a href="#Plain"><code>Plain</code></a>, <a href="#RawBlock"><code>RawBlock</code></a>, <a href="#Table"><code>Table</code></a>, <a href="#TableBody"><code>TableBody</code></a>, <a href="#TableFoot"><code>TableFoot</code></a>, <a href="#TableHead"><code>TableHead</code></a>, <a href="#Text"><code>Text</code></a>.

<div id="BlockQuote"></div>

??? note "`BlockQuote`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    BlockQuote([Block])
    ```

    <h5>See also</h5>
    
    <a href="#Block"><code>Block</code></a>.

<div id="Bool"></div>

??? note "`Bool`"

    Primitive type

    <h5>Signature</h5>

    ``` skip
    bool
    ```



<div id="BulletList"></div>

??? note "`BulletList`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    BulletList([[Block]])
    ```

    <h5>See also</h5>
    
    <a href="#Block"><code>Block</code></a>.

<div id="Caption"></div>

??? note "`Caption`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Caption(ShortCaption or None, [Block])
    ```

    <h5>See also</h5>
    
    <a href="#Block"><code>Block</code></a>, <a href="#ShortCaption"><code>ShortCaption</code></a>.

<div id="Cell"></div>

??? note "`Cell`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Cell(Attr, Alignment, RowSpan, ColSpan, [Block])
    ```

    <h5>See also</h5>
    
    <a href="#Alignment"><code>Alignment</code></a>, <a href="#Attr"><code>Attr</code></a>, <a href="#Block"><code>Block</code></a>, <a href="#ColSpan"><code>ColSpan</code></a>, <a href="#RowSpan"><code>RowSpan</code></a>.

<div id="Citation"></div>

??? note "`Citation`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Citation(Text, [Inline], [Inline], CitationMode, Int, Int)
    ```

    <h5>See also</h5>
    
    <a href="#CitationMode"><code>CitationMode</code></a>, <a href="#Inline"><code>Inline</code></a>, <a href="#Int"><code>Int</code></a>, <a href="#Text"><code>Text</code></a>.

<div id="CitationMode"></div>

??? note "`CitationMode`"

    Abstract data type

    <h5>Signature</h5>

    ``` skip
    CitationMode = AuthorInText()
                 | SuppressAuthor()
                 | NormalCitation()
    ```

    <h5>See also</h5>
    
    <a href="#AuthorInText"><code>AuthorInText</code></a>, <a href="#NormalCitation"><code>NormalCitation</code></a>, <a href="#SuppressAuthor"><code>SuppressAuthor</code></a>.

<div id="Cite"></div>

??? note "`Cite`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Cite([Citation], [Inline])
    ```

    <h5>See also</h5>
    
    <a href="#Citation"><code>Citation</code></a>, <a href="#Inline"><code>Inline</code></a>.

<div id="Code"></div>

??? note "`Code`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Code(Attr, Text)
    ```

    <h5>See also</h5>
    
    <a href="#Attr"><code>Attr</code></a>, <a href="#Text"><code>Text</code></a>.

<div id="CodeBlock"></div>

??? note "`CodeBlock`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    CodeBlock(Attr, Text)
    ```

    <h5>See also</h5>
    
    <a href="#Attr"><code>Attr</code></a>, <a href="#Text"><code>Text</code></a>.

<div id="ColSpan"></div>

??? note "`ColSpan`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    ColSpan(Int)
    ```

    <h5>See also</h5>
    
    <a href="#Int"><code>Int</code></a>.

<div id="ColSpec"></div>

??? note "`ColSpec`"

    Typedef

    <h5>Signature</h5>

    ``` skip
    ColSpec = (Alignment, ColWidth)
    ```

    <h5>See also</h5>
    
    <a href="#Alignment"><code>Alignment</code></a>, <a href="#ColWidth"><code>ColWidth</code></a>.

<div id="ColWidth"></div>

??? note "`ColWidth`"

    Abstract data type

    <h5>Signature</h5>

    ``` skip
    ColWidth = ColWidth_(Double)
             | ColWidthDefault()
    ```

    <h5>See also</h5>
    
    <a href="#ColWidthDefault"><code>ColWidthDefault</code></a>, <a href="#ColWidth_"><code>ColWidth_</code></a>, <a href="#Double"><code>Double</code></a>.

<div id="ColWidthDefault"></div>

??? note "`ColWidthDefault`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    ColWidthDefault()
    ```



<div id="ColWidth_"></div>

??? note "`ColWidth_`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    ColWidth_(Double)
    ```

    <h5>See also</h5>
    
    <a href="#Double"><code>Double</code></a>.

<div id="Decimal"></div>

??? note "`Decimal`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Decimal()
    ```



<div id="DefaultDelim"></div>

??? note "`DefaultDelim`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    DefaultDelim()
    ```



<div id="DefaultStyle"></div>

??? note "`DefaultStyle`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    DefaultStyle()
    ```



<div id="DefinitionList"></div>

??? note "`DefinitionList`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    DefinitionList([([Inline], [[Block]])])
    ```

    <h5>See also</h5>
    
    <a href="#Block"><code>Block</code></a>, <a href="#Inline"><code>Inline</code></a>.

<div id="DisplayMath"></div>

??? note "`DisplayMath`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    DisplayMath()
    ```



<div id="Div"></div>

??? note "`Div`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Div(Attr, [Block])
    ```

    <h5>See also</h5>
    
    <a href="#Attr"><code>Attr</code></a>, <a href="#Block"><code>Block</code></a>.

<div id="Double"></div>

??? note "`Double`"

    Primitive type

    <h5>Signature</h5>

    ``` skip
    float
    ```



<div id="DoubleQuote"></div>

??? note "`DoubleQuote`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    DoubleQuote()
    ```



<div id="Emph"></div>

??? note "`Emph`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Emph([Inline])
    ```

    <h5>See also</h5>
    
    <a href="#Inline"><code>Inline</code></a>.

<div id="Example"></div>

??? note "`Example`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Example()
    ```



<div id="Format"></div>

??? note "`Format`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Format(Text)
    ```

    <h5>See also</h5>
    
    <a href="#Text"><code>Text</code></a>.

<div id="Header"></div>

??? note "`Header`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Header(Int, Attr, [Inline])
    ```

    <h5>See also</h5>
    
    <a href="#Attr"><code>Attr</code></a>, <a href="#Inline"><code>Inline</code></a>, <a href="#Int"><code>Int</code></a>.

<div id="HorizontalRule"></div>

??? note "`HorizontalRule`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    HorizontalRule()
    ```



<div id="Image"></div>

??? note "`Image`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Image(Attr, [Inline], Target)
    ```

    <h5>See also</h5>
    
    <a href="#Attr"><code>Attr</code></a>, <a href="#Inline"><code>Inline</code></a>, <a href="#Target"><code>Target</code></a>.

<div id="Inline"></div>

??? note "`Inline`"

    Abstract data type

    <h5>Signature</h5>

    ``` skip
    Inline = Str(Text)
           | Emph([Inline])
           | Underline([Inline])
           | Strong([Inline])
           | Strikeout([Inline])
           | Superscript([Inline])
           | Subscript([Inline])
           | SmallCaps([Inline])
           | Quoted(QuoteType, [Inline])
           | Cite([Citation], [Inline])
           | Code(Attr, Text)
           | Space()
           | SoftBreak()
           | LineBreak()
           | Math(MathType, Text)
           | RawInline(Format, Text)
           | Link(Attr, [Inline], Target)
           | Image(Attr, [Inline], Target)
           | Note([Block])
           | Span(Attr, [Inline])
    ```

    <h5>See also</h5>
    
    <a href="#Attr"><code>Attr</code></a>, <a href="#Block"><code>Block</code></a>, <a href="#Citation"><code>Citation</code></a>, <a href="#Cite"><code>Cite</code></a>, <a href="#Code"><code>Code</code></a>, <a href="#Emph"><code>Emph</code></a>, <a href="#Format"><code>Format</code></a>, <a href="#Image"><code>Image</code></a>, <a href="#LineBreak"><code>LineBreak</code></a>, <a href="#Link"><code>Link</code></a>, <a href="#Math"><code>Math</code></a>, <a href="#MathType"><code>MathType</code></a>, <a href="#Note"><code>Note</code></a>, <a href="#QuoteType"><code>QuoteType</code></a>, <a href="#Quoted"><code>Quoted</code></a>, <a href="#RawInline"><code>RawInline</code></a>, <a href="#SmallCaps"><code>SmallCaps</code></a>, <a href="#SoftBreak"><code>SoftBreak</code></a>, <a href="#Space"><code>Space</code></a>, <a href="#Span"><code>Span</code></a>, <a href="#Str"><code>Str</code></a>, <a href="#Strikeout"><code>Strikeout</code></a>, <a href="#Strong"><code>Strong</code></a>, <a href="#Subscript"><code>Subscript</code></a>, <a href="#Superscript"><code>Superscript</code></a>, <a href="#Target"><code>Target</code></a>, <a href="#Text"><code>Text</code></a>, <a href="#Underline"><code>Underline</code></a>.

<div id="InlineMath"></div>

??? note "`InlineMath`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    InlineMath()
    ```



<div id="Int"></div>

??? note "`Int`"

    Primitive type

    <h5>Signature</h5>

    ``` skip
    int
    ```



<div id="LineBlock"></div>

??? note "`LineBlock`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    LineBlock([[Inline]])
    ```

    <h5>See also</h5>
    
    <a href="#Inline"><code>Inline</code></a>.

<div id="LineBreak"></div>

??? note "`LineBreak`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    LineBreak()
    ```



<div id="Link"></div>

??? note "`Link`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Link(Attr, [Inline], Target)
    ```

    <h5>See also</h5>
    
    <a href="#Attr"><code>Attr</code></a>, <a href="#Inline"><code>Inline</code></a>, <a href="#Target"><code>Target</code></a>.

<div id="ListAttributes"></div>

??? note "`ListAttributes`"

    Typedef

    <h5>Signature</h5>

    ``` skip
    ListAttributes = (Int, ListNumberStyle, ListNumberDelim)
    ```

    <h5>See also</h5>
    
    <a href="#Int"><code>Int</code></a>, <a href="#ListNumberDelim"><code>ListNumberDelim</code></a>, <a href="#ListNumberStyle"><code>ListNumberStyle</code></a>.

<div id="ListNumberDelim"></div>

??? note "`ListNumberDelim`"

    Abstract data type

    <h5>Signature</h5>

    ``` skip
    ListNumberDelim = DefaultDelim()
                    | Period()
                    | OneParen()
                    | TwoParens()
    ```

    <h5>See also</h5>
    
    <a href="#DefaultDelim"><code>DefaultDelim</code></a>, <a href="#OneParen"><code>OneParen</code></a>, <a href="#Period"><code>Period</code></a>, <a href="#TwoParens"><code>TwoParens</code></a>.

<div id="ListNumberStyle"></div>

??? note "`ListNumberStyle`"

    Abstract data type

    <h5>Signature</h5>

    ``` skip
    ListNumberStyle = DefaultStyle()
                    | Example()
                    | Decimal()
                    | LowerRoman()
                    | UpperRoman()
                    | LowerAlpha()
                    | UpperAlpha()
    ```

    <h5>See also</h5>
    
    <a href="#Decimal"><code>Decimal</code></a>, <a href="#DefaultStyle"><code>DefaultStyle</code></a>, <a href="#Example"><code>Example</code></a>, <a href="#LowerAlpha"><code>LowerAlpha</code></a>, <a href="#LowerRoman"><code>LowerRoman</code></a>, <a href="#UpperAlpha"><code>UpperAlpha</code></a>, <a href="#UpperRoman"><code>UpperRoman</code></a>.

<div id="LowerAlpha"></div>

??? note "`LowerAlpha`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    LowerAlpha()
    ```



<div id="LowerRoman"></div>

??? note "`LowerRoman`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    LowerRoman()
    ```



<div id="Math"></div>

??? note "`Math`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Math(MathType, Text)
    ```

    <h5>See also</h5>
    
    <a href="#MathType"><code>MathType</code></a>, <a href="#Text"><code>Text</code></a>.

<div id="MathType"></div>

??? note "`MathType`"

    Abstract data type

    <h5>Signature</h5>

    ``` skip
    MathType = DisplayMath()
             | InlineMath()
    ```

    <h5>See also</h5>
    
    <a href="#DisplayMath"><code>DisplayMath</code></a>, <a href="#InlineMath"><code>InlineMath</code></a>.

<div id="Meta"></div>

??? note "`Meta`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Meta({Text: MetaValue})
    ```

    <h5>See also</h5>
    
    <a href="#MetaValue"><code>MetaValue</code></a>, <a href="#Text"><code>Text</code></a>.

<div id="MetaBlocks"></div>

??? note "`MetaBlocks`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    MetaBlocks([Block])
    ```

    <h5>See also</h5>
    
    <a href="#Block"><code>Block</code></a>.

<div id="MetaBool"></div>

??? note "`MetaBool`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    MetaBool(Bool)
    ```

    <h5>See also</h5>
    
    <a href="#Bool"><code>Bool</code></a>.

<div id="MetaInlines"></div>

??? note "`MetaInlines`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    MetaInlines([Inline])
    ```

    <h5>See also</h5>
    
    <a href="#Inline"><code>Inline</code></a>.

<div id="MetaList"></div>

??? note "`MetaList`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    MetaList([MetaValue])
    ```

    <h5>See also</h5>
    
    <a href="#MetaValue"><code>MetaValue</code></a>.

<div id="MetaMap"></div>

??? note "`MetaMap`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    MetaMap({Text: MetaValue})
    ```

    <h5>See also</h5>
    
    <a href="#MetaValue"><code>MetaValue</code></a>, <a href="#Text"><code>Text</code></a>.

<div id="MetaString"></div>

??? note "`MetaString`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    MetaString(Text)
    ```

    <h5>See also</h5>
    
    <a href="#Text"><code>Text</code></a>.

<div id="MetaValue"></div>

??? note "`MetaValue`"

    Abstract data type

    <h5>Signature</h5>

    ``` skip
    MetaValue = MetaMap({Text: MetaValue})
              | MetaList([MetaValue])
              | MetaBool(Bool)
              | MetaString(Text)
              | MetaInlines([Inline])
              | MetaBlocks([Block])
    ```

    <h5>See also</h5>
    
    <a href="#Block"><code>Block</code></a>, <a href="#Bool"><code>Bool</code></a>, <a href="#Inline"><code>Inline</code></a>, <a href="#MetaBlocks"><code>MetaBlocks</code></a>, <a href="#MetaBool"><code>MetaBool</code></a>, <a href="#MetaInlines"><code>MetaInlines</code></a>, <a href="#MetaList"><code>MetaList</code></a>, <a href="#MetaMap"><code>MetaMap</code></a>, <a href="#MetaString"><code>MetaString</code></a>, <a href="#Text"><code>Text</code></a>.

<div id="NormalCitation"></div>

??? note "`NormalCitation`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    NormalCitation()
    ```



<div id="Note"></div>

??? note "`Note`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Note([Block])
    ```

    <h5>See also</h5>
    
    <a href="#Block"><code>Block</code></a>.

<div id="Null"></div>

??? note "`Null`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Null()
    ```



<div id="OneParen"></div>

??? note "`OneParen`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    OneParen()
    ```



<div id="OrderedList"></div>

??? note "`OrderedList`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    OrderedList(ListAttributes, [[Block]])
    ```

    <h5>See also</h5>
    
    <a href="#Block"><code>Block</code></a>, <a href="#ListAttributes"><code>ListAttributes</code></a>.

<div id="Pandoc"></div>

??? note "`Pandoc`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Pandoc(Meta, [Block])
    ```

    <h5>See also</h5>
    
    <a href="#Block"><code>Block</code></a>, <a href="#Meta"><code>Meta</code></a>.

<div id="Para"></div>

??? note "`Para`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Para([Inline])
    ```

    <h5>See also</h5>
    
    <a href="#Inline"><code>Inline</code></a>.

<div id="Period"></div>

??? note "`Period`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Period()
    ```



<div id="Plain"></div>

??? note "`Plain`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Plain([Inline])
    ```

    <h5>See also</h5>
    
    <a href="#Inline"><code>Inline</code></a>.

<div id="QuoteType"></div>

??? note "`QuoteType`"

    Abstract data type

    <h5>Signature</h5>

    ``` skip
    QuoteType = SingleQuote()
              | DoubleQuote()
    ```

    <h5>See also</h5>
    
    <a href="#DoubleQuote"><code>DoubleQuote</code></a>, <a href="#SingleQuote"><code>SingleQuote</code></a>.

<div id="Quoted"></div>

??? note "`Quoted`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Quoted(QuoteType, [Inline])
    ```

    <h5>See also</h5>
    
    <a href="#Inline"><code>Inline</code></a>, <a href="#QuoteType"><code>QuoteType</code></a>.

<div id="RawBlock"></div>

??? note "`RawBlock`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    RawBlock(Format, Text)
    ```

    <h5>See also</h5>
    
    <a href="#Format"><code>Format</code></a>, <a href="#Text"><code>Text</code></a>.

<div id="RawInline"></div>

??? note "`RawInline`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    RawInline(Format, Text)
    ```

    <h5>See also</h5>
    
    <a href="#Format"><code>Format</code></a>, <a href="#Text"><code>Text</code></a>.

<div id="Row"></div>

??? note "`Row`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Row(Attr, [Cell])
    ```

    <h5>See also</h5>
    
    <a href="#Attr"><code>Attr</code></a>, <a href="#Cell"><code>Cell</code></a>.

<div id="RowHeadColumns"></div>

??? note "`RowHeadColumns`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    RowHeadColumns(Int)
    ```

    <h5>See also</h5>
    
    <a href="#Int"><code>Int</code></a>.

<div id="RowSpan"></div>

??? note "`RowSpan`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    RowSpan(Int)
    ```

    <h5>See also</h5>
    
    <a href="#Int"><code>Int</code></a>.

<div id="ShortCaption"></div>

??? note "`ShortCaption`"

    Typedef

    <h5>Signature</h5>

    ``` skip
    ShortCaption = [Inline]
    ```

    <h5>See also</h5>
    
    <a href="#Inline"><code>Inline</code></a>.

<div id="SingleQuote"></div>

??? note "`SingleQuote`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    SingleQuote()
    ```



<div id="SmallCaps"></div>

??? note "`SmallCaps`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    SmallCaps([Inline])
    ```

    <h5>See also</h5>
    
    <a href="#Inline"><code>Inline</code></a>.

<div id="SoftBreak"></div>

??? note "`SoftBreak`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    SoftBreak()
    ```



<div id="Space"></div>

??? note "`Space`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Space()
    ```



<div id="Span"></div>

??? note "`Span`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Span(Attr, [Inline])
    ```

    <h5>See also</h5>
    
    <a href="#Attr"><code>Attr</code></a>, <a href="#Inline"><code>Inline</code></a>.

<div id="Str"></div>

??? note "`Str`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Str(Text)
    ```

    <h5>See also</h5>
    
    <a href="#Text"><code>Text</code></a>.

<div id="Strikeout"></div>

??? note "`Strikeout`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Strikeout([Inline])
    ```

    <h5>See also</h5>
    
    <a href="#Inline"><code>Inline</code></a>.

<div id="String"></div>

??? note "`String`"

    Primitive type

    <h5>Signature</h5>

    ``` skip
    str
    ```



<div id="Strong"></div>

??? note "`Strong`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Strong([Inline])
    ```

    <h5>See also</h5>
    
    <a href="#Inline"><code>Inline</code></a>.

<div id="Subscript"></div>

??? note "`Subscript`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Subscript([Inline])
    ```

    <h5>See also</h5>
    
    <a href="#Inline"><code>Inline</code></a>.

<div id="Superscript"></div>

??? note "`Superscript`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Superscript([Inline])
    ```

    <h5>See also</h5>
    
    <a href="#Inline"><code>Inline</code></a>.

<div id="SuppressAuthor"></div>

??? note "`SuppressAuthor`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    SuppressAuthor()
    ```



<div id="Table"></div>

??? note "`Table`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Table(Attr, Caption, [ColSpec], TableHead, [TableBody], TableFoot)
    ```

    <h5>See also</h5>
    
    <a href="#Attr"><code>Attr</code></a>, <a href="#Caption"><code>Caption</code></a>, <a href="#ColSpec"><code>ColSpec</code></a>, <a href="#TableBody"><code>TableBody</code></a>, <a href="#TableFoot"><code>TableFoot</code></a>, <a href="#TableHead"><code>TableHead</code></a>.

<div id="TableBody"></div>

??? note "`TableBody`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    TableBody(Attr, RowHeadColumns, [Row], [Row])
    ```

    <h5>See also</h5>
    
    <a href="#Attr"><code>Attr</code></a>, <a href="#Row"><code>Row</code></a>, <a href="#RowHeadColumns"><code>RowHeadColumns</code></a>.

<div id="TableFoot"></div>

??? note "`TableFoot`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    TableFoot(Attr, [Row])
    ```

    <h5>See also</h5>
    
    <a href="#Attr"><code>Attr</code></a>, <a href="#Row"><code>Row</code></a>.

<div id="TableHead"></div>

??? note "`TableHead`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    TableHead(Attr, [Row])
    ```

    <h5>See also</h5>
    
    <a href="#Attr"><code>Attr</code></a>, <a href="#Row"><code>Row</code></a>.

<div id="Target"></div>

??? note "`Target`"

    Typedef

    <h5>Signature</h5>

    ``` skip
    Target = (Text, Text)
    ```

    <h5>See also</h5>
    
    <a href="#Text"><code>Text</code></a>.

<div id="Text"></div>

??? note "`Text`"

    Primitive type

    <h5>Signature</h5>

    ``` skip
    str
    ```



<div id="TwoParens"></div>

??? note "`TwoParens`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    TwoParens()
    ```



<div id="Underline"></div>

??? note "`Underline`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    Underline([Inline])
    ```

    <h5>See also</h5>
    
    <a href="#Inline"><code>Inline</code></a>.

<div id="UpperAlpha"></div>

??? note "`UpperAlpha`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    UpperAlpha()
    ```



<div id="UpperRoman"></div>

??? note "`UpperRoman`"

    Concrete data type

    <h5>Signature</h5>

    ``` skip
    UpperRoman()
    ```


