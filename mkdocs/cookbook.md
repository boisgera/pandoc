# Cookbook

``` python
import pandoc
from pandoc.types import *
```

We will use the commonmark spec as an example of a rather complex markdown document:

``` python
from urllib.request import urlopen
PATH = "raw.githubusercontent.com/commonmark/commonmark-spec"
HASH = "499ebbad90163881f51498c4c620652d0c66fb2e" 
URL = f"https://{PATH}/{HASH}/spec.txt"
COMMONMARK_SPEC = urlopen(URL).read().decode("utf-8")
```

``` pycon
>>> print(COMMONMARK_SPEC[:583]) # excerpt
---
title: CommonMark Spec
author: John MacFarlane
version: '0.30'
date: '2021-06-19'
license: '[CC-BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/)'
...
<BLANKLINE>
# Introduction
<BLANKLINE>
## What is Markdown?
<BLANKLINE>
Markdown is a plain text format for writing structured documents,
based on conventions for indicating formatting in email
and usenet posts.  It was developed by John Gruber (with
help from Aaron Swartz) and released in 2004 in the form of a
[syntax description](http://daringfireball.net/projects/markdown/syntax)
and a Perl script (`Markdown.pl`) for converting Markdown to
HTML.
```

``` python
commonmark_doc = pandoc.read(COMMONMARK_SPEC)
```

## Access

When we know the location and type of some information in a document,
we can use either random access or pattern matching to retrieve it.

### Random access

A date is often included as inline text into a document's metadata; 
in this case, we can access it and return it as a markdown string:

``` python
def get_date(doc):
    meta = doc[0] # doc: Pandoc(Meta, [Block])
    meta_dict = meta[0] # meta: Meta({Text: MetaValue})
    date = meta_dict["date"]
    date_inlines = date[0] # date: MetaInlines([Inline])
    return pandoc.write(date_inlines).strip()
```

The commonmark specification includes such a date:
``` pycon
>>> print(COMMONMARK_SPEC) # doctest: +ELLIPSIS
---
title: CommonMark Spec
author: John MacFarlane
version: '0.30'
date: '2021-06-19'
license: '[CC-BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/)'
...
```

and therefore

``` pycon
>>> get_date(commonmark_doc)
'2021-06-19'
```

After the metadata, the document starts with a header.
To get its title, we can use

``` python
def get_first_header_title(doc):
    blocks = doc[1] # doc: Pandoc(Meta, [Block])
    header = blocks[0]
    title_inlines = header[2] # header: Header(Int, Attr, [Inline])
    return pandoc.write(title_inlines).strip()
```

``` pycon
>>> get_first_header_title(commonmark_doc)
'Introduction'
```

### Structural checks

The functions `get_date` and `get_first_header_title` may fail if they are
used on a document which doesn't have the expected structure. 
For example, for the simple "Hello world!" document

``` pycon
>>> helloworld_doc = pandoc.read("Hello world!")
>>> helloworld_doc
Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])
```

which has no `date` metadata field, and doesn't start with a header,
we end up with

``` pycon
>>> get_date(helloworld_doc)
Traceback (most recent call last):
...
KeyError: 'date'
```

``` pycon
>>> get_first_header_title(helloworld_doc)
Traceback (most recent call last):
...
IndexError: list index out of range
```

A more robust version of these functions may return `None` when
the document does not have the expected structure:

``` python
def get_date(doc):
    meta = doc[0] # doc: Pandoc(Meta, [Block])
    meta_dict = meta[0] # meta: Meta({Text: MetaValue})
    date = meta_dict.get("date")
    if isinstance(date, MetaInlines):
        date_inlines = date[0] # date: MetaInlines([Inline])
        return pandoc.write(date_inlines).strip()
```

``` pycon
>>> get_date(commonmark_doc)
'2021-06-19'
>>> get_date(helloworld_doc)
```

``` python
def get_first_header_title(doc):
    blocks = doc[1] # doc: Pandoc(Meta, [Block])
    if blocks and isinstance(blocks[0], Header):
        header = blocks[0]
        title_inlines = header[2] # header: Header(Int, Attr, [Inline])
        return pandoc.write(title_inlines).strip()
```

``` pycon
>>> get_first_header_title(commonmark_doc)
'Introduction'
>>> get_first_header_title(helloworld_doc)
```

