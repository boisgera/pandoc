!!! warning
    This documentation is dedicated to the [latest version of the project
    available on github](https://github.com/boisgera/pandoc). 
    It is automatically tested against pandoc 2.14.2,
    [the latest release of pandoc](https://pandoc.org/releases.html) so far.


Containers and Iteration
================================================================================

``` python
import pandoc
from pandoc.types import *
```

Container
--------------------------------------------------------------------------------

All concrete[^1] Pandoc element (of type `Pandoc`, `Para`, `Str`, etc.) are list-like ;
their items are the arguments passed to their constructor. 
We present here several familiar methods to access this content.

[^1]: any custom pandoc type that can be instantiated. If needed, refer to the [kind of types](document/#kinds-of-types) section of the documentation for additional explanations.

We illustrate this interface with the `"Hello world!"` document:

``` python
meta = Meta({})
blocks = [Para([Str('Hello'), Space(), Str('world!')])]
doc = Pandoc(meta, blocks)
```

### Random access

Indexing and slicing for this element work pretty much as in lists:

``` python
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

The same patterns apply to change the element contents:

``` pycon
>>> maths = [Para([Math(InlineMath(), 'a=1')])]
>>> doc[1] = maths
>>> doc
Pandoc(Meta({}), [Para([Math(InlineMath(), 'a=1')])])
>>> meta = Meta({'title': MetaInlines([Str('Maths')])})
>>> doc[:] = meta, maths
>>> doc
Pandoc(Meta({'title': MetaInlines([Str('Maths')])}), [Para([Math(InlineMath(), 'a=1')])])
```

### Length

The length of element is the number of items it contains.
Here for `doc`, the `meta` and `blocks` arguments of its constructor:

``` pycon
>>> len(doc)
2
>>> len(doc) == len(doc[:])
True
```

### Equality

Pandoc elements can be compared. 
The equality test checks for equality of type, 
then (recusively if needed) for equality of contents:

``` pycon
>>> para = doc[1][0]
>>> para == Para([Math(InlineMath(), 'a=1')])
True
>>> para == Para([Math(DisplayMath(), 'a=1')])
False
>>> para == Para([Math(InlineMath(), 'a=2')])
False
```

### Membership

A membership test – that leverages the equality test – is also available:

``` pycon
>>> Meta({}) in doc
False
>>> Meta({'title': MetaInlines([Str('Maths')])}) in doc
True
```

### Iteration


All pandoc item can be iterated. Consider

``` python
doc = pandoc.read("Hello world!")
```

We have:

``` pycon
>>> for elt in doc:
...     print(elt)
Meta({})
[Para([Str('Hello'), Space(), Str('world!')])]
>>> meta, blocks = doc[:]
>>> for elt in meta:
...     print(elt)
{}
>>> para = blocks[0]
>>> for elt in para:
...     print(elt)
[Str('Hello'), Space(), Str('world!')]
>>> world = para[0][2]
>>> for elt in world:
...      print(elt)
world!
```

Tree Iteration
--------------------------------------------------------------------------------

### Depth-first traversal

Python's built-in `iter` – which is used implicitly in the for loops – 
yields the children of the pandoc element, 
the arguments that were given to its constructor ;
therefore it is non-recursive. 
On the contrary, `pandoc.iter` iterates a pandoc item recursively, 
in document order ; it performs a (preoder) depth-first traversal.

For example, with the following document

``` pycon
>>> doc = pandoc.read("""
... # Title
... Content
... """)
>>> doc
Pandoc(Meta({}), [Header(1, ('title', [], []), [Str('Title')]), Para([Str('Content')])])
```

we have on one hand

``` pycon
>>> for elt in iter(doc):
...     print(elt)
Meta({})
[Header(1, ('title', [], []), [Str('Title')]), Para([Str('Content')])]
```

and on the other hand

``` pycon
>>> for elt in pandoc.iter(doc):
...     print(elt)
Pandoc(Meta({}), [Header(1, ('title', [], []), [Str('Title')]), Para([Str('Content')])])
Meta({})
{}
[Header(1, ('title', [], []), [Str('Title')]), Para([Str('Content')])]
Header(1, ('title', [], []), [Str('Title')])
1
('title', [], [])
title
[]
[]
[Str('Title')]
Str('Title')
Title
Para([Str('Content')])
[Str('Content')]
Str('Content')
Content
```
### Built-in types

The `pandoc.iter` function can be applied to Python builts-in types.
For any item which is not iterable with the built-in `iter` function,
`pandoc.iter` yields the item itself:

```pycon
>>> for elt in True:
...     print(elt)
Traceback (most recent call last):
...
TypeError: 'bool' object is not iterable
>>> for elt in pandoc.iter(True):
...     print(elt)
True
>>> for elt in 1:
...     print(elt)
Traceback (most recent call last):
...
TypeError: 'int' object is not iterable
>>> for elt in pandoc.iter(1):
...     print(elt)
1
```

The same behavior applies to strings ; `pandoc.iter` does not iterate on characters:

``` pycon
>>> for elt in "Hello!":
...     print(elt)
H
e
l
l
o
!
>>> for elt in pandoc.iter("Hello!"):
...     print(elt)
Hello!
```

### TODO

  - `pandoc.iter` for lists, tuples and dicts,

  - explain `path` iteration. 