# Pandoc's Markdown

**Source:**
<https://raw.githubusercontent.com/jgm/pandoc/2.14.2/MANUAL.txt>

Pandoc understands an extended and slightly revised version of John
Gruber's [Markdown](https://daringfireball.net/projects/markdown/)
syntax. This document explains the syntax, noting differences from
standard Markdown. Except where noted, these differences can be
suppressed by using the `markdown_strict` format instead of `markdown`.
Extensions can be enabled or disabled to specify the behavior more
granularly. They are described in the following. See also
[Extensions](#extensions) above, for extensions that work also on other
formats.

## Philosophy

Markdown is designed to be easy to write, and, even more importantly,
easy to read:

> A Markdown-formatted document should be publishable as-is, as plain
> text, without looking like it's been marked up with tags or formatting
> instructions. -- [John
> Gruber](https://daringfireball.net/projects/markdown/syntax#philosophy)

This principle has guided pandoc's decisions in finding syntax for
tables, footnotes, and other extensions.

There is, however, one respect in which pandoc's aims are different from
the original aims of Markdown. Whereas Markdown was originally designed
with HTML generation in mind, pandoc is designed for multiple output
formats. Thus, while pandoc allows the embedding of raw HTML, it
discourages it, and provides other, non-HTMLish ways of representing
important document elements like definition lists, tables, mathematics,
and footnotes.

## Paragraphs

A paragraph is one or more lines of text followed by one or more blank
lines. Newlines are treated as spaces, so you can reflow your paragraphs
as you like. If you need a hard line break, put two or more spaces at
the end of a line.

#### Extension: `escaped_line_breaks`

A backslash followed by a newline is also a hard line break. Note: in
multiline and grid table cells, this is the only way to create a hard
line break, since trailing spaces in the cells are ignored.

## Headings

There are two kinds of headings: Setext and ATX.

### Setext-style headings

A setext-style heading is a line of text "underlined" with a row of `=`
signs (for a level-one heading) or `-` signs (for a level-two heading):

=== "Markdown"

        A level-one heading
        ===================
        
        A level-two heading
        -------------------

=== "Python"

        Pandoc(Meta({}), [Header(1, ('a-level-one-heading', [], []), [Str('A'), Space(), Str('level-one'), Space(), Str('heading')]), Header(2, ('a-level-two-heading', [], []), [Str('A'), Space(), Str('level-two'), Space(), Str('heading')])])

<!-- prevent container tabs merge -->

The heading text can contain inline formatting, such as emphasis (see
[Inline formatting](#inline-formatting), below).

### ATX-style headings

An ATX-style heading consists of one to six `#` signs and a line of
text, optionally followed by any number of `#` signs. The number of `#`
signs at the beginning of the line is the heading level:

=== "Markdown"

        ## A level-two heading
        
        ### A level-three heading ###

=== "Python"

        Pandoc(Meta({}), [Header(2, ('a-level-two-heading', [], []), [Str('A'), Space(), Str('level-two'), Space(), Str('heading')]), Header(3, ('a-level-three-heading', [], []), [Str('A'), Space(), Str('level-three'), Space(), Str('heading')])])

<!-- prevent container tabs merge -->

As with setext-style headings, the heading text can contain formatting:

=== "Markdown"

        # A level-one heading with a [link](/url) and *emphasis*

=== "Python"

        Pandoc(Meta({}), [Header(1, ('a-level-one-heading-with-a-link-and-emphasis', [], []), [Str('A'), Space(), Str('level-one'), Space(), Str('heading'), Space(), Str('with'), Space(), Str('a'), Space(), Link(('', [], []), [Str('link')], ('/url', '')), Space(), Str('and'), Space(), Emph([Str('emphasis')])])])

<!-- prevent container tabs merge -->

#### Extension: `blank_before_header`

Standard Markdown syntax does not require a blank line before a heading.
Pandoc does require this (except, of course, at the beginning of the
document). The reason for the requirement is that it is all too easy for
a `#` to end up at the beginning of a line by accident (perhaps through
line wrapping). Consider, for example:

=== "Markdown"

        I like several of their flavors of ice cream:
        #22, for example, and #5.

=== "Python"

        Pandoc(Meta({}), [Para([Str('I'), Space(), Str('like'), Space(), Str('several'), Space(), Str('of'), Space(), Str('their'), Space(), Str('flavors'), Space(), Str('of'), Space(), Str('ice'), Space(), Str('cream:'), SoftBreak(), Str('#22,'), Space(), Str('for'), Space(), Str('example,'), Space(), Str('and'), Space(), Str('#5.')])])

<!-- prevent container tabs merge -->

#### Extension: `space_in_atx_header`

Many Markdown implementations do not require a space between the opening
`#`s of an ATX heading and the heading text, so that `#5 bolt` and
`#hashtag` count as headings. With this extension, pandoc does require
the space.

### Heading identifiers

See also the [`auto_identifiers` extension](#extension-auto_identifiers)
above.

#### Extension: `header_attributes`

Headings can be assigned attributes using this syntax at the end of the
line containing the heading text:

=== "Markdown"

        {#identifier .class .class key=value key=value}

=== "Python"

        Pandoc(Meta({}), [Para([Str('{#identifier'), Space(), Str('.class'), Space(), Str('.class'), Space(), Str('key=value'), Space(), Str('key=value}')])])

<!-- prevent container tabs merge -->

Thus, for example, the following headings will all be assigned the
identifier `foo`:

=== "Markdown"

        # My heading {#foo}
        
        ## My heading ##    {#foo}
        
        My other heading   {#foo}
        ---------------

=== "Python"

        Pandoc(Meta({}), [Header(1, ('foo', [], []), [Str('My'), Space(), Str('heading')]), Header(2, ('foo', [], []), [Str('My'), Space(), Str('heading')]), Header(2, ('foo', [], []), [Str('My'), Space(), Str('other'), Space(), Str('heading')])])

<!-- prevent container tabs merge -->

(This syntax is compatible with [PHP Markdown
Extra](https://michelf.ca/projects/php-markdown/extra/).)

Note that although this syntax allows assignment of classes and
key/value attributes, writers generally don't use all of this
information. Identifiers, classes, and key/value attributes are used in
HTML and HTML-based formats such as EPUB and slidy. Identifiers are used
for labels and link anchors in the LaTeX, ConTeXt, Textile, Jira markup,
and AsciiDoc writers.

Headings with the class `unnumbered` will not be numbered, even if
`--number-sections` is specified. A single hyphen (`-`) in an attribute
context is equivalent to `.unnumbered`, and preferable in non-English
documents. So,

=== "Markdown"

        # My heading {-}

=== "Python"

        Pandoc(Meta({}), [Header(1, ('my-heading', ['unnumbered'], []), [Str('My'), Space(), Str('heading')])])

<!-- prevent container tabs merge -->

is just the same as

=== "Markdown"

        # My heading {.unnumbered}

=== "Python"

        Pandoc(Meta({}), [Header(1, ('my-heading', ['unnumbered'], []), [Str('My'), Space(), Str('heading')])])

<!-- prevent container tabs merge -->

If the `unlisted` class is present in addition to `unnumbered`, the
heading will not be included in a table of contents. (Currently this
feature is only implemented for certain formats: those based on LaTeX
and HTML, PowerPoint, and RTF.)

#### Extension: `implicit_header_references`

Pandoc behaves as if reference links have been defined for each heading.
So, to link to a heading

=== "Markdown"

        # Heading identifiers in HTML

=== "Python"

        Pandoc(Meta({}), [Header(1, ('heading-identifiers-in-html', [], []), [Str('Heading'), Space(), Str('identifiers'), Space(), Str('in'), Space(), Str('HTML')])])

<!-- prevent container tabs merge -->

you can simply write

=== "Markdown"

        [Heading identifiers in HTML]

=== "Python"

        Pandoc(Meta({}), [Para([Str('[Heading'), Space(), Str('identifiers'), Space(), Str('in'), Space(), Str('HTML]')])])

<!-- prevent container tabs merge -->

or

=== "Markdown"

        [Heading identifiers in HTML][]

=== "Python"

        Pandoc(Meta({}), [Para([Str('[Heading'), Space(), Str('identifiers'), Space(), Str('in'), Space(), Str('HTML][]')])])

<!-- prevent container tabs merge -->

or

=== "Markdown"

        [the section on heading identifiers][heading identifiers in
        HTML]

=== "Python"

        Pandoc(Meta({}), [Para([Str('[the'), Space(), Str('section'), Space(), Str('on'), Space(), Str('heading'), Space(), Str('identifiers][heading'), Space(), Str('identifiers'), Space(), Str('in'), SoftBreak(), Str('HTML]')])])

<!-- prevent container tabs merge -->

instead of giving the identifier explicitly:

=== "Markdown"

        [Heading identifiers in HTML](#heading-identifiers-in-html)

=== "Python"

        Pandoc(Meta({}), [Para([Link(('', [], []), [Str('Heading'), Space(), Str('identifiers'), Space(), Str('in'), Space(), Str('HTML')], ('#heading-identifiers-in-html', ''))])])

<!-- prevent container tabs merge -->

If there are multiple headings with identical text, the corresponding
reference will link to the first one only, and you will need to use
explicit links to link to the others, as described above.

Like regular reference links, these references are case-insensitive.

Explicit link reference definitions always take priority over implicit
heading references. So, in the following example, the link will point to
`bar`, not to `#foo`:

=== "Markdown"

        # Foo
        
        [foo]: bar
        
        See [foo]

=== "Python"

        Pandoc(Meta({}), [Header(1, ('foo', [], []), [Str('Foo')]), Para([Str('See'), Space(), Link(('', [], []), [Str('foo')], ('bar', ''))])])

<!-- prevent container tabs merge -->

## Block quotations

Markdown uses email conventions for quoting blocks of text. A block
quotation is one or more paragraphs or other block elements (such as
lists or headings), with each line preceded by a `>` character and an
optional space. (The `>` need not start at the left margin, but it
should not be indented more than three spaces.)

=== "Markdown"

        > This is a block quote. This
        > paragraph has two lines.
        >
        > 1. This is a list inside a block quote.
        > 2. Second item.

=== "Python"

        Pandoc(Meta({}), [BlockQuote([Para([Str('This'), Space(), Str('is'), Space(), Str('a'), Space(), Str('block'), Space(), Str('quote.'), Space(), Str('This'), SoftBreak(), Str('paragraph'), Space(), Str('has'), Space(), Str('two'), Space(), Str('lines.')]), OrderedList((1, Decimal(), Period()), [[Plain([Str('This'), Space(), Str('is'), Space(), Str('a'), Space(), Str('list'), Space(), Str('inside'), Space(), Str('a'), Space(), Str('block'), Space(), Str('quote.')])], [Plain([Str('Second'), Space(), Str('item.')])]])])])

<!-- prevent container tabs merge -->

A "lazy" form, which requires the `>` character only on the first line
of each block, is also allowed:

=== "Markdown"

        > This is a block quote. This
        paragraph has two lines.
        
        > 1. This is a list inside a block quote.
        2. Second item.

=== "Python"

        Pandoc(Meta({}), [BlockQuote([Para([Str('This'), Space(), Str('is'), Space(), Str('a'), Space(), Str('block'), Space(), Str('quote.'), Space(), Str('This'), SoftBreak(), Str('paragraph'), Space(), Str('has'), Space(), Str('two'), Space(), Str('lines.')])]), BlockQuote([OrderedList((1, Decimal(), Period()), [[Plain([Str('This'), Space(), Str('is'), Space(), Str('a'), Space(), Str('list'), Space(), Str('inside'), Space(), Str('a'), Space(), Str('block'), Space(), Str('quote.')])], [Plain([Str('Second'), Space(), Str('item.')])]])])])

<!-- prevent container tabs merge -->

Among the block elements that can be contained in a block quote are
other block quotes. That is, block quotes can be nested:

=== "Markdown"

        > This is a block quote.
        >
        > > A block quote within a block quote.

=== "Python"

        Pandoc(Meta({}), [BlockQuote([Para([Str('This'), Space(), Str('is'), Space(), Str('a'), Space(), Str('block'), Space(), Str('quote.')]), BlockQuote([Para([Str('A'), Space(), Str('block'), Space(), Str('quote'), Space(), Str('within'), Space(), Str('a'), Space(), Str('block'), Space(), Str('quote.')])])])])

<!-- prevent container tabs merge -->

If the `>` character is followed by an optional space, that space will
be considered part of the block quote marker and not part of the
indentation of the contents. Thus, to put an indented code block in a
block quote, you need five spaces after the `>`:

=== "Markdown"

        >     code

=== "Python"

        Pandoc(Meta({}), [BlockQuote([CodeBlock(('', [], []), 'code')])])

<!-- prevent container tabs merge -->

#### Extension: `blank_before_blockquote`

Standard Markdown syntax does not require a blank line before a block
quote. Pandoc does require this (except, of course, at the beginning of
the document). The reason for the requirement is that it is all too easy
for a `>` to end up at the beginning of a line by accident (perhaps
through line wrapping). So, unless the `markdown_strict` format is used,
the following does not produce a nested block quote in pandoc:

=== "Markdown"

        > This is a block quote.
        >> Nested.

=== "Python"

        Pandoc(Meta({}), [BlockQuote([Para([Str('This'), Space(), Str('is'), Space(), Str('a'), Space(), Str('block'), Space(), Str('quote.'), SoftBreak(), Str('>'), Space(), Str('Nested.')])])])

<!-- prevent container tabs merge -->

## Verbatim (code) blocks

### Indented code blocks

A block of text indented four spaces (or one tab) is treated as verbatim
text: that is, special characters do not trigger special formatting, and
all spaces and line breaks are preserved. For example,

=== "Markdown"

            if (a > 3) {
              moveShip(5 * gravity, DOWN);
            }

=== "Python"

        Pandoc(Meta({}), [CodeBlock(('', [], []), 'if (a > 3) {\n  moveShip(5 * gravity, DOWN);\n}')])

<!-- prevent container tabs merge -->

The initial (four space or one tab) indentation is not considered part
of the verbatim text, and is removed in the output.

Note: blank lines in the verbatim text need not begin with four spaces.

### Fenced code blocks

#### Extension: `fenced_code_blocks`

In addition to standard indented code blocks, pandoc supports *fenced*
code blocks. These begin with a row of three or more tildes (`~`) and
end with a row of tildes that must be at least as long as the starting
row. Everything between these lines is treated as code. No indentation
is necessary:

=== "Markdown"

        ~~~~~~~
        if (a > 3) {
          moveShip(5 * gravity, DOWN);
        }
        ~~~~~~~

=== "Python"

        Pandoc(Meta({}), [CodeBlock(('', [], []), 'if (a > 3) {\n  moveShip(5 * gravity, DOWN);\n}')])

<!-- prevent container tabs merge -->

Like regular code blocks, fenced code blocks must be separated from
surrounding text by blank lines.

If the code itself contains a row of tildes or backticks, just use a
longer row of tildes or backticks at the start and end:

=== "Markdown"

        ~~~~~~~~~~~~~~~~
        ~~~~~~~~~~
        code including tildes
        ~~~~~~~~~~
        ~~~~~~~~~~~~~~~~

=== "Python"

        Pandoc(Meta({}), [CodeBlock(('', [], []), '~~~~~~~~~~\ncode including tildes\n~~~~~~~~~~')])

<!-- prevent container tabs merge -->

#### Extension: `backtick_code_blocks`

Same as `fenced_code_blocks`, but uses backticks (`` ` ``) instead of
tildes (`~`).

#### Extension: `fenced_code_attributes`

Optionally, you may attach attributes to fenced or backtick code block
using this syntax:

=== "Markdown"

        ~~~~ {#mycode .haskell .numberLines startFrom="100"}
        qsort []     = []
        qsort (x:xs) = qsort (filter (< x) xs) ++ [x] ++
                       qsort (filter (>= x) xs)
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

=== "Python"

        Pandoc(Meta({}), [CodeBlock(('mycode', ['haskell', 'numberLines'], [('startFrom', '100')]), 'qsort []     = []\nqsort (x:xs) = qsort (filter (< x) xs) ++ [x] ++\n               qsort (filter (>= x) xs)')])

<!-- prevent container tabs merge -->

Here `mycode` is an identifier, `haskell` and `numberLines` are classes,
and `startFrom` is an attribute with value `100`. Some output formats
can use this information to do syntax highlighting. Currently, the only
output formats that uses this information are HTML, LaTeX, Docx, Ms, and
PowerPoint. If highlighting is supported for your output format and
language, then the code block above will appear highlighted, with
numbered lines. (To see which languages are supported, type
`pandoc --list-highlight-languages`.) Otherwise, the code block above
will appear as follows:

=== "Markdown"

        <pre id="mycode" class="haskell numberLines" startFrom="100">
          <code>
          ...
          </code>
        </pre>

=== "Python"

        Pandoc(Meta({}), [RawBlock(Format('html'), '<pre id="mycode" class="haskell numberLines" startFrom="100">\n  <code>\n  ...\n  </code>\n</pre>')])

<!-- prevent container tabs merge -->

The `numberLines` (or `number-lines`) class will cause the lines of the
code block to be numbered, starting with `1` or the value of the
`startFrom` attribute. The `lineAnchors` (or `line-anchors`) class will
cause the lines to be clickable anchors in HTML output.

A shortcut form can also be used for specifying the language of the code
block:

=== "Markdown"

        ```haskell
        qsort [] = []
        ```

=== "Python"

        Pandoc(Meta({}), [CodeBlock(('', ['haskell'], []), 'qsort [] = []')])

<!-- prevent container tabs merge -->

This is equivalent to:

=== "Markdown"

        ``` {.haskell}
        qsort [] = []
        ```

=== "Python"

        Pandoc(Meta({}), [CodeBlock(('', ['haskell'], []), 'qsort [] = []')])

<!-- prevent container tabs merge -->

If the `fenced_code_attributes` extension is disabled, but input
contains class attribute(s) for the code block, the first class
attribute will be printed after the opening fence as a bare word.

To prevent all highlighting, use the `--no-highlight` flag. To set the
highlighting style, use `--highlight-style`. For more information on
highlighting, see [Syntax highlighting](#syntax-highlighting), below.

## Line blocks

#### Extension: `line_blocks`

A line block is a sequence of lines beginning with a vertical bar (`|`)
followed by a space. The division into lines will be preserved in the
output, as will any leading spaces; otherwise, the lines will be
formatted as Markdown. This is useful for verse and addresses:

=== "Markdown"

        | The limerick packs laughs anatomical
        | In space that is quite economical.
        |    But the good ones I've seen
        |    So seldom are clean
        | And the clean ones so seldom are comical
        
        | 200 Main St.
        | Berkeley, CA 94718

=== "Python"

        Pandoc(Meta({}), [LineBlock([[Str('The'), Space(), Str('limerick'), Space(), Str('packs'), Space(), Str('laughs'), Space(), Str('anatomical')], [Str('In'), Space(), Str('space'), Space(), Str('that'), Space(), Str('is'), Space(), Str('quite'), Space(), Str('economical.')], [Str('\xa0\xa0\xa0But'), Space(), Str('the'), Space(), Str('good'), Space(), Str('ones'), Space(), Str('I’ve'), Space(), Str('seen')], [Str('\xa0\xa0\xa0So'), Space(), Str('seldom'), Space(), Str('are'), Space(), Str('clean')], [Str('And'), Space(), Str('the'), Space(), Str('clean'), Space(), Str('ones'), Space(), Str('so'), Space(), Str('seldom'), Space(), Str('are'), Space(), Str('comical')]]), LineBlock([[Str('200'), Space(), Str('Main'), Space(), Str('St.')], [Str('Berkeley,'), Space(), Str('CA'), Space(), Str('94718')]])])

<!-- prevent container tabs merge -->

The lines can be hard-wrapped if needed, but the continuation line must
begin with a space.

=== "Markdown"

        | The Right Honorable Most Venerable and Righteous Samuel L.
          Constable, Jr.
        | 200 Main St.
        | Berkeley, CA 94718

=== "Python"

        Pandoc(Meta({}), [LineBlock([[Str('The'), Space(), Str('Right'), Space(), Str('Honorable'), Space(), Str('Most'), Space(), Str('Venerable'), Space(), Str('and'), Space(), Str('Righteous'), Space(), Str('Samuel'), Space(), Str('L.'), Space(), Str('Constable,'), Space(), Str('Jr.')], [Str('200'), Space(), Str('Main'), Space(), Str('St.')], [Str('Berkeley,'), Space(), Str('CA'), Space(), Str('94718')]])])

<!-- prevent container tabs merge -->

Inline formatting (such as emphasis) is allowed in the content, but not
block-level formatting (such as block quotes or lists).

This syntax is borrowed from
[reStructuredText](https://docutils.sourceforge.io/docs/ref/rst/introduction.html).

## Lists

### Bullet lists

A bullet list is a list of bulleted list items. A bulleted list item
begins with a bullet (`*`, `+`, or `-`). Here is a simple example:

=== "Markdown"

        * one
        * two
        * three

=== "Python"

        Pandoc(Meta({}), [BulletList([[Plain([Str('one')])], [Plain([Str('two')])], [Plain([Str('three')])]])])

<!-- prevent container tabs merge -->

This will produce a "compact" list. If you want a "loose" list, in which
each item is formatted as a paragraph, put spaces between the items:

=== "Markdown"

        * one
        
        * two
        
        * three

=== "Python"

        Pandoc(Meta({}), [BulletList([[Para([Str('one')])], [Para([Str('two')])], [Para([Str('three')])]])])

<!-- prevent container tabs merge -->

The bullets need not be flush with the left margin; they may be indented
one, two, or three spaces. The bullet must be followed by whitespace.

List items look best if subsequent lines are flush with the first line
(after the bullet):

=== "Markdown"

        * here is my first
          list item.
        * and my second.

=== "Python"

        Pandoc(Meta({}), [BulletList([[Plain([Str('here'), Space(), Str('is'), Space(), Str('my'), Space(), Str('first'), SoftBreak(), Str('list'), Space(), Str('item.')])], [Plain([Str('and'), Space(), Str('my'), Space(), Str('second.')])]])])

<!-- prevent container tabs merge -->

But Markdown also allows a "lazy" format:

=== "Markdown"

        * here is my first
        list item.
        * and my second.

=== "Python"

        Pandoc(Meta({}), [BulletList([[Plain([Str('here'), Space(), Str('is'), Space(), Str('my'), Space(), Str('first'), SoftBreak(), Str('list'), Space(), Str('item.')])], [Plain([Str('and'), Space(), Str('my'), Space(), Str('second.')])]])])

<!-- prevent container tabs merge -->

### Block content in list items

A list item may contain multiple paragraphs and other block-level
content. However, subsequent paragraphs must be preceded by a blank line
and indented to line up with the first non-space content after the list
marker.

=== "Markdown"

          * First paragraph.
        
            Continued.
        
          * Second paragraph. With a code block, which must be indented
            eight spaces:
        
                { code }

=== "Python"

        Pandoc(Meta({}), [BulletList([[Para([Str('First'), Space(), Str('paragraph.')]), Para([Str('Continued.')])], [Para([Str('Second'), Space(), Str('paragraph.'), Space(), Str('With'), Space(), Str('a'), Space(), Str('code'), Space(), Str('block,'), Space(), Str('which'), Space(), Str('must'), Space(), Str('be'), Space(), Str('indented'), SoftBreak(), Str('eight'), Space(), Str('spaces:')]), CodeBlock(('', [], []), '{ code }')]])])

<!-- prevent container tabs merge -->

Exception: if the list marker is followed by an indented code block,
which must begin 5 spaces after the list marker, then subsequent
paragraphs must begin two columns after the last character of the list
marker:

=== "Markdown"

        *     code
        
          continuation paragraph

=== "Python"

        Pandoc(Meta({}), [BulletList([[CodeBlock(('', [], []), 'code'), Plain([Str('continuation'), Space(), Str('paragraph')])]])])

<!-- prevent container tabs merge -->

List items may include other lists. In this case the preceding blank
line is optional. The nested list must be indented to line up with the
first non-space character after the list marker of the containing list
item.

=== "Markdown"

        * fruits
          + apples
            - macintosh
            - red delicious
          + pears
          + peaches
        * vegetables
          + broccoli
          + chard

=== "Python"

        Pandoc(Meta({}), [BulletList([[Plain([Str('fruits')]), BulletList([[Plain([Str('apples')]), BulletList([[Plain([Str('macintosh')])], [Plain([Str('red'), Space(), Str('delicious')])]])], [Plain([Str('pears')])], [Plain([Str('peaches')])]])], [Plain([Str('vegetables')]), BulletList([[Plain([Str('broccoli')])], [Plain([Str('chard')])]])]])])

<!-- prevent container tabs merge -->

As noted above, Markdown allows you to write list items "lazily,"
instead of indenting continuation lines. However, if there are multiple
paragraphs or other blocks in a list item, the first line of each must
be indented.

=== "Markdown"

        + A lazy, lazy, list
        item.
        
        + Another one; this looks
        bad but is legal.
        
            Second paragraph of second
        list item.

=== "Python"

        Pandoc(Meta({}), [BulletList([[Para([Str('A'), Space(), Str('lazy,'), Space(), Str('lazy,'), Space(), Str('list'), SoftBreak(), Str('item.')])], [Para([Str('Another'), Space(), Str('one;'), Space(), Str('this'), Space(), Str('looks'), SoftBreak(), Str('bad'), Space(), Str('but'), Space(), Str('is'), Space(), Str('legal.')]), Para([Str('Second'), Space(), Str('paragraph'), Space(), Str('of'), Space(), Str('second'), SoftBreak(), Str('list'), Space(), Str('item.')])]])])

<!-- prevent container tabs merge -->

### Ordered lists

Ordered lists work just like bulleted lists, except that the items begin
with enumerators rather than bullets.

In standard Markdown, enumerators are decimal numbers followed by a
period and a space. The numbers themselves are ignored, so there is no
difference between this list:

=== "Markdown"

        1.  one
        2.  two
        3.  three

=== "Python"

        Pandoc(Meta({}), [OrderedList((1, Decimal(), Period()), [[Plain([Str('one')])], [Plain([Str('two')])], [Plain([Str('three')])]])])

<!-- prevent container tabs merge -->

and this one:

=== "Markdown"

        5.  one
        7.  two
        1.  three

=== "Python"

        Pandoc(Meta({}), [OrderedList((5, Decimal(), Period()), [[Plain([Str('one')])], [Plain([Str('two')])], [Plain([Str('three')])]])])

<!-- prevent container tabs merge -->

#### Extension: `fancy_lists`

Unlike standard Markdown, pandoc allows ordered list items to be marked
with uppercase and lowercase letters and roman numerals, in addition to
Arabic numerals. List markers may be enclosed in parentheses or followed
by a single right-parentheses or period. They must be separated from the
text that follows by at least one space, and, if the list marker is a
capital letter with a period, by at least two spaces.[^1]

The `fancy_lists` extension also allows '`#`' to be used as an ordered
list marker in place of a numeral:

=== "Markdown"

        #. one
        #. two

=== "Python"

        Pandoc(Meta({}), [OrderedList((1, DefaultStyle(), DefaultDelim()), [[Plain([Str('one')])], [Plain([Str('two')])]])])

<!-- prevent container tabs merge -->

#### Extension: `startnum`

Pandoc also pays attention to the type of list marker used, and to the
starting number, and both of these are preserved where possible in the
output format. Thus, the following yields a list with numbers followed
by a single parenthesis, starting with 9, and a sublist with lowercase
roman numerals:

=== "Markdown"

         9)  Ninth
        10)  Tenth
        11)  Eleventh
               i. subone
              ii. subtwo
             iii. subthree

=== "Python"

        Pandoc(Meta({}), [OrderedList((9, Decimal(), OneParen()), [[Plain([Str('Ninth')])], [Plain([Str('Tenth')])], [Plain([Str('Eleventh')]), OrderedList((1, LowerRoman(), Period()), [[Plain([Str('subone')])], [Plain([Str('subtwo')])], [Plain([Str('subthree')])]])]])])

<!-- prevent container tabs merge -->

Pandoc will start a new list each time a different type of list marker
is used. So, the following will create three lists:

=== "Markdown"

        (2) Two
        (5) Three
        1.  Four
        *   Five

=== "Python"

        Pandoc(Meta({}), [OrderedList((2, Decimal(), TwoParens()), [[Plain([Str('Two')])], [Plain([Str('Three')])]]), OrderedList((1, Decimal(), Period()), [[Plain([Str('Four')])]]), BulletList([[Plain([Str('Five')])]])])

<!-- prevent container tabs merge -->

If default list markers are desired, use `#.`:

=== "Markdown"

        #.  one
        #.  two
        #.  three

=== "Python"

        Pandoc(Meta({}), [OrderedList((1, DefaultStyle(), DefaultDelim()), [[Plain([Str('one')])], [Plain([Str('two')])], [Plain([Str('three')])]])])

<!-- prevent container tabs merge -->

#### Extension: `task_lists`

Pandoc supports task lists, using the syntax of GitHub-Flavored
Markdown.

=== "Markdown"

        - [ ] an unchecked task list item
        - [x] checked item

=== "Python"

        Pandoc(Meta({}), [BulletList([[Plain([Str('☐'), Space(), Str('an'), Space(), Str('unchecked'), Space(), Str('task'), Space(), Str('list'), Space(), Str('item')])], [Plain([Str('☒'), Space(), Str('checked'), Space(), Str('item')])]])])

<!-- prevent container tabs merge -->

### Definition lists

#### Extension: `definition_lists`

Pandoc supports definition lists, using the syntax of [PHP Markdown
Extra](https://michelf.ca/projects/php-markdown/extra/) with some
extensions.[^2]

=== "Markdown"

        Term 1
        
        :   Definition 1
        
        Term 2 with *inline markup*
        
        :   Definition 2
        
                { some code, part of Definition 2 }
        
            Third paragraph of definition 2.

=== "Python"

        Pandoc(Meta({}), [DefinitionList([([Str('Term'), Space(), Str('1')], [[Para([Str('Definition'), Space(), Str('1')])]]), ([Str('Term'), Space(), Str('2'), Space(), Str('with'), Space(), Emph([Str('inline'), Space(), Str('markup')])], [[Para([Str('Definition'), Space(), Str('2')]), CodeBlock(('', [], []), '{ some code, part of Definition 2 }'), Para([Str('Third'), Space(), Str('paragraph'), Space(), Str('of'), Space(), Str('definition'), Space(), Str('2.')])]])])])

<!-- prevent container tabs merge -->

Each term must fit on one line, which may optionally be followed by a
blank line, and must be followed by one or more definitions. A
definition begins with a colon or tilde, which may be indented one or
two spaces.

A term may have multiple definitions, and each definition may consist of
one or more block elements (paragraph, code block, list, etc.), each
indented four spaces or one tab stop. The body of the definition
(including the first line, aside from the colon or tilde) should be
indented four spaces. However, as with other Markdown lists, you can
"lazily" omit indentation except at the beginning of a paragraph or
other block element:

=== "Markdown"

        Term 1
        
        :   Definition
        with lazy continuation.
        
            Second paragraph of the definition.

=== "Python"

        Pandoc(Meta({}), [DefinitionList([([Str('Term'), Space(), Str('1')], [[Para([Str('Definition'), SoftBreak(), Str('with'), Space(), Str('lazy'), Space(), Str('continuation.')]), Para([Str('Second'), Space(), Str('paragraph'), Space(), Str('of'), Space(), Str('the'), Space(), Str('definition.')])]])])])

<!-- prevent container tabs merge -->

If you leave space before the definition (as in the example above), the
text of the definition will be treated as a paragraph. In some output
formats, this will mean greater spacing between term/definition pairs.
For a more compact definition list, omit the space before the
definition:

=== "Markdown"

        Term 1
          ~ Definition 1
        
        Term 2
          ~ Definition 2a
          ~ Definition 2b

=== "Python"

        Pandoc(Meta({}), [DefinitionList([([Str('Term'), Space(), Str('1')], [[Plain([Str('Definition'), Space(), Str('1')])]]), ([Str('Term'), Space(), Str('2')], [[Plain([Str('Definition'), Space(), Str('2a')])], [Plain([Str('Definition'), Space(), Str('2b')])]])])])

<!-- prevent container tabs merge -->

Note that space between items in a definition list is required. (A
variant that loosens this requirement, but disallows "lazy" hard
wrapping, can be activated with `compact_definition_lists`: see
[Non-default extensions](#non-default-extensions), below.)

### Numbered example lists

#### Extension: `example_lists`

The special list marker `@` can be used for sequentially numbered
examples. The first list item with a `@` marker will be numbered '1',
the next '2', and so on, throughout the document. The numbered examples
need not occur in a single list; each new list using `@` will take up
where the last stopped. So, for example:

=== "Markdown"

        (@)  My first example will be numbered (1).
        (@)  My second example will be numbered (2).
        
        Explanation of examples.
        
        (@)  My third example will be numbered (3).

=== "Python"

        Pandoc(Meta({}), [OrderedList((1, Example(), TwoParens()), [[Plain([Str('My'), Space(), Str('first'), Space(), Str('example'), Space(), Str('will'), Space(), Str('be'), Space(), Str('numbered'), Space(), Str('(1).')])], [Plain([Str('My'), Space(), Str('second'), Space(), Str('example'), Space(), Str('will'), Space(), Str('be'), Space(), Str('numbered'), Space(), Str('(2).')])]]), Para([Str('Explanation'), Space(), Str('of'), Space(), Str('examples.')]), OrderedList((3, Example(), TwoParens()), [[Plain([Str('My'), Space(), Str('third'), Space(), Str('example'), Space(), Str('will'), Space(), Str('be'), Space(), Str('numbered'), Space(), Str('(3).')])]])])

<!-- prevent container tabs merge -->

Numbered examples can be labeled and referred to elsewhere in the
document:

=== "Markdown"

        (@good)  This is a good example.
        
        As (@good) illustrates, ...

=== "Python"

        Pandoc(Meta({}), [OrderedList((1, Example(), TwoParens()), [[Plain([Str('This'), Space(), Str('is'), Space(), Str('a'), Space(), Str('good'), Space(), Str('example.')])]]), Para([Str('As'), Space(), Str('(1)'), Space(), Str('illustrates,'), Space(), Str('…')])])

<!-- prevent container tabs merge -->

The label can be any string of alphanumeric characters, underscores, or
hyphens.

Note: continuation paragraphs in example lists must always be indented
four spaces, regardless of the length of the list marker. That is,
example lists always behave as if the `four_space_rule` extension is
set. This is because example labels tend to be long, and indenting
content to the first non-space character after the label would be
awkward.

### Ending a list

What if you want to put an indented code block after a list?

=== "Markdown"

        -   item one
        -   item two
        
            { my code block }

=== "Python"

        Pandoc(Meta({}), [BulletList([[Para([Str('item'), Space(), Str('one')])], [Para([Str('item'), Space(), Str('two')]), Para([Str('{'), Space(), Str('my'), Space(), Str('code'), Space(), Str('block'), Space(), Str('}')])]])])

<!-- prevent container tabs merge -->

Trouble! Here pandoc (like other Markdown implementations) will treat
`{ my code block }` as the second paragraph of item two, and not as a
code block.

To "cut off" the list after item two, you can insert some non-indented
content, like an HTML comment, which won't produce visible output in any
format:

=== "Markdown"

        -   item one
        -   item two
        
        <!-- end of list -->
        
            { my code block }

=== "Python"

        Pandoc(Meta({}), [BulletList([[Plain([Str('item'), Space(), Str('one')])], [Plain([Str('item'), Space(), Str('two')])]]), RawBlock(Format('html'), '<!-- end of list -->'), CodeBlock(('', [], []), '{ my code block }')])

<!-- prevent container tabs merge -->

You can use the same trick if you want two consecutive lists instead of
one big list:

=== "Markdown"

        1.  one
        2.  two
        3.  three
        
        <!-- -->
        
        1.  uno
        2.  dos
        3.  tres

=== "Python"

        Pandoc(Meta({}), [OrderedList((1, Decimal(), Period()), [[Plain([Str('one')])], [Plain([Str('two')])], [Plain([Str('three')])]]), RawBlock(Format('html'), '<!-- -->'), OrderedList((1, Decimal(), Period()), [[Plain([Str('uno')])], [Plain([Str('dos')])], [Plain([Str('tres')])]])])

<!-- prevent container tabs merge -->

## Horizontal rules

A line containing a row of three or more `*`, `-`, or `_` characters
(optionally separated by spaces) produces a horizontal rule:

=== "Markdown"

        *  *  *  *
        
        ---------------

=== "Python"

        Pandoc(Meta({}), [HorizontalRule(), HorizontalRule()])

<!-- prevent container tabs merge -->

## Tables

Four kinds of tables may be used. The first three kinds presuppose the
use of a fixed-width font, such as Courier. The fourth kind can be used
with proportionally spaced fonts, as it does not require lining up
columns.

#### Extension: `table_captions`

A caption may optionally be provided with all 4 kinds of tables (as
illustrated in the examples below). A caption is a paragraph beginning
with the string `Table:` (or just `:`), which will be stripped off. It
may appear either before or after the table.

#### Extension: `simple_tables`

Simple tables look like this:

=== "Markdown"

          Right     Left     Center     Default
        -------     ------ ----------   -------
             12     12        12            12
            123     123       123          123
              1     1          1             1
        
        Table:  Demonstration of simple table syntax.

=== "Python"

        Pandoc(Meta({}), [Table(('', [], []), Caption(None, [Plain([Str('Demonstration'), Space(), Str('of'), Space(), Str('simple'), Space(), Str('table'), Space(), Str('syntax.')])]), [(AlignRight(), ColWidthDefault()), (AlignLeft(), ColWidthDefault()), (AlignCenter(), ColWidthDefault()), (AlignDefault(), ColWidthDefault())], TableHead(('', [], []), [Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Right')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Left')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Center')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Default')])])])]), [TableBody(('', [], []), RowHeadColumns(0), [], [Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('12')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('12')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('12')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('12')])])]), Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('123')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('123')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('123')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('123')])])]), Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('1')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('1')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('1')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('1')])])])])], TableFoot(('', [], []), []))])

