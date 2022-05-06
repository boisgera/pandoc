
Labs 🧪
================================================================================

!!! warning

    The `pandoc.labs` module is an experiment ; its interface is highly
    unstable. Don't build anything serious on top of it!


``` python
import pandoc
from pandoc.types import *
from pandoc.labs import *
```


``` python
HELLOWORLD_DOC = pandoc.read("Hello world!")
```

``` python
from urllib.request import urlopen
PATH = "raw.githubusercontent.com/commonmark/commonmark-spec"
HASH = "499ebbad90163881f51498c4c620652d0c66fb2e" # pinned version
URL = f"https://{PATH}/{HASH}/spec.txt"
COMMONMARK_SPEC = urlopen(URL).read().decode("utf-8")
COMMONMARK_DOC = pandoc.read(COMMONMARK_SPEC)
```

```python
>>> HELLOWORLD_DOC
Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])
>>> query(HELLOWORLD_DOC)
- Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])
```

**TODO.** Explain what query does: a collection which 
stores multiple document elements on which parallel operations can be applied
and that "automagically" know their location within the root document.

```python
>>> q = query(HELLOWORLD_DOC)
```

```python
>>> isinstance(q, Query)
True
```

**TODO:** consider a change of name for `Query`: `Results`, `Match`, `Collection`,
etc?

At this stage, the query only contains the document itself.

```python
>>> q
- Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])
```

### Types

The `find` method allows to select items within the initial collection.
To begin with, we can search items by type:


```python
>>> q.find(Meta)
- Meta({})
>>> q.find(Para)
- Para([Str('Hello'), Space(), Str('world!')])
```

Abstract types can also be used:

```python
>>> q.find(Block)
- Para([Str('Hello'), Space(), Str('world!')])
>>> q.find(Inline)
- Str('Hello')
- Space()
- Str('world!')
```

To find all pandoc elements:

```python
>>> q.find(Type)
- Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])
- Meta({})
- Para([Str('Hello'), Space(), Str('world!')])
- Str('Hello')
- Space()
- Str('world!')
```

Finding python builtin types works too:

```python
>>> q.find(dict)
- {}
>>> q.find(list)
- [Para([Str('Hello'), Space(), Str('world!')])]
- [Str('Hello'), Space(), Str('world!')]
>>> q.find(str)
- 'Hello'
- 'world!'
```

To get every possible item, in document order, we can search for Python objects:

```python
>>> q.find(object)
- Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])
- Meta({})
- {}
- [Para([Str('Hello'), Space(), Str('world!')])]
- Para([Str('Hello'), Space(), Str('world!')])
- [Str('Hello'), Space(), Str('world!')]
- Str('Hello')
- 'Hello'
- Space()
- Str('world!')
- 'world!'
```

### Logic

We can search for items that match one of several conditions:
```python
>>> q.find(Str, Space)
- Str('Hello')
- Space()
- Str('world!')
```

If the list of arguments is empty, there is no match:
```python
>>> q.find()
<BLANKLINE>
```
In a boolean context, a query with no results is considered `False`

```python
>>> bool(q.find())
False
>>> if not q.find():
...     print("no result")
no result
```

To add match several conditions at once, the `filter` method can be used:

```python
>>> q.find(Inline).filter(Str)
- Str('Hello')
- Str('world!')
```
The `filter` method can be used implicitly: a query is callable
```python
>>> q.find(Inline)(Str)
- Str('Hello')
- Str('world!')
```

We can also match the negation of a condition

```python
>>> q.find(Inline)(not_(Space))
- Str('Hello')
- Str('world!')
```

### Tests

Types are not the only possible selectors, predicates -- functions that take
a pandoc element and return a boolean value -- can be used too:

```python
>>> def startswith_H(elt):
...     return isinstance(elt, Str) and elt[0].startswith("H")
... 
>>> q.find(startswith_H)
- Str('Hello')
```

You can use predicate to define and select "virtual types" in a document.
For example,

```python
def AttrHolder(elt):
    return isinstance(elt, (Code, Link, Image, Span, Div, CodeBlock, Header, Table))
```

**TODO:** match by attributes (id, classes, key-values); use keyword arguments 
in find with "or" semantics for lists; allow for predicates. For key values
match, match for key existence, key-value pair, predicate as a whole or just
for value.


### Navigation


**TODO.** Parent, children, next, previous, next_sibling, previous_sibling.

```python
>>> q
- Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])
>>> q.next
- Meta({})
>>> q.next.next
- {}
>>> q.next.next.next
- [Para([Str('Hello'), Space(), Str('world!')])]
>>> q.next.next.next.next
- Para([Str('Hello'), Space(), Str('world!')])
>>> q.next.next.next.next.next
- [Str('Hello'), Space(), Str('world!')]
>>> q.next.next.next.next.next.next
- Str('Hello')
>>> q.next.next.next.next.next.next.next
- 'Hello'
>>> q.next.next.next.next.next.next.next.next
- Space()
>>> q.next.next.next.next.next.next.next.next.next
- Str('world!')
>>> q.next.next.next.next.next.next.next.next.next.next
- 'world!'
>>> q.next.next.next.next.next.next.next.next.next.next.next
<BLANKLINE>
```

