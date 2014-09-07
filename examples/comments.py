#!/usr/bin/env python
"""
Pandoc filter that causes everything between
'<!-- BEGIN COMMENT -->' and '<!-- END COMMENT -->'
to be ignored.  The comment lines must appear on
lines by themselves, with blank lines surrounding
them.
"""

# Python 2.7 Standard Library
import sys

# Third-Party Libraries
from pandoc import *


in_comment = False

def comment(item):
    global in_comment

    if isinstance(item, RawBlock):
        format, content = item.args
        if format == "html":
            if "<!-- BEGIN COMMENT -->" in content:
                in_comment = True
                return nothing # None is ambiguous ?
                # if there is no None in the documents, go for it right ?
                # or reserve None for "implicitly return the input argument ?"
            elif "<!-- END COMMENT -->" in content:
                in_comment = False
                return nothing

    if isinstance(item, PandocType):
        if not in_comment:
            return item
        else:
            return nothing
    elif isinstance(item, list):
        return [x for x in item if x is not nothing]
    else:
        return item           
                
if __name__ == "__main__":
    input = sys.stdin.read()
    doc = read(input)
    print write(fold(comment, doc))
