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

We can access the Pandoc document contents by index, this way it's possible to
explore interactively this document in a more precise manner:

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

We can also access the Pandoc document contents by field name. By default the
field names are not shown when printing the document, but we can enable this
with the following command:

```python
pandoc.types.set_data_repr(show_fields=True)
```

If we print again the document the field names of the different elements of the
document will be displayed:

```pycon
>>> doc
Pandoc(meta=Meta(map={}), blocks=[Para(content=[Str(text='Hello,'), Space(), Str(text='World!')])])
```

This way we can explore interactively the document as before but using field names:

``` pycon
>>> doc
Pandoc(meta=Meta(map={}), blocks=[Para(content=[Str(text='Hello,'), Space(), Str(text='World!')])])
>>> meta = doc.meta
>>> meta
Meta(map={})
>>> meta.map
{}
>>> contents = doc.blocks
>>> contents
[Para(content=[Str(text='Hello,'), Space(), Str(text='World!')])]
>>> paragraph = contents[0]
>>> paragraph
Para(content=[Str(text='Hello,'), Space(), Str(text='World!')])
>>> paragraph.content
[Str(text='Hello,'), Space(), Str(text='World!')]
>>> world = paragraph.content[2]
>>> world
Str(text='World!')
```

Finally, we can reset the default behavior of displaying the field names with the command:

```python
pandoc.types.set_data_repr(show_fields=False)
```

I recommend that you try to reproduce the process above for small documents
that feature titles, headers, emphasized text, lists, etc. to become familiar
with the way that these constructs are described in pandoc documents.

!!! note
    The field names are derived automatically from the pandoc types to be as close
    as possible to the Pandoc Lua filters API (<https://pandoc.org/lua-filters.html>).
    Note however that there are some differences.

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
Pandoc(meta: Meta = Meta({}), blocks: [Block] = [])
```

which means that the `Pandoc` type is defined by two fields:

- `meta`: an instance of `Meta` (the document metadata), with a default value of `Meta({})`.
- `blocks`: a list of blocks, with a default value of `[]`.

In our example above, the metadata was not very interesting:
`Meta({})`. Still, we can make sure that this fragment is valid: the `Meta`
type signature is

``` pycon
>>> Meta
Meta(map: {Text: MetaValue} = {})
```

which reads as: metadata instances have a single field `map` containing a
dictionary of `Text` keys and `MetaValue` values. In our example, this
dictionary was empty, hence we don't need to explore the structure of `Text`
and `MetaValue` any further to conclude that the fragment is valid.

Now, let's explore the content of the document which is defined as a list of
blocks. The `Block` type signature is

``` pycon
>>> Block
Block = Plain(content: [Inline] = [])
      | Para(content: [Inline] = [])
      | LineBlock(content: [[Inline]] = [])
      | CodeBlock(attr: Attr = ('', [], []), text: Text = '')
      | RawBlock(format: Format = Format(''), text: Text = '')
      | BlockQuote(content: [Block] = [])
      | OrderedList(list_attributes: ListAttributes = (0, DefaultStyle(), DefaultDelim()), content: [[Block]] = [])
      | BulletList(content: [[Block]] = [])
      | DefinitionList(content: [([Inline], [[Block]])] = [])
      | Header(level: Int = 0, attr: Attr = ('', [], []), content: [Inline] = [])
      | HorizontalRule()
      | Table(attr: Attr = ('', [], []), caption: Caption = Caption(None, []), col_specs: [ColSpec] = [], head: TableHead = TableHead(('', [], []), []), bodies: [TableBody] = [], foot: TableFoot = TableFoot(('', [], []), []))
      | Figure(attr: Attr = ('', [], []), caption: Caption = Caption(None, []), content: [Block] = [])
      | Div(attr: Attr = ('', [], []), content: [Block] = [])
```

Each `"|"` symbol in the signature represents an alternative: blocks may
be instances of `Plain`, `Para`, `LineBlock`, etc. In our example document, the
only type of block that was used is the paragraph type `Para`, whose signature
is:

``` pycon
>>> Para
Para(content: [Inline] = [])
```

Paragraphs contain a list of inlines. An inline is

``` pycon
>>> Inline
Inline = Str(text: Text = '')
       | Emph(content: [Inline] = [])
       | Underline(content: [Inline] = [])
       | Strong(content: [Inline] = [])
       | Strikeout(content: [Inline] = [])
       | Superscript(content: [Inline] = [])
       | Subscript(content: [Inline] = [])
       | SmallCaps(content: [Inline] = [])
       | Quoted(quote_type: QuoteType = SingleQuote(), content: [Inline] = [])
       | Cite(citations: [Citation] = [], content: [Inline] = [])
       | Code(attr: Attr = ('', [], []), text: Text = '')
       | Space()
       | SoftBreak()
       | LineBreak()
       | Math(type: MathType = DisplayMath(), text: Text = '')
       | RawInline(format: Format = Format(''), text: Text = '')
       | Link(attr: Attr = ('', [], []), content: [Inline] = [], target: Target = ('', ''))
       | Image(attr: Attr = ('', [], []), content: [Inline] = [], target: Target = ('', ''))
       | Note(content: [Block] = [])
       | Span(attr: Attr = ('', [], []), content: [Inline] = [])
```

In our plain text example, only two types of inlines where used: strings
`Str` and white space `Space`. Since

``` pycon
>>> Str
Str(text: Text = '')
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
Inline = Str(text: Text = '')
       | Emph(content: [Inline] = [])
       | Underline(content: [Inline] = [])
       | Strong(content: [Inline] = [])
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
Link(attr: Attr = ('', [], []), content: [Inline] = [], target: Target = ('', ''))
```

instead of `Link(attr: (Text, [Text], [(Text, Text)]), content: [Inline], target: (Text, Text))`
without them.

<!--

???+ error "TODO"
    Generate error on `isinstance` test for typedefs, even if structurally valid.
    Or tweak isinstance to make the appropriare structural test?
    That would be a lousy pattern matching practice **but** also a handy
    type checking construct.

    `isinstance(("text", "text"), Target)` ???
-->

To mimic closely the original Haskell type hierarchy, we also define aliases
for some Python primitive types. For example, the `Text` type used in the `Str`
data constructor is not a custom Pandoc type:

``` pycon
>>> Str
Str(text: Text = '')
>>> issubclass(Text, Type)
False
```

Instead, it's a mere alias for the builtin Python string:

``` pycon
>>> Text
<class 'str'>
```
