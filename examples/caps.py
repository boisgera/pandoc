#!/usr/bin/env python
"""
Pandoc filter to convert all regular text to uppercase.
Code, link URLs, etc. are not affected.
"""

# Python 2.7 Standard Library
import sys

# Third-Party Libraries
import pandoc

def caps(item):
    if isinstance(item, pandoc.Str):
        content = item.args[0]
        return pandoc.Str(content.upper())
    else:
        return item

if __name__ == "__main__":
    input = sys.stdin.read()
    doc = pandoc.read(input)
    print pandoc.write(pandoc.fold(caps, doc))