<!--
We can also find the document's author name in the document metadata and 
return it (as a markdown string).
``` python
def get_author(doc):
    meta = doc[0] # doc: Pandoc(Meta, [Block])
    meta_dict = meta[0] # meta: Meta({Text: MetaValue})
    author = meta_dict.get("author")
    if author:
        if isinstance(author, MetaInlines): # author: MetaInlines([Inline])
            author_inlines = author[0]
            return pandoc.write(author_inlines).strip()
        elif isinstance(author, MetaList): # author: MetaList([MetaValue])
            authors_meta = author[0]
            if all(isinstance(elt, MetaInlines) for elt in authors_meta):
                authors_inlines = [elt[0] for elt in authors_meta]
                return [pandoc.write(inline).strip() for inline in authors_inlines]
```

``` pycon
>>> get_author(commonmark_doc)
'John MacFarlane'
```

This `get_author` function is more complex than `get_date` but it can also 
deal with multiple authors, specified as a list of inline texts. For example,
with

``` python
doc = pandoc.read("""
---
author: 
  - Author 1
  - Author 2
  - Author 3
---
""")
```
it yields
``` pycon
>>> get_author(doc)
['Author 1', 'Author 2', 'Author 3']
```

-->

### Pattern matching

With Python 3.10 or later, [pattern matching] can be used to combine
random access and structural checks. The implementation of `get_date`

``` python
def get_date(doc):
    match doc:
        case Pandoc(Meta({"date": MetaInlines(date_inlines)}), _):
            return pandoc.write(date_inlines).strip()
```

and the previous one have identical behaviors:

``` pycon
>>> get_date(commonmark_doc)
'2021-06-19'
>>> get_date(helloworld_doc)
```

The behavior of the following `get_first_header_title` function

``` python
def get_first_header_title(doc):
    match doc:
        case Pandoc(_, [Header(_, _, header_inlines), *_]):
            return pandoc.write(header_inlines).strip()
```

is also unchanged:

``` pycon
>>> get_first_header_title(commonmark_doc)
'Introduction'
>>> get_first_header_title(helloworld_doc)
```

[pattern matching]: https://www.python.org/dev/peps/pep-0634/

## Find

### Read

Extraction of information from a document – a very common use case in
the automatic processing of documents – requires usually to find the
document fragments that meet some condition first and foremost. 
This condition typically discriminates on the type of the fragment 
and optionally its contents. This "fetch" pattern, 
does not require any transformation of the document itself,
often leads to rather straightforward implementations.




We can build a simple table of contents of the document:
``` python
def table_of_contents(doc):
    headers = [elt for elt in pandoc.iter(doc) if isinstance(elt, Header)]
    toc_lines = []
    for header in headers:
       level, _, inlines = header[:] # header: Header(Int, Attr, [Inline]) 
       header_title = pandoc.write(inlines).strip()
       indent = (level - 1) * 4 * " "
       toc_lines.append(f"{indent}  - {header_title}")
    return "\n".join(toc_lines)
```

``` pycon
>>> print(table_of_contents(commonmark_doc)) # doctest: +ELLIPSIS
  - Introduction
      - What is Markdown?
      - Why is a spec needed?
      - About this document
  - Preliminaries
      - Characters and lines
      - Tabs
      - Insecure characters
      - Backslash escapes
      - Entity and numeric character references
  ...
  - Appendix: A parsing strategy
      - Overview
      - Phase 1: block structure
      - Phase 2: inline structure
          - An algorithm for parsing nested emphasis and links
              - *look for link or image*
              - *process emphasis*
```

We can display all external link URLs used in the commonmark specification.

``` python
def display_external_links(doc):
    links = [elt for elt in pandoc.iter(doc) if isinstance(elt, Link)]
    for link in links:
        _, _, target = link # Link signature is Link(Attr, [Inline], Target)
        url, title = target # Target signature is (Text, Text)
        if url.startswith("http"):
            print(url)
```

