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

We introduce a simple function to display pandoc elements in markdown:

```pycon
>>> def display(elt):
...     print(pandoc.write(elt))
```

We also define a `to` function `to` to get a specific type of element inside
a document:

``` pycon
>>> def to(elt, type):
...     for _elt in pandoc.iter(elt):
...         if isinstance(_elt, type):
...             return _elt
```

Since we're a bit reckless, we monkey-patch the pandoc type base class 
to use `to` as a method:

``` pycon
>>> Type.to = to
```

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
```

``` pycon
>>> metadata = doc[0][0]
>>> metadata["title"]
MetaInlines([Str('Document'), Space(), Str('Title')])
>>> metadata["author"]
MetaList([MetaInlines([Str('Author'), Space(), Str('One,'), Space(), Str('Author'), Space(), Str('Two')])])
>>> metadata["date"]
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