<!-- prevent container tabs merge -->

The header and table rows must each fit on one line. Column alignments
are determined by the position of the header text relative to the dashed
line below it:[^3]

-   If the dashed line is flush with the header text on the right side
    but extends beyond it on the left, the column is right-aligned.
-   If the dashed line is flush with the header text on the left side
    but extends beyond it on the right, the column is left-aligned.
-   If the dashed line extends beyond the header text on both sides, the
    column is centered.
-   If the dashed line is flush with the header text on both sides, the
    default alignment is used (in most cases, this will be left).

The table must end with a blank line, or a line of dashes followed by a
blank line.

The column header row may be omitted, provided a dashed line is used to
end the table. For example:

=== "Markdown"

        -------     ------ ----------   -------
             12     12        12             12
            123     123       123           123
              1     1          1              1
        -------     ------ ----------   -------

=== "Python"

        Pandoc(Meta({}), [Table(('', [], []), Caption(None, []), [(AlignRight(), ColWidthDefault()), (AlignLeft(), ColWidthDefault()), (AlignCenter(), ColWidthDefault()), (AlignRight(), ColWidthDefault())], TableHead(('', [], []), []), [TableBody(('', [], []), RowHeadColumns(0), [], [Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('12')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('12')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('12')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('12')])])]), Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('123')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('123')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('123')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('123')])])]), Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('1')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('1')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('1')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('1')])])])])], TableFoot(('', [], []), []))])

