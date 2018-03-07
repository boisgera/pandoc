
Configuration
================================================================================

Auto-magically with

    >>> import pandoc.types

is equivalent to the longer sequence

    >>> import pandoc
    >>> pandoc.configure(auto=True)
    >>> import pandoc.types

the `configure` function can take arguments. 

Default value of configuration is `None`

main arguments: 

  - `auto`, 

  - `path`, 

  - `version`

  - `pandoc_types_version`

extra: 

  - `read` (returns the configuration); can coexist with other arguments

  - `reset` (set configuration to `None`, 
    remove the types from the `pandoc.types` modules).
    Error if other non-None arguments.

The empty `pandoc.configure()` returns an error (the meaning of the 
call is somehow ambiguous).