``` pycon
>>> display_external_links(commonmark_doc)
http://creativecommons.org/licenses/by-sa/4.0/
http://daringfireball.net/projects/markdown/syntax
http://daringfireball.net/projects/markdown/
http://www.methods.co.nz/asciidoc/
http://daringfireball.net/projects/markdown/syntax
http://article.gmane.org/gmane.text.markdown.general/1997
http://article.gmane.org/gmane.text.markdown.general/2146
http://article.gmane.org/gmane.text.markdown.general/2554
https://html.spec.whatwg.org/entities.json
http://www.aaronsw.com/2002/atx/atx.py
http://docutils.sourceforge.net/rst.html
http://daringfireball.net/projects/markdown/syntax#em
http://www.vfmd.org/vfmd-spec/specification/#procedure-for-identifying-emphasis-tags
https://html.spec.whatwg.org/multipage/forms.html#e-mail-state-(type=email)
http://www.w3.org/TR/html5/syntax.html#comments
```

We can get the list of the code blocks types (registered as classes):

``` python
def fetch_code_types(doc):
    code_blocks = [elt for elt in pandoc.iter(doc) if isinstance(elt, CodeBlock)]
    types = set()
    for code_block in code_blocks:
        attr = code_block[0] # CodeBlock(Attr, Text)
        _, classes, _ = attr # Attr = (Text, [Text], [(Text, Text)])
        types.update(classes)
    return sorted(list(types))
```

``` pycon
>>> code_types = fetch_code_types(commonmark_doc)
>>> code_types
['example', 'html', 'markdown', 'tree']

```

### Write

The "match" pattern is also valuable to get a list of (mutable) items and then 
change their content. For example, to change all http links in the document to 
their https counterpart:

``` python
def to_https(doc):
    links = [elt for elt in pandoc.iter(doc) if isinstance(elt, Link)]
    for link in links:
        target = link[2] # link: Link(Attr, [Inline], Target)
        url, title = target # target: (Text, Text)
        if url.startswith("http:"):
            url = url.replace("http:", "https:")
            target = url, title
            link[2] = target
```

We can check that this function performs the expected change in the document:

``` pycon
>>> to_https(commonmark_doc)
>>> display_external_links(commonmark_doc)
https://creativecommons.org/licenses/by-sa/4.0/
https://daringfireball.net/projects/markdown/syntax
https://daringfireball.net/projects/markdown/
https://www.methods.co.nz/asciidoc/
https://daringfireball.net/projects/markdown/syntax
https://article.gmane.org/gmane.text.markdown.general/1997
https://article.gmane.org/gmane.text.markdown.general/2146
https://article.gmane.org/gmane.text.markdown.general/2554
https://html.spec.whatwg.org/entities.json
https://www.aaronsw.com/2002/atx/atx.py
https://docutils.sourceforge.net/rst.html
https://daringfireball.net/projects/markdown/syntax#em
https://www.vfmd.org/vfmd-spec/specification/#procedure-for-identifying-emphasis-tags
https://html.spec.whatwg.org/multipage/forms.html#e-mail-state-(type=email)
https://www.w3.org/TR/html5/syntax.html#comments
```

## Locate

Another very common transformation pattern is when you need to locate the
items meeting some condition in the document in order to replace them or 
to delete them. In this case, fetching a list of items is not enough;
instead we should obtain the location of the item in the document,
which is given as a pair of item `holder` and item `index`, such that
`item` is `holder[index]`.

This information is avaible as `path[-1]` where `elt, path` is yielded by
`pandoc.iter` with the option `path=True`. For example:

``` pycon
>>> doc = pandoc.read("Hello world!")
>>> for elt, path in pandoc.iter(doc, path=True):
...     if elt != doc: # elt == doc is the document root, it has no holder
...          holder, index = path[-1]
...          print(f"elt: {elt!r}")
...          print(f"  -> holder: {holder}")
...          print(f"  -> index: {index}")
elt: Meta({})
  -> holder: Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])
  -> index: 0
elt: {}
  -> holder: Meta({})
  -> index: 0
elt: [Para([Str('Hello'), Space(), Str('world!')])]
  -> holder: Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])
  -> index: 1
elt: Para([Str('Hello'), Space(), Str('world!')])
  -> holder: [Para([Str('Hello'), Space(), Str('world!')])]
  -> index: 0
elt: [Str('Hello'), Space(), Str('world!')]
  -> holder: Para([Str('Hello'), Space(), Str('world!')])
  -> index: 0
elt: Str('Hello')
  -> holder: [Str('Hello'), Space(), Str('world!')]
  -> index: 0
elt: 'Hello'
  -> holder: Str('Hello')
  -> index: 0
elt: Space()
  -> holder: [Str('Hello'), Space(), Str('world!')]
  -> index: 1
elt: Str('world!')
  -> holder: [Str('Hello'), Space(), Str('world!')]
  -> index: 2
elt: 'world!'
  -> holder: Str('world!')
  -> index: 0
```

