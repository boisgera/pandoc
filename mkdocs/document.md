Document structure
================================================================================

!!! warning
    This documentation is dedicated to the [latest version of the project
    available on github](https://github.com/boisgera/pandoc). 
    It is automatically tested against pandoc 2.14.1,
    [the latest release of pandoc](https://pandoc.org/releases.html) so far.


```python
import pandoc
from pandoc.types import *
```

# Meta-model

Pandoc models every document as a tree of elements. Each element has
a well-defined type such as paragraph, image, note link, etc. and of 
course the document type. These elements are combined using a well-defined
set of rules which defines the document meta-model[^1].

[^1]: A document model represents a given document. The document
meta-model represents the document model itself, or in other words 
the set of all valid documents.

Basic use of pandoc, to convert one format to another with a few configuration
options does not require to know anything about this. However, advanced usage
where one analyzes, creates or transforms the content of documents requires
at least some working knowledge of this meta-model.

# Haskell & Python

The primary source of information about pandoc's meta-model is the hierarchy
of types defined by the [pandoc-types](https://hackage.haskell.org/package/pandoc-types) 
Haskell package. The meta-model, represented by a collection of Haskell types,
is described in [the documentation of the `Text.Pandoc.Definition` module](<https://hackage.haskell.org/package/pandoc-types-1.22/docs/Text-Pandoc-Definition.html>).

However, this source of information requires some understanding of the Haskell
programming language. This pandoc Python library brings to Python the hierarchy 
of types of the pandoc Haskell library ; it also offers an alternate and 
interactive way to become familiar with this meta-model. This is what
we describe in the following sections.

# Documents

## Read and explore
The basic idea here is that you can create markdown documents that feature
exactly the kind of document constructs that you are intersted in, and
then read them as pandoc documents to see how they look like. 
By construction, these documents converted from markdown will be valid, 
that is consistent with the pandoc meta-model. 
And since you can display them, it's a great way to build some understanding
on how things work.

For example, the plain text `"Hello World!"` is represented in
the following manner:

```python
>>> text = "Hello, World!"
>>> doc = pandoc.read(text)
>>> doc
Pandoc(Meta({}), [Para([Str('Hello,'), Space(), Str('World!')])])
```

We can see that this document is an instance of the `Pandoc` type,
which contains some (empty) metadata and whose contents are a single 
paragraph which contains strings and spaces.

It's possible to explore interactively this document in a more precise manner:
```python
>>> doc
Pandoc(Meta({}), [Para([Str('Hello,'), Space(), Str('World!')])])
>>> meta = doc[0]
>>> meta
Meta({})
>>> meta[0]
{}
>>> contents = doc[1]
>>> contents
[Para([Str('Hello,'), Space(), Str('World!')])]
>>> paragraph = contents[0]
>>> paragraph
Para([Str('Hello,'), Space(), Str('World!')])
>>> paragraph[0]
[Str('Hello,'), Space(), Str('World!')]
>>> world = paragraph[0][2]
>>> world
Str('World!')
```

## Create from scratch

At this stage, even if you have not studied formally the meta-model, 
I am pretty sure that you have gathered enough knowledge to build a 
simple plain text document from scratch.

```python
>>> text = [Str("Python"), Space(), Str("&"), Space(), Str("Pandoc")]
>>> paragraph = Para(text)
>>> metadata = Meta({})
>>> doc = Pandoc(metadata, [paragraph])
```

We can check that our document is valid and describes what we are expecting
by converting it to markdown and displaying the result:
```python
>>> print(pandoc.write(doc)) # doctest: +NORMALIZE_WHITESPACE
Python & Pandoc
```

# Types 

The insights gathered in the previous sections were a good starting point to
get a feel of the possible document structure. Now, to be certain that we
always deal with valid documents, we need to explore the document meta-model 
itself, i.e. the hierarchy of pandoc types, such as
`Pandoc`, `Meta`, `Para`, `Str`, `Space`, etc.
Luckily for us, these types are self-documented: in the Python interpreter 
they are represented by a type signature. This signature described 
how they can be constructed.

For example, the top-level type `Pandoc` is represented as:
```python
>>> Pandoc
Pandoc(Meta, [Block])
```
which means that a `Pandoc` instance is defined by an instance of `Meta`
(the document metadata) and a list of blocks. In our exemple above,
the metadata was not very interesting: `Meta({})`. Still, we can make
sure that this fragment is valid: the `Meta` type signature is
```python
>>> Meta
Meta({Text: MetaValue})
```
which reads as: metadata instances contain a dictionary of `Text` keys and
`MetaValue` values. In our example, this dictionary was empty, hence we
don't need to explore the structure of `Text` and `MetaValue` any further
to conclude that the fragment is valid.

Now, let's explore the content of the document which is defined as a list of
blocks. The `Block` type signature is

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
Each `"|"` symbol in the signature represents an alternative: blocks are 
either instances of `Plain` or `Para` or `LineBlock`, etc. In our example
document, the only type of block that was used is the paragraph type `Para`,
whose signature is:
```python
>>> Para
Para([Inline])
```
Paragraphs contain a list of inlines. An inline is
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
In our plain text example, only two types of inlines where used: strings
`Str` and white space `Space`. Since
```python
>>> Str
Str(Text)
>>> Text
<class 'str'>
```
we see that `Str` merely wraps an instance of `Text` which is simply a 
synonym for the Python string type. On the other hand, the white space
is a type without any content:
```python
>>> Space
Space()
```
<!-- DEPRECATED
# Notations

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

-->