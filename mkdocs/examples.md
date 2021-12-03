Examples
================================================================================

``` python
import pandoc
from pandoc.types import *
```

Uppercase
--------------------------------------------------------------------------------

🚀 **Change all text to upper case.**

``` python
def uppercase(doc):
    for elt in pandoc.iter(doc):
        if isinstance(elt, Str):
            elt[0] = elt[0].upper() # elt: Str(Text)
```

``` pycon
>>> doc = pandoc.read("Hello world!")
>>> uppercase(doc)
>>> print(pandoc.write(doc).strip())
HELLO WORLD!
```

De-emphasize
--------------------------------------------------------------------------------

🚀 **Turn emphasized text into normal text.**

```python
def de_emphasize(doc):
    locations = []
    for elt, path in pandoc.iter(doc, path=True):
        if isinstance(elt, Emph):
            holder, index = path[-1]
            locations.append((elt, holder, index))
    # Perform the change in reverse document order 
    # not to invalidate the remaining matches.
    for elt, holder, index in reversed(locations):
        assert isinstance(elt, Emph)
        inlines = elt[0] # elt: Emph([Inline])
        holder[index:index+1] = inlines
```

``` pycon
>>> doc = pandoc.read("**strong**, *emphasized*, normal")
>>> de_emphasize(doc)
>>> print(pandoc.write(doc).strip())
**strong**, emphasized, normal
```

This implementation will remove nested layers of emphasis:

``` pycon
>>> doc = pandoc.read("0x _1x *2x*_")
>>> de_emphasize(doc)
>>> print(pandoc.write(doc).strip())
0x 1x 2x
```

<!--
The reversal of locations is necessary during the transformation phase since 
a replacement in a document may invalidate the locations after it. Without it:

```python
def de_emphasize(doc):
    locations = []
    for elt, path in pandoc.iter(doc, path=True):
        if isinstance(elt, Emph):
            holder, index = path[-1]
            locations.append((elt, holder, index))
    for elt, holder, index in locations:
        assert isinstance(elt, Emph)
        inlines = elt[0] # elt: Emph([Inline])
        holder[index:index+1] = inlines
```

``` pycon
>>> doc = pandoc.read("0x _1x *2x*_")
>>> de_emphasize(doc)
>>> print(pandoc.write(doc).strip())
0x 1x *2x*
```
Here the replacement of `*2x*` by `2x` takes place, but the holder of this
content has been removed from the document during the removal of the outer
emphasis.
-->

To remove only one layer of emphasis instead (the outer layer), 
we can filter out all elements that are already emphasized.

```python
from math import inf

def de_emphasize(doc):
    locations = []
    depth = inf
    for elt, path in pandoc.iter(doc, path=True):
        if len(path) <= depth: # not emphasized
            depth = inf
            if isinstance(elt, Emph):
                holder, index = path[-1]
                locations.append((elt, holder, index))
                depth = len(path)
    # Perform the change in reverse document order 
    # not to invalidate the remaining matches.
    for elt, holder, index in reversed(locations):
        assert isinstance(elt, Emph)
        inlines = elt[0] # elt: Emph([Inline])
        holder[index:index+1] = inlines
```

The behavior with simply emphasized items is unchanged:

``` pycon
>>> doc = pandoc.read("**strong**, *emphasized*, normal")
>>> de_emphasize(doc)
>>> print(pandoc.write(doc).strip())
**strong**, emphasized, normal
```

but differs for multiply emphasized text:

``` pycon
>>> doc = pandoc.read("0x _1x *2x*_")
>>> de_emphasize(doc)
>>> print(pandoc.write(doc).strip())
0x 1x *2x*
```

LaTeX theorems
--------------------------------------------------------------------------------

🚀 **Convert divs tagged as theorems into LaTeX theorems.**

First we need to detect this kind of divs:

``` python
def is_theorem(elt):
    if isinstance(elt, Div):
        attrs = elt[0] # elt: Div(Attr, [Block])
        classes = attrs[1] # attrs: (Text, [Text], [(Text, Text)])
        if "theorem" in classes:
            return True
    return False
```

Or equivalenty, with Python 3.10 (or newer), using pattern matching:

``` python
def is_theorem(elt):
    match elt:
        case Div((_, classes, _), _) if "theorem" in classes:
            return True
        case _:
            return False
```

Now we can implement the transformation itself:

``` python
def LaTeX(text):
    return RawBlock(Format("latex"), text)
```

``` python
def theoremize(doc):
    for elt in pandoc.iter(doc):
        if is_theorem(elt):
            attr, blocks = elt # elt: Div(Attr, [Block])
            id_ = attr[0] # attrs: (Text, [Text], [(Text, Text)])
            label = r"\label{" + id_ + "}" if id_ else ""
            start_theorem = LaTeX(r'\begin{theorem}' + label)
            end_theorem   = LaTeX(r'\end{theorem}')
            blocks[:] = [start_theorem] + blocks + [end_theorem]
```