The previous components of the path contain the holder and index that locate
the element holder, then their holder and index, etc. up to the document root:
``` pycon
>>> for elt, path in pandoc.iter(doc, path=True):
...     if elt == "world!":
...         for holder, index in path:
...             print(f"-> {holder}[{index}]")
-> Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])[1]
-> [Para([Str('Hello'), Space(), Str('world!')])][0]
-> Para([Str('Hello'), Space(), Str('world!')])[0]
-> [Str('Hello'), Space(), Str('world!')][2]
-> Str('world!')[0]
```

### Replace

"Find-and-replace" is a very frequent pattern in document transformations.
In most use cases, the implementation is straightforward ; but some others
require a bit more subtelty.

**TODO.** Don't change while you iterate.

For example, to replace all instances of emphasized text with strong text,
you first need locate emphasized text instances, that is find the collections
of holders `holder` and indices `i` such that `emph = holder[i]`.

``` python
doc = pandoc.read("""
# Title with *emphasis*
Text with *emphasis*.
""")
```

``` python
emph_locations = []
for elt, path in pandoc.iter(doc, path=True):
    if isinstance(elt, Emph):
        holder, i = path[-1]
        emph_locations.append((holder, i))
```

``` pycon
>>> for holder, i in emph_locations:
...    emph = holder[i] 
...    inlines = emph[0]        # Emph signature is Emph([Inline])
...    strong = Strong(inlines) # Strong signature is Strong([Inline])
...    holder[i] = strong
```

**Question.** When is the "not-reversed-scheme" ok? When are the next locations
still valid? Even with most recursive scheme, that should be ok. Think more of
it here & document the stuff. Distinguish simple replacement with "extensive
surgery" that may invalidate the inner locations. Talk about (shallow) replacement?

### Delete

**TODO.**

## Scoping

Some patterns require to treat elements differently when one of their ancestors
meet some condition. For example, to count the number of words in your document
(defined as the number of `Str` instances), excluding those inside a `notes` div 
(a way to inside speaker notes when reveal.js presentations are the target).

Let's use the following example document:

``` python
doc = pandoc.read("""
The words in this paragraph should be counted.

::: notes ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

But these words should be excluded.

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
""")
```

Counting all words is easy

``` pycon
>>> len([item for item in pandoc.iter(doc) if isinstance(item, Str)])
14
```

But to exclude all words with a `notes` div, we need to detect when the iteration
enters and exits such an element. The easiest way to do this is to record the
depth of such divs[^99] when we enter them. As long as we iterate on items
at a greater depth, we're still in the div scope ; when this depth becomes
equal or smaller than this recorded depth, we're out of it. 
Thus, a possible implementation of this pattern is:

``` python
def count_words(doc):
    in_notes, depth = False, None
    count = 0
    for elt, path in pandoc.iter(doc, path=True):
        # Detect entry & exit from notes div
        if not in_notes:
            if isinstance(elt, Div):
                attr = elt[0]     # Div(Attr, [Block])
                classes = attr[1] # attr = (id, classes, kvs)
                if "notes" in classes:
                    in_notes, depth = True, len(path) 
        else:
            if len(path) <= depth:
                in_notes, depth = False, None
        # Count words outside of notes divs
        if isinstance(elt, Str) and not in_notes:
            count += 1
    return count
```

It provides the expected result:
``` pycon
>>> count_words(doc)
8
```

[^99]: or the depths if they can be nested.

## Immutable data

Every non-trivial pandoc document contains data that is immutable.
To perform in-place modifications of your document, 
you have to deal with them specifically. And this is a good thing!

### Hello world!
Consider the most basic "Hello world!" paragraph:

``` pycon
>>> paragraph = Para([Str('Hello'), Space(), Str('world!')])
>>> string = paragraph[0][2]
>>> string
Str('world!')
>>> text = string[0]
>>> text
'world!'
```