<!-- prevent container tabs merge -->

When the header row is omitted, column alignments are determined on the
basis of the first line of the table body. So, in the tables above, the
columns would be right, left, center, and right aligned, respectively.

#### Extension: `multiline_tables`

Multiline tables allow header and table rows to span multiple lines of
text (but cells that span multiple columns or rows of the table are not
supported). Here is an example:

=== "Markdown"

        -------------------------------------------------------------
         Centered   Default           Right Left
          Header    Aligned         Aligned Aligned
        ----------- ------- --------------- -------------------------
           First    row                12.0 Example of a row that
                                            spans multiple lines.
        
          Second    row                 5.0 Here's another one. Note
                                            the blank line between
                                            rows.
        -------------------------------------------------------------
        
        Table: Here's the caption. It, too, may span
        multiple lines.

=== "Python"

        Pandoc(Meta({}), [Table(('', [], []), Caption(None, [Plain([Str('Here’s'), Space(), Str('the'), Space(), Str('caption.'), Space(), Str('It,'), Space(), Str('too,'), Space(), Str('may'), Space(), Str('span'), SoftBreak(), Str('multiple'), Space(), Str('lines.')])]), [(AlignCenter(), ColWidth_(0.16666666666666666)), (AlignDefault(), ColWidth_(0.1111111111111111)), (AlignRight(), ColWidth_(0.2222222222222222)), (AlignLeft(), ColWidth_(0.3611111111111111))], TableHead(('', [], []), [Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Centered'), SoftBreak(), Str('Header')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Default'), SoftBreak(), Str('Aligned')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Right'), SoftBreak(), Str('Aligned')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Left'), SoftBreak(), Str('Aligned')])])])]), [TableBody(('', [], []), RowHeadColumns(0), [], [Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('First')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('row')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('12.0')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Example'), Space(), Str('of'), Space(), Str('a'), Space(), Str('row'), Space(), Str('that'), SoftBreak(), Str('spans'), Space(), Str('multiple'), Space(), Str('lines.')])])]), Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Second')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('row')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('5.0')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Here’s'), Space(), Str('another'), Space(), Str('one.'), Space(), Str('Note'), SoftBreak(), Str('the'), Space(), Str('blank'), Space(), Str('line'), Space(), Str('between'), SoftBreak(), Str('rows.')])])])])], TableFoot(('', [], []), []))])

<!-- prevent container tabs merge -->

These work like simple tables, but with the following differences:

-   They must begin with a row of dashes, before the header text (unless
    the header row is omitted).
-   They must end with a row of dashes, then a blank line.
-   The rows must be separated by blank lines.

In multiline tables, the table parser pays attention to the widths of
the columns, and the writers try to reproduce these relative widths in
the output. So, if you find that one of the columns is too narrow in the
output, try widening it in the Markdown source.

The header may be omitted in multiline tables as well as simple tables:

=== "Markdown"

        ----------- ------- --------------- -------------------------
           First    row                12.0 Example of a row that
                                            spans multiple lines.
        
          Second    row                 5.0 Here's another one. Note
                                            the blank line between
                                            rows.
        ----------- ------- --------------- -------------------------
        
        : Here's a multiline table without a header.

=== "Python"

        Pandoc(Meta({}), [Table(('', [], []), Caption(None, [Plain([Str('Here’s'), Space(), Str('a'), Space(), Str('multiline'), Space(), Str('table'), Space(), Str('without'), Space(), Str('a'), Space(), Str('header.')])]), [(AlignCenter(), ColWidth_(0.16666666666666666)), (AlignLeft(), ColWidth_(0.1111111111111111)), (AlignRight(), ColWidth_(0.2222222222222222)), (AlignLeft(), ColWidth_(0.3611111111111111))], TableHead(('', [], []), []), [TableBody(('', [], []), RowHeadColumns(0), [], [Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('First')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('row')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('12.0')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Example'), Space(), Str('of'), Space(), Str('a'), Space(), Str('row'), Space(), Str('that'), SoftBreak(), Str('spans'), Space(), Str('multiple'), Space(), Str('lines.')])])]), Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Second')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('row')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('5.0')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Here’s'), Space(), Str('another'), Space(), Str('one.'), Space(), Str('Note'), SoftBreak(), Str('the'), Space(), Str('blank'), Space(), Str('line'), Space(), Str('between'), SoftBreak(), Str('rows.')])])])])], TableFoot(('', [], []), []))])

<!-- prevent container tabs merge -->

It is possible for a multiline table to have just one row, but the row
should be followed by a blank line (and then the row of dashes that ends
the table), or the table may be interpreted as a simple table.

#### Extension: `grid_tables`

Grid tables look like this:

=== "Markdown"

        : Sample grid table.
        
        +---------------+---------------+--------------------+
        | Fruit         | Price         | Advantages         |
        +===============+===============+====================+
        | Bananas       | $1.34         | - built-in wrapper |
        |               |               | - bright color     |
        +---------------+---------------+--------------------+
        | Oranges       | $2.10         | - cures scurvy     |
        |               |               | - tasty            |
        +---------------+---------------+--------------------+

=== "Python"

        Pandoc(Meta({}), [Table(('', [], []), Caption(None, [Plain([Str('Sample'), Space(), Str('grid'), Space(), Str('table.')])]), [(AlignDefault(), ColWidth_(0.2222222222222222)), (AlignDefault(), ColWidth_(0.2222222222222222)), (AlignDefault(), ColWidth_(0.2916666666666667))], TableHead(('', [], []), [Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Fruit')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Price')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Advantages')])])])]), [TableBody(('', [], []), RowHeadColumns(0), [], [Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Bananas')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('$1.34')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [BulletList([[Plain([Str('built-in'), Space(), Str('wrapper')])], [Plain([Str('bright'), Space(), Str('color')])]])])]), Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Oranges')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('$2.10')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [BulletList([[Plain([Str('cures'), Space(), Str('scurvy')])], [Plain([Str('tasty')])]])])])])], TableFoot(('', [], []), []))])

<!-- prevent container tabs merge -->

The row of `=`s separates the header from the table body, and can be
omitted for a headerless table. The cells of grid tables may contain
arbitrary block elements (multiple paragraphs, code blocks, lists,
etc.). Cells that span multiple columns or rows are not supported. Grid
tables can be created easily using Emacs' table-mode
(`M-x table-insert`).

Alignments can be specified as with pipe tables, by putting colons at
the boundaries of the separator line after the header:

=== "Markdown"

        +---------------+---------------+--------------------+
        | Right         | Left          | Centered           |
        +==============:+:==============+:==================:+
        | Bananas       | $1.34         | built-in wrapper   |
        +---------------+---------------+--------------------+

=== "Python"

        Pandoc(Meta({}), [Table(('', [], []), Caption(None, []), [(AlignRight(), ColWidth_(0.2222222222222222)), (AlignLeft(), ColWidth_(0.2222222222222222)), (AlignCenter(), ColWidth_(0.2916666666666667))], TableHead(('', [], []), [Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Right')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Left')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Centered')])])])]), [TableBody(('', [], []), RowHeadColumns(0), [], [Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Bananas')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('$1.34')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('built-in'), Space(), Str('wrapper')])])])])], TableFoot(('', [], []), []))])

