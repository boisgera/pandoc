
⚠️ Random notes & TODOs.

```python
import pandoc
from pandoc.types import *
```

# Find / Analyze / etc.

```python
# elts = [elt for elt in pandoc.iter(doc) if condition(elt)]
```

# Replacement

To replace items, for example all instances of emphasized text with strong text,
you first need locate emphasized text instances, that is find the collections
of holders `holder` and indices `i` such that `emph = holder[i]`.

```python
# emph_locations = []
# for elt, path in pandoc.iter(doc, path=True):
#     if isinstance(elt, Emph):
#         holder, i = path[-1]
#         emph_locations.append((holder, i))
```

**Question.** When is the "not-reversed-scheme" ok? When are the next locations
still valid? Even with most recursive scheme, that should be ok. Think more of
it here & document the stuff. Distinguish simple replacement with "extensive
surgery" that may invalidate the inner locations. Talk about (shallow) replacement?

```python
# >>> for holder, i in emph_locations:
# ...    emph = holder[i] 
# ...    inlines = emph[0] # Emph signature is Emph([Inline])
# ...    strong = Strong(inlines) # Strong signature is Strong([Inline])
# ...    holder[i] = strong
```

## Transformation of Immutable Data

!!! warning 
    Issue intertwined with the "type synomym" and "type safety" issue 
    at the moment. Revisit/improve?

Say that you want to find all links in your document whose target URL is
`"https://pandoc.org"` and make sure that the associated title is 
`"Pandoc - About pandoc"`. The relevant piece of the document structure is:

```python
>>> Link
Link(Attr, [Inline], Target)
>>> Target
Target = (Text, Text)
```

You may be tempted to iterate the document to find all pairs of text[^0],
then select those whose first item is "`https://pandoc.org`" and modify them. 
But this approach will not work:

  1. It is unsafe: you may find some items which are not targets[^1].
  
  2. You cannot modify the targets in-place since tuples are immutable.

[^0]: `Target` is not a "real" type but a mere synonym for pairs of `Text`. 
There are not instances of `Target` and thus attempts to pattern 
match targets with `isinstance(..., Text)` will always fail.

[^1]: these items would simply happen to share the same structure. 
      For example, this can happend with attributes: 
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
>>> pandoc.write(doc)
'[Link to pandoc.org](https://pandoc.org "Pandoc - About pandoc")\n'
```

There are a few other types in the document structure that are also immutable,
the most notable being `Attr`:

```python
>>> Attr
Attr = (Text, [Text], [(Text, Text)])
```

`Attr` is composed of an identifier, a list of classes, and a list of
key-value pairs. To transform `Attr` content, again the easiest way to
proceed is to target their holders. Say that we want add a numbered
"anonymous" identifier for inline elements wit no identifier. 
Since we have

```python
>>> Inline
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

we need to target `Code`, `Link`, `Image` and `Span` instances.

```python
def add_id(doc):
    id_number = 1
    for elt in pandoc.iter(doc):
        if isinstance(elt, (Code, Link, Image, Span)):
            identifier, classes, key_value_pairs = elt[0]
            if not identifier:
                identifier = f"anonymous-{id_number:02}"
                elt[0] = identifier, classes, key_value_pairs
                id_number += 1
```

```python
>>> doc = pandoc.read("[Link to pandoc.org](https://pandoc.org)")
>>> add_id(doc)
>>> pandoc.write(doc)
'[Link to pandoc.org](https://pandoc.org){#anonymous-01}\n'
```

# TODO: Move fragments

(example: move some fragments to some annex)

# Deletion

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



# Transform (more extensively)



## TODO. two-pass find / replace in reverse-order pattern.



## TODO. deal with tuples / immutability