Here `text` is a Python string, which is immutable.
Thus, we cannot modify it in-place:

``` pycon
>>> text[:] = "pandoc!"
Traceback (most recent call last):
...
TypeError: 'str' object does not support item assignment
```

Does it mean that we cannot modify any word of this sentence?
Absolutely not! Because instead of modifying the Python string,
we can *replace it* in its container instead:

``` pycon
>>> string[0] = "pandoc!"
>>> paragraph
Para([Str('Hello'), Space(), Str('pandoc!')])
```

This works because the container of `"world!"` is an instance of `Str`,
a custom Pandoc type, which is mutable.

### Type safety

While the above approach may seem to be a workaround at first, 
it is actually *a good thing*, because it helps you to carefully consider
the type of data that you select and transform. Python strings for example
are of course in documents to describe pieces of text, but also in many
other roles. 

Consider the HTML fragment:
``` pycon
>>> blocks = [ # <p>html rocks!</p>
...     RawBlock(Format('html'), '<p>'), 
...     Plain([Str('html'), Space(), Str('rocks!')]), 
...     RawBlock(Format('html'), '</p>')
... ]
```
Let's say that we want to replace `'html'` with `'pandoc'` in the document text.
Notice that the string `'html'` is used in the `"html rocks!"`, 
but also as a type field in the `Format` instance. 
If Python strings were mutable, you could carelessly try to replace all
`'html'` strings in the document model regardless of their role. 
And you would end up with the (invalid) document fragment:

``` pycon
>>> invalid_blocks = [
...     RawBlock(Format('pandoc'), '<p>'), 
...     Plain([Str('pandoc'), Space(), Str('rocks!')]),  
...     RawBlock(Format('pandoc'), '</p>')
... ]
```

Fortunately this approach will fail loudly:

```pycon
>>> for elt in pandoc.iter(blocks):
...     if elt == "html":
...         elt[:] = "pandoc"
Traceback (most recent call last):
...
TypeError: 'str' object does not support item assignment
```

A correct, type-safe, way to proceed is instead:

``` pycon
>>> for elt in pandoc.iter(blocks):
...     if isinstance(elt, Str) and elt[0] == "html":
...         elt[0] = "pandoc"
... 
>>> blocks == [
...     RawBlock(Format('html'), '<p>'), 
...     Plain([Str('pandoc'), Space(), Str('rocks!')]), 
...     RawBlock(Format('html'), '</p>')
... ]
True
```

### Use cases

Python strings is an example of primitive type which is immutable and thus
require special handling when in-place algorithms are used. 
Boolean, integers and floating-point numbers are also found in document
and can be handled similarly.
The other immutable types that appears in documents are based on tuples.
We illustrate how to deal with them on the two most common use cases: 
targets and attributes.

#### Targets

In pandoc, targets are pairs of Python strings

```pycon
>>> Target
Target = (Text, Text)
>>> Text
<class 'str'>
```

The first text represents an URL and the second a title.
Targets are used in link and image elements and only there.

Say that you want to find all links in your document whose target URL is
`"https://pandoc.org"` and make sure that the associated title is 
`"Pandoc - About pandoc"`. The relevant type signature is:

```pycon
>>> Link
Link(Attr, [Inline], Target)
```

You may be tempted to iterate the document to find all pairs of text,
then select those whose first item is "`https://pandoc.org`" and modify them. 
But this approach will not work: we know by now that it is unsafe, since
you may find some items which are not really targets[^1] ; and additionally,
you cannot modify the targets in-place since tuples are immutable.

[^1]: These items would simply happen to share the same structure. 
      For example, this can happen with attributes: 
      since `Attr = (Text, [Text], [(Text, Text)])`,
      the third component of every attribute – its list of key-value pairs – 
      will contain some pairs of `Text` if it's not empty.

The easiest way to handle this situation is to search for links that target 
pandoc's web site.

``` pycon
>>> doc = pandoc.read("[Link to pandoc.org](https://pandoc.org)")
>>> for elt in pandoc.iter(doc):
...     if isinstance(elt, Link):
...         attr, inlines, target = elt[:]
...         if target[0] == "https://pandoc.org":
...             new_target = (target[0], "Pandoc - About pandoc")
...             elt[2] = new_target
... 
>>> print(pandoc.write(doc)) # doctest: +NORMALIZE_WHITESPACE
[Link to pandoc.org](https://pandoc.org "Pandoc - About pandoc")
```