<!-- prevent container tabs merge -->

For headerless tables, the colons go on the top line instead:

=== "Markdown"

        +--------------:+:--------------+:------------------:+
        | Right         | Left          | Centered           |
        +---------------+---------------+--------------------+

=== "Python"

        Pandoc(Meta({}), [Table(('', [], []), Caption(None, []), [(AlignRight(), ColWidth_(0.2222222222222222)), (AlignLeft(), ColWidth_(0.2222222222222222)), (AlignCenter(), ColWidth_(0.2916666666666667))], TableHead(('', [], []), []), [TableBody(('', [], []), RowHeadColumns(0), [], [Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Right')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Left')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Centered')])])])])], TableFoot(('', [], []), []))])

<!-- prevent container tabs merge -->

##### Grid Table Limitations

Pandoc does not support grid tables with row spans or column spans. This
means that neither variable numbers of columns across rows nor variable
numbers of rows across columns are supported by Pandoc. All grid tables
must have the same number of columns in each row, and the same number of
rows in each column. For example, the Docutils [sample grid
tables](https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#grid-tables)
will not render as expected with Pandoc.

#### Extension: `pipe_tables`

Pipe tables look like this:

=== "Markdown"

        | Right | Left | Default | Center |
        |------:|:-----|---------|:------:|
        |   12  |  12  |    12   |    12  |
        |  123  |  123 |   123   |   123  |
        |    1  |    1 |     1   |     1  |
        
          : Demonstration of pipe table syntax.

=== "Python"

        Pandoc(Meta({}), [Table(('', [], []), Caption(None, [Plain([Str('Demonstration'), Space(), Str('of'), Space(), Str('pipe'), Space(), Str('table'), Space(), Str('syntax.')])]), [(AlignRight(), ColWidthDefault()), (AlignLeft(), ColWidthDefault()), (AlignDefault(), ColWidthDefault()), (AlignCenter(), ColWidthDefault())], TableHead(('', [], []), [Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Right')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Left')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Default')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Center')])])])]), [TableBody(('', [], []), RowHeadColumns(0), [], [Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('12')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('12')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('12')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('12')])])]), Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('123')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('123')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('123')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('123')])])]), Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('1')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('1')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('1')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('1')])])])])], TableFoot(('', [], []), []))])

<!-- prevent container tabs merge -->

The syntax is identical to [PHP Markdown Extra
tables](https://michelf.ca/projects/php-markdown/extra/#table). The
beginning and ending pipe characters are optional, but pipes are
required between all columns. The colons indicate column alignment as
shown. The header cannot be omitted. To simulate a headerless table,
include a header with blank cells.

Since the pipes indicate column boundaries, columns need not be
vertically aligned, as they are in the above example. So, this is a
perfectly legal (though ugly) pipe table:

=== "Markdown"

        fruit| price
        -----|-----:
        apple|2.05
        pear|1.37
        orange|3.09

=== "Python"

        Pandoc(Meta({}), [Table(('', [], []), Caption(None, []), [(AlignDefault(), ColWidthDefault()), (AlignRight(), ColWidthDefault())], TableHead(('', [], []), [Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('fruit')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('price')])])])]), [TableBody(('', [], []), RowHeadColumns(0), [], [Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('apple')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('2.05')])])]), Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('pear')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('1.37')])])]), Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('orange')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('3.09')])])])])], TableFoot(('', [], []), []))])

<!-- prevent container tabs merge -->

The cells of pipe tables cannot contain block elements like paragraphs
and lists, and cannot span multiple lines. If a pipe table contains a
row whose Markdown content is wider than the column width (see
`--columns`), then the table will take up the full text width and the
cell contents will wrap, with the relative cell widths determined by the
number of dashes in the line separating the table header from the table
body. (For example `---|-` would make the first column 3/4 and the
second column 1/4 of the full text width.) On the other hand, if no
lines are wider than column width, then cell contents will not be
wrapped, and the cells will be sized to their contents.

Note: pandoc also recognizes pipe tables of the following form, as can
be produced by Emacs' orgtbl-mode:

=== "Markdown"

        | One | Two   |
        |-----+-------|
        | my  | table |
        | is  | nice  |

=== "Python"

        Pandoc(Meta({}), [Table(('', [], []), Caption(None, []), [(AlignDefault(), ColWidthDefault()), (AlignDefault(), ColWidthDefault())], TableHead(('', [], []), [Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('One')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('Two')])])])]), [TableBody(('', [], []), RowHeadColumns(0), [], [Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('my')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('table')])])]), Row(('', [], []), [Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('is')])]), Cell(('', [], []), AlignDefault(), RowSpan(1), ColSpan(1), [Plain([Str('nice')])])])])], TableFoot(('', [], []), []))])

<!-- prevent container tabs merge -->

The difference is that `+` is used instead of `|`. Other orgtbl features
are not supported. In particular, to get non-default column alignment,
you'll need to add colons as above.

## Metadata blocks

#### Extension: `pandoc_title_block`

If the file begins with a title block

=== "Markdown"

        % title
        % author(s) (separated by semicolons)
        % date

=== "Python"

        Pandoc(Meta({'author': MetaList([MetaInlines([Str('author(s)'), Space(), Str('(separated'), Space(), Str('by'), Space(), Str('semicolons)')])]), 'date': MetaInlines([Str('date')]), 'title': MetaInlines([Str('title')])}), [])

<!-- prevent container tabs merge -->

it will be parsed as bibliographic information, not regular text. (It
will be used, for example, in the title of standalone LaTeX or HTML
output.) The block may contain just a title, a title and an author, or
all three elements. If you want to include an author but no title, or a
title and a date but no author, you need a blank line:

=== "Markdown"

        %
        % Author

=== "Python"

        Pandoc(Meta({'author': MetaList([MetaInlines([Str('Author')])])}), [])

<!-- prevent container tabs merge -->

=== "Markdown"

        % My title
        %
        % June 15, 2006

=== "Python"

        Pandoc(Meta({'author': MetaList([MetaInlines([])]), 'date': MetaInlines([Str('June'), Space(), Str('15,'), Space(), Str('2006')]), 'title': MetaInlines([Str('My'), Space(), Str('title')])}), [])

<!-- prevent container tabs merge -->

The title may occupy multiple lines, but continuation lines must begin
with leading space, thus:

=== "Markdown"

        % My title
          on multiple lines

=== "Python"

        Pandoc(Meta({'title': MetaInlines([Str('My'), Space(), Str('title'), SoftBreak(), Str('on'), Space(), Str('multiple'), Space(), Str('lines')])}), [])

<!-- prevent container tabs merge -->

If a document has multiple authors, the authors may be put on separate
lines with leading space, or separated by semicolons, or both. So, all
of the following are equivalent:

=== "Markdown"

        % Author One
          Author Two

=== "Python"

        Pandoc(Meta({'title': MetaInlines([Str('Author'), Space(), Str('One'), SoftBreak(), Str('Author'), Space(), Str('Two')])}), [])

<!-- prevent container tabs merge -->

=== "Markdown"

        % Author One; Author Two

=== "Python"

        Pandoc(Meta({'title': MetaInlines([Str('Author'), Space(), Str('One;'), Space(), Str('Author'), Space(), Str('Two')])}), [])

<!-- prevent container tabs merge -->

=== "Markdown"

        % Author One;
          Author Two

=== "Python"

        Pandoc(Meta({'title': MetaInlines([Str('Author'), Space(), Str('One;'), SoftBreak(), Str('Author'), Space(), Str('Two')])}), [])

<!-- prevent container tabs merge -->

The date must fit on one line.

All three metadata fields may contain standard inline formatting
(italics, links, footnotes, etc.).

Title blocks will always be parsed, but they will affect the output only
when the `--standalone` (`-s`) option is chosen. In HTML output, titles
will appear twice: once in the document head -- this is the title that
will appear at the top of the window in a browser -- and once at the
beginning of the document body. The title in the document head can have
an optional prefix attached (`--title-prefix` or `-T` option). The title
in the body appears as an H1 element with class "title", so it can be
suppressed or reformatted with CSS. If a title prefix is specified with
`-T` and no title block appears in the document, the title prefix will
be used by itself as the HTML title.

The man page writer extracts a title, man page section number, and other
header and footer information from the title line. The title is assumed
to be the first word on the title line, which may optionally end with a
(single-digit) section number in parentheses. (There should be no space
between the title and the parentheses.) Anything after this is assumed
to be additional footer and header text. A single pipe character (`|`)
should be used to separate the footer text from the header text. Thus,

=== "Markdown"

        % PANDOC(1)

=== "Python"

        Pandoc(Meta({'title': MetaInlines([Str('PANDOC(1)')])}), [])

<!-- prevent container tabs merge -->

will yield a man page with the title `PANDOC` and section 1.

=== "Markdown"

        % PANDOC(1) Pandoc User Manuals

=== "Python"

        Pandoc(Meta({'title': MetaInlines([Str('PANDOC(1)'), Space(), Str('Pandoc'), Space(), Str('User'), Space(), Str('Manuals')])}), [])

<!-- prevent container tabs merge -->

will also have "Pandoc User Manuals" in the footer.

=== "Markdown"

        % PANDOC(1) Pandoc User Manuals | Version 4.0

=== "Python"

        Pandoc(Meta({'title': MetaInlines([Str('PANDOC(1)'), Space(), Str('Pandoc'), Space(), Str('User'), Space(), Str('Manuals'), Space(), Str('|'), Space(), Str('Version'), Space(), Str('4.0')])}), [])

<!-- prevent container tabs merge -->

will also have "Version 4.0" in the header.

#### Extension: `yaml_metadata_block`

