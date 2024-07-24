Document structure
================================================================================

``` python
import pandoc
from pandoc.types import *
```

Meta-model
--------------------------------------------------------------------------------

Pandoc models every document as a tree of elements. Each element has
a well-defined type such as paragraph, image, note link, etc. and of
course the document type. These elements are combined using a well-defined
set of rules which defines the document meta-model[^1].

[^1]: A document model represents a given document. The document
meta-model represents the document model itself, i.e. the set of all valid
documents.

Pandoc can be used a converter between different document formats;
this usage requires very little knowledge about the document structure.
However, if one wishes to analyze, create or transform documents,
some working knowledge of this meta-model becomes necessary.

Haskell & Python
--------------------------------------------------------------------------------

The primary source of information about pandoc's meta-model is the hierarchy
of types defined by the [pandoc-types](https://hackage.haskell.org/package/pandoc-types)
Haskell package. The meta-model, represented by a collection of Haskell types,
is described in [the documentation of the `Text.Pandoc.Definition` module](<https://hackage.haskell.org/package/pandoc-types-1.22/docs/Text-Pandoc-Definition.html>).

However, this source of information requires some understanding of the Haskell
programming language. The pandoc Python library brings to Python this hierarchy
of types ; it also offers an alternate and interactive way to become familiar
with the meta-model. This is what we describe in the following sections.

Documents
--------------------------------------------------------------------------------

### Explore

The basic idea here is that you can create markdown documents that feature
exactly the kind of document constructs that you are interested in, and
then read them as pandoc documents to see how they look like.
By construction, these documents converted from markdown will be valid,
i.e. consistent with the pandoc meta-model.
And since you can display them, it's a great way to build some understanding
on how things work.

For example, the plain text `"Hello World!"` is represented in
the following manner:

``` pycon
>>> text = "Hello, World!"
>>> doc = pandoc.read(text)
>>> doc
Pandoc(Meta({}), [Para([Str('Hello,'), Space(), Str('World!')])])
```

We can see that this document is an instance of the `Pandoc` type,
which contains some (empty) metadata and whose contents are a single
paragraph which contains strings and spaces.

It's possible to explore interactively this document in a more precise manner:

``` pycon
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

I recommend that you try to reproduce the process above for small documents
that feature titles, headers, emphasized text, lists, etc. to become familiar
with the way that these constructs are described in pandoc documents.

### Create

At this stage, even if we have not yet described formally the meta-model,
we have already gathered enough knowledge to build a simple plain text document
from scratch.

``` pycon
>>> text = [Str("Python"), Space(), Str("&"), Space(), Str("Pandoc")]
>>> paragraph = Para(text)
>>> metadata = Meta({})
>>> doc = Pandoc(metadata, [paragraph])
```

We can check that our document is valid and describes what we are expecting
by converting it to markdown and displaying the result:

``` pycon
>>> print(pandoc.write(doc)) # doctest: +NORMALIZE_WHITESPACE
Python & Pandoc
```

Types
--------------------------------------------------------------------------------

### Explore

The insights gathered in the previous sections were a good starting point to
get a feel of the possible document structure. Now, to be certain that we
always deal with valid documents, we need to explore the document meta-model
itself, i.e. the hierarchy of pandoc types, such as
`Pandoc`, `Meta`, `Para`, `Str`, `Space`, etc.
Luckily for us, these types are self-documented: in the Python interpreter
they are represented by a type signature. This signature described
how they can be constructed.

For example, the top-level type `Pandoc` is represented as:

``` pycon
>>> Pandoc
Pandoc(Meta, [Block])
```

which means that a `Pandoc` instance is defined by an instance of `Meta`
(the document metadata) and a list of blocks. In our exemple above,
the metadata was not very interesting: `Meta({})`. Still, we can make
sure that this fragment is valid: the `Meta` type signature is

``` pycon
>>> Meta
Meta({Text: MetaValue})
```

which reads as: metadata instances contain a dictionary of `Text` keys and
`MetaValue` values. In our example, this dictionary was empty, hence we
don't need to explore the structure of `Text` and `MetaValue` any further
to conclude that the fragment is valid.

Now, let's explore the content of the document which is defined as a list of
blocks. The `Block` type signature is

``` pycon
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
      | Figure(Attr, Caption, [Block])
      | Div(Attr, [Block])
```

Each `"|"` symbol in the signature represents an alternative: blocks are
either instances of `Plain` or `Para` or `LineBlock`, etc. In our example
document, the only type of block that was used is the paragraph type `Para`,
whose signature is:

``` pycon
>>> Para
Para([Inline])
```

Paragraphs contain a list of inlines. An inline is

``` pycon
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

``` pycon
>>> Str
Str(Text)
>>> Text
<class 'str'>
```

we see that `Str` merely wraps an instance of `Text` which is simply a
synonym for the Python string type. On the other hand, the white space
is a type without any content:

``` pycon
>>> Space
Space()
```

We now have successfully discovered all pandoc types used in our simple
"Hello world!" document. Again, I recommend that you reproduce this process
for all document constructs that you are interested in.

### Kinds of Types

The types defined in `pandoc.types` are either data types, typedefs or aliases
for Python built-ins.

``` pycon
>>> from pandoc.types import *
```

The `Pandoc` type is an example of data type:

``` pycon
>>> issubclass(Pandoc, Type)
True
>>> issubclass(Pandoc, Data)
True
```

Data types come in two flavors: abstract or concrete. The signature of abstract
data types lists the collection of concrete types they correspond to:

``` pycon
>>> Inline # doctest: +ELLIPSIS
Inline = Str(Text)
       | Emph([Inline])
       | Underline([Inline])
       | Strong([Inline])
...
>>> issubclass(Inline, Type)
True
>>> issubclass(Inline, Data)
True
```

The concrete types on the right-hand side of this signature are constructor
(concrete) types. The abstract type itself is not a constructor ;
it cannot be instantiated:

``` pycon
>>> issubclass(Inline, Constructor)
False
>>> Inline()
Traceback (most recent call last):
...
TypeError: Can't instantiate abstract class Inline
```

The constructors associated to some abstract data type are concrete:

``` pycon
>>> issubclass(Str, Type)
True
>>> issubclass(Str, Data)
True
>>> issubclass(Str, Constructor)
True
```

They can be instantiated and the classic inheritance test apply:

``` pycon
>>> string = Str("Hello")
>>> isinstance(string, Str)
True
```

Constructor types inherit from the corresponding abstract data type:

``` pycon
>>> issubclass(Str, Inline)
True
>>> isinstance(string, Inline)
True
```

Typedefs are also another kind of abstract type. They are merely introduced
so that we can name some constructs in the type hierarchy, but no instance
of such types exist in documents. For example, consider
the `Attr` and `Target` types:

``` pycon
>>> Attr
Attr = (Text, [Text], [(Text, Text)])
>>> Target
Target = (Text, Text)
```

They are pandoc types which are not data types but typedefs:

``` pycon
>>> issubclass(Attr, Type)
True
>>> issubclass(Attr, Data)
False
>>> issubclass(Attr, TypeDef)
True
>>> issubclass(Target, Type)
True
>>> issubclass(Target, Data)
False
>>> issubclass(Target, TypeDef)
True
```

They enable more compact and readable types signatures.
For example, with typedefs, the `Link` signature is:

``` pycon
>>> Link
Link(Attr, [Inline], Target)
```

instead of `Link((Text, [Text], [(Text, Text)]), [Inline], (Text, Text))`
without them.

<!--

???+ error "TODO"
    Generate error on `isinstance` test for typedefs, even if structurally valid.
    Or tweak isinstance to make the appropriare structural test?
    That would be a lousy pattern matching practice **but** also a handy
    type checking construct.

    `isinstance(("text", "text"), Target)` ???
-->

To mimick closely the original Haskell type hierarchy, we also define aliases
for some Python primitive types. For example, the `Text` type used in the `Str`
data constructor is not a custom Pandoc type:

``` pycon
>>> Str
Str(Text)
>>> issubclass(Text, Type)
False
```

Instead, it's a mere alias for the builtin Python string:

``` pycon
>>> Text
<class 'str'>
```
