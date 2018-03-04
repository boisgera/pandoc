
Configuration
================================================================================

Auto-magically with

    >>> import pandoc.types

is equivalent to the longer sequence

    >>> import pandoc
    >>> _  = pandoc.configure()
    >>> import pandoc.types

the `configure` function can take arguments. Explain this
