
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

