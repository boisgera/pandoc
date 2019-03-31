
AST / Document (Meta-)Model
================================================================================

Use the new metaclass-based representation to drive an exploration of the
document model. Link to the proper documentation when needed, or use
exemple from markdown text to see what every construct is about.

Explore an existing document or create from scratch?
First explore, then build from scratch?

Explain that the person willing to analyze/transform documents has to 
understand how each (or some of the) document pieces are represented?
And that it's what we try to do here?

-----

    >>> import pandoc
    >>> from pandoc.types import *


    >>> text = "Hello, World!"
    >>> doc = pandoc.read(text)
    >>> doc
    Pandoc(Meta(map()), [Para([Str('Hello,'), Space(), Str('World!')])])

A document is an instance of the `Pandoc` class; it has two arguments

    >>> Pandoc
    Pandoc(Meta, [Block])

The first argument, the instance of `Meta`, represents the document metadata.
Since in this very simple example there is no metadata, we will ignore it and
focus on the second argument instead, the document contents, which 
is a list of blocks:

    >>> blocks = doc[1]
    >>> blocks
    [Para([Str('Hello,'), Space(), Str('World!')])]

Actually, there is a single block here

    >>> len(blocks)
    1

There are several possible types of blocks: headers, paragraphs, lists, etc.

    >>> Block
    Block = Plain([Inline])
          | Para([Inline])
          | LineBlock([[Inline]])
          | CodeBlock(Attr, String)
          | RawBlock(Format, String)
          | BlockQuote([Block])
          | OrderedList(ListAttributes, [[Block]])
          | BulletList([[Block]])
          | DefinitionList([([Inline], [[Block]])])
          | Header(Int, Attr, [Inline])
          | HorizontalRule()
          | Table([Inline], [Alignment], [Double], [TableCell], [[TableCell]])
          | Div(Attr, [Block])
          | Null()

Here our single block is a paragraph:

    >>> para = blocks[0]
    >>> para
    Para([Str('Hello,'), Space(), Str('World!')])
    >>> isinstance(para, Para)
    True

In general, paragraphs contain lists of inline elements:

    >>> Para
    Para([Inline])
    >>> inlines = para[0]

Inlines can be several things: ordinary text, emphasized text,
strong text, etc.

    >>> Inline
    Inline = Str(String)
           | Emph([Inline])
           | Strong([Inline])
           | Strikeout([Inline])
           | Superscript([Inline])
           | Subscript([Inline])
           | SmallCaps([Inline])
           | Quoted(QuoteType, [Inline])
           | Cite([Citation], [Inline])
           | Code(Attr, String)
           | Space()
           | SoftBreak()
           | LineBreak()
           | Math(MathType, String)
           | RawInline(Format, String)
           | Link(Attr, [Inline], Target)
           | Image(Attr, [Inline], Target)
           | Note([Block])
           | Span(Attr, [Inline])

Here we simply have a mixture of ordinary text and space.

    >>> inlines = para[0]
    >>> inlines
    [Str('Hello,'), Space(), Str('World!')]

Instances of `Space` have no argument while instances of `Str` 
contain a text string

    >>> Space
    Space()
    >>> Str
    Str(String)
    >>> String == type(u"")
    True

Finally

    >>> print(inlines[0][0] + " " + inlines[2][0])
    Hello, World!


Helpers
--------------------------------------------------------------------------------

We introduce the helper function `show` to display a document or document 
fragment (inline or block) as markdown:

    >>> def show(elt):
    ...     if isinstance(elt, Pandoc):
    ...         doc = elt
    ...         print(pandoc.write(doc, format="markdown"))
    ...     elif isinstance(elt, list):
    ...         elts = elt
    ...         if len(elts) > 0:
    ...             if isinstance(elts[0], Block):
    ...                 blocks = elts
    ...                 show(Pandoc(Meta({}), blocks))
    ...             elif isinstance(elts[0], Inline):
    ...                 inlines = elts
    ...                 block = Plain(elts)
    ...                 show([block])
    ...     elif isinstance(elt, (Inline, Block)):
    ...         show([elt])

We also introduce a function `find` to get the first element of a given type
in a document or document fragment:

    >>> def find(elt, type):
    ...     for _elt in pandoc.iter(elt):
    ...         if isinstance(_elt, type):
    ...             return _elt

We monkey-patch the base class for pandoc types to be able to call `find` 
as a method:

    >>> pandoc.types.Type.find = find

Paragraphs
--------------------------------------------------------------------------------

Headers
--------------------------------------------------------------------------------

Quotations
--------------------------------------------------------------------------------

