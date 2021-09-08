!!! warning
    This documentation is dedicated to the [latest version of the project
    available on github](https://github.com/boisgera/pandoc). 
    It is automatically tested against pandoc 2.14.1,
    [the latest release of pandoc](https://pandoc.org/releases.html) so far.


Containers and Iteration
================================================================================

```python
import pandoc
from pandoc.types import *
```

Container Interface
--------------------------------------------------------------------------------

All concrete[^1] Pandoc data types (`Pandoc`, `Para`, `Str`, etc.) are list-like ;
their items are the arguments passed to their constructor. 
We present here several familiar methods to access this content.

[^1]: any custom pandoc type that can be instantiated. If needed, refer to the [kind of types](document/#kinds-of-types) section of the documentation for additional explanations.

We illustrate this interace with the following `doc` instance of the `Pandoc` type:

```python
meta = Meta({})
blocks = [Para([Str('Hello'), Space(), Str('world!')])]
doc = Pandoc(meta, blocks)
```

Indexing and slicing for this object work pretty much as in lists:
```python
>>> doc[0]
Meta({})
>>> doc[1]
[Para([Str('Hello'), Space(), Str('world!')])]
>>> meta, blocks = doc[:]
>>> meta
Meta({})
>>> blocks
[Para([Str('Hello'), Space(), Str('world!')])]
```

The same patterns apply to change the object contents:

```python
>>> maths = [Para([Math(InlineMath(), 'a=1')])]
>>> doc[1] = maths
>>> doc
Pandoc(Meta({}), [Para([Math(InlineMath(), 'a=1')])])
>>> meta = Meta({'title': MetaInlines([Str('Maths')])})
>>> doc[:] = meta, maths
>>> doc
Pandoc(Meta({'title': MetaInlines([Str('Maths')])}), [Para([Math(InlineMath(), 'a=1')])])
```

The length of `doc` counts the number of items it contains
(here: the `meta` and `blocks` arguments of its constructor):
```python
>>> len(doc)
2
>>> len(doc) == len(doc[:])
True
```

Two instances of concrete pandoc types can be compared. 
The equality test checks for equality of type, 
then (recusively if needed) for equality of contents:

```python
>>> para = doc[1][0]
>>> para == Para([Math(InlineMath(), 'a=1')])
True
>>> para == Para([Math(DisplayMath(), 'a=1')])
False
>>> para == Para([Math(InlineMath(), 'a=2')])
False
```

The membership test is also available:
```python
>>> Meta({}) in doc
False
>>> Meta({'title': MetaInlines([Str('Maths')])}) in doc
True
```

And finally, the items of a concrete pandoc type can be iterated:
```python
>>> for elt in doc:
...     print(elt)
Meta({'title': MetaInlines([Str('Maths')])})
[Para([Math(InlineMath(), 'a=1')])]
```



Document Iteration
--------------------------------------------------------------------------------

`iter` is non-recursive. `pandoc.iter` is

(preorder) depth-first traversal, document order, etc.

  - `pandoc.iter` (examples, use `NORMALIZE_WHITESPACE` when appropriate)

  - `pandoc.iter` manages dicts (and strings) differently, explain

  - explain `path` iteration. 