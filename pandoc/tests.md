
Preamble
================================================================================

Pandoc (Haskell)
--------------------------------------------------------------------------------

This test suite requires pandoc 1.16:

    >>> from subprocess import Popen, PIPE
    >>> p = Popen(["pandoc", "-v"], stdout=PIPE)
    >>> if "pandoc 1.16" not in p.communicate()[0]:
    ...     raise RuntimeError("pandoc 1.16 not found")


Imports
--------------------------------------------------------------------------------

    >>> from pandoc.types import *
    >>> import pandoc


Helper functions
--------------------------------------------------------------------------------

    >>> from subprocess import Popen, PIPE
    >>> import json
    >>> def to_json(txt):
    ...     p = Popen(["pandoc", "-tjson"], 
    ...               stdout=PIPE, stdin=PIPE, stderr=PIPE)
    ...     json_string = p.communicate(input=txt.encode("utf-8"))[0]
    ...     json_doc = json.loads(json_string)
    ...     return json_doc

    >>> def linebreak(text, length=80):
    ...     chunks = [text[i:i+length] for i in range(0, len(text), length)]
    ...     return "\n".join(chunks)

    >>> def show(txt):
    ...     global doc, json_ref, json_res
    ...     json_ref = to_json(txt)
    ...     doc = pandoc.read(json_ref)
    ...     print linebreak(repr(doc), length=80-4)
    ...     json_res = pandoc.write(doc)
    ...     if json_ref != json_res:
    ...         error = """\
    ... pandoc read-write roundtrip failed. 
    ...
    ... The reference:
    ...
    ... {0}
    ...
    ... and the actual result:
    ...
    ... {1}
    ...
    ... are different.
    ... """
    ...         raise ValueError(error.format(json_ref, json_res))

    >>> def wrap_blocks(*json_blocks):
    ...     return [{"unMeta":{}}, list(json_blocks)]
    >>> def wrap_inlines(*json_inlines):
    ...     return wrap_blocks({"t":"Para", "c":list(json_inlines)})


Pandoc Test Suite
================================================================================

Source: [Pandoc's User Guide](http://pandoc.org/README.html)


Paragraphs
--------------------------------------------------------------------------------

    >>> show("""\
    ... a paragraph
    ...
    ... another paragraph""")
    Pandoc(Meta(map()), [Para([Str(u'a'), Space(), Str(u'paragraph')]), Para([St
    r(u'another'), Space(), Str(u'paragraph')])])

    >>> show("a paragraph  \nanother paragraph""")
    Pandoc(Meta(map()), [Para([Str(u'a'), Space(), Str(u'paragraph'), LineBreak(
    ), Str(u'another'), Space(), Str(u'paragraph')])])


#### Extension: `escaped_line_breaks`

    >>> show(r"""a paragraph\
    ... another paragraph""")
    Pandoc(Meta(map()), [Para([Str(u'a'), Space(), Str(u'paragraph'), LineBreak(
    ), Str(u'another'), Space(), Str(u'paragraph')])])


Headers
--------------------------------------------------------------------------------

### Setext-style headers

    >>> show("""\
    ... A level-one header
    ... ==================
    ... 
    ... A level-two header
    ... ------------------
    ... """)
    Pandoc(Meta(map()), [Header(1, (u'a-level-one-header', [], []), [Str(u'A'), 
    Space(), Str(u'level-one'), Space(), Str(u'header')]), Header(2, (u'a-level-
    two-header', [], []), [Str(u'A'), Space(), Str(u'level-two'), Space(), Str(u
    'header')])])

