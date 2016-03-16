
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


Pandoc Test Suite
================================================================================

Source: [Pandoc's User Guide](http://pandoc.org/README.html)


Paragraphs
--------------------------------------------------------------------------------

    >>> """
    ... a paragraph
    ...
    ... another paragraph
    ... """ 
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [Para([Str(u'a'), Space(), Str(u'paragraph')]), Para([St
    r(u'another'), Space(), Str(u'paragraph')])])

    >>> "a paragraph  \nanother paragraph" # doctest: +PANDOC
    Pandoc(Meta(map()), [Para([Str(u'a'), Space(), Str(u'paragraph'), LineBreak(
    ), Str(u'another'), Space(), Str(u'paragraph')])])


#### Extension: `escaped_line_breaks`

    >>> r"""
    ... a paragraph\
    ... another paragraph
    ... """
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [Para([Str(u'a'), Space(), Str(u'paragraph'), LineBreak(
    ), Str(u'another'), Space(), Str(u'paragraph')])])


Headers
--------------------------------------------------------------------------------

### Setext-style headers

    >>> """
    ... A level-one header
    ... ==================
    ... 
    ... A level-two header
    ... ------------------
    ... """
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [Header(1, (u'a-level-one-header', [], []), [Str(u'A'), 
    Space(), Str(u'level-one'), Space(), Str(u'header')]), Header(2, (u'a-level-
    two-header', [], []), [Str(u'A'), Space(), Str(u'level-two'), Space(), Str(u
    'header')])])

