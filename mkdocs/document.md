Document
================================================================================

!!! warning
    This documentation is dedicated to the [latest version of the project
    available on github](https://github.com/boisgera/pandoc). 
    It is automatically tested against pandoc 2.14.1,
    [the latest release of pandoc](https://pandoc.org/releases.html) so far.

!!! note "TODO"
    Use the new metaclass-based representation to drive an exploration of the
    document model. Link to the proper documentation when needed, or use
    exemple from markdown text to see what every construct is about.

    Explore an existing document or create from scratch?
    First explore, then build from scratch?

    Explain that the person willing to analyze/transform documents has to 
    understand how each (or some of the) document pieces are represented?
    And that it's what we try to do here?


```python
import pandoc
from pandoc.types import *
```

```python
>>> text = "Hello, World!"
>>> doc = pandoc.read(text)
>>> doc
Pandoc(Meta({}), [Para([Str('Hello,'), Space(), Str('World!')])])
```

A document is an instance of the `Pandoc` class; it has two arguments

```python
>>> Pandoc
Pandoc(Meta, [Block])
```

The first argument, the instance of `Meta`, represents the document metadata.
Since in this very simple example there is no metadata, we will ignore it and
focus on the second argument instead, the document contents, which 
is a list of blocks:

```python
>>> blocks = doc[1]
>>> blocks
[Para([Str('Hello,'), Space(), Str('World!')])]
```

Actually, there is a single block here

```python
>>> len(blocks)
1
```

There are several possible types of blocks: headers, paragraphs, lists, etc.

```python
>>> Block
Block = Plain([Inline])
      | Para([Inline])
      | LineBlock([[Inline]])
      | CodeBlock(Attr, Text)
      | RawBlock(Format, Text)
      | BlockQuote([Block])
      | OrderedList(ListAttributes, [[Block]])
      | BulletList([[Block]])
      | DefinitionList([([Inline], [[Block]])])
      | Header(Int, Attr, [Inline])
      | HorizontalRule()
      | Table(Attr, Caption, [ColSpec], TableHead, [TableBody], TableFoot)
      | Div(Attr, [Block])
      | Null()
```

Here our single block is a paragraph:

```python
>>> para = blocks[0]
>>> para
Para([Str('Hello,'), Space(), Str('World!')])
>>> isinstance(para, Para)
True
```

In general, paragraphs contain lists of inline elements:

```python
>>> Para
Para([Inline])
>>> inlines = para[0]
```

Inlines can be several things: ordinary text, emphasized text,
strong text, etc.

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

Here we simply have a mixture of ordinary text and space.

```python
>>> inlines = para[0]
>>> inlines
[Str('Hello,'), Space(), Str('World!')]
```

Instances of `Space` have no argument while instances of `Str` 
contain a text Text

```python
>>> Space
Space()
>>> Str
Str(Text)
>>> Text == type(u"")
True
```

Finally

```python
>>> print(inlines[0][0] + " " + inlines[2][0])
Hello, World!
```

