
Configuration
================================================================================

Introduction
--------------------------------------------------------------------------------

The good news are that you generally don't need to configure anything:
when you use the `pandoc` Python library,
it does inspect your system to find the available `pandoc` 
command-line tool and configures itself accordingly. 
Most of the time, this is what you want.

However, if you need more control on this configuration step,
you can import `pandoc` and call `configure`
before you do anything else with the library:

    import pandoc
    pandoc.configure(...)
    
If you do this, the implicit configuration does not take place;
it is triggered only when no configuration is specified when 

  - you import `pandoc.types` or

  - you call `pandoc.read` or `pandoc.write`. 



Options
--------------------------------------------------------------------------------

To have the library find a `pandoc` executable in your path, 
and configure itself accordingly, enable the `auto` option

    pandoc.configure(auto=True)

This is the method used by the implicit configuration.
If instead you want to specify manually the pandoc executable,
use the `path` argument, for example:

    pandoc.configure(path='/usr/bin/pandoc')

Some features[^features] of the Python `pandoc` library 
do not require the `pandoc` executable, but in this case 
we still need to know what version of pandoc you target,
so specify for example:

    pandoc.configure(version='1.16.0.2')

[^features]: typically conversion between json and Python object representations 
of documents and analysis or transformations of documents as Python objects.
As soon as you use convert to or from any other format, markdown for example,
you need a pandoc executable. 

Actually, the exact version of pandoc is not even required. 
Instead what matters is the version of the document model 
that you intend to use, or equivalently, the version of the
[`pandoc-types`][pt] Haskell package used by the pandoc executable.
Accordingly, you may configure `pandoc` with the 
`pandoc_types_version` argument:

    pandoc.configure(pandoc_types_version='1.16.1.1')

[pt]: https://hackage.haskell.org/package/pandoc-types


Extra Arguments
--------------------------------------------------------------------------------

To get a copy of the configuration
(or `None` if the library is not configured yet),
enable the `read` option. The call 

    pandoc.configure(read=True)

does not change the current configuration 
but returns a dictionary whose keys are `auto`, `path`, 
`version` and `pandoc_types_version`, such as

    {
      'auto': True, 
      'path': '/usr/bin/pandoc', 
      'version': '1.16.0.2', 
      'pandoc_types_version': '1.16.1.1'
    }

The `read` option may be combined with other arguments, for example

    config = pandoc.configure(auto=True, read=True)

This is actually a good way to know where the pandoc executable has been
found, what is its version and the corresponding version of `pandoc-types`.

When it is needed, it is also possible to restore the unconfigured state:

    pandoc.configure(reset=True)