### ATX-style headers

    >>> show("""\
    ... ## A level-two header
    ... 
    ... ### A level-three header ###
    ... """)
    Pandoc(Meta(map()), [Header(2, (u'a-level-two-header', [], []), [Str(u'A'), 
    Space(), Str(u'level-two'), Space(), Str(u'header')]), Header(3, (u'a-level-
    three-header', [], []), [Str(u'A'), Space(), Str(u'level-three'), Space(), S
    tr(u'header')])])

    >>> show("# A level-one header with a [link](/url) and *emphasis*")
    Pandoc(Meta(map()), [Header(1, (u'a-level-one-header-with-a-link-and-emphasi
    s', [], []), [Str(u'A'), Space(), Str(u'level-one'), Space(), Str(u'header')
    , Space(), Str(u'with'), Space(), Str(u'a'), Space(), Link((u'', [], []), [S
    tr(u'link')], (u'/url', u'')), Space(), Str(u'and'), Space(), Emph([Str(u'em
    phasis')])])])

#### Extension: `blank_before_header`

    >>> show("""\
    ... I like several of their flavors of ice cream:
    ... #22, for example, and #5.""")
    Pandoc(Meta(map()), [Para([Str(u'I'), Space(), Str(u'like'), Space(), Str(u'
    several'), Space(), Str(u'of'), Space(), Str(u'their'), Space(), Str(u'flavo
    rs'), Space(), Str(u'of'), Space(), Str(u'ice'), Space(), Str(u'cream:'), So
    ftBreak(), Str(u'#22,'), Space(), Str(u'for'), Space(), Str(u'example,'), Sp
    ace(), Str(u'and'), Space(), Str(u'#5.')])])


Header identifiers
--------------------------------------------------------------------------------

#### Extension: `header_attributes`

    >>> show("""
    ... # My header {#foo}
    ... 
    ... ## My header ##    {#foo}
    ... 
    ... My other header   {#foo}
    ... ---------------""")
    Pandoc(Meta(map()), [Header(1, (u'foo', [], []), [Str(u'My'), Space(), Str(u
    'header')]), Header(2, (u'foo', [], []), [Str(u'My'), Space(), Str(u'header'
    )]), Header(2, (u'foo', [], []), [Str(u'My'), Space(), Str(u'other'), Space(
    ), Str(u'header')])])

    >>> show("# My header {-}")
    Pandoc(Meta(map()), [Header(1, (u'my-header', [u'unnumbered'], []), [Str(u'M
    y'), Space(), Str(u'header')])])

    >>> show("# My header {.unnumbered}")
    Pandoc(Meta(map()), [Header(1, (u'my-header', [u'unnumbered'], []), [Str(u'M
    y'), Space(), Str(u'header')])])

#### Extension: `auto_identifiers`

This extension does not work for JSON output format.

#### Extension: `implicit_header_references`

    >>> show("""
    ... # Header Identifiers
    ... 
    ... [header identifiers](#header-identifiers),
    ... [header identifiers],
    ... [header identifiers][],
    ... [the section on header identifiers][header identifiers]
    ... """)
    Pandoc(Meta(map()), [Header(1, (u'header-identifiers', [], []), [Str(u'Heade
    r'), Space(), Str(u'Identifiers')]), Para([Link((u'', [], []), [Str(u'header
    '), Space(), Str(u'identifiers')], (u'#header-identifiers', u'')), Str(u',')
    , SoftBreak(), Link((u'', [], []), [Str(u'header'), Space(), Str(u'identifie
    rs')], (u'#header-identifiers', u'')), Str(u','), SoftBreak(), Link((u'', []
    , []), [Str(u'header'), Space(), Str(u'identifiers')], (u'#header-identifier
    s', u'')), Str(u','), SoftBreak(), Link((u'', [], []), [Str(u'the'), Space()
    , Str(u'section'), Space(), Str(u'on'), Space(), Str(u'header'), Space(), St
    r(u'identifiers')], (u'#header-identifiers', u''))])])

    >>> show("""
    ... # Foo
    ... 
    ... [foo]: bar
    ... 
    ... See [foo]
    ... """)
    Pandoc(Meta(map()), [Header(1, (u'foo', [], []), [Str(u'Foo')]), Para([Str(u
    'See'), Space(), Link((u'', [], []), [Str(u'foo')], (u'bar', u''))])])


Block Quotations
--------------------------------------------------------------------------------

    >>> show("""
    ... > This is a block quote. This
    ... > paragraph has two lines.
    ... >
    ... > 1. This is a list inside a block quote.
    ... > 2. Second item.
    ... """)
    Pandoc(Meta(map()), [BlockQuote([Para([Str(u'This'), Space(), Str(u'is'), Sp
    ace(), Str(u'a'), Space(), Str(u'block'), Space(), Str(u'quote.'), Space(), 
    Str(u'This'), SoftBreak(), Str(u'paragraph'), Space(), Str(u'has'), Space(),
     Str(u'two'), Space(), Str(u'lines.')]), OrderedList((1, Decimal(), Period()
    ), [[Plain([Str(u'This'), Space(), Str(u'is'), Space(), Str(u'a'), Space(), 
    Str(u'list'), Space(), Str(u'inside'), Space(), Str(u'a'), Space(), Str(u'bl
    ock'), Space(), Str(u'quote.')])], [Plain([Str(u'Second'), Space(), Str(u'it
    em.')])]])])])

    >>> show("""
    ... > This is a block quote. This
    ... paragraph has two lines.
    ... 
    ... > 1. This is a list inside a block quote.
    ... 2. Second item.
    ... """)
    Pandoc(Meta(map()), [BlockQuote([Para([Str(u'This'), Space(), Str(u'is'), Sp
    ace(), Str(u'a'), Space(), Str(u'block'), Space(), Str(u'quote.'), Space(), 
    Str(u'This'), SoftBreak(), Str(u'paragraph'), Space(), Str(u'has'), Space(),
     Str(u'two'), Space(), Str(u'lines.')])]), BlockQuote([OrderedList((1, Decim
    al(), Period()), [[Plain([Str(u'This'), Space(), Str(u'is'), Space(), Str(u'
    a'), Space(), Str(u'list'), Space(), Str(u'inside'), Space(), Str(u'a'), Spa
    ce(), Str(u'block'), Space(), Str(u'quote.')])], [Plain([Str(u'Second'), Spa
    ce(), Str(u'item.')])]])])])

    >>> show("""
    ... > This is a block quote.
    ... >
    ... > > A block quote within a block quote.
    ... """)
    Pandoc(Meta(map()), [BlockQuote([Para([Str(u'This'), Space(), Str(u'is'), Sp
    ace(), Str(u'a'), Space(), Str(u'block'), Space(), Str(u'quote.')]), BlockQu
    ote([Para([Str(u'A'), Space(), Str(u'block'), Space(), Str(u'quote'), Space(
    ), Str(u'within'), Space(), Str(u'a'), Space(), Str(u'block'), Space(), Str(
    u'quote.')])])])])

    >>> show(">     code")
    Pandoc(Meta(map()), [BlockQuote([CodeBlock((u'', [], []), u'code')])])

#### Extension: `blank_before_blockquote`

    >>> show("""
    ... > This is a block quote.
    ... >> Nested.
    ... """)
    Pandoc(Meta(map()), [BlockQuote([Para([Str(u'This'), Space(), Str(u'is'), Sp
    ace(), Str(u'a'), Space(), Str(u'block'), Space(), Str(u'quote.'), SoftBreak
    (), Str(u'>'), Space(), Str(u'Nested.')])])])


Emphasis
--------------------------------------------------------------------------------

    >>> show("""This text is _emphasized with underscores_, and this
    ... is *emphasized with asterisks*.""")
    Pandoc(Meta(map()), [Para([Str(u'This'), Space(), Str(u'text'), Space(), Str
    (u'is'), Space(), Emph([Str(u'emphasized'), Space(), Str(u'with'), Space(), 
    Str(u'underscores')]), Str(u','), Space(), Str(u'and'), Space(), Str(u'this'
    ), SoftBreak(), Str(u'is'), Space(), Emph([Str(u'emphasized'), Space(), Str(
    u'with'), Space(), Str(u'asterisks')]), Str(u'.')])])

    >>> show("This is **strong emphasis** and __with underscores__.")
    Pandoc(Meta(map()), [Para([Str(u'This'), Space(), Str(u'is'), Space(), Stron
    g([Str(u'strong'), Space(), Str(u'emphasis')]), Space(), Str(u'and'), Space(
    ), Strong([Str(u'with'), Space(), Str(u'underscores')]), Str(u'.')])])

    >>> show("This is * not emphasized *, and \*neither is this\*.")
    Pandoc(Meta(map()), [Para([Str(u'This'), Space(), Str(u'is'), Space(), Str(u
    '*'), Space(), Str(u'not'), Space(), Str(u'emphasized'), Space(), Str(u'*,')
    , Space(), Str(u'and'), Space(), Str(u'*neither'), Space(), Str(u'is'), Spac
    e(), Str(u'this*.')])])

    >>> show("feas*ible*, not feas*able*.")
    Pandoc(Meta(map()), [Para([Str(u'feas'), Emph([Str(u'ible')]), Str(u','), Sp
    ace(), Str(u'not'), Space(), Str(u'feas'), Emph([Str(u'able')]), Str(u'.')])
    ])


Strikeout
--------------------------------------------------------------------------------

    >>> show("This ~~is deleted text.~~")
    Pandoc(Meta(map()), [Para([Str(u'This'), Space(), Strikeout([Str(u'is'), Spa
    ce(), Str(u'deleted'), Space(), Str(u'text.')])])])


Superscripts and Subscripts
--------------------------------------------------------------------------------

    >>> show("H~2~O is a liquid.  2^10^ is 1024.")
    Pandoc(Meta(map()), [Para([Str(u'H'), Subscript([Str(u'2')]), Str(u'O'), Spa
    ce(), Str(u'is'), Space(), Str(u'a'), Space(), Str(u'liquid.'), Space(), Str
    (u'2'), Superscript([Str(u'10')]), Space(), Str(u'is'), Space(), Str(u'1024.
    ')])])


Verbatim
--------------------------------------------------------------------------------

    >>> show("What is the difference between `>>=` and `>>`?")
    Pandoc(Meta(map()), [Para([Str(u'What'), Space(), Str(u'is'), Space(), Str(u
    'the'), Space(), Str(u'difference'), Space(), Str(u'between'), Space(), Code
    ((u'', [], []), u'>>='), Space(), Str(u'and'), Space(), Code((u'', [], []), 
    u'>>'), Str(u'?')])])

    >>> show("Here is a literal backtick `` ` ``.")
    Pandoc(Meta(map()), [Para([Str(u'Here'), Space(), Str(u'is'), Space(), Str(u
    'a'), Space(), Str(u'literal'), Space(), Str(u'backtick'), Space(), Code((u'
    ', [], []), u'`'), Str(u'.')])])

    >>> show("This is a backslash followed by an asterisk: `\*`.")
    Pandoc(Meta(map()), [Para([Str(u'This'), Space(), Str(u'is'), Space(), Str(u
    'a'), Space(), Str(u'backslash'), Space(), Str(u'followed'), Space(), Str(u'
    by'), Space(), Str(u'an'), Space(), Str(u'asterisk:'), Space(), Code((u'', [
    ], []), u'\\*'), Str(u'.')])])

    >>> show("`<$>`{.haskell}")
    Pandoc(Meta(map()), [Para([Code((u'', [u'haskell'], []), u'<$>')])])


Small Caps
--------------------------------------------------------------------------------

    >>> show("<span style='font-variant:small-caps;'>Small caps</span>")
    Pandoc(Meta(map()), [Para([SmallCaps([Str(u'Small'), Space(), Str(u'caps')])
    ])])


Math
--------------------------------------------------------------------------------

    >>> show("$a=1$")
    Pandoc(Meta(map()), [Para([Math(InlineMath(), u'a=1')])])

    >>> show("$$\int_0^1 f(x)\, dx$$")
    Pandoc(Meta(map()), [Para([Math(DisplayMath(), u'\\int_0^1 f(x)\\, dx')])])


Raw HTML
--------------------------------------------------------------------------------

    >>> show("<html></html>")
    Pandoc(Meta(map()), [RawBlock(Format(u'html'), u'<html>'), RawBlock(Format(u
    'html'), u'</html>')])

    >>> show("""\
    ... <table>
    ... <tr>
    ... <td>*one*</td>
    ... <td>[a link](http://google.com)</td>
    ... </tr>
    ... </table>""")
    Pandoc(Meta(map()), [RawBlock(Format(u'html'), u'<table>'), RawBlock(Format(
    u'html'), u'<tr>'), RawBlock(Format(u'html'), u'<td>'), Plain([Emph([Str(u'o
    ne')])]), RawBlock(Format(u'html'), u'</td>'), RawBlock(Format(u'html'), u'<
    td>'), Plain([Link((u'', [], []), [Str(u'a'), Space(), Str(u'link')], (u'htt
    p://google.com', u''))]), RawBlock(Format(u'html'), u'</td>'), RawBlock(Form
    at(u'html'), u'</tr>'), RawBlock(Format(u'html'), u'</table>')])


Raw TeX
--------------------------------------------------------------------------------

    >>> show("This result was proved in \cite{jones.1967}.")
    Pandoc(Meta(map()), [Para([Str(u'This'), Space(), Str(u'result'), Space(), S
    tr(u'was'), Space(), Str(u'proved'), Space(), Str(u'in'), Space(), RawInline
    (Format(u'tex'), u'\\cite{jones.1967}'), Str(u'.')])])

    >>> show(r"""\begin{tabular}{|l|l|}\hline
    ... Age & Frequency \\ \hline
    ... 18--25  & 15 \\
    ... 26--35  & 33 \\
    ... 36--45  & 22 \\ \hline
    ... \end{tabular}""")
    Pandoc(Meta(map()), [RawBlock(Format(u'latex'), u'\\begin{tabular}{|l|l|}\\h
    line\nAge & Frequency \\\\ \\hline\n18--25  & 15 \\\\\n26--35  & 33 \\\\\n36
    --45  & 22 \\\\ \\hline\n\\end{tabular}')])

    >>> show(r"""\newcommand{\tuple}[1]{\langle #1 \rangle}
    ...
    ... $\tuple{a, b, c}$""")
    Pandoc(Meta(map()), [Para([Math(InlineMath(), u'{\\langle a, b, c \\rangle}'
    )])])




