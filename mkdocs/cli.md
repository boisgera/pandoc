
Command-Line Interface
================================================================================

The Pandoc Python library includes a command-line tool to convert pandoc
documents to their python representation. It is invoked with `python -m pandoc`
followed by the `read` or `write` subcommands.

You may use it to visualize the structure of markdown snippets:
simply pipe them into the `read` subcommand standard input:

```bash
$ echo "Hello world!" | python -m pandoc read 
Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])
```

Alternatively, you can use markdown files as inputs:

```bash
$ echo "Hello world!" > hello.md
$ cat hello.md
Hello world!
$ python -m pandoc read hello.md
Pandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])
```

Note that the output of `python -m pandoc read` is always compact:
it holds on a single line.
Consider the `README.md` file of this project for example

```bash
$ URL="https://raw.githubusercontent.com/boisgera/pandoc/master/README.md"
$ curl $URL --output README.md 
$ cat README.md | head -n 10

Pandoc (Python Library)
================================================================================

[![build](https://github.com/boisgera/pandoc/actions/workflows/build.yml/badge.svg)](https://github.com/boisgera/pandoc/actions/workflows/build.yml)
[![Downloads](https://pepy.tech/badge/pandoc)](https://pepy.tech/project/pandoc)
[![Gitter chat](https://badges.gitter.im/boisgera/python-pandoc.svg)](https://gitter.im/python-pandoc/community#)

*This README is about the 2.x branch of the library (alpha stage!). Only the 1.x branch is available on PyPi at the moment.*
```

The output of the read subcommand is a very long line:

```bash
$ python -m pandoc read README.md
Pandoc(Meta({}), [Header(1, ('pandoc-python-library', [], []), [Str('Pandoc'), Space(), Str('(Python'), Space(), Str('Library)')]), Para([Link(('', [], []), [Image(('', [], []), [Str('build')], ('https://github.com/boisgera/pandoc/actions/workflows/build.yml/badge.svg', ''))], ('https://github.com/boisgera/pandoc/actions/workflows/build.yml', '')), SoftBreak(), Link(('', [], []), [Image(('', [], []), [Str('Downloads')], ('https://pepy.tech/badge/pandoc', ''))], ('https://pepy.tech/project/pandoc', '')), SoftBreak(), Link(('', [], []), [Image(('', [], []), [Str('Gitter'), Space(), Str('chat')], ('https://badges.gitter.im/boisgera/python-pandoc.svg', ''))], ('https://gitter.im/python-pandoc/community#', ''))]), Para([Emph([Str('This'), Space(), Str('README'), Space(), Str('is'), Space(), Str('about'), Space(), Str('the'), Space(), Str('2.x'), Space(), Str('branch'), Space(), Str('of'), Space(), Str('the'), Space(), Str('library'), Space(), Str('(alpha'), Space(), Str('stage!).'), Space(), Str('Only'), Space(), Str('the'), Space(), Str('1.x'), Space(), Str('branch'), Space(), Str('is'), Space(), Str('available'), Space(), Str('on'), Space(), Str('PyPi'), Space(), Str('at'), Space(), Str('the'), Space(), Str('moment.')])]), Header(2, ('getting-started', [], []), [Str('Getting'), Space(), Str('started')]), Para([Str('Install'), Space(), Str('the'), Space(), Str('latest'), Space(), Str('version'), Space(), Str('with:')]), CodeBlock(('', [], []), '$ pip install --upgrade git+https://github.com/boisgera/pandoc.git'), Para([Str('The'), Space(), Link(('', [], []), [Str('Pandoc')], ('http://pandoc.org/', '')), Space(), Str('command-line'), Space(), Str('tool'), Space(), Str('is'), Space(), Str('a'), Space(), Str('also'), Space(), Str('required'), Space(), Str('dependency'), Space(), Str(';'), SoftBreak(), Str('you'), Space(), Str('may'), Space(), Str('install'), Space(), Str('it'), Space(), Str('with'), Space(), Str(':')]), CodeBlock(('', [], []), '$ conda install -c conda-forge pandoc'), Header(2, ('overview', [], []), [Str('Overview')]), Para([Str('This'), Space(), Str('project'), Space(), Str('brings'), Space(), Link(('', [], []), [Str('Pandoc')], ('http://pandoc.org/', '')), Str('’s'), Space(), Str('data'), Space(), Str('model'), Space(), Str('for'), Space(), Str('markdown'), Space(), Str('documents'), Space(), Str('to'), Space(), Str('Python:')]), CodeBlock(('', [], []), '$ echo "Hello world!" | python -m pandoc read \nPandoc(Meta({}), [Para([Str(\'Hello\'), Space(), Str(\'world!\')])])'), Para([Str('It'), Space(), Str('can'), Space(), Str('be'), Space(), Str('used'), Space(), Str('to'), Space(), Str('analyze,'), Space(), Str('create'), Space(), Str('and'), Space(), Str('transform'), Space(), Str('documents,'), Space(), Str('in'), Space(), Str('Python'), Space(), Str(':')]), CodeBlock(('', [], []), '>>> import pandoc\n>>> text = "Hello world!"\n>>> doc = pandoc.read(text)\n>>> doc\nPandoc(Meta({}), [Para([Str(\'Hello\'), Space(), Str(\'world!\')])])\n\n>>> paragraph = doc[1][0]\n>>> paragraph\nPara([Str(\'Hello\'), Space(), Str(\'world!\')])\n>>> from pandoc.types import Str\n>>> paragraph[0][2] = Str(\'Python!\')\n>>> text = pandoc.write(doc)\n>>> print(text)\nHello Python!'), Para([Link(('', [], []), [Str('Pandoc')], ('http://pandoc.org/', '')), Space(), Str('is'), Space(), Str('the'), Space(), Str('general'), Space(), Str('markup'), Space(), Str('converter'), Space(), Str('(and'), Space(), Str('Haskell'), Space(), Str('library)'), Space(), Str('written'), Space(), Str('by'), Space(), Link(('', [], []), [Str('John'), Space(), Str('MacFarlane')], ('http://johnmacfarlane.net/', '')), Str('.')])])
```