#### Attributes

The other most notable immutable type in documents is `Attr`:

``` pycon
>>> Attr
Attr = (Text, [Text], [(Text, Text)])
```

`Attr` is composed of an identifier, a list of classes, and a list of
key-value pairs. To transform `Attr` content, again the easiest way to
proceed is to target their holders. Say that we want add a class tag 
that described the type of the pandoc element for every element which 
is a `Attr` holder. 
The relevant type signatures – we display all `Attr` holders – are:

``` pycon
>>> Inline # doctest: +ELLIPSIS
Inline = ...
       | Code(Attr, Text)
       ...
       | Link(Attr, [Inline], Target)
       | Image(Attr, [Inline], Target)
       ...
       | Span(Attr, [Inline])
```

and 

``` pycon
>>> Block  # doctest: +ELLIPSIS
Block = ...
      | CodeBlock(Attr, Text)
      ...
      | Header(Int, Attr, [Inline])
      ...
      | Table(Attr, Caption, [ColSpec], TableHead, [TableBody], TableFoot)
      | Div(Attr, [Block])
      ...
```

So we need to target `Code`, `Link`, `Image`, `Span`, `Div`,`CodeBlock`,
`Header`, `Table` and `Div` instances. `Header` is a special case here 
since its attributes are its second item ; for every other type,
the attributes come first. The transformation can be implemented as follows:

``` python
AttrHolder = (Code, Link, Image, Span, Div, CodeBlock, Header, Table, Div)

def add_class(doc):
    for elt in pandoc.iter(doc):
        if isinstance(elt, AttrHolder):
            attr_index = 0 if not isinstance(elt, Header) else 1
            identifier, classes, key_value_pairs = elt[attr_index]
            typename = type(elt).__name__.lower()
            classes.append(typename)
```

The transformation works as expected:

``` pycon
>>> markdown = """
... # Pandoc {#pandoc}
... [Link to pandoc.org](https://pandoc.org)
... """
>>> doc = pandoc.read(markdown)
>>> add_class(doc)
>>> print(pandoc.write(doc)) # doctest: +NORMALIZE_WHITESPACE
# Pandoc {#pandoc .header}
[Link to pandoc.org](https://pandoc.org){.link}
```

Note that here we can get away without changing the attribute tuple entirely
because its mutability is shallow: while we cannot rebind the reference to
its items, if these items are mutable they can still be changed in-place.
Here precisely, `classes` cannot be rebound, but since it is mutable,
its contents can be changed.

If we want to change the element ids instead, we would need to use a new tuple.
For example, to add the id `anonymous` to every attribute holder without
identifier, we can do:

```python
def add_id(doc):
    for elt in pandoc.iter(doc):
        if isinstance(elt, AttrHolder):
            attr_index = 0 if not isinstance(elt, Header) else 1
            identifier, classes, key_value_pairs = elt[attr_index]
            if not identifier:
                identifier = "anonymous"
                elt[attr_index] = identifier, classes, key_value_pairs
```

and this transformation would result in:

``` pycon
>>> add_id(doc)
>>> print(pandoc.write(doc)) # doctest: +NORMALIZE_WHITESPACE
# Pandoc {#pandoc .header}
[Link to pandoc.org](https://pandoc.org){#anonymous .link}
```


## TODO: Move fragments

(example: move some fragments to some annex)

## Deletion

**TODO.** start with a problem (either plain error or deletions that did no
go as expected?)

Deletion is conceptually similar to replacement, but a deletion may invalidate 
the next location that you are willing to delete. Give a simple example and
step by step what would happen if we were to delete the items in document 
order?

Merge with "complex replacement"? Or **before**, yes, more common use case.

**TODO.** deal with immutable content? There are a limited number of use cases
here: Attr, Target, Colspec, ListAttributes, that's all. Start with the
list of such stuff ? Or even focus with Attr or Target (mutation or deletion).
For `Target`, this is easy, the only parents are images or links ; `Attr` is 
much more pervasive.

## Transform (more extensively)

### TODO. two-pass find / replace in reverse-order pattern.

## TODO. functional style (copy / recreate, not in-place)
