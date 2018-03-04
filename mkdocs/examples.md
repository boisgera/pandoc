
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

**TODO:** think of some support for visitor patterns? 
We see a lot of "do this in-place if this condition is met". 
Or can we use the basic pandoc map/filter? Dunno. Think of it.
Arf with filter or map we have to deal with linearized data types?
We can linearize but can we reassemble. How are filter and map used
for hierarchial structures in functional programming? Have a look at
Haskell.

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
    <div id="cauchy-formula" class="theorem">
    <BLANKLINE>
    \begin{theorem}\label{cauchy-formula}
    $$f(z) = \frac{1}{i2\pi} \int \frac{f(w){w-z}\, dw$$
    <BLANKLINE>
    \end{theorem}
    <BLANKLINE>
    </div>
    <BLANKLINE>
    Right?
    <BLANKLINE>