Code Blocks
--------------------------------------------------------------------------------

Line Blocks
--------------------------------------------------------------------------------

Lists
--------------------------------------------------------------------------------

Horizontal Rules
--------------------------------------------------------------------------------

Tables
--------------------------------------------------------------------------------

**Reference:** [Pandoc User's Guide / Tables](https://pandoc.org/MANUAL.html#tables)

Simple tables in markdown typically look like this:

    >>> text = """
    ...   Right     Left     Center     Default
    ... -------     ------ ----------   -------
    ...      12     12        12            12
    ...     123     123       123          123
    ...       1     1          1             1
    ... ---------------------------------------
    ...
    ... Table: Demonstration of simple table syntax.
    ... """


A table is defined by 5 arguments:

    >>> Table
    Table([Inline], [Alignment], [Double], [TableCell], [[TableCell]])
    
They define respectively the table caption, column alignments, column widths,
headers and rows. The most important are the last two, headers and rows.
Headers are described by a list of table cells: it's the content of 
first table row. The last argument refers to the remaining table rows,
each row being described as a list of table cells.

The content of a table cell can be arbitrarily complex: 
anything that can be used in a document content (except for the metadata) 
can be used in a table cell.
Actually, `TableCell` is not a new type, but an alias for "list of blocks":

    >>> TableCell
    TableCell = [Block]

Let's have a look at the attributes of the table above:

    >>> doc = pandoc.read(text)
    >>> table = doc.find(Table)
    >>> caption, alignments, widths, headers, rows = table[:] 

Here are the column headers:

    >>> headers
    [[Plain([Str('Right')])], [Plain([Str('Left')])], [Plain([Str('Center')])], [Plain([Str('Default')])]]
    >>> for cell in headers:
    ...     show(cell)
    Right
    <BLANKLINE>
    Left
    <BLANKLINE>
    Center
    <BLANKLINE>
    Default
    <BLANKLINE>

The structure of rows are similar. 
For example, we can display the contents of the first row:

    >>> rows
    [[[Plain([Str('12')])], [Plain([Str('12')])], [Plain([Str('12')])], [Plain([Str('12')])]], [[Plain([Str('123')])], [Plain([Str('123')])], [Plain([Str('123')])], [Plain([Str('123')])]], [[Plain([Str('1')])], [Plain([Str('1')])], [Plain([Str('1')])], [Plain([Str('1')])]]]
    >>> first_row = rows[0]
    >>> for cell in first_row:
    ...     show(cell)
    12
    <BLANKLINE>
    12
    <BLANKLINE>
    12
    <BLANKLINE>
    12
    <BLANKLINE>

The three other table arguments are caption, column alignments and column widths.
Caption is the obvious one: it's the content of the (optional) table caption,
described as a list of inlines:

    >>> caption
    [Str('Demonstration'), Space(), Str('of'), Space(), Str('simple'), Space(), Str('table'), Space(), Str('syntax.')]

Column alignments is a list of alignment options, 
among the four possible choices below:

    >>> Alignment
    Alignment = AlignLeft()
              | AlignRight()
              | AlignCenter()
              | AlignDefault()

In the current table, the four kinds are effectively used:

    >>> alignments
    [AlignRight(), AlignLeft(), AlignCenter(), AlignDefault()]

The third argument is a list of floating-point numbers which are 
fractions of 1 and determine the column widths. 
Either their sum is one of they are all set to zero, 
in which vase the attribute carries no information. 
Here, we are in this default case:

    >>> widths
    [0.0, 0.0, 0.0, 0.0]

Column widths are relevant in the context of multiline tables
(see [Pandoc User's Guide / Tables](https://pandoc.org/MANUAL.html#tables))
that look like this:

    >>> text = """
    ... -------------------------------------------------------------
    ...  Centered   Default           Right Left
    ...   Header    Aligned         Aligned Aligned
    ... ----------- ------- --------------- -------------------------
    ...    First    row                12.0 Example of a row that
    ...                                     spans multiple lines.
    ... 
    ...   Second    row                 5.0 Here's another one. Note
    ...                                     the blank line between
    ...                                     rows.
    ... -------------------------------------------------------------
    ... 
    ... Table: Here's the caption. It, too, may span
    ... multiple lines.
    ... """

For this multiline table, the table parser computes the relative column widths:

    >>> table = pandoc.read(text).find(Table)
    >>> _, _, widths, _, _ = table[:]
    >>> widths
    [0.16666666666666666, 0.1111111111111111, 0.2222222222222222, 0.3611111111111111]

Now, since the last column has a lot of content and the third one 
has plenty of empty space, we could select relative widths to narrow 
the third column and enlarge the last one. Here is how that looks:

    >>> table[2] = [1/6, 1/9, 1/9, 5/12] # the sum is 1.0
    >>> show(table)
      -------------------------------------------------------------
       Centered   Default       Right Left Aligned
        Header    Aligned     Aligned 
      ----------- --------- --------- -----------------------------
         First    row            12.0 Example of a row that spans
                                      multiple lines.
    <BLANKLINE>
        Second    row             5.0 Here's another one. Note the
                                      blank line between rows.
      -------------------------------------------------------------
    <BLANKLINE>
      : Here's the caption. It, too, may span multiple lines.
    <BLANKLINE>

Of course, it is possible to create tables programmatically:

!!! note "Example: Multiplication Table"

    We show how to build a multiplication table. 
    First, we decide the size of the table: 
    here we will compute products up to 5x5:

        >>> n = 5

    We won't need any caption, are ok with the 
    default column alignments and don't specify explicitly
    the column widths:

        >>> caption = []
        >>> alignments = n * [AlignDefault()]
        >>> widths = n * [0.0]

    Now, since the structure of a table cell in pandoc is so general, 
    it may be a bit cumbersome when the content is so simple.
    To ease this pain, we define a small `cell` function
    which creates a table cell that wraps some arbitrary 
    text-like content.
        
        >>> def cell(text):
        ...     inline = Str(str(text))
        ...     blocks = [Plain([inline])]
        ...     return blocks

    Now we may define the table headers

        >>> headers = [cell("x")]
        >>> for j in range(1, n+1):
        ...     headers.append(cell(j))

    and rows

        >>> rows = []
        >>> for i in range(1, n+1):
        ...     row = [cell(i)]
        ...     for j in range(1, n+1):
        ...         row.append(cell(i * j))
        ...     rows.append(row)

    The final table is:

        >>> table = Table(caption, alignments, widths, headers, rows)
        >>> show(table)
          x   1   2    3    4    5
          --- --- ---- ---- ---- ----
          1   1   2    3    4    5
          2   2   4    6    8    10
          3   3   6    9    12   15
          4   4   8    12   16   20
          5   5   10   15   20   25
        <BLANKLINE>


Inline Formatting
--------------------------------------------------------------------------------

LaTeX and Math
--------------------------------------------------------------------------------

HTML
--------------------------------------------------------------------------------


Links
--------------------------------------------------------------------------------

Images
--------------------------------------------------------------------------------

Divs and Spans
--------------------------------------------------------------------------------

Footnotes
--------------------------------------------------------------------------------

Citations
--------------------------------------------------------------------------------

Metadata
--------------------------------------------------------------------------------    

**Reference:** [Pandoc User's Guide / Metadata Blocks](https://pandoc.org/MANUAL.html#metadata-blocks)

**TODO.** Start with document without metadata, then simple title and contents, 
then more advanced metadata ... and finally YAML blocks?

**TODO:** specify use cases: use for custom templates, misc. configuration
options (e.g. stylesheets, EPUB metadata, bibliography, etc.)

    >>> Meta
    Meta({String: MetaValue})

...

    >>> MetaValue
    MetaValue = MetaMap({String: MetaValue})
              | MetaList([MetaValue])
              | MetaBool(Bool)
              | MetaString(String)
              | MetaInlines([Inline])
              | MetaBlocks([Block])

...

    >>> text = """\
    ... % Document Title
    ... % Author One, Author Two
    ... % Date
    ... """

...


    >>> doc = pandoc.read(text)
    >>> doc == \
    ... Pandoc(
    ...   Meta(map([
    ...     ('date', MetaInlines([Str('Date')])), 
    ...     ('author', MetaList([MetaInlines(
    ...       [Str('Author'), Space(), Str('One,'), Space(), Str('Author'), Space(), Str('Two')])])), 
    ...     ('title', MetaInlines([Str('Document'), Space(), Str('Title')]))
    ...   ])), 
    ...   []
    ... )
    True

...

    >>> metadata = doc[0][0]
    >>> metadata["title"]
    MetaInlines([Str('Document'), Space(), Str('Title')])
    >>> metadata["author"]
    MetaList([MetaInlines([Str('Author'), Space(), Str('One,'), Space(), Str('Author'), Space(), Str('Two')])])
    >>> metadata["date"]
    MetaInlines([Str('Date')])



**TODO:** discuss simple vs general (YAML) syntax.

**TODO:** explain goals: simple doc metadata + "compiler" / template 
directives + any kind of user-defined goals.

**TODO:** parsing: when MetaInlines, when MetaBlocks? Test stuff, read code.
Also distinguish MetaString vs MetaInlines ... (ex: '42': there is no number
type allowed in pandoc metadata).

**TODO:** check if order in maps is preserved in markdown to JSON repr
(I think I remember it is not). Well, the [spec](http://yaml.org/spec/1.2/spec.html)
tells us mappings are not ordered, so we're good here. Apparently, there is
a compact notation to represent ordered mappings as lists of unordered mappings
with a single entry (OK, I can see how that plays: you just prefix every
key with `-`)

**Code Analysis.**

Pandoc metadata reading code: 
[Source on GitHub](https://github.com/jgm/pandoc/blob/master/src/Text/Pandoc/Readers/Markdown.hs)

  - handling is in the `yamlMetaBlock` function

  - the YAML text to YAML structure is mostly delegated to the [`Data.YAML`](http://hackage.haskell.org/package/yaml-0.8.30/docs/Data-Yaml.html) library

  - the translation from the `Data.YAML` YAML item representation to
    the `Meta` stuff of pandoc is managed by `yamlToMeta`.
    There everything is mostly simple and unsurprising
    (maybe except for a little micro management of numbers, 
    but well, ok: floats that are integers are "integerized").
    The real deal is the management of strings, delegated to
    `toMetaValue`. Note that only numbers (and NULL / empty) 
    are returned as `MetaStrings`, strings are not.

  - `toMetaValue`: AFAICT: if the strings ends with a newline,
    it's some blocks, otherwise it's some inline. The easiest
    way to get some blocks is to use

So to get a block, you can use in particular any folded or literal style
(see [stack overflow](https://stackoverflow.com/questions/3790454/in-yaml-how-do-i-break-a-string-over-multiple-lines?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa).
Essentially folded won't remember the linebreak at all while the literal style
will remember them as soft breaks.

Nota: "normal" multiline strings won't get a newline so they won't be
reconized as blocks. If they contain newlines, it will be recognized as
a simple softbreak.

Nota: adding a newline at the end of a quoted string does not trigger
MetaBlocks. Why? Is it somehow in the spec of YAML that strip such strings?
Well, ok, let's accept that at face value.

----

**TODO:** Nota: round-tripping is not stable here: start with say the YAML
metadata block:

    ---
    a: '42'
    ---

The stuff gets parsed as MetaInlines; but write it again (in standalone mode)
and you get 42 without the quotes, that gets parsed as MetaString instead.
So, well, if we end up with a sorta weakly typed representation, we should
not worry too much since in some respect pandoc management of this metadata
is kinda weak anyway.


**OR** you can argue that the behavior above is a bug. But actually, 
there is no way to know what the original type was, no the arbitrary
serialization can hardly be objected ... right?

**Another round-tripping issue.** MetaBlocks may be serialized without 
as 'normal' strings, not blocks, 
so if they are parsed again, they will be considered MetaInlines.
This one suck badly and can be considered to be a bug.
You need something like at least two blocks to be serialized as a block?
I have to have a look at the markdown writer (but, well, it may be hidden
in the YAML library code, not clear I can explicit the issue with pandoc's
code only). There, the metadata if first converted to a JSON-like structure
before being cast to YAML (search for `metaToJSON`). The JSON stuff knows
shit about how the strings has been specified so this is where the stuff
goes bad? Is the newline content somehow preserved in this translation at
least? And is `jsonToYaml` taking that into account? Yeah, well 
`jsonToYaml` is using literal stuff all right if there is a newline in
the string. So the issue is above, to check that `metaToJSON` does its
job properly ... the bug should be there.

And `metaToJSON` is [here](https://github.com/jgm/pandoc/blob/7e389cb3dbdc11126b9bdb6a7741a65e5a94a43e/src/Text/Pandoc/Writers/Shared.hs).

Well actually `blockListToMarkdown` and `blockToMarkdown` may be the functions
to investigate. Is `blockListToMarkdown` missing a trailing newline (at least
in the context of it use in `metaToJSON` ? Fuck, I cannot grok this code in
reasonable time, just log an issue with the example.

**TODO:** to and from "naked" yaml / json ? Discuss ambiguity 
(empty stuff essentially? Then we don't know if we have lists 
or inlines or blocks, that's about it right?).

**Pragmatic approach** (without bugfix): cast everything to strings
and promote to blocks if it contains (or ends with?) a newline?

Shit: adding a linebreak to MetaBlocks serializes some shit?
Like a `\` at the end of string (which is still not a block).