If this is not what you want, remember that this output is valid Python code
that any code formatter can handle. For example,
if the [black](https://black.readthedocs.io/en/stable/) formatter is available,
you can pretty-print the output with:

```bash
$ python -m pandoc read README.md | black -q -
Pandoc(
    Meta({}),
    [
        Header(
            1,
            ("pandoc-python-library", [], []),
            [Str("Pandoc"), Space(), Str("(Python"), Space(), Str("Library)")],
        ),
        Para(
            [
                Link(
                    ("", [], []),
                    [
                        Image(
                            ("", [], []),
                            [Str("build")],
                            (
                                "https://github.com/boisgera/pandoc/actions/workflows/build.yml/badge.svg",
                                "",
                            ),
                        )
                    ],
                    (
                        "https://github.com/boisgera/pandoc/actions/workflows/build.yml",
                        "",
                    ),
                ),
                SoftBreak(),
                Link(
                    ("", [], []),
                    [
                        Image(
                            ("", [], []),
                            [Str("Downloads")],
                            ("https://pepy.tech/badge/pandoc", ""),
                        )
                    ],
                    ("https://pepy.tech/project/pandoc", ""),
                ),
                SoftBreak(),
                Link(
                    ("", [], []),
                    [
                        Image(
                            ("", [], []),
                            [Str("Gitter"), Space(), Str("chat")],
                            ("https://badges.gitter.im/boisgera/python-pandoc.svg", ""),
                        )
                    ],
                    ("https://gitter.im/python-pandoc/community#", ""),
                ),
            ]
        ),
        Para(
            [
                Emph(
                    [
                        Str("This"),
                        Space(),
                        Str("README"),
                        Space(),
                        Str("is"),
                        Space(),
                        Str("about"),
                        Space(),
                        Str("the"),
                        Space(),
                        Str("2.x"),
                        Space(),
                        Str("branch"),
                        Space(),
                        Str("of"),
                        Space(),
                        Str("the"),
                        Space(),
                        Str("library"),
                        Space(),
                        Str("(alpha"),
                        Space(),
                        Str("stage!)."),
                        Space(),
                        Str("Only"),
                        Space(),
                        Str("the"),
                        Space(),
                        Str("1.x"),
                        Space(),
                        Str("branch"),
                        Space(),
                        Str("is"),
                        Space(),
                        Str("available"),
                        Space(),
                        Str("on"),
                        Space(),
                        Str("PyPi"),
                        Space(),
                        Str("at"),
                        Space(),
                        Str("the"),
                        Space(),
                        Str("moment."),
                    ]
                )
            ]
        ),
        Header(
            2, ("getting-started", [], []), [Str("Getting"), Space(), Str("started")]
        ),
        Para(
            [
                Str("Install"),
                Space(),
                Str("the"),
                Space(),
                Str("latest"),
                Space(),
                Str("version"),
                Space(),
                Str("with:"),
            ]
        ),
        CodeBlock(
            ("", [], []),
            "$ pip install --upgrade git+https://github.com/boisgera/pandoc.git",
        ),
        Para(
            [
                Str("The"),
                Space(),
                Link(("", [], []), [Str("Pandoc")], ("http://pandoc.org/", "")),
                Space(),
                Str("command-line"),
                Space(),
                Str("tool"),
                Space(),
                Str("is"),
                Space(),
                Str("a"),
                Space(),
                Str("also"),
                Space(),
                Str("required"),
                Space(),
                Str("dependency"),
                Space(),
                Str(";"),
                SoftBreak(),
                Str("you"),
                Space(),
                Str("may"),
                Space(),
                Str("install"),
                Space(),
                Str("it"),
                Space(),
                Str("with"),
                Space(),
                Str(":"),
            ]
        ),
        CodeBlock(("", [], []), "$ conda install -c conda-forge pandoc"),
        Header(2, ("overview", [], []), [Str("Overview")]),
        Para(
            [
                Str("This"),
                Space(),
                Str("project"),
                Space(),
                Str("brings"),
                Space(),
                Link(("", [], []), [Str("Pandoc")], ("http://pandoc.org/", "")),
                Str("’s"),
                Space(),
                Str("data"),
                Space(),
                Str("model"),
                Space(),
                Str("for"),
                Space(),
                Str("markdown"),
                Space(),
                Str("documents"),
                Space(),
                Str("to"),
                Space(),
                Str("Python:"),
            ]
        ),
        CodeBlock(
            ("", [], []),
            "$ echo \"Hello world!\" | python -m pandoc read \nPandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])",
        ),
        Para(
            [
                Str("It"),
                Space(),
                Str("can"),
                Space(),
                Str("be"),
                Space(),
                Str("used"),
                Space(),
                Str("to"),
                Space(),
                Str("analyze,"),
                Space(),
                Str("create"),
                Space(),
                Str("and"),
                Space(),
                Str("transform"),
                Space(),
                Str("documents,"),
                Space(),
                Str("in"),
                Space(),
                Str("Python"),
                Space(),
                Str(":"),
            ]
        ),
        CodeBlock(
            ("", [], []),
            ">>> import pandoc\n>>> text = \"Hello world!\"\n>>> doc = pandoc.read(text)\n>>> doc\nPandoc(Meta({}), [Para([Str('Hello'), Space(), Str('world!')])])\n\n>>> paragraph = doc[1][0]\n>>> paragraph\nPara([Str('Hello'), Space(), Str('world!')])\n>>> from pandoc.types import Str\n>>> paragraph[0][2] = Str('Python!')\n>>> text = pandoc.write(doc)\n>>> print(text)\nHello Python!",
        ),
        Para(
            [
                Link(("", [], []), [Str("Pandoc")], ("http://pandoc.org/", "")),
                Space(),
                Str("is"),
                Space(),
                Str("the"),
                Space(),
                Str("general"),
                Space(),
                Str("markup"),
                Space(),
                Str("converter"),
                Space(),
                Str("(and"),
                Space(),
                Str("Haskell"),
                Space(),
                Str("library)"),
                Space(),
                Str("written"),
                Space(),
                Str("by"),
                Space(),
                Link(
                    ("", [], []),
                    [Str("John"), Space(), Str("MacFarlane")],
                    ("http://johnmacfarlane.net/", ""),
                ),
                Str("."),
            ]
        ),
    ],
)
```
