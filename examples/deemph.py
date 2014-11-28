#!/usr/bin/env python
"Pandoc filter that causes emphasized text to be displayed in ALL CAPS."

# Uhu ? Keeps the emphasis or not ?

# Python 2.7 Standard Library
import sys

# Third-Party Libraries
from pandoc import *

def de_emphasize(item):
    if isinstance(item, Emph):
        # need to de-emphasize, and (recursively) apply-all caps.
        return item.args
    else:
        return item           

if __name__ == "__main__":
    pass
    #input = sys.stdin.read()
    #doc = read(input)
    #print write(fold(de_emphasize, doc))

