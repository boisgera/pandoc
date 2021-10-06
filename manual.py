#!/usr/bin/env python

# Python Standard Library
from urllib.request import urlopen

# Pandoc
import pandoc
from pandoc.types import (
    CodeBlock,
    DoubleQuote,
    Format,
    Header,
    Meta,
    Pandoc,
    Para,
    Quoted,
    RawBlock,
    Space,
    Str,
)

# ------------------------------------------------------------------------------
URL = "https://raw.githubusercontent.com/jgm/pandoc/2.14.2/MANUAL.txt"

src = urlopen(URL).read().decode("utf-8")

### TODO: create and insert diff here?

doc = pandoc.read(src)

in_section = False
new_doc = Pandoc(Meta({}), [])
meta, blocks = doc[:]
for block in blocks:
    if not in_section:
        if isinstance(block, Header):
            header = block
            level, attr, inlines = header[:]
            if level == 1:
                if inlines == [Str("Pandoc’s"), Space(), Str("Markdown")]:
                    in_section = True
                    new_doc[1].append(header)
    else:
        if isinstance(block, Header) and block[0] == 1:
            in_section = False
        else:
            new_doc[1].append(block)

# Add manual source
# ------------------------------------------------------------------------------
reference = pandoc.read(f"**Source:** <{URL}>")[1]
new_doc[1][1:1] = reference

# Massage code blocks
# ------------------------------------------------------------------------------
locations = [
    path[-1]
    for elt, path in pandoc.iter(new_doc, path=True)
    if isinstance(elt, CodeBlock)
]

for holder, i in reversed(locations):
    attr, text = codeblock = holder[i]
    codeblock[0] = ("", ["markdown"], [])
    indented_text = "\n".join(4 * " " + line for line in text.splitlines())
    wrapper = CodeBlock(("", [], []), indented_text)

    elt = pandoc.read(text)
    python_repr = repr(elt)

    replacement = [
        Para([Str("==="), Space(), Quoted(DoubleQuote(), [Str("Markdown")])]),
        wrapper,
        Para([Str("==="), Space(), Quoted(DoubleQuote(), [Str("Python")])]),
        CodeBlock(("", [], []), 4 * " " + python_repr),
        RawBlock(Format("html"), "<!-- prevent container tabs merge -->"),
    ]
    holder[i : i + 1] = replacement

# ------------------------------------------------------------------------------

pandoc.write(new_doc, "mkdocs/markdown.md", format="markdown-raw_attribute")