Here are the results:

``` python
markdown = r"""
<div id='cauchy-formula' class='theorem'>
$$f(z) = \frac{1}{i2\pi} \int \frac{f(w)}{w-z}\, dw$$
</div>
"""
```

``` pycon
>>> doc = pandoc.read(markdown)
>>> print(pandoc.write(doc, format="latex")) # doctest: +NORMALIZE_WHITESPACE
\leavevmode\vadjust pre{\hypertarget{cauchy-formula}{}}%
\[f(z) = \frac{1}{i2\pi} \int \frac{f(w)}{w-z}\, dw\]
>>> theoremize(doc)
>>> print(pandoc.write(doc, format="latex")) # doctest: +NORMALIZE_WHITESPACE
\hypertarget{cauchy-formula}{}
\begin{theorem}\label{cauchy-formula}
\[f(z) = \frac{1}{i2\pi} \int \frac{f(w)}{w-z}\, dw\]
\end{theorem}
```

Jupyter Notebooks
--------------------------------------------------------------------------------

🚀 **Transform a markdown document into a Jupyter notebook.**

📖 Reference: [the notebook file format](http://nbformat.readthedocs.io/en/latest/format_description.html#the-notebook-file-format)

Jupyter notebook helpers (building blocks):

``` python
import copy
import uuid

def Notebook():
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "cells": [],
        "metadata": {},
    }

def CodeCell():
    return {
        "cell_type": "code",
        "source": [],
        "execution_count": None,
        "outputs": [],
        "id": uuid.uuid4().hex,
        "metadata": {},
    }

def MarkdownCell(): 
    return {
        "cell_type": "markdown",
        "source": [],
        "id": uuid.uuid4().hex,
        "metadata": {},
    }
```

The core transformation code:

``` python
def notebookify(doc):
    notebook = Notebook()
    cells = notebook["cells"]
    blocks = doc[1] # doc: Pandoc(Meta, [Block])
    for block in blocks:
        source, cell = None, None
        if isinstance(block, CodeBlock):
            source = block[1] # block: CodeBlock(Attr, Text)
            cell = CodeCell()
        else:
            source = pandoc.write(block).strip()
            cell = MarkdownCell()
        cell["source"] = source.splitlines(keepends=True)
        cells.append(cell)
    return notebook
```

``` python
markdown = """
# Hello world!
Print `Hello world!`:

    >>> print("Hello world!")
"""
doc = pandoc.read(markdown)
```

``` pycon
>>> doc
Pandoc(Meta({}), [Header(1, ('hello-world', [], []), [Str('Hello'), Space(), Str('world!')]), Para([Str('Print'), Space(), Code(('', [], []), 'Hello world!'), Str(':')]), CodeBlock(('', [], []), '>>> print("Hello world!")')])
>>> ipynb = notebookify(doc)
>>> import pprint
>>> pprint.pprint(ipynb) # doctest: +ELLIPSIS
{'cells': [{'cell_type': 'markdown',
            'id': ...,
            'metadata': {},
            'source': ['# Hello world!']},
           {'cell_type': 'markdown',
            'id': ...,
            'metadata': {},
            'source': ['Print `Hello world!`:']},
           {'cell_type': 'code',
            'execution_count': None,
            'id': ...,
            'metadata': {},
            'outputs': [],
            'source': ['>>> print("Hello world!")']}],
 'metadata': {},
 'nbformat': 4,
 'nbformat_minor': 5}
```

To use `notebookify` from the command-line we may create a `main` entry point:

``` python
import json
from pathlib import Path
import sys

def main():
    filename = sys.argv[1]
    doc = pandoc.read(file=filename)
    notebook = notebookify(doc)
    ipynb = Path(filename).with_suffix(".ipynb")
    with open(ipynb, "w", encoding="utf-8") as output:
        json.dump(notebook, output, ensure_ascii=False, indent=2)
```

If we specify on the command-line a (temporary) markdown file, 
`main()` creates the corresponding notebook:

``` pycon
>>> import tempfile
>>> with tempfile.TemporaryDirectory() as tmp_dir: # doctest: +ELLIPSIS
...     md_path = Path(tmp_dir).joinpath("doc.md")
...     with open(md_path, "w", encoding="utf-8") as md_file:
...         _ = md_file.write(markdown)
...     sys.argv[:] = ["notebookify", str(md_path)]
...     main()
...     with open(md_path.with_suffix(".ipynb"), encoding="utf-8") as ipynb:
...         pprint.pprint(json.load(ipynb))
{'cells': [{'cell_type': 'markdown',
            'id': ...,
            'metadata': {},
            'source': ['# Hello world!']},
           {'cell_type': 'markdown',
            'id': ...,
            'metadata': {},
            'source': ['Print `Hello world!`:']},
           {'cell_type': 'code',
            'execution_count': None,
            'id': ...,
            'metadata': {},
            'outputs': [],
            'source': ['>>> print("Hello world!")']}],
 'metadata': {},
 'nbformat': 4,
 'nbformat_minor': 5}
```

<!--
Unpack divs
--------------------------------------------------------------------------------

🚀 **Flatten a div hierarchy**

### In-place & two-pass


``` python
def unpack_divs(doc):
    "Unpack divs - Two-pass, in-Place algorithm"
    # Locate the divs and extract the relevant data
    matches = []
    for elt, path in pandoc.iter(doc, path=True):
        if isinstance(elt, Div):
            holder, index = path[-1]
            # blocks are held in lists (cf. the document model).
            assert isinstance(holder, list)
            contents = elt[1] # elt: Div(Attr, [Block])
            matches.append((holder, index, contents))
    # Unpack the divs in reverse document order 
    # not to invalidate the remaining matches.
    for holder, index, contents in reversed(matches):
        holder[index:index+1] = contents
```

``` python
doc = pandoc.read(
"""
<div>
A
<div>
B
<div>
C
</div>
</div>
</div>""", format="html"
)
```

``` pycon
>>> doc
Pandoc(Meta({}), [Div(('', [], []), [Plain([Str('A')]), Div(('', [], []), [Plain([Str('B')]), Div(('', [], []), [Plain([Str('C')])])])])])
>>> print(pandoc.write(doc, format="html").strip())
<div>
A
<div>
B
<div>
C
</div>
</div>
</div>
```

``` pycon
>>> unpack_divs(doc)
>>> doc
Pandoc(Meta({}), [Plain([Str('A')]), Plain([Str('B')]), Plain([Str('C')])])
>>> print(pandoc.write(doc, format="html").strip())
A
B
C
```

<!--
### Functional method

You may find that the approach above is convoluted. 
It's actually perfectly possible to achieve the same transformation 
in one pass if we build a new document 
instead of modifying the original.

This is best achieved using recursion. To get a feeling how recursion
can be used to create modified copies of a document, we can first 
implement a copy without modification:

``` python
def copy(elt):
    "Copy the document (or document fragment) recursively"
    # List, tuple, map and (non-primitive) Pandoc types
    if hasattr(elt, "__iter__") and not isinstance(elt, String):
        type_ = type(elt)
        if type_ is map:
            args = list(elt.items())
        else:
            args = elt[:]
        new_args = [copy(arg) for arg in args]
        if issubclass(type_, (list, tuple, map)):
            return type_(new_args)
        else: # Pandoc types
            return type_(*new_args)
    else: # Python atomic (immutable) types
        return elt 
```

Note that the name of the function argument is not `doc` but `elt` since the 
`copy` function may be used with any document fragment, not merely with a
document.

Let's go back to our original problem, which is div unpacking. 
Since divs are held in lists of blocks, 
we define a predicate that identifies lists of blocks:

``` python
def is_blocks(elt): 
    "Identify (non-empty) lists of blocks"
    return isinstance(elt, list) and \
            len(elt) != 0 and \
            isinstance(elt[0], Block)
```

And now we are ready to define the alternate implementation of `unpack_div`.
First, we detect when `elt` is a list of blocks and 
in this case, if some of these blocks are divs, 
we expand them:

``` python
def unpack_divs(elt):
    "Unpack Divs - One-Pass, Recursive, Non-Destructive Algorithm"
    # Find the list of blocks and their div children and unpack them
    if is_blocks(elt):
        blocks = elt
        new_blocks = []
        for block in blocks:
            if isinstance(block, Div):
                div = block
                contents = div[1]
                new_blocks.extend(unpack_divs(contents))
            else:
                new_blocks.append(unpack_divs(block))
        assert not any([isinstance(block, Div) for block in new_blocks])
        return new_blocks
    # We now need to handle the remaining cases, but this is easy
    # since this is similar to what the recursive `copy` is doing:
    # List, tuple, map and (non-primitive) Pandoc types
    elif hasattr(elt, "__iter__") and not isinstance(elt, String):
        type_ = type(elt)
        if type_ is map:
            args = list(elt.items())
        else:
            args = elt[:]
        new_args = [unpack_divs(arg) for arg in args]
        if issubclass(type_, (list, tuple, map)):
            return type_(new_args)
        else: # Pandoc types
            return type_(*new_args)
    else: # Python atomic (immutable) types
        return elt 
```
-->