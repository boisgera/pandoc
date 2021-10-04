!!! warning
    This documentation is dedicated to the [latest version of the project
    available on github](https://github.com/boisgera/pandoc). 
    It is automatically tested against pandoc 2.14.2,
    [the latest release of pandoc](https://pandoc.org/releases.html) so far.


Containers and iteration
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
yields the children of the pandoc element, that is the arguments 
that were given to its constructor ;
it is non-recursive: the contents of these children are not explored. 

On the contrary, `pandoc.iter` iterates a pandoc item recursively, 
in document order. It performs a (preoder) depth-first traversal:
the iteration first yields the element given as argument to `pandoc.iter`
(the root), then its first child (if any), then the first child of this child 
(if any), etc. recursively, before it yields the second child of the root (if
any), then the first child of this child, etc.

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

### Python built-in types

#### Numbers

Tree iteration can be applied to Python builts-in types, including those which
are not usually considered containers and thus are not iterable with the
built-in `iter` function. The `Bool`, `Int` and `Double` primitive types
(that is `bool`, `int` and `float`) fall in this case:


``` pycon
>>> assert isinstance(True, Bool)
>>> iter(True)
Traceback (most recent call last):
...
TypeError: 'bool' object is not iterable
```

``` pycon
>>> assert isinstance(1, Int)
>>> iter(1)
Traceback (most recent call last):
...
TypeError: 'int' object is not iterable
```

``` pycon
>>> assert isinstance(3.14, Double)
>>> iter(3.14)
Traceback (most recent call last):
...
TypeError: 'float' object is not iterable
```

Since these elements have no child, tree iteration will only yield the elements
themselves:

``` pycon
>>> for elt in pandoc.iter(True):
...     print(elt)
True
>>> for elt in pandoc.iter(1):
...     print(elt)
1
>>> for elt in pandoc.iter(3.14):
...     print(elt)
3.14
```

#### Strings

Python strings are iterable, but in the context of tree iteration, we consider
them as atomic objects like booleans, integers and doubles. Thus `pandoc.iter` 
will not iterate on characters like the built-in `iter` function:

``` pycon
>>> isinstance("Hello!", Text)
True
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

#### Tuples, lists, dicts

Tree iteration for tuples holds no surprise:

``` pycon
>>> elts = (1, (2, 3))
>>> for elt in elts:
...     print(elt)
1
(2, 3)
>>> for elt in pandoc.iter(elts):
...     print(elt)
(1, (2, 3))
1
(2, 3)
2
3
```

List iteration is very similar:

``` pycon
>>> elts = [1, [2, 3]]
>>> for elt in elts:
...     print(elt)
1
[2, 3]
>>> for elt in pandoc.iter(elts):
...     print(elt)
[1, [2, 3]]
1
[2, 3]
2
3
```

For maps/dicts, tree iteration combine recursivity and iteration on key-value
pairs, while standard iteration is flat and iterates on keys only. In other
words, tree iteration adds recursivity to the dict `items` iterator:

``` pycon
>>> elts = {"a": True, "b": [1, 2]}
>>> for elt in elts:
...     print(elt)
a
b
>>> for elt in elts.items():
...     print(elt)
('a', True)
('b', [1, 2])
>>> for elt in pandoc.iter(elts):
...     print(elt)
{'a': True, 'b': [1, 2]}
('a', True)
a
True
('b', [1, 2])
b
[1, 2]
1
2
```

### Path 

#### Principles

The function `pandoc.iter` accepts an optional boolean argument `path`.
When it is set to `True`, the iteration returns `elt, path` pairs.
In this pair, `elt` is equal to what the iteration with `path` set to
`False` would have yielded and `path` contains additional 
information about the location of `elt` in the iteration root.

Path is a list of `(holder, i)` pairs which is not empty unless `elt` is `root` and such that:

  - the first holder in the path is the root of the iteration,
  
  - the i-th item in holder is the next holder in the path ...

  - or `elt` if we are at the end of the path.

Here i-th item in holder should be understood as `holder[i]` unless `holder`
is a dict. In this special case, it would be its i-th key-value pair:

``` python
def getitem(elt, i):
    if isinstance(elt, dict):
        elt = list(elt.items())
    return elt[i]
```

In any case, the following assertion is always valid:

``` python
def check(root, elt, path):
    if path == []:
        assert elt is root
    else:
        assert path[0][0] is root
        for i, (holder, index) in enumerate(path):
            next_elt = getitem(holder, index)
            if i < len(path) - 1:
                assert next_elt is path[i+1][0]
            else:
                assert next_elt is elt
```

And indeed, if we consider the following document:

``` python
doc = pandoc.read("""
# Title
Content
""")
```

the check works at any level:

``` pycon
>>> for elt, path in pandoc.iter(doc, path=True):
...     check(doc, elt, path)
```


#### Use cases

The length of `path` provides the depth of `elt` with respect to the root:

```pycon
>>> for elt, path in pandoc.iter(doc, path=True):
...     print(f"{len(path)} - {elt!r}")
0 - Pandoc(Meta({}), [Header(1, ('title', [], []), [Str('Title')]), Para([Str('Content')])])
1 - Meta({})
2 - {}
1 - [Header(1, ('title', [], []), [Str('Title')]), Para([Str('Content')])]
2 - Header(1, ('title', [], []), [Str('Title')])
3 - 1
3 - ('title', [], [])
4 - 'title'
4 - []
4 - []
3 - [Str('Title')]
4 - Str('Title')
5 - 'Title'
2 - Para([Str('Content')])
3 - [Str('Content')]
4 - Str('Content')
5 - 'Content'
```

The latest item of `path` provides the parent of the current element
and its index in this parent:

``` pycon
>>> for elt, path in pandoc.iter(doc, path=True):
...     try:
...         holder, index = path[-1]
...         print(f"{elt!r} == {holder!r}[{index}]")
...     except IndexError:
...         assert elt is doc
Meta({}) == Pandoc(Meta({}), [Header(1, ('title', [], []), [Str('Title')]), Para([Str('Content')])])[0]
{} == Meta({})[0]
[Header(1, ('title', [], []), [Str('Title')]), Para([Str('Content')])] == Pandoc(Meta({}), [Header(1, ('title', [], []), [Str('Title')]), Para([Str('Content')])])[1]
Header(1, ('title', [], []), [Str('Title')]) == [Header(1, ('title', [], []), [Str('Title')]), Para([Str('Content')])][0]
1 == Header(1, ('title', [], []), [Str('Title')])[0]
('title', [], []) == Header(1, ('title', [], []), [Str('Title')])[1]
'title' == ('title', [], [])[0]
[] == ('title', [], [])[1]
[] == ('title', [], [])[2]
[Str('Title')] == Header(1, ('title', [], []), [Str('Title')])[2]
Str('Title') == [Str('Title')][0]
'Title' == Str('Title')[0]
Para([Str('Content')]) == [Header(1, ('title', [], []), [Str('Title')]), Para([Str('Content')])][1]
[Str('Content')] == Para([Str('Content')])[0]
Str('Content') == [Str('Content')][0]
'Content' == Str('Content')[0]
```

Grand-parents are available in the previous path items, all the way up to the
root, allowing us to locate the current element with respect to the root if
needed:

``` pycon
>>> for elt, path in pandoc.iter(doc, path=True):
...     indices = [i for holder, i in path]
...     z = "".join(f"[{i}]" for i in indices)
...     print(f"doc{z} == {elt!r}")
doc == Pandoc(Meta({}), [Header(1, ('title', [], []), [Str('Title')]), Para([Str('Content')])])
doc[0] == Meta({})
doc[0][0] == {}
doc[1] == [Header(1, ('title', [], []), [Str('Title')]), Para([Str('Content')])]
doc[1][0] == Header(1, ('title', [], []), [Str('Title')])
doc[1][0][0] == 1
doc[1][0][1] == ('title', [], [])
doc[1][0][1][0] == 'title'
doc[1][0][1][1] == []
doc[1][0][1][2] == []
doc[1][0][2] == [Str('Title')]
doc[1][0][2][0] == Str('Title')
doc[1][0][2][0][0] == 'Title'
doc[1][1] == Para([Str('Content')])
doc[1][1][0] == [Str('Content')]
doc[1][1][0][0] == Str('Content')
doc[1][1][0][0][0] == 'Content'
```
