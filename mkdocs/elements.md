!!! warning
    This documentation is dedicated to the [latest version of the project
    available on github](https://github.com/boisgera/pandoc). 
    It is automatically tested against pandoc 2.14.2,
    [the latest release of pandoc](https://pandoc.org/releases.html) so far.


Elements
================================================================================

``` pycon
>>> import pandoc
>>> from pandoc.types import *
```

Helpers
--------------------------------------------------------------------------------

``` python
def findall(text, types):
    doc = pandoc.read(text)
    return [elt for elt in pandoc.iter(doc) if isinstance(elt, types)]
```

``` python
def find(text, type_):
    doc = pandoc.read(text)
    for elt in pandoc.iter(doc):
        if isinstance(elt, type_):
            return elt
```

``` python
def display(text, types):
    for elt in findall(text, types):
        print(elt)
```

Paragraphs
--------------------------------------------------------------------------------

``` python
text = """
First paragraph

Second paragraph

Third paragraph;
new lines introduce a soft line break.

Fourth paragraph;  
two or more spaces at the end of the line generate a hard line break.
"""
```

``` pycon
>>> display(text, Para)
Para([Str('First'), Space(), Str('paragraph')])
Para([Str('Second'), Space(), Str('paragraph')])
Para([Str('Third'), Space(), Str('paragraph;'), SoftBreak(), Str('new'), Space(), Str('lines'), Space(), Str('introduce'), Space(), Str('a'), Space(), Str('soft'), Space(), Str('line'), Space(), Str('break.')])
Para([Str('Fourth'), Space(), Str('paragraph;'), LineBreak(), Str('two'), Space(), Str('or'), Space(), Str('more'), Space(), Str('spaces'), Space(), Str('at'), Space(), Str('the'), Space(), Str('end'), Space(), Str('of'), Space(), Str('the'), Space(), Str('line'), Space(), Str('generate'), Space(), Str('a'), Space(), Str('hard'), Space(), Str('line'), Space(), Str('break.')])
```

``` pycon
>>> display(text, (SoftBreak, LineBreak))
SoftBreak()
LineBreak()
```

### Escaped line breaks

``` python
text = r"""
A backslash followed by a newline \
is also a hard line break
"""
```

``` pycon
>>> display(text, Para)
Para([Str('A'), Space(), Str('backslash'), Space(), Str('followed'), Space(), Str('by'), Space(), Str('a'), Space(), Str('newline'), LineBreak(), Str('is'), Space(), Str('also'), Space(), Str('a'), Space(), Str('hard'), Space(), Str('line'), Space(), Str('break')])
>>> display(text, LineBreak)
LineBreak()
```

Headings
--------------------------------------------------------------------------------

### Setext-style headings

``` python
text = """
A level-one heading
===================

A level-two heading
-------------------
"""
```

``` pycon
>>> display(text, Header)
Header(1, ('a-level-one-heading', [], []), [Str('A'), Space(), Str('level-one'), Space(), Str('heading')])
Header(2, ('a-level-two-heading', [], []), [Str('A'), Space(), Str('level-two'), Space(), Str('heading')])
```

### ATX-style headings

``` python
text = """
A level-one heading
===================

A level-two heading
-------------------
"""
```

``` pycon
>>> display(text, Header)
Header(1, ('a-level-one-heading', [], []), [Str('A'), Space(), Str('level-one'), Space(), Str('heading')])
Header(2, ('a-level-two-heading', [], []), [Str('A'), Space(), Str('level-two'), Space(), Str('heading')])
```

``` python
text = "# A level-one heading with a [link](/url) and *emphasis*"
```

``` pycon
>>> display(text, Header)
Header(1, ('a-level-one-heading-with-a-link-and-emphasis', [], []), [Str('A'), Space(), Str('level-one'), Space(), Str('heading'), Space(), Str('with'), Space(), Str('a'), Space(), Link(('', [], []), [Str('link')], ('/url', '')), Space(), Str('and'), Space(), Emph([Str('emphasis')])])
```

### Heading identifiers

#### Header attributes

``` python
text = """
# My heading {#foo}

## My heading ##    {#foo}

My other heading   {#foo}
---------------
"""
```

``` pycon
>>> display(text, Header)
Header(1, ('foo', [], []), [Str('My'), Space(), Str('heading')])
Header(2, ('foo', [], []), [Str('My'), Space(), Str('heading')])
Header(2, ('foo', [], []), [Str('My'), Space(), Str('other'), Space(), Str('heading')])
```

``` python
text = """
# My heading {-}

# My heading {.unnumbered}
"""
```

``` pycon
>>> display(text, Header)
Header(1, ('my-heading', ['unnumbered'], []), [Str('My'), Space(), Str('heading')])
Header(1, ('my-heading-1', ['unnumbered'], []), [Str('My'), Space(), Str('heading')])
```

#### Implicit Header References

``` python
text = """
# Heading identifiers in HTML

[Heading identifiers in HTML]

[Heading identifiers in HTML][]

[the section on heading identifiers][heading identifiers in
HTML]

[Heading identifiers in HTML](#heading-identifiers-in-html)
"""
```

``` pycon
>>> display(text, Link)
Link(('', [], []), [Str('Heading'), Space(), Str('identifiers'), Space(), Str('in'), Space(), Str('HTML')], ('#heading-identifiers-in-html', ''))
Link(('', [], []), [Str('Heading'), Space(), Str('identifiers'), Space(), Str('in'), Space(), Str('HTML')], ('#heading-identifiers-in-html', ''))
Link(('', [], []), [Str('the'), Space(), Str('section'), Space(), Str('on'), Space(), Str('heading'), Space(), Str('identifiers')], ('#heading-identifiers-in-html', ''))
Link(('', [], []), [Str('Heading'), Space(), Str('identifiers'), Space(), Str('in'), Space(), Str('HTML')], ('#heading-identifiers-in-html', ''))
```

Block quotations
--------------------------------------------------------------------------------

``` python
text = """
> This is a block quote. This
> paragraph has two lines.
>
> 1. This is a list inside a block quote.
> 2. Second item.
"""
```

``` pycon
>>> display(text, BlockQuote)
BlockQuote([Para([Str('This'), Space(), Str('is'), Space(), Str('a'), Space(), Str('block'), Space(), Str('quote.'), Space(), Str('This'), SoftBreak(), Str('paragraph'), Space(), Str('has'), Space(), Str('two'), Space(), Str('lines.')]), OrderedList((1, Decimal(), Period()), [[Plain([Str('This'), Space(), Str('is'), Space(), Str('a'), Space(), Str('list'), Space(), Str('inside'), Space(), Str('a'), Space(), Str('block'), Space(), Str('quote.')])], [Plain([Str('Second'), Space(), Str('item.')])]])])
```

A “lazy” form, which requires the > character only on the first line of each block, is also allowed:

``` python
text = """
> This is a block quote. This
paragraph has two lines.

> 1. This is a list inside a block quote.
2. Second item.
"""
```

``` pycon
>>> display(text, BlockQuote)
BlockQuote([Para([Str('This'), Space(), Str('is'), Space(), Str('a'), Space(), Str('block'), Space(), Str('quote.'), Space(), Str('This'), SoftBreak(), Str('paragraph'), Space(), Str('has'), Space(), Str('two'), Space(), Str('lines.')])])
BlockQuote([OrderedList((1, Decimal(), Period()), [[Plain([Str('This'), Space(), Str('is'), Space(), Str('a'), Space(), Str('list'), Space(), Str('inside'), Space(), Str('a'), Space(), Str('block'), Space(), Str('quote.')])], [Plain([Str('Second'), Space(), Str('item.')])]])])
```

``` python
text = """
> This is a block quote.
>
> > A block quote within a block quote.
"""
```

``` pycon
>>> display(text, BlockQuote)
BlockQuote([Para([Str('This'), Space(), Str('is'), Space(), Str('a'), Space(), Str('block'), Space(), Str('quote.')]), BlockQuote([Para([Str('A'), Space(), Str('block'), Space(), Str('quote'), Space(), Str('within'), Space(), Str('a'), Space(), Str('block'), Space(), Str('quote.')])])])
BlockQuote([Para([Str('A'), Space(), Str('block'), Space(), Str('quote'), Space(), Str('within'), Space(), Str('a'), Space(), Str('block'), Space(), Str('quote.')])])
```

``` python
text = """
>     code
"""
```

``` pycon
>>> display(text, BlockQuote)
BlockQuote([CodeBlock(('', [], []), 'code')])
```

#### Blank before blockquote

``` python
text = """
> This is a block quote.
>> Nested.
"""
```

``` pycon
>>> display(text, BlockQuote)
BlockQuote([Para([Str('This'), Space(), Str('is'), Space(), Str('a'), Space(), Str('block'), Space(), Str('quote.'), SoftBreak(), Str('>'), Space(), Str('Nested.')])])
```

Verbatim (code) blocks
--------------------------------------------------------------------------------

### Indented code blocks

``` python
text = """
    if (a > 3) {
      moveShip(5 * gravity, DOWN);
    }
"""
```

``` pycon
>>> display(text, CodeBlock)
CodeBlock(('', [], []), 'if (a > 3) {\n  moveShip(5 * gravity, DOWN);\n}')
```

### Fenced code blocks

``` python
text = """
~~~~~~~
if (a > 3) {
  moveShip(5 * gravity, DOWN);
}
~~~~~~~
"""
```

``` pycon
>>> display(text, CodeBlock)
CodeBlock(('', [], []), 'if (a > 3) {\n  moveShip(5 * gravity, DOWN);\n}')
```

``` python
text = """
~~~~~~~~~~~~~~~~
~~~~~~~~~~
code including tildes
~~~~~~~~~~
~~~~~~~~~~~~~~~~
"""
```

``` pycon
>>> display(text, CodeBlock)
CodeBlock(('', [], []), '~~~~~~~~~~\ncode including tildes\n~~~~~~~~~~')
```

#### Backtick code blocks

~~~ python
text = """
```
if (a > 3) {
  moveShip(5 * gravity, DOWN);
}
```
"""
~~~

``` pycon
>>> display(text, CodeBlock)
CodeBlock(('', [], []), 'if (a > 3) {\n  moveShip(5 * gravity, DOWN);\n}')
```

#### Fenced code attributes

``` python
text = """
~~~~ {#mycode .haskell .numberLines startFrom="100"}
qsort []     = []
qsort (x:xs) = qsort (filter (< x) xs) ++ [x] ++
               qsort (filter (>= x) xs)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
```

``` pycon
>>> display(text, CodeBlock)
CodeBlock(('mycode', ['haskell', 'numberLines'], [('startFrom', '100')]), 'qsort []     = []\nqsort (x:xs) = qsort (filter (< x) xs) ++ [x] ++\n               qsort (filter (>= x) xs)')
```

~~~ python
text = """
```haskell
qsort [] = []
```
"""
~~~

``` pycon
>>> display(text, CodeBlock)
CodeBlock(('', ['haskell'], []), 'qsort [] = []')
```



Line Blocks
--------------------------------------------------------------------------------

``` python
text = """
| The limerick packs laughs anatomical
| In space that is quite economical.
|    But the good ones I've seen
|    So seldom are clean
| And the clean ones so seldom are comical

| 200 Main St.
| Berkeley, CA 94718
"""
```

``` pycon
>>> display(text, LineBlock)
LineBlock([[Str('The'), Space(), Str('limerick'), Space(), Str('packs'), Space(), Str('laughs'), Space(), Str('anatomical')], [Str('In'), Space(), Str('space'), Space(), Str('that'), Space(), Str('is'), Space(), Str('quite'), Space(), Str('economical.')], [Str('\xa0\xa0\xa0But'), Space(), Str('the'), Space(), Str('good'), Space(), Str('ones'), Space(), Str('I’ve'), Space(), Str('seen')], [Str('\xa0\xa0\xa0So'), Space(), Str('seldom'), Space(), Str('are'), Space(), Str('clean')], [Str('And'), Space(), Str('the'), Space(), Str('clean'), Space(), Str('ones'), Space(), Str('so'), Space(), Str('seldom'), Space(), Str('are'), Space(), Str('comical')]])
LineBlock([[Str('200'), Space(), Str('Main'), Space(), Str('St.')], [Str('Berkeley,'), Space(), Str('CA'), Space(), Str('94718')]])
```


``` python
text = """
| The Right Honorable Most Venerable and Righteous Samuel L.
  Constable, Jr.
| 200 Main St.
| Berkeley, CA 94718
"""
```

``` pycon
>>> display(text, LineBlock)
LineBlock([[Str('The'), Space(), Str('Right'), Space(), Str('Honorable'), Space(), Str('Most'), Space(), Str('Venerable'), Space(), Str('and'), Space(), Str('Righteous'), Space(), Str('Samuel'), Space(), Str('L.'), Space(), Str('Constable,'), Space(), Str('Jr.')], [Str('200'), Space(), Str('Main'), Space(), Str('St.')], [Str('Berkeley,'), Space(), Str('CA'), Space(), Str('94718')]])
```

Lists (TODO)
--------------------------------------------------------------------------------

Horizontal Rules (TODO)
--------------------------------------------------------------------------------

Tables (TODO)
--------------------------------------------------------------------------------

Inline Formatting (TODO)
--------------------------------------------------------------------------------

LaTeX and Math (TODO)
--------------------------------------------------------------------------------

HTML (TODO)
--------------------------------------------------------------------------------


Links (TODO)
--------------------------------------------------------------------------------

Images (TODO)
--------------------------------------------------------------------------------

Divs and Spans (TODO)
--------------------------------------------------------------------------------

Footnotes (wip)
--------------------------------------------------------------------------------

``` python
text = """
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
"""
```

``` pycon
>>> display(text, Note)
Note([Para([Str('Here'), Space(), Str('is'), Space(), Str('the'), Space(), Str('footnote.')])])
Note([Para([Str('Here’s'), Space(), Str('one'), Space(), Str('with'), Space(), Str('multiple'), Space(), Str('blocks.')]), Para([Str('Subsequent'), Space(), Str('paragraphs'), Space(), Str('are'), Space(), Str('indented'), Space(), Str('to'), Space(), Str('show'), Space(), Str('that'), Space(), Str('they'), SoftBreak(), Str('belong'), Space(), Str('to'), Space(), Str('the'), Space(), Str('previous'), Space(), Str('footnote.')]), CodeBlock(('', [], []), '{ some.code }'), Para([Str('The'), Space(), Str('whole'), Space(), Str('paragraph'), Space(), Str('can'), Space(), Str('be'), Space(), Str('indented,'), Space(), Str('or'), Space(), Str('just'), Space(), Str('the'), Space(), Str('first'), SoftBreak(), Str('line.'), Space(), Str('In'), Space(), Str('this'), Space(), Str('way,'), Space(), Str('multi-paragraph'), Space(), Str('footnotes'), Space(), Str('work'), Space(), Str('like'), SoftBreak(), Str('multi-paragraph'), Space(), Str('list'), Space(), Str('items.')])])
```

Citations
--------------------------------------------------------------------------------

Metadata (wip)
--------------------------------------------------------------------------------    

**Reference:** [Pandoc User's Guide / Metadata Blocks](https://pandoc.org/MANUAL.html#metadata-blocks)

**TODO.** Start with document without metadata, then simple title and contents, 
then more advanced metadata ... and finally YAML blocks?

**TODO:** specify use cases: use for custom templates, misc. configuration
options (e.g. stylesheets, EPUB metadata, bibliography, etc.)

``` pycon
>>> Meta
Meta({Text: MetaValue})
```

``` pycon
>>> MetaValue
MetaValue = MetaMap({Text: MetaValue})
          | MetaList([MetaValue])
          | MetaBool(Bool)
          | MetaString(Text)
          | MetaInlines([Inline])
          | MetaBlocks([Block])
```

``` pycon
>>> text = """\
... % Document Title
... % Author One, Author Two
... % Date
... """
```

``` pycon
>>> metadata = find(text, Meta)
>>> metadata == \
... Meta(map([
...   ('date', MetaInlines([Str('Date')])), 
...   ('author', MetaList([MetaInlines(
...     [Str('Author'), Space(), Str('One,'), Space(), Str('Author'), Space(), Str('Two')])])), 
...   ('title', MetaInlines([Str('Document'), Space(), Str('Title')]))
... ]))
True
```

``` pycon
>>> metamap = metadata[0]
>>> metamap["title"]
MetaInlines([Str('Document'), Space(), Str('Title')])
>>> metamap["author"]
MetaList([MetaInlines([Str('Author'), Space(), Str('One,'), Space(), Str('Author'), Space(), Str('Two')])])
>>> metamap["date"]
MetaInlines([Str('Date')])
```


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


