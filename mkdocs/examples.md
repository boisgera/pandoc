
**TODO:** plain text (no image, no link, no div, not attribute, etc.). 
Now that attributes & divs are captured from HTML, it can become VERY
noisy, a filter like that could alleviate the problem. Test it on
pandoc's web site for example? This is interesting, we will have
to 'flatten' the divs. At least get rid of everything that smells
too much HTML (link *may* be ok?), like raw html & divs.
Wait there is no raw html in this case right? Get rid of it anyway.

Examples
================================================================================

    >>> import pandoc
    >>> from pandoc.types import *

    >>> def T(function):
    ...     def _f(markdown):
    ...         doc = pandoc.read(markdown)
    ...         _doc = function(doc)
    ...         if _doc is not None:
    ...             doc = _doc
    ...         print(pandoc.write(doc))
    ...     return _f

Uppercase
--------------------------------------------------------------------------------

    >>> def capitalize(doc):
    ...     for elt in pandoc.iter(doc):
    ...         if isinstance(elt, Str):
    ...             elt[0] = elt[0].upper()
 

    >>> T(capitalize)("I can't feel my legs")
    I CAN'T FEEL MY LEGS
    <BLANKLINE>

**TODO:** extra NEWLINE in the output, solve this.
OR maybe this is to be expected? A doc DOES END with a newline?
See what pandoc does about this.


De-emphasize
--------------------------------------------------------------------------------

**TODO:** think of the pattern: if something matches a condition, 
          replace it with something (and stop the iteration in this
          branch? Or iterate on the new object?). 
          Pandoc-filters has the ability to let the 
          "atomic transformation" control the rest of the iteration
          by calling walk. See how this is done, study walk.
         


    >>> def capitalize(doc):
    ...     for elt in pandoc.iter(doc):
    ...         if isinstance(elt, Str):
    ...             elt[0] = elt[0].upper()
 

    >>> T(capitalize)("I can't feel my legs")
    I CAN'T FEEL MY LEGS
    <BLANKLINE>

**TODO:** extra NEWLINE in the output, solve this.
OR maybe this is to be expected? A doc DOES END with a newline?
See what pandoc does about this.



Comments
--------------------------------------------------------------------------------

Remove everything between `<!-- BEGIN COMMENT -->` and `<!-- END COMMENT -->`.
The comment lines must appear on lines by themselves, 
with blank lines surrounding them.

**TODO:** find HTML RawBlocks, check for start/end markers, 
remove the items within.

**TODO:** these scheme *may* fail with tuples right?
          Improve the "Block holder" detection.

    >>> def begin_comment(elt):
    ...     return isinstance(elt, RawBlock) and \
    ...            elt[0] == Format(u"html") and \
    ...            "<!-- BEGIN COMMENT -->" in elt[1]
    ...
    >>> def end_comment(elt):
    ...     return isinstance(elt, RawBlock) and \
    ...            elt[0] == Format(u"html") and \
    ...            "<!-- END COMMENT -->" in elt[1]

And now

    >>> def ignore_comments(doc):
    ...     for elt in pandoc.iter(doc):
    ...         if isinstance(elt, list) and len(elt) > 0 and isinstance(elt[0], Block):            
    ...             children = []
    ...             in_comment = False
    ...             for child in elt[:]:
    ...                 if begin_comment(child):
    ...                     in_comment = True
    ...                 elif end_comment(child):
    ...                     in_comment = False
    ...                 else:
    ...                     if not in_comment:
    ...                         children.append(child)
    ...             elt[:] = children

Leads to

    >>> markdown = """\
    ... Regular text
    ...
    ... <!-- BEGIN COMMENT -->
    ... A comment
    ...
    ... <!-- END COMMENT -->
    ... Moar regular text
    ... """
    >>> T(ignore_comments)(markdown)
    Regular text
    <BLANKLINE>
    Moar regular text
    <BLANKLINE>


Theorems
--------------------------------------------------------------------------------

Convert divs with class="theorem" to LaTeX theorem environments in LaTeX output,
and to numbered theorems in HTML output.

**TODO:** to HTML version. Also export to LaTeX and HTML to see the outputs?
Can it be done with an option to the `T` function?

