
# Cookbook

⚠️ Random notes & TODOs.

```python
import pandoc
from pandoc.types import *
```

## Fetch


**TODO.** explain use get (get info, analysis, read-only)

**TODO.** explain commonmark spec doc.

```python
from urllib.request import urlopen
PATH = "raw.githubusercontent.com/commonmark/commonmark-spec"
HASH = "499ebbad90163881f51498c4c620652d0c66fb2e" 
URL = f"https://{PATH}/{HASH}/spec.txt"
COMMONMARK_SPEC = urlopen(URL).read().decode("utf-8")
```

```python
doc = pandoc.read(COMMONMARK_SPEC)
```

Display all external (http/https) link URLs used in the commonmark specification.

``` python
def display_external_links(doc):
    links = [elt for elt in pandoc.iter(doc) if isinstance(elt, Link)]
    for link in links:
        _, _, target = link # Link signature is Link(Attr, [Inline], Target)
        url, title = target # Target signature is (Text, Text)
        if url.startswith("http"):
            print(url)
```

```python
>>> display_external_links(doc)
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

## Find (/ Analyze / etc.)

```python
# elts = [elt for elt in pandoc.iter(doc) if condition(elt)]
```

**TODO.** differentiate fetch (get the stuff matching a pattern) from find
(get their path, either holder index or from the top).

## Replace

"Find-and-replace" is a very frequent pattern in document transformations.
In most use cases, the implementation is straightforward ; but some others
require a bit more subtelty.

**TODO.** Don't change while you iterate.

For example, to replace all instances of emphasized text with strong text,
you first need locate emphasized text instances, that is find the collections
of holders `holder` and indices `i` such that `emph = holder[i]`.

```python
doc = pandoc.read("""
# Title with *emphasis*
Text with *emphasis*.
""")
```

```python
emph_locations = []
for elt, path in pandoc.iter(doc, path=True):
    if isinstance(elt, Emph):
        holder, i = path[-1]
        emph_locations.append((holder, i))
```

```python
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



## Immutable data

Every non-trivial pandoc document contains data that is immutable.
To perform in-place modifications of your document, 
you have to deal with them specifically. And this is a good thing!

### Hello world!
Consider the most basic "Hello world!" paragraph:

```python
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

```python
>>> text[:] = "pandoc!"
Traceback (most recent call last):
...
TypeError: 'str' object does not support item assignment
```

Does it mean that we cannot modify any word of this sentence?
Absolutely not! Because instead of modifying the Python string,
we can *replace it* in its container instead:

```python
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
```python
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
```python
>>> invalid_blocks = [
...     RawBlock(Format('pandoc'), '<p>'), 
...     Plain([Str('pandoc'), Space(), Str('rocks!')]),  
...     RawBlock(Format('pandoc'), '</p>')
... ]
```
Fortunately this approach will fail loudly:
```python
>>> for elt in pandoc.iter(blocks):
...     if elt == "html":
...         elt[:] = "pandoc"
Traceback (most recent call last):
...
TypeError: 'str' object does not support item assignment
```
A correct, type-safe, way to proceed is instead:
```python
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
```python
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

```python
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
      the third component of every attribute -- its list of key-value pairs -- 
      will contain some pairs of `Text` if it's not empty.

The easiest way to handle this situation is to search for links that target 
pandoc's web site.

```python
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

```python
>>> Attr
Attr = (Text, [Text], [(Text, Text)])
```

`Attr` is composed of an identifier, a list of classes, and a list of
key-value pairs. To transform `Attr` content, again the easiest way to
proceed is to target their holders. Say that we want add a class tag 
that described the type of the pandoc element for every element which 
is a `Attr` holder. 
The relevant type signatures – we display all `Attr` holders – are:

```python
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

```python
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

```python
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
```python
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
```python
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