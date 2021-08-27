
⚠️ Random notes & TODOs.

```python
import pandoc
from pandoc.types import *
```

# Find / Analyze / etc.

```python
elts = [elt for elt in pandoc.iter(doc) if condition(elt)]
```

# Replacement

To replace items, for example all instances of emphasized text with strong text,
you first need locate emphasized text instances, that is find the collections
of holders `holder` and indices `i` such that `emph = holder[i]`.

```python
emph_locations = []
for elt, path in pandoc.iter(doc, path=True):
    if isinstance(elt, Emph):
        holder, i = path[-1]
        emph_locations.append((holder, i))
```

**Question.** When is the "not-reversed-scheme" ok? When are the next locations
still valid? Even with most recursive scheme, that should be ok. Think more of
it here & document the stuff. Distinguish simple replacement with "extensive
surgery" that may invalidate the inner locations. Talk about (shallow) replacement?

```python
>>> for holder, i in emph_locations:
...    emph = holder[i] 
...    inlines = emph[0] # Emph signature is Emph([Inline])
...    strong = Strong(inlines) # Strong signature is Strong([Inline])
...    holder[i] = strong
```

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