
Preamble
================================================================================

Pandoc (Haskell)
--------------------------------------------------------------------------------

This test suite requires pandoc 1.16:

    >>> from subprocess import Popen, PIPE
    >>> p = Popen(["pandoc", "-v"], stdout=PIPE)
    >>> if "pandoc 1.16" not in p.communicate()[0]:
    ...     raise RuntimeError("pandoc 1.16 not found")


Imports
--------------------------------------------------------------------------------

    >>> from pandoc.types import *
    >>> import pandoc




    >>> "AAA" # doctest: +PANDOC
    Traceback (most recent call last):
    ...
    ValueError: MUHAHAHA!