**TODO:** think of some support for visitor patterns? 
We see a lot of "do this in-place if this condition is met". 
Or can we use the basic pandoc map/filter? Dunno. Think of it.
Arf with filter or map we have to deal with linearized data types?
We can linearize but can we reassemble. How are filter and map used
for hierarchial structures in functional programming? Have a look at
Haskell (e.g. <https://stackoverflow.com/questions/7624774/haskell-map-for-trees>).
So, define a `pandoc.map` helper?

    >>> def is_theorem(elt):
    ...     if isinstance(elt, Div):
    ...         attrs = elt[0]
    ...         _, classes, _ = attrs
    ...         if "theorem" in classes:
    ...             return True
    ...     return False

    >>> def LaTeX(text):
    ...     return RawBlock(Format('latex'), text)

    >>> def theorem_latex(doc):
    ...     for elt in pandoc.iter(doc):
    ...         if is_theorem(elt):
    ...             id_ = elt[0][0]
    ...             label = ""
    ...             if id_:
    ...                 label = r'\label{' + id_ + '}'
    ...             start_theorem = LaTeX(r'\begin{theorem}' + label)
    ...             end_theorem   = LaTeX(r'\end{theorem}')
    ...             elt[1][:] = [start_theorem] + elt[1] + [end_theorem]
    
    >>> markdown = r"""
    ... I'd like to introduce the following theorem:
    ... <div id='cauchy-formula' class='theorem'>
    ... $$f(z) = \frac{1}{i2\pi} \int \frac{f(w){w-z}\, dw$$
    ... </div>
    ... Right?
    ... """
    
    >>> T(theorem_latex)(markdown)
    I'd like to introduce the following theorem:
    <BLANKLINE>
    ::: {#cauchy-formula .theorem}
    \begin{theorem}\label{cauchy-formula}
    <BLANKLINE>
    $$f(z) = \frac{1}{i2\pi} \int \frac{f(w){w-z}\, dw$$
    <BLANKLINE>
    \end{theorem}
    :::
    <BLANKLINE>
    Right?
    <BLANKLINE>



Notebooks
--------------------------------------------------------------------------------

<http://nbformat.readthedocs.io/en/latest/format_description.html#the-notebook-file-format>


    #!/usr/bin/env python

    # Python Standard Library
    import copy
    import json
    import os.path
    import sys

    # Pandoc
    import pandoc


    def Notebook():
        return copy.deepcopy(
          {
            "cells": [],
            "metadata": {
              "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
              },
              "language_info": {
                "codemirror_mode": {
                  "name": "ipython",
                  "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.6.4"
               }
            },
            "nbformat": 4,
            "nbformat_minor": 2
          }
        )

    def CodeCell():
        return copy.deepcopy(
          {
            "cell_type": "code",
            "execution_count": 1,
            "metadata": {},
            "outputs": [],
            "source": []
          }
        )

    def MarkdownCell(): 
        return copy.deepcopy(
          {
            "cell_type": "markdown",
            "metadata": {},
            "source": []
          }
        )

    def notebookify(doc):
        from pandoc.types import Pandoc, Meta, CodeBlock
        notebook = Notebook()
        cells = notebook['cells']
        blocks = doc[1]
        #print(blocks)
        execution_count = 1
        for block in blocks:
            if isinstance(block, CodeBlock):
                source = block[1]
                code_cell = CodeCell()
                code_cell['source'] = source
                code_cell['execution_count'] = execution_count
                execution_count += 1
                cells.append(code_cell)
            else:
                wrapper = Pandoc(Meta({}), [block])
                #print(wrapper)
                source = pandoc.write(wrapper)
                markdown_cell = MarkdownCell()
                markdown_cell['source'] = source
                cells.append(markdown_cell)
        return notebook

    if __name__ == '__main__':
        filename = sys.argv[1]
        doc = pandoc.read(file=filename)
        notebook = notebookify(doc)
        base, _ = os.path.splitext(filename)
        output = open(base + '.ipynb', 'w')
        output.write(json.dumps(notebook, indent=2))
        output.close()


Save Web Documents
--------------------------------------------------------------------------------

When you find an interesting piece of content on the Web,
you may want to archive it on your computer.
Since you are only interested in the content 
and not the full web page, 
there are things in the HTML document 
that you want probably want to remove in the process
(ads, social media, etc.). 
And while you're at it, 
why not store the result as Markdown, 
which is a simpler document description language?
We know that thanks to pandoc, we can convert it 
to something fancy like PDF if the need arises.

Consider for example the ["Getting started"](https://pandoc.org/getting-started.html) 
section of the the pandoc documentation. This is a useful document,
I want to keep a copy of it in my hard drive.
Downloading it and converting it to Markdown is easy:

    $ curl https://pandoc.org/getting-started.html > getting-started.html
    $ pandoc -o getting-started.md getting-started.html

However, when you look at the result, this is very "noisy".
Its starts with

    ::: {#doc .container-fluid}
    ::: {#flattr}
    [](https://pandoc.org){.FlattrButton}

    [![Flattr
    this](https://api.flattr.com/button/flattr-badge-large.png "Flattr this")](https://flattr.com/thing/936364/Pandoc)
    :::

    ::: {#paypal}
    ![](https://www.paypalobjects.com/en_US/i/scr/pixel.gif){width="1"
    height="1"}
    :::

    [Pandoc]{.big}   [a universal document converter]{.small}

    ::: {#bd}
    ::: {.navbar-header}
    [Toggle navigation]{.sr-only} []{.icon-bar} []{.icon-bar} []{.icon-bar}
    :::

    ::: {.navbar-collapse .collapse}
    -   [About](index.html)
    -   [Installing](installing.html)
    -   ...
    :::

    ::: {.col-md-9 .col-sm-8 role="main"}
    ::: {.row}
    ::: {#toc}
    -   [Step 1: Install pandoc](#step-1-install-pandoc)
    -   [Step 2: Open a terminal](#step-2-open-a-terminal)
    -   ...
    :::

[^1]: We could also disable the `native_divs` option in pandoc to get rid 
of the div soup, but where would be the fun then?


There are two different kind of things here:

  - a "div soup", characterized by the sheer number of `:::` symbols[^1].
    In pandoc-flavored Markdown, the `:::` syntax corresponds to
    the `<div>` tag in HTML.
    Div hierarchies are often used to style HTML elements, 
    so this is something that we don't need anymore.

  - components that don't make sense out of the web page: 
    some buttons, a navigation bar, etc.

It's only after this long and noisy preamble that you find the real content.
It looks like this:

    This document is for people who are unfamiliar with command line tools.
    Command-line experts can go straight to the [User's Guide](README.html)
    or the pandoc man page.

    Step 1: Install pandoc
    ======================

    First, install pandoc, following the [instructions for your
    platform](installing.html).

    Step 2: Open a terminal
    =======================

    ...

And finally, you close the four divs in which the content is nested:

    :::
    :::
    :::
    :::

This is probably not the document that you want to store. 
To simplify it, we are going to remove all the hierarchy 
of divs and get rid of the preamble.



### Unpack Divs

    def unpack_divs(doc):
        "Unpack Divs - Two-pass, In-Place Algorithm"

        # Locate the divs and extract the relevant data
        matches = []
        for elt, path in pandoc.iter(doc, path=True):
            if isinstance(elt, Div):
                div = elt
                parent, index = path[-1]
                contents = div[1]
                # Blocks are always held in lists (cf. the document model).
                assert isinstance(parent, list)
                matches.append((parent, index, contents))

        # We need to unpack the divs in reverse document order 
        # not to invalidate the remaining matches.
        for parent, index, contents in reversed(matches):
            del parent[index]
            parent[index:index] = contents

        return doc



### Unpack Divs (Variant)

You may find that the approach above is convoluted. 
It's actually perfectly possible to achieve the same transformation 
in one pass if we build a new document 
instead of modifying the original.

This is best achieved using recursion. To get a feeling how recursion
can be used to create modified copies of a document, we can first 
implement a copy without modification:

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

Note that the name of the function argument is not `doc` but `elt` since the 
`copy` function may be used with any document fragment, not merely with a
document.

Let's go back to our original problem, which is div unpacking. 
Since divs are held in lists of blocks, 
we define a predicate that identifies lists of blocks:

    def is_blocks(elt): 
        "Identify (non-empty) lists of blocks"
        return isinstance(elt, list) and \
               len(elt)!=0 and \
               isinstance(elt[0], Block)


And now we are ready to define the alternate implementation of `unpack_div`.
First, we detect when `elt` is a list of blocks and 
in this case, if some of these blocks are divs, 
we expand them:

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

We also need to handle the remaining cases, but this is easy
since this is similar to what the recursive `copy` is doing:

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

### Remove The Preamble

At this stage, if you wrap any of the `unpack_divs` into

    # file: simplify.py
    if __name__ == "__main__":
        url = 'https://pandoc.org/getting-started.html'
        src = urllib.request.urlopen(url).read()
        doc = pandoc.read(src, format="html")
        doc = unpack_divs(doc)
        print(pandoc.write(doc, format="markdown", options=["-s"]))

This is what you get when you execute the script:

    $ python simplify.py 
    ---
    lang: en
    title: 'Pandoc - Getting started with pandoc'
    viewport: 'width=device-width, initial-scale=1.0'
    ---

    [](https://pandoc.org){.FlattrButton}

    [![Flattr
    this](https://api.flattr.com/button/flattr-badge-large.png "Flattr this")](https://flattr.com/thing/936364/Pandoc)

    ![](https://www.paypalobjects.com/en_US/i/scr/pixel.gif){width="1"
    height="1"}

    [Pandoc]{.big}   [a universal document converter]{.small}

    [Toggle navigation]{.sr-only} []{.icon-bar} []{.icon-bar} []{.icon-bar}

    -   [About](index.html)
    -   [Installing](installing.html)
    -   ...

    -   [Step 1: Install pandoc](#step-1-install-pandoc)
    -   [Step 2: Open a terminal](#step-2-open-a-terminal)
    -   ...

    This document is for people who are unfamiliar with command line tools.
    Command-line experts can go straight to the [User's Guide](README.html)
    or the pandoc man page.

    Step 1: Install pandoc
    ======================

    First, install pandoc, following the [instructions for your
    platform](installing.html).

    Step 2: Open a terminal
    =======================

    ...

    If you get stuck, you can always ask questions on the
    [pandoc-discuss](http://groups.google.com/group/pandoc-discuss) mailing
    list. But be sure to check the [FAQs](faqs.html) first, and search
    through the mailing list to see if your question has been answered
    before.

This is better, since there is no more div, but we still need to get rid 
of everything before the first real paragraph, 
the one that starts with some plain text: "This document ...".
So we can detect this first paragraph 
– for example because it starts with an instance of `Str` – 
and remove everything before it from the document:

    def remove_preamble(doc):
        "Remove everything before the first real paragraph"
        blocks = doc[1]
        for i, block in enumerate(blocks):
            if isinstance(block, Para):
                para = block
                inlines = para[0]
                if len(inlines) > 0 and isinstance(inlines[0], Str):
                    break
        doc[1] = blocks[i:]
        return doc

Now, change the main entry point accordingly:

    # file: simplify.py
    if __name__ == "__main__":
        url = 'https://pandoc.org/getting-started.html'
        src = urllib.request.urlopen(url).read()
        doc = pandoc.read(src, format="html")
        doc = unpack_divs(doc)
        doc = remove_preamble(doc)
        print(pandoc.write(doc, format="markdown", options=["-s"]))

and this is what you get:

    $ python simplify.py
    ---
    lang: en
    title: 'Pandoc - Getting started with pandoc'
    viewport: 'width=device-width, initial-scale=1.0'
    ---

    This document is for people who are unfamiliar with command line tools.
    Command-line experts can go straight to the [User's Guide](README.html)
    or the pandoc man page.

    Step 1: Install pandoc
    ======================

    First, install pandoc, following the [instructions for your
    platform](installing.html).

    Step 2: Open a terminal
    =======================

    ...

    If you get stuck, you can always ask questions on the
    [pandoc-discuss](http://groups.google.com/group/pandoc-discuss) mailing
    list. But be sure to check the [FAQs](faqs.html) first, and search
    through the mailing list to see if your question has been answered
    before.

Mission accomplished!

