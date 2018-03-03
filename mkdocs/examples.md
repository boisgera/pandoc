
Examples
================================================================================

**TODO:** there is an issue here with the pandoc.types import *:
the configure stuff has NOT been called yet, so the types just ain't there ...
Im solving the stuff manually here, but the process should be addressed

    >>> import pandoc; _ = pandoc.configure()
    >>> from pandoc.types import *

    >>> def F(function):
    ...     def _f(markdown):
    ...         doc = pandoc.read(markdown)
    ...         _doc = function(doc)
    ...         if _doc is not None:
    ...             doc = _doc
    ...         return pandoc.write(doc)
    ...     return _f

Uppercase
--------------------------------------------------------------------------------

    >>> def capitalize(doc):
    ...     for elt in pandoc.iter(doc):
    ...         if isinstance(elt, Str):
    ...             elt[0] = elt[0].upper()
 

    >>> print(F(capitalize)("I can't feel my legs"))
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
    ...         if len(elt) > 0 and isinstance(elt[0], Block):
    ...             children = []
    ...             incomment = False
    ...             for child in elt[:]:
    ...                 if begin_comment(child):
    ...                     incomment = True
    ...                 elif end_comment(child):
    ...                     incomment = False
    ...                 else:
    ...                     if not incomment:
    ...                         children.append(child)
    ...             elt[:] = children

    >>> markdown = """\
    ... Regular text
    ...
    ... <!-- BEGIN COMMENT -->
    ... A comment
    ...
    ... <!-- END COMMENT -->
    ... Moar regular text
    ... """
    >>> print(F(ignore_comments)(markdown))
    Regular text
    <BLANKLINE>
    Moar regular text
    <BLANKLINE>

