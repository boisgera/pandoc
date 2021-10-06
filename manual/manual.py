#!/usr/bin/env python

# Python Standard Library
from urllib.request import urlopen

# Pandoc
import pandoc
from pandoc.types import (
    BulletList,
    CodeBlock,
    DefinitionList,
    DoubleQuote,
    Format,
    Header,
    Meta,
    Pandoc,
    Para,
    Plain,
    Quoted,
    RawBlock,
    Space,
    Str,
    Strong,
)

# ------------------------------------------------------------------------------
URL = "https://raw.githubusercontent.com/jgm/pandoc/2.14.2/MANUAL.txt"
# src = urlopen(URL).read().decode("utf-8")
src = open("MANUAL-patched.txt").read()

### TODO: create and insert diff here?

# Hack to avoid having the "links" header title repeated
# ------------------------------------------------------------------------------
src = src.replace("#### Links", "#### ???") # remove the links h4 title

# Extract the "Pandoc's Markdown" section
# ------------------------------------------------------------------------------
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
        if isinstance(block, Header) and \
            block[2] == [Str("Non-default"), Space(), Str("extensions")]:
            in_section = False
            break
        else:
            new_doc[1].append(block)

# Add Pandoc's manual reference
# ------------------------------------------------------------------------------
reference = pandoc.read(f"**Source:** <{URL}>")[1]
new_doc[1][1:1] = reference

# Manage definition lists
# ------------------------------------------------------------------------------
found = []
for elt, path in pandoc.iter(new_doc, path=True):
    if isinstance(elt, DefinitionList):
        found.append(path[-1])

for holder, i in reversed(found):
    definition_list = holder[i]
    list_of_blocks = []
    for term, definitions in definition_list[0]:
        # definitions is a list of list of blocks (several defs are possible)
        assert len(definitions) == 1 # document-dependent
        blocks = [Plain([Strong(term + [Str(".")])])] + definitions[0]
        list_of_blocks.append(blocks)

    holder[i] = BulletList(list_of_blocks)

# Massage code blocks
# ------------------------------------------------------------------------------
locations = [
    path[-1]
    for elt, path in pandoc.iter(new_doc, path=True)
    if isinstance(elt, CodeBlock) and "skip" not in elt[0][1] # classes
]

def indent(text, lvl=4):
    return "\n".join(lvl*" " + line for line in text.splitlines)


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

pandoc.write(new_doc, "../mkdocs/markdown.md", format="markdown-raw_attribute")