A [YAML](https://yaml.org/spec/1.2/spec.html "YAML v1.2 Spec") metadata
block is a valid YAML object, delimited by a line of three hyphens
(`---`) at the top and a line of three hyphens (`---`) or three dots
(`...`) at the bottom. A YAML metadata block may occur anywhere in the
document, but if it is not at the beginning, it must be preceded by a
blank line. (Note that, because of the way pandoc concatenates input
files when several are provided, you may also keep the metadata in a
separate YAML file and pass it to pandoc as an argument, along with your
Markdown files:

=== "Markdown"

        pandoc chap1.md chap2.md chap3.md metadata.yaml -s -o book.html

=== "Python"

        Pandoc(Meta({}), [Para([Str('pandoc'), Space(), Str('chap1.md'), Space(), Str('chap2.md'), Space(), Str('chap3.md'), Space(), Str('metadata.yaml'), Space(), Str('-s'), Space(), Str('-o'), Space(), Str('book.html')])])

<!-- prevent container tabs merge -->

Just be sure that the YAML file begins with `---` and ends with `---` or
`...`.) Alternatively, you can use the `--metadata-file` option. Using
that approach however, you cannot reference content (like footnotes)
from the main markdown input document.

Metadata will be taken from the fields of the YAML object and added to
any existing document metadata. Metadata can contain lists and objects
(nested arbitrarily), but all string scalars will be interpreted as
Markdown. Fields with names ending in an underscore will be ignored by
pandoc. (They may be given a role by external processors.) Field names
must not be interpretable as YAML numbers or boolean values (so, for
example, `yes`, `True`, and `15` cannot be used as field names).

A document may contain multiple metadata blocks. If two metadata blocks
attempt to set the same field, the value from the second block will be
taken.

Each metadata block is handled internally as an independent YAML
document. This means, for example, that any YAML anchors defined in a
block cannot be referenced in another block.

When pandoc is used with `-t markdown` to create a Markdown document, a
YAML metadata block will be produced only if the `-s/--standalone`
option is used. All of the metadata will appear in a single block at the
beginning of the document.

Note that [YAML](https://yaml.org/spec/1.2/spec.html "YAML v1.2 Spec")
escaping rules must be followed. Thus, for example, if a title contains
a colon, it must be quoted, and if it contains a backslash escape, then
it must be ensured that it is not treated as a [YAML escape
sequence](https://yaml.org/spec/1.2/spec.html#id2776092). The pipe
character (`|`) can be used to begin an indented block that will be
interpreted literally, without need for escaping. This form is necessary
when the field contains blank lines or block-level formatting:

=== "Markdown"

        ---
        title:  'This is the title: it contains a colon'
        author:
        - Author One
        - Author Two
        keywords: [nothing, nothingness]
        abstract: |
          This is the abstract.
        
          It consists of two paragraphs.
        ...

=== "Python"

        Pandoc(Meta({'abstract': MetaBlocks([Para([Str('This'), Space(), Str('is'), Space(), Str('the'), Space(), Str('abstract.')]), Para([Str('It'), Space(), Str('consists'), Space(), Str('of'), Space(), Str('two'), Space(), Str('paragraphs.')])]), 'author': MetaList([MetaInlines([Str('Author'), Space(), Str('One')]), MetaInlines([Str('Author'), Space(), Str('Two')])]), 'keywords': MetaList([MetaInlines([Str('nothing')]), MetaInlines([Str('nothingness')])]), 'title': MetaInlines([Str('This'), Space(), Str('is'), Space(), Str('the'), Space(), Str('title:'), Space(), Str('it'), Space(), Str('contains'), Space(), Str('a'), Space(), Str('colon')])}), [])

<!-- prevent container tabs merge -->

The literal block after the `|` must be indented relative to the line
containing the `|`. If it is not, the YAML will be invalid and pandoc
will not interpret it as metadata. For an overview of the complex rules
governing YAML, see the [Wikipedia entry on YAML
syntax](https://en.m.wikipedia.org/wiki/YAML#Syntax).

Template variables will be set automatically from the metadata. Thus,
for example, in writing HTML, the variable `abstract` will be set to the
HTML equivalent of the Markdown in the `abstract` field:

=== "Markdown"

        <p>This is the abstract.</p>
        <p>It consists of two paragraphs.</p>

=== "Python"

        Pandoc(Meta({}), [RawBlock(Format('html'), '<p>'), Plain([Str('This'), Space(), Str('is'), Space(), Str('the'), Space(), Str('abstract.')]), RawBlock(Format('html'), '</p>'), RawBlock(Format('html'), '<p>'), Plain([Str('It'), Space(), Str('consists'), Space(), Str('of'), Space(), Str('two'), Space(), Str('paragraphs.')]), RawBlock(Format('html'), '</p>')])

<!-- prevent container tabs merge -->

Variables can contain arbitrary YAML structures, but the template must
match this structure. The `author` variable in the default templates
expects a simple list or string, but can be changed to support more
complicated structures. The following combination, for example, would
add an affiliation to the author if one is given:

=== "Markdown"

        ---
        title: The document title
        author:
        - name: Author One
          affiliation: University of Somewhere
        - name: Author Two
          affiliation: University of Nowhere
        ...

=== "Python"

        Pandoc(Meta({'author': MetaList([MetaMap({'affiliation': MetaInlines([Str('University'), Space(), Str('of'), Space(), Str('Somewhere')]), 'name': MetaInlines([Str('Author'), Space(), Str('One')])}), MetaMap({'affiliation': MetaInlines([Str('University'), Space(), Str('of'), Space(), Str('Nowhere')]), 'name': MetaInlines([Str('Author'), Space(), Str('Two')])})]), 'title': MetaInlines([Str('The'), Space(), Str('document'), Space(), Str('title')])}), [])

<!-- prevent container tabs merge -->

To use the structured authors in the example above, you would need a
custom template:

=== "Markdown"

        $for(author)$
        $if(author.name)$
        $author.name$$if(author.affiliation)$ ($author.affiliation$)$endif$
        $else$
        $author$
        $endif$
        $endfor$

=== "Python"

        Pandoc(Meta({}), [Para([Math(InlineMath(), 'for(author)'), SoftBreak(), Math(InlineMath(), 'if(author.name)'), SoftBreak(), Math(InlineMath(), 'author.name'), Math(InlineMath(), 'if(author.affiliation)'), Space(), Str('('), Math(InlineMath(), 'author.affiliation'), Str(')'), Math(InlineMath(), 'endif'), SoftBreak(), Math(InlineMath(), 'else'), SoftBreak(), Math(InlineMath(), 'author'), SoftBreak(), Math(InlineMath(), 'endif'), SoftBreak(), Math(InlineMath(), 'endfor')])])

<!-- prevent container tabs merge -->

Raw content to include in the document's header may be specified using
`header-includes`; however, it is important to mark up this content as
raw code for a particular output format, using the [`raw_attribute`
extension](#extension-raw_attribute)), or it will be interpreted as
markdown. For example:

=== "Markdown"

        header-includes:
        - |
          ```{=latex}
          \let\oldsection\section
          \renewcommand{\section}[1]{\clearpage\oldsection{#1}}
          ```

=== "Python"

        Pandoc(Meta({}), [Para([Str('header-includes:'), SoftBreak(), Str('-'), Space(), Str('|'), SoftBreak(), Code(('', [], []), '{=latex}   \\let\\oldsection\\section   \\renewcommand{\\section}[1]{\\clearpage\\oldsection{#1}}')])])

<!-- prevent container tabs merge -->

Note: the `yaml_metadata_block` extension works with `commonmark` as
well as `markdown` (and it is enabled by default in `gfm` and
`commonmark_x`). However, in these formats the following restrictions
apply:

-   The YAML metadata block must occur at the beginning of the document
    (and there can be only one). If multiple files are given as
    arguments to pandoc, only the first can be a YAML metadata block.

-   The leaf nodes of the YAML structure are parsed in isolation from
    each other and from the rest of the document. So, for example, you
    can't use a reference link in these contexts if the link definition
    is somewhere else in the document.

## Backslash escapes

#### Extension: `all_symbols_escapable`

Except inside a code block or inline code, any punctuation or space
character preceded by a backslash will be treated literally, even if it
would normally indicate formatting. Thus, for example, if one writes

=== "Markdown"

        *\*hello\**

=== "Python"

        Pandoc(Meta({}), [Para([Emph([Str('*hello*')])])])

<!-- prevent container tabs merge -->

one will get

=== "Markdown"

        <em>*hello*</em>

=== "Python"

        Pandoc(Meta({}), [Para([RawInline(Format('html'), '<em>'), Emph([Str('hello')]), RawInline(Format('html'), '</em>')])])

<!-- prevent container tabs merge -->

instead of

=== "Markdown"

        <strong>hello</strong>

=== "Python"

        Pandoc(Meta({}), [Para([RawInline(Format('html'), '<strong>'), Str('hello'), RawInline(Format('html'), '</strong>')])])

<!-- prevent container tabs merge -->

This rule is easier to remember than standard Markdown's rule, which
allows only the following characters to be backslash-escaped:

=== "Markdown"

        \`*_{}[]()>#+-.!

=== "Python"

        Pandoc(Meta({}), [Para([Str('`*_{}'), Link(('', [], []), [], ('', '')), Str('>#+-.!')])])

<!-- prevent container tabs merge -->

(However, if the `markdown_strict` format is used, the standard Markdown
rule will be used.)

A backslash-escaped space is parsed as a nonbreaking space. In TeX
output, it will appear as `~`. In HTML and XML output, it will appear as
a literal unicode nonbreaking space character (note that it will thus
actually look "invisible" in the generated HTML source; you can still
use the `--ascii` command-line option to make it appear as an explicit
entity).

A backslash-escaped newline (i.e. a backslash occurring at the end of a
line) is parsed as a hard line break. It will appear in TeX output as
`\\` and in HTML as `<br />`. This is a nice alternative to Markdown's
"invisible" way of indicating hard line breaks using two trailing spaces
on a line.

Backslash escapes do not work in verbatim contexts.

## Inline formatting

### Emphasis

To *emphasize* some text, surround it with `*`s or `_`, like this:

=== "Markdown"

        This text is _emphasized with underscores_, and this
        is *emphasized with asterisks*.

=== "Python"

        Pandoc(Meta({}), [Para([Str('This'), Space(), Str('text'), Space(), Str('is'), Space(), Emph([Str('emphasized'), Space(), Str('with'), Space(), Str('underscores')]), Str(','), Space(), Str('and'), Space(), Str('this'), SoftBreak(), Str('is'), Space(), Emph([Str('emphasized'), Space(), Str('with'), Space(), Str('asterisks')]), Str('.')])])

<!-- prevent container tabs merge -->

Double `*` or `_` produces **strong emphasis**:

=== "Markdown"

        This is **strong emphasis** and __with underscores__.

=== "Python"

        Pandoc(Meta({}), [Para([Str('This'), Space(), Str('is'), Space(), Strong([Str('strong'), Space(), Str('emphasis')]), Space(), Str('and'), Space(), Strong([Str('with'), Space(), Str('underscores')]), Str('.')])])

<!-- prevent container tabs merge -->

A `*` or `_` character surrounded by spaces, or backslash-escaped, will
not trigger emphasis:

=== "Markdown"

        This is * not emphasized *, and \*neither is this\*.

=== "Python"

        Pandoc(Meta({}), [Para([Str('This'), Space(), Str('is'), Space(), Str('*'), Space(), Str('not'), Space(), Str('emphasized'), Space(), Str('*,'), Space(), Str('and'), Space(), Str('*neither'), Space(), Str('is'), Space(), Str('this*.')])])

<!-- prevent container tabs merge -->

#### Extension: `intraword_underscores`

Because `_` is sometimes used inside words and identifiers, pandoc does
not interpret a `_` surrounded by alphanumeric characters as an emphasis
marker. If you want to emphasize just part of a word, use `*`:

=== "Markdown"

        feas*ible*, not feas*able*.

=== "Python"

        Pandoc(Meta({}), [Para([Str('feas'), Emph([Str('ible')]), Str(','), Space(), Str('not'), Space(), Str('feas'), Emph([Str('able')]), Str('.')])])

<!-- prevent container tabs merge -->

### Strikeout

#### Extension: `strikeout`

To strikeout a section of text with a horizontal line, begin and end it
with `~~`. Thus, for example,

=== "Markdown"

        This ~~is deleted text.~~

=== "Python"

        Pandoc(Meta({}), [Para([Str('This'), Space(), Strikeout([Str('is'), Space(), Str('deleted'), Space(), Str('text.')])])])

<!-- prevent container tabs merge -->

### Superscripts and subscripts

#### Extension: `superscript`, `subscript`

Superscripts may be written by surrounding the superscripted text by `^`
characters; subscripts may be written by surrounding the subscripted
text by `~` characters. Thus, for example,

=== "Markdown"

        H~2~O is a liquid.  2^10^ is 1024.

=== "Python"

        Pandoc(Meta({}), [Para([Str('H'), Subscript([Str('2')]), Str('O'), Space(), Str('is'), Space(), Str('a'), Space(), Str('liquid.'), Space(), Str('2'), Superscript([Str('10')]), Space(), Str('is'), Space(), Str('1024.')])])

<!-- prevent container tabs merge -->

The text between `^...^` or `~...~` may not contain spaces or newlines.
If the superscripted or subscripted text contains spaces, these spaces
must be escaped with backslashes. (This is to prevent accidental
superscripting and subscripting through the ordinary use of `~` and `^`,
and also bad interactions with footnotes.) Thus, if you want the letter
P with 'a cat' in subscripts, use `P~a\ cat~`, not `P~a cat~`.

### Verbatim

To make a short span of text verbatim, put it inside backticks:

=== "Markdown"

        What is the difference between `>>=` and `>>`?

=== "Python"

        Pandoc(Meta({}), [Para([Str('What'), Space(), Str('is'), Space(), Str('the'), Space(), Str('difference'), Space(), Str('between'), Space(), Code(('', [], []), '>>='), Space(), Str('and'), Space(), Code(('', [], []), '>>'), Str('?')])])

<!-- prevent container tabs merge -->

If the verbatim text includes a backtick, use double backticks:

=== "Markdown"

        Here is a literal backtick `` ` ``.

=== "Python"

        Pandoc(Meta({}), [Para([Str('Here'), Space(), Str('is'), Space(), Str('a'), Space(), Str('literal'), Space(), Str('backtick'), Space(), Code(('', [], []), '`'), Str('.')])])

<!-- prevent container tabs merge -->

(The spaces after the opening backticks and before the closing backticks
will be ignored.)

The general rule is that a verbatim span starts with a string of
consecutive backticks (optionally followed by a space) and ends with a
string of the same number of backticks (optionally preceded by a space).

Note that backslash-escapes (and other Markdown constructs) do not work
in verbatim contexts:

=== "Markdown"

        This is a backslash followed by an asterisk: `\*`.

=== "Python"

        Pandoc(Meta({}), [Para([Str('This'), Space(), Str('is'), Space(), Str('a'), Space(), Str('backslash'), Space(), Str('followed'), Space(), Str('by'), Space(), Str('an'), Space(), Str('asterisk:'), Space(), Code(('', [], []), '\\*'), Str('.')])])

<!-- prevent container tabs merge -->

#### Extension: `inline_code_attributes`

Attributes can be attached to verbatim text, just as with [fenced code
blocks](#fenced-code-blocks):

=== "Markdown"

        `<$>`{.haskell}

=== "Python"

        Pandoc(Meta({}), [Para([Code(('', ['haskell'], []), '<$>')])])

<!-- prevent container tabs merge -->

### Underline

To underline text, use the `underline` class:

=== "Markdown"

        [Underline]{.underline}

=== "Python"

        Pandoc(Meta({}), [Para([Underline([Str('Underline')])])])

<!-- prevent container tabs merge -->

Or, without the `bracketed_spans` extension (but with `native_spans`):

=== "Markdown"

        <span class="underline">Underline</span>

=== "Python"

        Pandoc(Meta({}), [Para([Underline([Str('Underline')])])])

<!-- prevent container tabs merge -->

This will work in all output formats that support underline.

### Small caps

To write small caps, use the `smallcaps` class:

=== "Markdown"

        [Small caps]{.smallcaps}

=== "Python"

        Pandoc(Meta({}), [Para([SmallCaps([Str('Small'), Space(), Str('caps')])])])

<!-- prevent container tabs merge -->

Or, without the `bracketed_spans` extension:

=== "Markdown"

        <span class="smallcaps">Small caps</span>

=== "Python"

        Pandoc(Meta({}), [Para([SmallCaps([Str('Small'), Space(), Str('caps')])])])

<!-- prevent container tabs merge -->

For compatibility with other Markdown flavors, CSS is also supported:

=== "Markdown"

        <span style="font-variant:small-caps;">Small caps</span>

=== "Python"

        Pandoc(Meta({}), [Para([SmallCaps([Str('Small'), Space(), Str('caps')])])])

<!-- prevent container tabs merge -->

This will work in all output formats that support small caps.

## Math

#### Extension: `tex_math_dollars`

Anything between two `$` characters will be treated as TeX math. The
opening `$` must have a non-space character immediately to its right,
while the closing `$` must have a non-space character immediately to its
left, and must not be followed immediately by a digit. Thus,
`$20,000 and $30,000` won't parse as math. If for some reason you need
to enclose text in literal `$` characters, backslash-escape them and
they won't be treated as math delimiters.

For display math, use `$$` delimiters. (In this case, the delimiters may
be separated from the formula by whitespace. However, there can be no
blank lines betwen the opening and closing `$$` delimiters.)

TeX math will be printed in all output formats. How it is rendered
depends on the output format:

-   **LaTeX.**
    It will appear verbatim surrounded by `\(...\)` (for inline math) or
    `\[...\]` (for display math).
-   **Markdown, Emacs Org mode, ConTeXt, ZimWiki.**
    It will appear verbatim surrounded by `$...$` (for inline math) or
    `$$...$$` (for display math).
-   **XWiki.**
    It will appear verbatim surrounded by `{{formula}}..{{/formula}}`.
-   **reStructuredText.**
    It will be rendered using an [interpreted text role
    `:math:`](https://docutils.sourceforge.io/docs/ref/rst/roles.html#math).
-   **AsciiDoc.**
    For AsciiDoc output format (`-t asciidoc`) it will appear verbatim
    surrounded by `latexmath:[$...$]` (for inline math) or
    `[latexmath]++++\[...\]+++` (for display math). For AsciiDoctor
    output format (`-t asciidoctor`) the LaTex delimiters (`$..$` and
    `\[..\]`) are omitted.
-   **Texinfo.**
    It will be rendered inside a `@math` command.
-   **roff man, Jira markup.**
    It will be rendered verbatim without `$`'s.
-   **MediaWiki, DokuWiki.**
    It will be rendered inside `<math>` tags.
-   **Textile.**
    It will be rendered inside `<span class="math">` tags.
-   **RTF, OpenDocument.**
    It will be rendered, if possible, using Unicode characters, and will
    otherwise appear verbatim.
-   **ODT.**
    It will be rendered, if possible, using MathML.
-   **DocBook.**
    If the `--mathml` flag is used, it will be rendered using MathML in
    an `inlineequation` or `informalequation` tag. Otherwise it will be
    rendered, if possible, using Unicode characters.
-   **Docx.**
    It will be rendered using OMML math markup.
-   **FictionBook2.**
    If the `--webtex` option is used, formulas are rendered as images
    using CodeCogs or other compatible web service, downloaded and
    embedded in the e-book. Otherwise, they will appear verbatim.
-   **HTML, Slidy, DZSlides, S5, EPUB.**
    The way math is rendered in HTML will depend on the command-line
    options selected. Therefore see [Math rendering in
    HTML](#math-rendering-in-html) above.

## Raw HTML

#### Extension: `raw_html`

Markdown allows you to insert raw HTML (or DocBook) anywhere in a
document (except verbatim contexts, where `<`, `>`, and `&` are
interpreted literally). (Technically this is not an extension, since
standard Markdown allows it, but it has been made an extension so that
it can be disabled if desired.)

The raw HTML is passed through unchanged in HTML, S5, Slidy, Slideous,
DZSlides, EPUB, Markdown, CommonMark, Emacs Org mode, and Textile
output, and suppressed in other formats.

For a more explicit way of including raw HTML in a Markdown document,
see the [`raw_attribute` extension](#extension-raw_attribute).

In the CommonMark format, if `raw_html` is enabled, superscripts,
subscripts, strikeouts and small capitals will be represented as HTML.
Otherwise, plain-text fallbacks will be used. Note that even if
`raw_html` is disabled, tables will be rendered with HTML syntax if they
cannot use pipe syntax.

#### Extension: `markdown_in_html_blocks`

Standard Markdown allows you to include HTML "blocks": blocks of HTML
between balanced tags that are separated from the surrounding text with
blank lines, and start and end at the left margin. Within these blocks,
everything is interpreted as HTML, not Markdown; so (for example), `*`
does not signify emphasis.

Pandoc behaves this way when the `markdown_strict` format is used; but
by default, pandoc interprets material between HTML block tags as
Markdown. Thus, for example, pandoc will turn

=== "Markdown"

        <table>
        <tr>
        <td>*one*</td>
        <td>[a link](https://google.com)</td>
        </tr>
        </table>

=== "Python"

        Pandoc(Meta({}), [RawBlock(Format('html'), '<table>'), RawBlock(Format('html'), '<tr>'), RawBlock(Format('html'), '<td>'), Plain([Emph([Str('one')])]), RawBlock(Format('html'), '</td>'), RawBlock(Format('html'), '<td>'), Plain([Link(('', [], []), [Str('a'), Space(), Str('link')], ('https://google.com', ''))]), RawBlock(Format('html'), '</td>'), RawBlock(Format('html'), '</tr>'), RawBlock(Format('html'), '</table>')])

<!-- prevent container tabs merge -->

into

=== "Markdown"

        <table>
        <tr>
        <td><em>one</em></td>
        <td><a href="https://google.com">a link</a></td>
        </tr>
        </table>

=== "Python"

        Pandoc(Meta({}), [RawBlock(Format('html'), '<table>'), RawBlock(Format('html'), '<tr>'), RawBlock(Format('html'), '<td>'), Plain([RawInline(Format('html'), '<em>'), Str('one'), RawInline(Format('html'), '</em>')]), RawBlock(Format('html'), '</td>'), RawBlock(Format('html'), '<td>'), Plain([RawInline(Format('html'), '<a href="https://google.com">'), Str('a'), Space(), Str('link'), RawInline(Format('html'), '</a>')]), RawBlock(Format('html'), '</td>'), RawBlock(Format('html'), '</tr>'), RawBlock(Format('html'), '</table>')])

<!-- prevent container tabs merge -->

whereas `Markdown.pl` will preserve it as is.

There is one exception to this rule: text between `<script>`, `<style>`,
and `<textarea>` tags is not interpreted as Markdown.

This departure from standard Markdown should make it easier to mix
Markdown with HTML block elements. For example, one can surround a block
of Markdown text with `<div>` tags without preventing it from being
interpreted as Markdown.

#### Extension: `native_divs`

Use native pandoc `Div` blocks for content inside `<div>` tags. For the
most part this should give the same output as `markdown_in_html_blocks`,
but it makes it easier to write pandoc filters to manipulate groups of
blocks.

#### Extension: `native_spans`

Use native pandoc `Span` blocks for content inside `<span>` tags. For
the most part this should give the same output as `raw_html`, but it
makes it easier to write pandoc filters to manipulate groups of inlines.

#### Extension: `raw_tex`

In addition to raw HTML, pandoc allows raw LaTeX, TeX, and ConTeXt to be
included in a document. Inline TeX commands will be preserved and passed
unchanged to the LaTeX and ConTeXt writers. Thus, for example, you can
use LaTeX to include BibTeX citations:

=== "Markdown"

        This result was proved in \cite{jones.1967}.

=== "Python"

        Pandoc(Meta({}), [Para([Str('This'), Space(), Str('result'), Space(), Str('was'), Space(), Str('proved'), Space(), Str('in'), Space(), RawInline(Format('tex'), '\\cite{jones.1967}'), Str('.')])])

<!-- prevent container tabs merge -->

Note that in LaTeX environments, like

=== "Markdown"

        \begin{tabular}{|l|l|}\hline
        Age & Frequency \\ \hline
        18--25  & 15 \\
        26--35  & 33 \\
        36--45  & 22 \\ \hline
        \end{tabular}

=== "Python"

        Pandoc(Meta({}), [RawBlock(Format('tex'), '\\begin{tabular}{|l|l|}\\hline\nAge & Frequency \\\\ \\hline\n18--25  & 15 \\\\\n26--35  & 33 \\\\\n36--45  & 22 \\\\ \\hline\n\\end{tabular}')])

<!-- prevent container tabs merge -->

the material between the begin and end tags will be interpreted as raw
LaTeX, not as Markdown.

For a more explicit and flexible way of including raw TeX in a Markdown
document, see the [`raw_attribute` extension](#extension-raw_attribute).

Inline LaTeX is ignored in output formats other than Markdown, LaTeX,
Emacs Org mode, and ConTeXt.

### Generic raw attribute

#### Extension: `raw_attribute`

Inline spans and fenced code blocks with a special kind of attribute
will be parsed as raw content with the designated format. For example,
the following produces a raw roff `ms` block:

=== "Markdown"

        ```{=ms}
        .MYMACRO
        blah blah
        ```

=== "Python"

        Pandoc(Meta({}), [RawBlock(Format('ms'), '.MYMACRO\nblah blah')])

<!-- prevent container tabs merge -->

And the following produces a raw `html` inline element:

=== "Markdown"

        This is `<a>html</a>`{=html}

=== "Python"

        Pandoc(Meta({}), [Para([Str('This'), Space(), Str('is'), Space(), RawInline(Format('html'), '<a>html</a>')])])

<!-- prevent container tabs merge -->

This can be useful to insert raw xml into `docx` documents, e.g. a
pagebreak:

=== "Markdown"

        ```{=openxml}
        <w:p>
          <w:r>
            <w:br w:type="page"/>
          </w:r>
        </w:p>
        ```

=== "Python"

        Pandoc(Meta({}), [RawBlock(Format('openxml'), '<w:p>\n  <w:r>\n    <w:br w:type="page"/>\n  </w:r>\n</w:p>')])

<!-- prevent container tabs merge -->

The format name should match the target format name (see `-t/--to`,
above, for a list, or use `pandoc --list-output-formats`). Use `openxml`
for `docx` output, `opendocument` for `odt` output, `html5` for `epub3`
output, `html4` for `epub2` output, and `latex`, `beamer`, `ms`, or
`html5` for `pdf` output (depending on what you use for `--pdf-engine`).

This extension presupposes that the relevant kind of inline code or
fenced code block is enabled. Thus, for example, to use a raw attribute
with a backtick code block, `backtick_code_blocks` must be enabled.

The raw attribute cannot be combined with regular attributes.

## LaTeX macros

#### Extension: `latex_macros`

When this extension is enabled, pandoc will parse LaTeX macro
definitions and apply the resulting macros to all LaTeX math and raw
LaTeX. So, for example, the following will work in all output formats,
not just LaTeX:

=== "Markdown"

        \newcommand{\tuple}[1]{\langle #1 \rangle}
        
        $\tuple{a, b, c}$

=== "Python"

        Pandoc(Meta({}), [RawBlock(Format('tex'), '\\newcommand{\\tuple}[1]{\\langle #1 \\rangle}'), Para([Math(InlineMath(), '\\langle a, b, c \\rangle')])])

<!-- prevent container tabs merge -->

Note that LaTeX macros will not be applied if they occur inside a raw
span or block marked with the [`raw_attribute`
extension](#extension-raw_attribute).

When `latex_macros` is disabled, the raw LaTeX and math will not have
macros applied. This is usually a better approach when you are targeting
LaTeX or PDF.

Macro definitions in LaTeX will be passed through as raw LaTeX only if
`latex_macros` is not enabled. Macro definitions in Markdown source (or
other formats allowing `raw_tex`) will be passed through regardless of
whether `latex_macros` is enabled.

## Links

Markdown allows links to be specified in several ways.

### Automatic links

If you enclose a URL or email address in pointy brackets, it will become
a link:

=== "Markdown"

        <https://google.com>
        <sam@green.eggs.ham>

=== "Python"

        Pandoc(Meta({}), [Para([Link(('', ['uri'], []), [Str('https://google.com')], ('https://google.com', '')), SoftBreak(), Link(('', ['email'], []), [Str('sam@green.eggs.ham')], ('mailto:sam@green.eggs.ham', ''))])])

<!-- prevent container tabs merge -->

### Inline links

An inline link consists of the link text in square brackets, followed by
the URL in parentheses. (Optionally, the URL can be followed by a link
title, in quotes.)

=== "Markdown"

        This is an [inline link](/url), and here's [one with
        a title](https://fsf.org "click here for a good time!").

=== "Python"

        Pandoc(Meta({}), [Para([Str('This'), Space(), Str('is'), Space(), Str('an'), Space(), Link(('', [], []), [Str('inline'), Space(), Str('link')], ('/url', '')), Str(','), Space(), Str('and'), Space(), Str('here’s'), Space(), Link(('', [], []), [Str('one'), Space(), Str('with'), SoftBreak(), Str('a'), Space(), Str('title')], ('https://fsf.org', 'click here for a good time!')), Str('.')])])

<!-- prevent container tabs merge -->

There can be no space between the bracketed part and the parenthesized
part. The link text can contain formatting (such as emphasis), but the
title cannot.

Email addresses in inline links are not autodetected, so they have to be
prefixed with `mailto`:

=== "Markdown"

        [Write me!](mailto:sam@green.eggs.ham)

=== "Python"

        Pandoc(Meta({}), [Para([Link(('', [], []), [Str('Write'), Space(), Str('me!')], ('mailto:sam@green.eggs.ham', ''))])])

<!-- prevent container tabs merge -->

### Reference links

An *explicit* reference link has two parts, the link itself and the link
definition, which may occur elsewhere in the document (either before or
after the link).

The link consists of link text in square brackets, followed by a label
in square brackets. (There cannot be space between the two unless the
`spaced_reference_links` extension is enabled.) The link definition
consists of the bracketed label, followed by a colon and a space,
followed by the URL, and optionally (after a space) a link title either
in quotes or in parentheses. The label must not be parseable as a
citation (assuming the `citations` extension is enabled): citations take
precedence over link labels.

Here are some examples:

=== "Markdown"

        [my label 1]: /foo/bar.html  "My title, optional"
        [my label 2]: /foo
        [my label 3]: https://fsf.org (The free software foundation)
        [my label 4]: /bar#special  'A title in single quotes'

=== "Python"

        Pandoc(Meta({}), [])

<!-- prevent container tabs merge -->

The URL may optionally be surrounded by angle brackets:

=== "Markdown"

        [my label 5]: <http://foo.bar.baz>

=== "Python"

        Pandoc(Meta({}), [])

<!-- prevent container tabs merge -->

The title may go on the next line:

=== "Markdown"

        [my label 3]: https://fsf.org
          "The free software foundation"

=== "Python"

        Pandoc(Meta({}), [])

<!-- prevent container tabs merge -->

Note that link labels are not case sensitive. So, this will work:

=== "Markdown"

        Here is [my link][FOO]
        
        [Foo]: /bar/baz

=== "Python"

        Pandoc(Meta({}), [Para([Str('Here'), Space(), Str('is'), Space(), Link(('', [], []), [Str('my'), Space(), Str('link')], ('/bar/baz', ''))])])

<!-- prevent container tabs merge -->

In an *implicit* reference link, the second pair of brackets is empty:

=== "Markdown"

        See [my website][].
        
        [my website]: http://foo.bar.baz

=== "Python"

        Pandoc(Meta({}), [Para([Str('See'), Space(), Link(('', [], []), [Str('my'), Space(), Str('website')], ('http://foo.bar.baz', '')), Str('.')])])

<!-- prevent container tabs merge -->

Note: In `Markdown.pl` and most other Markdown implementations,
reference link definitions cannot occur in nested constructions such as
list items or block quotes. Pandoc lifts this arbitrary seeming
restriction. So the following is fine in pandoc, though not in most
other implementations:

=== "Markdown"

        > My block [quote].
        >
        > [quote]: /foo

=== "Python"

        Pandoc(Meta({}), [BlockQuote([Para([Str('My'), Space(), Str('block'), Space(), Link(('', [], []), [Str('quote')], ('/foo', '')), Str('.')])])])

<!-- prevent container tabs merge -->

#### Extension: `shortcut_reference_links`

In a *shortcut* reference link, the second pair of brackets may be
omitted entirely:

=== "Markdown"

        See [my website].
        
        [my website]: http://foo.bar.baz

=== "Python"

        Pandoc(Meta({}), [Para([Str('See'), Space(), Link(('', [], []), [Str('my'), Space(), Str('website')], ('http://foo.bar.baz', '')), Str('.')])])

<!-- prevent container tabs merge -->

### Internal links

To link to another section of the same document, use the automatically
generated identifier (see [Heading identifiers](#heading-identifiers)).
For example:

=== "Markdown"

        See the [Introduction](#introduction).

=== "Python"

        Pandoc(Meta({}), [Para([Str('See'), Space(), Str('the'), Space(), Link(('', [], []), [Str('Introduction')], ('#introduction', '')), Str('.')])])

<!-- prevent container tabs merge -->

or

=== "Markdown"

        See the [Introduction].
        
        [Introduction]: #introduction

=== "Python"

        Pandoc(Meta({}), [Para([Str('See'), Space(), Str('the'), Space(), Link(('', [], []), [Str('Introduction')], ('#introduction', '')), Str('.')])])

<!-- prevent container tabs merge -->

Internal links are currently supported for HTML formats (including HTML
slide shows and EPUB), LaTeX, and ConTeXt.

## Images

A link immediately preceded by a `!` will be treated as an image. The
link text will be used as the image's alt text:

=== "Markdown"

        ![la lune](lalune.jpg "Voyage to the moon")
        
        ![movie reel]
        
        [movie reel]: movie.gif

=== "Python"

        Pandoc(Meta({}), [Para([Image(('', [], []), [Str('la'), Space(), Str('lune')], ('lalune.jpg', 'fig:Voyage to the moon'))]), Para([Image(('', [], []), [Str('movie'), Space(), Str('reel')], ('movie.gif', 'fig:'))])])

<!-- prevent container tabs merge -->

#### Extension: `implicit_figures`

An image with nonempty alt text, occurring by itself in a paragraph,
will be rendered as a figure with a caption. The image's alt text will
be used as the caption.

=== "Markdown"

        ![This is the caption](/url/of/image.png)

=== "Python"

        Pandoc(Meta({}), [Para([Image(('', [], []), [Str('This'), Space(), Str('is'), Space(), Str('the'), Space(), Str('caption')], ('/url/of/image.png', 'fig:'))])])

<!-- prevent container tabs merge -->

How this is rendered depends on the output format. Some output formats
(e.g. RTF) do not yet support figures. In those formats, you'll just get
an image in a paragraph by itself, with no caption.

If you just want a regular inline image, just make sure it is not the
only thing in the paragraph. One way to do this is to insert a
nonbreaking space after the image:

=== "Markdown"

        ![This image won't be a figure](/url/of/image.png)\

=== "Python"

        Pandoc(Meta({}), [Para([Image(('', [], []), [Str('This'), Space(), Str('image'), Space(), Str('won’t'), Space(), Str('be'), Space(), Str('a'), Space(), Str('figure')], ('/url/of/image.png', '')), LineBreak()])])

<!-- prevent container tabs merge -->

Note that in reveal.js slide shows, an image in a paragraph by itself
that has the `stretch` class will fill the screen, and the caption and
figure tags will be omitted.

#### Extension: `link_attributes`

Attributes can be set on links and images:

=== "Markdown"

        An inline ![image](foo.jpg){#id .class width=30 height=20px}
        and a reference ![image][ref] with attributes.
        
        [ref]: foo.jpg "optional title" {#id .class key=val key2="val 2"}

=== "Python"

        Pandoc(Meta({}), [Para([Str('An'), Space(), Str('inline'), Space(), Image(('id', ['class'], [('width', '30'), ('height', '20px')]), [Str('image')], ('foo.jpg', '')), SoftBreak(), Str('and'), Space(), Str('a'), Space(), Str('reference'), Space(), Image(('id', ['class'], [('key', 'val'), ('key2', 'val 2')]), [Str('image')], ('foo.jpg', 'optional title')), Space(), Str('with'), Space(), Str('attributes.')])])

<!-- prevent container tabs merge -->

(This syntax is compatible with [PHP Markdown
Extra](https://michelf.ca/projects/php-markdown/extra/) when only `#id`
and `.class` are used.)

For HTML and EPUB, all known HTML5 attributes except `width` and
`height` (but including `srcset` and `sizes`) are passed through as is.
Unknown attributes are passed through as custom attributes, with `data-`
prepended. The other writers ignore attributes that are not specifically
supported by their output format.

The `width` and `height` attributes on images are treated specially.
When used without a unit, the unit is assumed to be pixels. However, any
of the following unit identifiers can be used: `px`, `cm`, `mm`, `in`,
`inch` and `%`. There must not be any spaces between the number and the
unit. For example:

=== "Markdown"

        ![](file.jpg){ width=50% }

=== "Python"

        Pandoc(Meta({}), [Para([Image(('', [], [('width', '50%')]), [], ('file.jpg', ''))])])

<!-- prevent container tabs merge -->

-   Dimensions may be converted to a form that is compatible with the
    output format (for example, dimensions given in pixels will be
    converted to inches when converting HTML to LaTeX). Conversion
    between pixels and physical measurements is affected by the `--dpi`
    option (by default, 96 dpi is assumed, unless the image itself
    contains dpi information).
-   The `%` unit is generally relative to some available space. For
    example the above example will render to the following.
    -   HTML: `<img href="file.jpg" style="width: 50%;" />`
    -   LaTeX:
        `\includegraphics[width=0.5\textwidth,height=\textheight]{file.jpg}`
        (If you're using a custom template, you need to configure
        `graphicx` as in the default template.)
    -   ConTeXt: `\externalfigure[file.jpg][width=0.5\textwidth]`
-   Some output formats have a notion of a class
    ([ConTeXt](https://wiki.contextgarden.net/Using_Graphics#Multiple_Image_Settings))
    or a unique identifier (LaTeX `\caption`), or both (HTML).
-   When no `width` or `height` attributes are specified, the fallback
    is to look at the image resolution and the dpi metadata embedded in
    the image file.

## Divs and Spans

Using the `native_divs` and `native_spans` extensions (see
[above](#extension-native_divs)), HTML syntax can be used as part of
markdown to create native `Div` and `Span` elements in the pandoc AST
(as opposed to raw HTML). However, there is also nicer syntax available:

#### Extension: `fenced_divs`

Allow special fenced syntax for native `Div` blocks. A Div starts with a
fence containing at least three consecutive colons plus some attributes.
The attributes may optionally be followed by another string of
consecutive colons. The attribute syntax is exactly as in fenced code
blocks (see [Extension:
`fenced_code_attributes`](#extension-fenced_code_attributes)). As with
fenced code blocks, one can use either attributes in curly braces or a
single unbraced word, which will be treated as a class name. The Div
ends with another line containing a string of at least three consecutive
colons. The fenced Div should be separated by blank lines from preceding
and following blocks.

Example:

=== "Markdown"

        ::::: {#special .sidebar}
        Here is a paragraph.
        
        And another.
        :::::

=== "Python"

        Pandoc(Meta({}), [Div(('special', ['sidebar'], []), [Para([Str('Here'), Space(), Str('is'), Space(), Str('a'), Space(), Str('paragraph.')]), Para([Str('And'), Space(), Str('another.')])])])

<!-- prevent container tabs merge -->

Fenced divs can be nested. Opening fences are distinguished because they
*must* have attributes:

=== "Markdown"

        ::: Warning ::::::
        This is a warning.
        
        ::: Danger
        This is a warning within a warning.
        :::
        ::::::::::::::::::

=== "Python"

        Pandoc(Meta({}), [Div(('', ['Warning'], []), [Para([Str('This'), Space(), Str('is'), Space(), Str('a'), Space(), Str('warning.')]), Div(('', ['Danger'], []), [Para([Str('This'), Space(), Str('is'), Space(), Str('a'), Space(), Str('warning'), Space(), Str('within'), Space(), Str('a'), Space(), Str('warning.')])])])])

<!-- prevent container tabs merge -->

Fences without attributes are always closing fences. Unlike with fenced
code blocks, the number of colons in the closing fence need not match
the number in the opening fence. However, it can be helpful for visual
clarity to use fences of different lengths to distinguish nested divs
from their parents.

#### Extension: `bracketed_spans`

A bracketed sequence of inlines, as one would use to begin a link, will
be treated as a `Span` with attributes if it is followed immediately by
attributes:

=== "Markdown"

        [This is *some text*]{.class key="val"}

=== "Python"

        Pandoc(Meta({}), [Para([Span(('', ['class'], [('key', 'val')]), [Str('This'), Space(), Str('is'), Space(), Emph([Str('some'), Space(), Str('text')])])])])

<!-- prevent container tabs merge -->

## Footnotes

#### Extension: `footnotes`

Pandoc's Markdown allows footnotes, using the following syntax:

=== "Markdown"

        Here is a footnote reference,[^1] and another.[^longnote]
        
        [^1]: Here is the footnote.
        
        [^longnote]: Here's one with multiple blocks.
        
            Subsequent paragraphs are indented to show that they
        belong to the previous footnote.
        
                { some.code }
        
            The whole paragraph can be indented, or just the first
            line.  In this way, multi-paragraph footnotes work like
            multi-paragraph list items.
        
        This paragraph won't be part of the note, because it
        isn't indented.

=== "Python"

        Pandoc(Meta({}), [Para([Str('Here'), Space(), Str('is'), Space(), Str('a'), Space(), Str('footnote'), Space(), Str('reference,'), Note([Para([Str('Here'), Space(), Str('is'), Space(), Str('the'), Space(), Str('footnote.')])]), Space(), Str('and'), Space(), Str('another.'), Note([Para([Str('Here’s'), Space(), Str('one'), Space(), Str('with'), Space(), Str('multiple'), Space(), Str('blocks.')]), Para([Str('Subsequent'), Space(), Str('paragraphs'), Space(), Str('are'), Space(), Str('indented'), Space(), Str('to'), Space(), Str('show'), Space(), Str('that'), Space(), Str('they'), SoftBreak(), Str('belong'), Space(), Str('to'), Space(), Str('the'), Space(), Str('previous'), Space(), Str('footnote.')]), CodeBlock(('', [], []), '{ some.code }'), Para([Str('The'), Space(), Str('whole'), Space(), Str('paragraph'), Space(), Str('can'), Space(), Str('be'), Space(), Str('indented,'), Space(), Str('or'), Space(), Str('just'), Space(), Str('the'), Space(), Str('first'), SoftBreak(), Str('line.'), Space(), Str('In'), Space(), Str('this'), Space(), Str('way,'), Space(), Str('multi-paragraph'), Space(), Str('footnotes'), Space(), Str('work'), Space(), Str('like'), SoftBreak(), Str('multi-paragraph'), Space(), Str('list'), Space(), Str('items.')])])]), Para([Str('This'), Space(), Str('paragraph'), Space(), Str('won’t'), Space(), Str('be'), Space(), Str('part'), Space(), Str('of'), Space(), Str('the'), Space(), Str('note,'), Space(), Str('because'), Space(), Str('it'), SoftBreak(), Str('isn’t'), Space(), Str('indented.')])])

<!-- prevent container tabs merge -->

The identifiers in footnote references may not contain spaces, tabs, or
newlines. These identifiers are used only to correlate the footnote
reference with the note itself; in the output, footnotes will be
numbered sequentially.

The footnotes themselves need not be placed at the end of the document.
They may appear anywhere except inside other block elements (lists,
block quotes, tables, etc.). Each footnote should be separated from
surrounding content (including other footnotes) by blank lines.

#### Extension: `inline_notes`

Inline footnotes are also allowed (though, unlike regular notes, they
cannot contain multiple paragraphs). The syntax is as follows:

=== "Markdown"

        Here is an inline note.^[Inlines notes are easier to write, since
        you don't have to pick an identifier and move down to type the
        note.]

=== "Python"

        Pandoc(Meta({}), [Para([Str('Here'), Space(), Str('is'), Space(), Str('an'), Space(), Str('inline'), Space(), Str('note.'), Note([Para([Str('Inlines'), Space(), Str('notes'), Space(), Str('are'), Space(), Str('easier'), Space(), Str('to'), Space(), Str('write,'), Space(), Str('since'), SoftBreak(), Str('you'), Space(), Str('don’t'), Space(), Str('have'), Space(), Str('to'), Space(), Str('pick'), Space(), Str('an'), Space(), Str('identifier'), Space(), Str('and'), Space(), Str('move'), Space(), Str('down'), Space(), Str('to'), Space(), Str('type'), Space(), Str('the'), SoftBreak(), Str('note.')])])])])

<!-- prevent container tabs merge -->

Inline and regular footnotes may be mixed freely.

## Citation syntax

#### Extension: `citations`

To cite a bibliographic item with an identifier foo, use the syntax
`@foo`. Normal citations should be included in square brackets, with
semicolons separating distinct items:

=== "Markdown"

        Blah blah [@doe99; @smith2000; @smith2004].

=== "Python"

        Pandoc(Meta({}), [Para([Str('Blah'), Space(), Str('blah'), Space(), Cite([Citation('doe99', [], [], NormalCitation(), 1, 0), Citation('smith2000', [], [], NormalCitation(), 1, 0), Citation('smith2004', [], [], NormalCitation(), 1, 0)], [Str('[@doe99;'), Space(), Str('@smith2000;'), Space(), Str('@smith2004]')]), Str('.')])])

<!-- prevent container tabs merge -->

How this is rendered depends on the citation style. In an author-date
style, it might render as

=== "Markdown"

        Blah blah (Doe 1999, Smith 2000, 2004).

=== "Python"

        Pandoc(Meta({}), [Para([Str('Blah'), Space(), Str('blah'), Space(), Str('(Doe'), Space(), Str('1999,'), Space(), Str('Smith'), Space(), Str('2000,'), Space(), Str('2004).')])])

<!-- prevent container tabs merge -->

In a footnote style, it might render as

=== "Markdown"

        Blah blah.[^1]
        
        [^1]:  John Doe, "Frogs," *Journal of Amphibians* 44 (1999);
        Susan Smith, "Flies," *Journal of Insects* (2000);
        Susan Smith, "Bees," *Journal of Insects* (2004).

=== "Python"

        Pandoc(Meta({}), [Para([Str('Blah'), Space(), Str('blah.'), Note([Para([Str('John'), Space(), Str('Doe,'), Space(), Quoted(DoubleQuote(), [Str('Frogs,')]), Space(), Emph([Str('Journal'), Space(), Str('of'), Space(), Str('Amphibians')]), Space(), Str('44'), Space(), Str('(1999);'), SoftBreak(), Str('Susan'), Space(), Str('Smith,'), Space(), Quoted(DoubleQuote(), [Str('Flies,')]), Space(), Emph([Str('Journal'), Space(), Str('of'), Space(), Str('Insects')]), Space(), Str('(2000);'), SoftBreak(), Str('Susan'), Space(), Str('Smith,'), Space(), Quoted(DoubleQuote(), [Str('Bees,')]), Space(), Emph([Str('Journal'), Space(), Str('of'), Space(), Str('Insects')]), Space(), Str('(2004).')])])])])

<!-- prevent container tabs merge -->

See the [CSL user documentation](https://citationstyles.org/authors/)
for more information about CSL styles and how they affect rendering.

Unless a citation key start with a letter, digit, or `_`, and contains
only alphanumerics and single internal punctuation characters
(`:.#$%&-+?<>~/`), it must be surrounded by curly braces, which are not
considered part of the key. In `@Foo_bar.baz.`, the key is `Foo_bar.baz`
because the final period is not *internal* punctuation, so it is not
included in the key. In `@{Foo_bar.baz.}`, the key is `Foo_bar.baz.`,
including the final period. In `@Foo_bar--baz`, the key is `Foo_bar`
because the repeated internal punctuation characters terminate the key.
The curly braces are recommended if you use URLs as keys:
`[@{https://example.com/bib?name=foobar&date=2000}, p.  33]`.

Citation items may optionally include a prefix, a locator, and a suffix.
In

=== "Markdown"

        Blah blah [see @doe99, pp. 33-35 and *passim*; @smith04, chap. 1].

=== "Python"

        Pandoc(Meta({}), [Para([Str('Blah'), Space(), Str('blah'), Space(), Cite([Citation('doe99', [Str('see')], [Str(','), Space(), Str('pp.\xa033-35'), Space(), Str('and'), Space(), Emph([Str('passim')])], NormalCitation(), 1, 0), Citation('smith04', [], [Str(','), Space(), Str('chap.\xa01')], NormalCitation(), 1, 0)], [Str('[see'), Space(), Str('@doe99,'), Space(), Str('pp.'), Space(), Str('33-35'), Space(), Str('and'), Space(), Str('*passim*;'), Space(), Str('@smith04,'), Space(), Str('chap.'), Space(), Str('1]')]), Str('.')])])

<!-- prevent container tabs merge -->

The first item (`doe99`) has prefix `see`, locator `pp.  33-35`, and
suffix `and *passim*`. The second item (`smith04`) has locator `chap. 1`
and no prefix or suffix.

Pandoc uses some heuristics to separate the locator from the rest of the
subject. It is sensitive to the locator terms defined in the [CSL locale
files](https://github.com/citation-style-language/locales). Either
abbreviated or unabbreviated forms are accepted. In the `en-US` locale,
locator terms can be written in either singular or plural forms, as
`book`, `bk.`/`bks.`; `chapter`, `chap.`/`chaps.`; `column`,
`col.`/`cols.`; `figure`, `fig.`/`figs.`; `folio`, `fol.`/`fols.`;
`number`, `no.`/`nos.`; `line`, `l.`/`ll.`; `note`, `n.`/`nn.`; `opus`,
`op.`/`opp.`; `page`, `p.`/`pp.`; `paragraph`, `para.`/`paras.`; `part`,
`pt.`/`pts.`; `section`, `sec.`/`secs.`; `sub verbo`, `s.v.`/`s.vv.`;
`verse`, `v.`/`vv.`; `volume`, `vol.`/`vols.`; `¶`/`¶¶`; `§`/`§§`. If no
locator term is used, "page" is assumed.

In complex cases, you can force something to be treated as a locator by
enclosing it in curly braces or prevent parsing the suffix as locator by
prepending curly braces:

=== "Markdown"

        [@smith{ii, A, D-Z}, with a suffix]
        [@smith, {pp. iv, vi-xi, (xv)-(xvii)} with suffix here]
        [@smith{}, 99 years later]

=== "Python"

        Pandoc(Meta({}), [Para([Cite([Citation('smith', [], [Str('{ii,'), Space(), Str('A,'), Space(), Str('D-Z},'), Space(), Str('with'), Space(), Str('a'), Space(), Str('suffix')], NormalCitation(), 1, 0)], [Str('[@smith{ii,'), Space(), Str('A,'), Space(), Str('D-Z},'), Space(), Str('with'), Space(), Str('a'), Space(), Str('suffix]')]), SoftBreak(), Cite([Citation('smith', [], [Str(','), Space(), Str('{pp.\xa0iv,'), Space(), Str('vi-xi,'), Space(), Str('(xv)-(xvii)}'), Space(), Str('with'), Space(), Str('suffix'), Space(), Str('here')], NormalCitation(), 2, 0)], [Str('[@smith,'), Space(), Str('{pp.'), Space(), Str('iv,'), Space(), Str('vi-xi,'), Space(), Str('(xv)-(xvii)}'), Space(), Str('with'), Space(), Str('suffix'), Space(), Str('here]')]), SoftBreak(), Cite([Citation('smith', [], [Str('{},'), Space(), Str('99'), Space(), Str('years'), Space(), Str('later')], NormalCitation(), 3, 0)], [Str('[@smith{},'), Space(), Str('99'), Space(), Str('years'), Space(), Str('later]')])])])

<!-- prevent container tabs merge -->

A minus sign (`-`) before the `@` will suppress mention of the author in
the citation. This can be useful when the author is already mentioned in
the text:

=== "Markdown"

        Smith says blah [-@smith04].

=== "Python"

        Pandoc(Meta({}), [Para([Str('Smith'), Space(), Str('says'), Space(), Str('blah'), Space(), Cite([Citation('smith04', [], [], SuppressAuthor(), 1, 0)], [Str('[-@smith04]')]), Str('.')])])

<!-- prevent container tabs merge -->

You can also write an author-in-text citation, by omitting the square
brackets:

=== "Markdown"

        @smith04 says blah.
        
        @smith04 [p. 33] says blah.

=== "Python"

        Pandoc(Meta({}), [Para([Cite([Citation('smith04', [], [], AuthorInText(), 1, 0)], [Str('@smith04')]), Space(), Str('says'), Space(), Str('blah.')]), Para([Cite([Citation('smith04', [], [Str('p.\xa033')], AuthorInText(), 2, 0)], [Str('@smith04'), Space(), Str('[p.'), Space(), Str('33]')]), Space(), Str('says'), Space(), Str('blah.')])])

<!-- prevent container tabs merge -->

This will cause the author's name to be rendered, followed by the
bibliographical details. Use this form when you want to make the
citation the subject of a sentence.

When you are using a note style, it is usually better to let citeproc
create the footnotes from citations rather than writing an explicit
note. If you do write an explicit note that contains a citation, note
that normal citations will be put in parentheses, while author-in-text
citations will not. For this reason, it is sometimes preferable to use
the author-in-text style inside notes when using a note style.

## Non-default extensions

The following Markdown syntax extensions are not enabled by default in
pandoc, but may be enabled by adding `+EXTENSION` to the format name,
where `EXTENSION` is the name of the extension. Thus, for example,
`markdown+hard_line_breaks` is Markdown with hard line breaks.

#### Extension: `rebase_relative_paths`

Rewrite relative paths for Markdown links and images, depending on the
path of the file containing the link or image link. For each link or
image, pandoc will compute the directory of the containing file,
relative to the working directory, and prepend the resulting path to the
link or image path.

The use of this extension is best understood by example. Suppose you
have a a subdirectory for each chapter of a book, `chap1`, `chap2`,
`chap3`. Each contains a file `text.md` and a number of images used in
the chapter. You would like to have `![image](spider.jpg)` in
`chap1/text.md` refer to `chap1/spider.jpg` and `![image](spider.jpg)`
in `chap2/text.md` refer to `chap2/spider.jpg`. To do this, use

=== "Markdown"

        pandoc chap*/*.md -f markdown+rebase_relative_paths

=== "Python"

        Pandoc(Meta({}), [Para([Str('pandoc'), Space(), Str('chap'), Emph([Str('/')]), Str('.md'), Space(), Str('-f'), Space(), Str('markdown+rebase_relative_paths')])])

<!-- prevent container tabs merge -->

Without this extension, you would have to use
`![image](chap1/spider.jpg)` in `chap1/text.md` and
`![image](chap2/spider.jpg)` in `chap2/text.md`. Links with relative
paths will be rewritten in the same way as images.

Absolute paths and URLs are not changed. Neither are empty paths or
paths consisting entirely of a fragment, e.g., `#foo`.

Note that relative paths in reference links and images will be rewritten
relative to the file containing the link reference definition, not the
file containing the reference link or image itself, if these differ.

#### Extension: `attributes`

Allows attributes to be attached to any inline or block-level element.
The syntax for the attributes is the same as that used in
[`header_attributes`](#extension-header_attributes).

-   Attributes that occur immediately after an inline element affect
    that element. If they follow a space, then they belong to the space.
    (Hence, this option subsumes `inline_code_attributes` and
    `link_attributes`.)
-   Attributes that occur immediately before a block element, on a line
    by themselves, affect that element.
-   Consecutive attribute specifiers may be used, either for blocks or
    for inlines. Their attributes will be combined.
-   Attributes that occur at the end of the text of a Setext or ATX
    heading (separated by whitespace from the text) affect the heading
    element. (Hence, this option subsumes `header_attributes`.)
-   Attributes that occur after the opening fence in a fenced code block
    affect the code block element. (Hence, this option subsumes
    `fenced_code_attributes`.)
-   Attributes that occur at the end of a reference link definition
    affect links that refer to that definition.

Note that pandoc's AST does not currently allow attributes to be
attached to arbitrary elements. Hence a Span or Div container will be
added if needed.

#### Extension: `old_dashes`

Selects the pandoc \<= 1.8.2.1 behavior for parsing smart dashes: `-`
before a numeral is an en-dash, and `--` is an em-dash. This option only
has an effect if `smart` is enabled. It is selected automatically for
`textile` input.

#### Extension: `angle_brackets_escapable`

Allow `<` and `>` to be backslash-escaped, as they can be in GitHub
flavored Markdown but not original Markdown. This is implied by pandoc's
default `all_symbols_escapable`.

#### Extension: `lists_without_preceding_blankline`

Allow a list to occur right after a paragraph, with no intervening blank
space.

#### Extension: `four_space_rule`

Selects the pandoc \<= 2.0 behavior for parsing lists, so that four
spaces indent are needed for list item continuation paragraphs.

#### Extension: `spaced_reference_links`

Allow whitespace between the two components of a reference link, for
example,

=== "Markdown"

        [foo] [bar].

=== "Python"

        Pandoc(Meta({}), [Para([Str('[foo]'), Space(), Str('[bar].')])])

<!-- prevent container tabs merge -->

#### Extension: `hard_line_breaks`

Causes all newlines within a paragraph to be interpreted as hard line
breaks instead of spaces.

#### Extension: `ignore_line_breaks`

Causes newlines within a paragraph to be ignored, rather than being
treated as spaces or as hard line breaks. This option is intended for
use with East Asian languages where spaces are not used between words,
but text is divided into lines for readability.

#### Extension: `east_asian_line_breaks`

Causes newlines within a paragraph to be ignored, rather than being
treated as spaces or as hard line breaks, when they occur between two
East Asian wide characters. This is a better choice than
`ignore_line_breaks` for texts that include a mix of East Asian wide
characters and other characters.

#### Extension: `emoji`

Parses textual emojis like `:smile:` as Unicode emoticons.

#### Extension: `tex_math_single_backslash`

Causes anything between `\(` and `\)` to be interpreted as inline TeX
math, and anything between `\[` and `\]` to be interpreted as display
TeX math. Note: a drawback of this extension is that it precludes
escaping `(` and `[`.

#### Extension: `tex_math_double_backslash`

Causes anything between `\\(` and `\\)` to be interpreted as inline TeX
math, and anything between `\\[` and `\\]` to be interpreted as display
TeX math.

#### Extension: `markdown_attribute`

By default, pandoc interprets material inside block-level tags as
Markdown. This extension changes the behavior so that Markdown is only
parsed inside block-level tags if the tags have the attribute
`markdown=1`.

#### Extension: `mmd_title_block`

Enables a [MultiMarkdown](https://fletcherpenney.net/multimarkdown/)
style title block at the top of the document, for example:

=== "Markdown"

        Title:   My title
        Author:  John Doe
        Date:    September 1, 2008
        Comment: This is a sample mmd title block, with
                 a field spanning multiple lines.

=== "Python"

        Pandoc(Meta({}), [Para([Str('Title:'), Space(), Str('My'), Space(), Str('title'), SoftBreak(), Str('Author:'), Space(), Str('John'), Space(), Str('Doe'), SoftBreak(), Str('Date:'), Space(), Str('September'), Space(), Str('1,'), Space(), Str('2008'), SoftBreak(), Str('Comment:'), Space(), Str('This'), Space(), Str('is'), Space(), Str('a'), Space(), Str('sample'), Space(), Str('mmd'), Space(), Str('title'), Space(), Str('block,'), Space(), Str('with'), SoftBreak(), Str('a'), Space(), Str('field'), Space(), Str('spanning'), Space(), Str('multiple'), Space(), Str('lines.')])])

<!-- prevent container tabs merge -->

See the MultiMarkdown documentation for details. If `pandoc_title_block`
or `yaml_metadata_block` is enabled, it will take precedence over
`mmd_title_block`.

#### Extension: `abbreviations`

Parses PHP Markdown Extra abbreviation keys, like

=== "Markdown"

        *[HTML]: Hypertext Markup Language

=== "Python"

        Pandoc(Meta({}), [Para([Str('*[HTML]:'), Space(), Str('Hypertext'), Space(), Str('Markup'), Space(), Str('Language')])])

<!-- prevent container tabs merge -->

Note that the pandoc document model does not support abbreviations, so
if this extension is enabled, abbreviation keys are simply skipped (as
opposed to being parsed as paragraphs).

#### Extension: `autolink_bare_uris`

Makes all absolute URIs into links, even when not surrounded by pointy
braces `<...>`.

#### Extension: `mmd_link_attributes`

Parses multimarkdown style key-value attributes on link and image
references. This extension should not be confused with the
[`link_attributes`](#extension-link_attributes) extension.

=== "Markdown"

        This is a reference ![image][ref] with multimarkdown attributes.
        
        [ref]: https://path.to/image "Image title" width=20px height=30px
               id=myId class="myClass1 myClass2"

=== "Python"

        Pandoc(Meta({}), [Para([Str('This'), Space(), Str('is'), Space(), Str('a'), Space(), Str('reference'), Space(), Str('[image][ref]'), Space(), Str('with'), Space(), Str('multimarkdown'), Space(), Str('attributes.')]), Para([Str('[ref]:'), Space(), Str('https://path.to/image'), Space(), Quoted(DoubleQuote(), [Str('Image'), Space(), Str('title')]), Space(), Str('width=20px'), Space(), Str('height=30px'), SoftBreak(), Str('id=myId'), Space(), Str('class='), Quoted(DoubleQuote(), [Str('myClass1'), Space(), Str('myClass2')])])])

<!-- prevent container tabs merge -->

#### Extension: `mmd_header_identifiers`

Parses multimarkdown style heading identifiers (in square brackets,
after the heading but before any trailing `#`s in an ATX heading).

#### Extension: `compact_definition_lists`

Activates the definition list syntax of pandoc 1.12.x and earlier. This
syntax differs from the one described above under [Definition
lists](#definition-lists) in several respects:

-   No blank line is required between consecutive items of the
    definition list.
-   To get a "tight" or "compact" list, omit space between consecutive
    items; the space between a term and its definition does not affect
    anything.
-   Lazy wrapping of paragraphs is not allowed: the entire definition
    must be indented four spaces.[^4]

#### Extension: `gutenberg`

Use [Project Gutenberg](https://www.gutenberg.org) conventions for
`plain` output: all-caps for strong emphasis, surround by underscores
for regular emphasis, add extra blank space around headings.

#### Extension: `sourcepos`

Include source position attributes when parsing `commonmark`. For
elements that accept attributes, a `data-pos` attribute is added; other
elements are placed in a surrounding Div or Span elemnet with a
`data-pos` attribute.

#### Extension: `short_subsuperscript`

Parse multimarkdown style subscripts and superscripts, which start with
a '\~' or '\^' character, respectively, and include the alphanumeric
sequence that follows. For example:

=== "Markdown"

        x^2 = 4

=== "Python"

        Pandoc(Meta({}), [Para([Str('x^2'), Space(), Str('='), Space(), Str('4')])])

<!-- prevent container tabs merge -->

or

=== "Markdown"

        Oxygen is O~2.

=== "Python"

        Pandoc(Meta({}), [Para([Str('Oxygen'), Space(), Str('is'), Space(), Str('O~2.')])])

<!-- prevent container tabs merge -->

## Markdown variants

In addition to pandoc's extended Markdown, the following Markdown
variants are supported:

-   `markdown_phpextra` (PHP Markdown Extra)
-   `markdown_github` (deprecated GitHub-Flavored Markdown)
-   `markdown_mmd` (MultiMarkdown)
-   `markdown_strict` (Markdown.pl)
-   `commonmark` (CommonMark)
-   `gfm` (Github-Flavored Markdown)
-   `commonmark_x` (CommonMark with many pandoc extensions)

To see which extensions are supported for a given format, and which are
enabled by default, you can use the command

=== "Markdown"

        pandoc --list-extensions=FORMAT

=== "Python"

        Pandoc(Meta({}), [Para([Str('pandoc'), Space(), Str('–list-extensions=FORMAT')])])

<!-- prevent container tabs merge -->

where `FORMAT` is replaced with the name of the format.

Note that the list of extensions for `commonmark`, `gfm`, and
`commonmark_x` are defined relative to default commonmark. So, for
example, `backtick_code_blocks` does not appear as an extension, since
it is enabled by default and cannot be disabled.

[^1]: The point of this rule is to ensure that normal paragraphs
    starting with people's initials, like

    === "Markdown"

            B. Russell was an English philosopher.

    === "Python"

            Pandoc(Meta({}), [Para([Str('B.'), Space(), Str('Russell'), Space(), Str('was'), Space(), Str('an'), Space(), Str('English'), Space(), Str('philosopher.')])])

    <!-- prevent container tabs merge -->

    do not get treated as list items.

    This rule will not prevent

    === "Markdown"

            (C) 2007 Joe Smith

    === "Python"

            Pandoc(Meta({}), [OrderedList((3, UpperAlpha(), TwoParens()), [[Plain([Str('2007'), Space(), Str('Joe'), Space(), Str('Smith')])]])])

    <!-- prevent container tabs merge -->

    from being interpreted as a list item. In this case, a backslash
    escape can be used:

    === "Markdown"

            (C\) 2007 Joe Smith

    === "Python"

            Pandoc(Meta({}), [Para([Str('(C)'), Space(), Str('2007'), Space(), Str('Joe'), Space(), Str('Smith')])])

    <!-- prevent container tabs merge -->

[^2]: I have been influenced by the suggestions of [David
    Wheeler](https://justatheory.com/2009/02/modest-markdown-proposal/).

[^3]: This scheme is due to Michel Fortin, who proposed it on the
    [Markdown discussion
    list](http://six.pairlist.net/pipermail/markdown-discuss/2005-March/001097.html).

[^4]: To see why laziness is incompatible with relaxing the requirement
    of a blank line between items, consider the following example:

    === "Markdown"

            bar
            :    definition
            foo
            :    definition

    === "Python"

            Pandoc(Meta({}), [DefinitionList([([Str('bar')], [[Plain([Str('definition'), SoftBreak(), Str('foo')])], [Plain([Str('definition')])]])])])

    <!-- prevent container tabs merge -->

    Is this a single list item with two definitions of "bar," the first
    of which is lazily wrapped, or two list items? To remove the
    ambiguity we must either disallow lazy wrapping or require a blank
    line between list items.