### ATX-style headers

    >>> """
    ... ## A level-two header
    ... 
    ... ### A level-three header ###
    ... """
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [Header(2, (u'a-level-two-header', [], []), [Str(u'A'), 
    Space(), Str(u'level-two'), Space(), Str(u'header')]), Header(3, (u'a-level-
    three-header', [], []), [Str(u'A'), Space(), Str(u'level-three'), Space(), S
    tr(u'header')])])

    >>> "# A level-one header with a [link](/url) and *emphasis*"
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [Header(1, (u'a-level-one-header-with-a-link-and-emphasi
    s', [], []), [Str(u'A'), Space(), Str(u'level-one'), Space(), Str(u'header')
    , Space(), Str(u'with'), Space(), Str(u'a'), Space(), Link((u'', [], []), [S
    tr(u'link')], (u'/url', u'')), Space(), Str(u'and'), Space(), Emph([Str(u'em
    phasis')])])])

#### Extension: `blank_before_header`

    >>> """
    ... I like several of their flavors of ice cream:
    ... #22, for example, and #5.
    ... """
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [Para([Str(u'I'), Space(), Str(u'like'), Space(), Str(u'
    several'), Space(), Str(u'of'), Space(), Str(u'their'), Space(), Str(u'flavo
    rs'), Space(), Str(u'of'), Space(), Str(u'ice'), Space(), Str(u'cream:'), So
    ftBreak(), Str(u'#22,'), Space(), Str(u'for'), Space(), Str(u'example,'), Sp
    ace(), Str(u'and'), Space(), Str(u'#5.')])])


Header identifiers
--------------------------------------------------------------------------------

#### Extension: `header_attributes`

    >>> """
    ... # My header {#foo}
    ... 
    ... ## My header ##    {#foo}
    ... 
    ... My other header   {#foo}
    ... ---------------
    ... """
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [Header(1, (u'foo', [], []), [Str(u'My'), Space(), Str(u
    'header')]), Header(2, (u'foo', [], []), [Str(u'My'), Space(), Str(u'header'
    )]), Header(2, (u'foo', [], []), [Str(u'My'), Space(), Str(u'other'), Space(
    ), Str(u'header')])])

    >>> "# My header {-}" # doctest: +PANDOC
    Pandoc(Meta(map()), [Header(1, (u'my-header', [u'unnumbered'], []), [Str(u'M
    y'), Space(), Str(u'header')])])

    >>> "# My header {.unnumbered}" # doctest: +PANDOC
    Pandoc(Meta(map()), [Header(1, (u'my-header', [u'unnumbered'], []), [Str(u'M
    y'), Space(), Str(u'header')])])

#### Extension: `auto_identifiers`

This extension does not work for JSON output format.

#### Extension: `implicit_header_references`

    >>> """
    ... # Header Identifiers
    ... 
    ... [header identifiers](#header-identifiers),
    ... [header identifiers],
    ... [header identifiers][],
    ... [the section on header identifiers][header identifiers]
    ... """
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [Header(1, (u'header-identifiers', [], []), [Str(u'Heade
    r'), Space(), Str(u'Identifiers')]), Para([Link((u'', [], []), [Str(u'header
    '), Space(), Str(u'identifiers')], (u'#header-identifiers', u'')), Str(u',')
    , SoftBreak(), Link((u'', [], []), [Str(u'header'), Space(), Str(u'identifie
    rs')], (u'#header-identifiers', u'')), Str(u','), SoftBreak(), Link((u'', []
    , []), [Str(u'header'), Space(), Str(u'identifiers')], (u'#header-identifier
    s', u'')), Str(u','), SoftBreak(), Link((u'', [], []), [Str(u'the'), Space()
    , Str(u'section'), Space(), Str(u'on'), Space(), Str(u'header'), Space(), St
    r(u'identifiers')], (u'#header-identifiers', u''))])])

    >>> """
    ... # Foo
    ... 
    ... [foo]: bar
    ... 
    ... See [foo]
    ... """
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [Header(1, (u'foo', [], []), [Str(u'Foo')]), Para([Str(u
    'See'), Space(), Link((u'', [], []), [Str(u'foo')], (u'bar', u''))])])


Block Quotations
--------------------------------------------------------------------------------

    >>> """
    ... > This is a block quote. This
    ... > paragraph has two lines.
    ... >
    ... > 1. This is a list inside a block quote.
    ... > 2. Second item.
    ... """
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [BlockQuote([Para([Str(u'This'), Space(), Str(u'is'), Sp
    ace(), Str(u'a'), Space(), Str(u'block'), Space(), Str(u'quote.'), Space(), 
    Str(u'This'), SoftBreak(), Str(u'paragraph'), Space(), Str(u'has'), Space(),
     Str(u'two'), Space(), Str(u'lines.')]), OrderedList((1, Decimal(), Period()
    ), [[Plain([Str(u'This'), Space(), Str(u'is'), Space(), Str(u'a'), Space(), 
    Str(u'list'), Space(), Str(u'inside'), Space(), Str(u'a'), Space(), Str(u'bl
    ock'), Space(), Str(u'quote.')])], [Plain([Str(u'Second'), Space(), Str(u'it
    em.')])]])])])

    >>> """
    ... > This is a block quote. This
    ... paragraph has two lines.
    ... 
    ... > 1. This is a list inside a block quote.
    ... 2. Second item.
    ... """
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [BlockQuote([Para([Str(u'This'), Space(), Str(u'is'), Sp
    ace(), Str(u'a'), Space(), Str(u'block'), Space(), Str(u'quote.'), Space(), 
    Str(u'This'), SoftBreak(), Str(u'paragraph'), Space(), Str(u'has'), Space(),
     Str(u'two'), Space(), Str(u'lines.')])]), BlockQuote([OrderedList((1, Decim
    al(), Period()), [[Plain([Str(u'This'), Space(), Str(u'is'), Space(), Str(u'
    a'), Space(), Str(u'list'), Space(), Str(u'inside'), Space(), Str(u'a'), Spa
    ce(), Str(u'block'), Space(), Str(u'quote.')])], [Plain([Str(u'Second'), Spa
    ce(), Str(u'item.')])]])])])

    >>> """
    ... > This is a block quote.
    ... >
    ... > > A block quote within a block quote.
    ... """
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [BlockQuote([Para([Str(u'This'), Space(), Str(u'is'), Sp
    ace(), Str(u'a'), Space(), Str(u'block'), Space(), Str(u'quote.')]), BlockQu
    ote([Para([Str(u'A'), Space(), Str(u'block'), Space(), Str(u'quote'), Space(
    ), Str(u'within'), Space(), Str(u'a'), Space(), Str(u'block'), Space(), Str(
    u'quote.')])])])])

    >>> ">     code" # doctest: +PANDOC
    Pandoc(Meta(map()), [BlockQuote([CodeBlock((u'', [], []), u'code')])])

#### Extension: `blank_before_blockquote`

    >>> """
    ... > This is a block quote.
    ... >> Nested.
    ... """
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [BlockQuote([Para([Str(u'This'), Space(), Str(u'is'), Sp
    ace(), Str(u'a'), Space(), Str(u'block'), Space(), Str(u'quote.'), SoftBreak
    (), Str(u'>'), Space(), Str(u'Nested.')])])])


Emphasis
--------------------------------------------------------------------------------

    >>> """
    ... This text is _emphasized with underscores_, and this
    ... is *emphasized with asterisks*.
    ... """
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [Para([Str(u'This'), Space(), Str(u'text'), Space(), Str
    (u'is'), Space(), Emph([Str(u'emphasized'), Space(), Str(u'with'), Space(), 
    Str(u'underscores')]), Str(u','), Space(), Str(u'and'), Space(), Str(u'this'
    ), SoftBreak(), Str(u'is'), Space(), Emph([Str(u'emphasized'), Space(), Str(
    u'with'), Space(), Str(u'asterisks')]), Str(u'.')])])

    >>> "This is **strong emphasis** and __with underscores__."
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [Para([Str(u'This'), Space(), Str(u'is'), Space(), Stron
    g([Str(u'strong'), Space(), Str(u'emphasis')]), Space(), Str(u'and'), Space(
    ), Strong([Str(u'with'), Space(), Str(u'underscores')]), Str(u'.')])])

    >>> "This is * not emphasized *, and \*neither is this\*."
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [Para([Str(u'This'), Space(), Str(u'is'), Space(), Str(u
    '*'), Space(), Str(u'not'), Space(), Str(u'emphasized'), Space(), Str(u'*,')
    , Space(), Str(u'and'), Space(), Str(u'*neither'), Space(), Str(u'is'), Spac
    e(), Str(u'this*.')])])

    >>> "feas*ible*, not feas*able*."
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [Para([Str(u'feas'), Emph([Str(u'ible')]), Str(u','), Sp
    ace(), Str(u'not'), Space(), Str(u'feas'), Emph([Str(u'able')]), Str(u'.')])
    ])


Strikeout
--------------------------------------------------------------------------------

    >>> "This ~~is deleted text.~~" # doctest: +PANDOC
    Pandoc(Meta(map()), [Para([Str(u'This'), Space(), Strikeout([Str(u'is'), Spa
    ce(), Str(u'deleted'), Space(), Str(u'text.')])])])


Superscripts and Subscripts
--------------------------------------------------------------------------------

    >>> "H~2~O is a liquid.  2^10^ is 1024." # doctest: +PANDOC
    Pandoc(Meta(map()), [Para([Str(u'H'), Subscript([Str(u'2')]), Str(u'O'), Spa
    ce(), Str(u'is'), Space(), Str(u'a'), Space(), Str(u'liquid.'), Space(), Str
    (u'2'), Superscript([Str(u'10')]), Space(), Str(u'is'), Space(), Str(u'1024.
    ')])])


Verbatim
--------------------------------------------------------------------------------

    >>> "What is the difference between `>>=` and `>>`?" # doctest: +PANDOC
    Pandoc(Meta(map()), [Para([Str(u'What'), Space(), Str(u'is'), Space(), Str(u
    'the'), Space(), Str(u'difference'), Space(), Str(u'between'), Space(), Code
    ((u'', [], []), u'>>='), Space(), Str(u'and'), Space(), Code((u'', [], []), 
    u'>>'), Str(u'?')])])

    >>> "Here is a literal backtick `` ` ``." # doctest: +PANDOC
    Pandoc(Meta(map()), [Para([Str(u'Here'), Space(), Str(u'is'), Space(), Str(u
    'a'), Space(), Str(u'literal'), Space(), Str(u'backtick'), Space(), Code((u'
    ', [], []), u'`'), Str(u'.')])])

    >>> "This is a backslash followed by an asterisk: `\*`." # doctest: +PANDOC
    Pandoc(Meta(map()), [Para([Str(u'This'), Space(), Str(u'is'), Space(), Str(u
    'a'), Space(), Str(u'backslash'), Space(), Str(u'followed'), Space(), Str(u'
    by'), Space(), Str(u'an'), Space(), Str(u'asterisk:'), Space(), Code((u'', [
    ], []), u'\\*'), Str(u'.')])])

    >>> "`<$>`{.haskell}" # doctest: +PANDOC
    Pandoc(Meta(map()), [Para([Code((u'', [u'haskell'], []), u'<$>')])])


Small Caps
--------------------------------------------------------------------------------

    >>> "<span style='font-variant:small-caps;'>Small caps</span>"
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [Para([SmallCaps([Str(u'Small'), Space(), Str(u'caps')])
    ])])


Math
--------------------------------------------------------------------------------

    >>> "$a=1$" # doctest: +PANDOC
    Pandoc(Meta(map()), [Para([Math(InlineMath(), u'a=1')])])

    >>> "$$\int_0^1 f(x)\, dx$$" # doctest: +PANDOC
    Pandoc(Meta(map()), [Para([Math(DisplayMath(), u'\\int_0^1 f(x)\\, dx')])])


Raw HTML
--------------------------------------------------------------------------------

    >>> "<html></html>" # doctest: +PANDOC
    Pandoc(Meta(map()), [RawBlock(Format(u'html'), u'<html>'), RawBlock(Format(u
    'html'), u'</html>')])

    >>> """
    ... <table>
    ... <tr>
    ... <td>*one*</td>
    ... <td>[a link](http://google.com)</td>
    ... </tr>
    ... </table>
    ... """
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [RawBlock(Format(u'html'), u'<table>'), RawBlock(Format(
    u'html'), u'<tr>'), RawBlock(Format(u'html'), u'<td>'), Plain([Emph([Str(u'o
    ne')])]), RawBlock(Format(u'html'), u'</td>'), RawBlock(Format(u'html'), u'<
    td>'), Plain([Link((u'', [], []), [Str(u'a'), Space(), Str(u'link')], (u'htt
    p://google.com', u''))]), RawBlock(Format(u'html'), u'</td>'), RawBlock(Form
    at(u'html'), u'</tr>'), RawBlock(Format(u'html'), u'</table>')])


Raw TeX
--------------------------------------------------------------------------------

    >>> "This result was proved in \cite{jones.1967}."
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [Para([Str(u'This'), Space(), Str(u'result'), Space(), S
    tr(u'was'), Space(), Str(u'proved'), Space(), Str(u'in'), Space(), RawInline
    (Format(u'tex'), u'\\cite{jones.1967}'), Str(u'.')])])

    >>> r"""
    ... \begin{tabular}{|l|l|}\hline
    ... Age & Frequency \\ \hline
    ... 18--25  & 15 \\
    ... 26--35  & 33 \\
    ... 36--45  & 22 \\ \hline
    ... \end{tabular}
    ... """
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [RawBlock(Format(u'latex'), u'\\begin{tabular}{|l|l|}\\h
    line\nAge & Frequency \\\\ \\hline\n18--25  & 15 \\\\\n26--35  & 33 \\\\\n36
    --45  & 22 \\\\ \\hline\n\\end{tabular}')])

    >>> r"""
    ... \newcommand{\tuple}[1]{\langle #1 \rangle}
    ...
    ... $\tuple{a, b, c}$
    ... """
    ... # doctest: +PANDOC
    Pandoc(Meta(map()), [Para([Math(InlineMath(), u'{\\langle a, b, c \\rangle}'
    )])])