```python
>>> q.find(str)
- 'Hello'
- 'world!'
>>> q.find(str)[1]
- 'world!'
>>> w = q.find(str)[1]
>>> w.previous
- Str('world!')
>>> w.previous.previous
- Space()
>>> w.previous.previous.previous
- 'Hello'
>>> w.previous.previous.previous.previous
- Str('Hello')
>>> w.previous.previous.previous.previous.previous
- [Str('Hello'), Space(), Str('world!')]
>>> w.previous.previous.previous.previous.previous.previous
- Para([Str('Hello'), Space(), Str('world!')])
>>> w.previous.previous.previous.previous.previous.previous.previous
- [Para([Str('Hello'), Space(), Str('world!')])]
>>> w.previous.previous.previous.previous.previous.previous.previous.previous
- {}
>>> w.previous.previous.previous.previous.previous.previous.previous.previous.previous
- Meta({})
>>> w.previous.previous.previous.previous.previous.previous.previous.previous.previous.previous
- Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])
>>> w.previous.previous.previous.previous.previous.previous.previous.previous.previous.previous.previous
<BLANKLINE>
```


--------------------------------------------------------------------------------


Nota: finding lists of inlines is difficult; finding *non-empty* lists of
inlines is easy, but empty lists is harder, we need to use some knowledge
of the type hierarchy.


<!--

``` pycon
#>>> f(HELLOWORLD_DOC, Meta)
#[Meta({})]
#>>> f(HELLOWORLD_DOC, Para)
#[Para([Str('Hello'), Space(), Str('world!')])]
#>>> f(HELLOWORLD_DOC, Str)
#[Str('Hello'), Str('world!')]
#>>> f(HELLOWORLD_DOC, LineBreak)
#[]
```

Types or multiple types can be specified (this is similar to what `isinstance`
does):

``` pycon
#>>> f(HELLOWORLD_DOC, (Str, Space))
#[Str('Hello'), Space(), Str('world!')]
```

Complex conditions based on types and values can be factored out in 
a predicate function, such as `is_http_or_https_link`:

``` python
#def get_url(link):
#    target = link[2] # link: Link(Attr, [Inline], Target)
#    url = target[0] # target: (Text, Text)
#    return url
#
#def is_http_or_https_link(elt):
#    if isinstance(elt, Link):
#        url = get_url(link=elt)
#        return url.startswith("http:") or url.startswith("https:")
#    else:
#        return False
```

``` pycon
#>>> for link in f(COMMONMARK_DOC, is_http_or_https_link):
#...     print(get_url(link))
#http://creativecommons.org/licenses/by-sa/4.0/
#http://daringfireball.net/projects/markdown/syntax
#http://daringfireball.net/projects/markdown/
#http://www.methods.co.nz/asciidoc/
#http://daringfireball.net/projects/markdown/syntax
#http://article.gmane.org/gmane.text.markdown.general/1997
#http://article.gmane.org/gmane.text.markdown.general/2146
#http://article.gmane.org/gmane.text.markdown.general/2554
#https://html.spec.whatwg.org/entities.json
#http://www.aaronsw.com/2002/atx/atx.py
#http://docutils.sourceforge.net/rst.html
#http://daringfireball.net/projects/markdown/syntax#em
#http://www.vfmd.org/vfmd-spec/specification/#procedure-for-identifying-emphasis-tags
#https://html.spec.whatwg.org/multipage/forms.html#e-mail-state-(type=email)
#http://www.w3.org/TR/html5/syntax.html#comments
```


Calling the finder as a method works too:

``` pycon
#>>> HELLOWORLD_DOC.f(Meta)
#[Meta({})]
#>>> HELLOWORLD_DOC.f(Para)
#[Para([Str('Hello'), Space(), Str('world!')])]
#>>> HELLOWORLD_DOC.f(Str)
#[Str('Hello'), Str('world!')]
#>>> HELLOWORLD_DOC.f(LineBreak)
#[]
```

``` pycon
#>>> COMMONMARK_DOC.f(Meta)
#[Meta({'author': MetaInlines([Str('John'), Space(), Str('MacFarlane')]), 'date': MetaInlines([Str('2021-06-19')]), 'license': MetaInlines([Link(('', [], []), [Str('CC-BY-SA'), Space(), Str('4.0')], ('http://creativecommons.org/licenses/by-sa/4.0/', ''))]), 'title': MetaInlines([Str('CommonMark'), Space(), Str('Spec')]), 'version': MetaInlines([Str('0.30')])})]
#>>> COMMONMARK_DOC.f(Meta)[0]
#{'author': MetaInlines([Str('John'), Space(), Str('MacFarlane')]), 'date': MetaInlines([Str('2021-06-19')]), 'license': MetaInlines([Link(('', [], []), [Str('CC-BY-SA'), Space(), Str('4.0')], ('http://creativecommons.org/licenses/by-sa/4.0/', ''))]), 'title': MetaInlines([Str('CommonMark'), Space(), Str('Spec')]), 'version': MetaInlines([Str('0.30')])})
```

-->
