#!/usr/bin/env python

import urllib

import pandoc
from pandoc.types import *

# ------------------------------------------------------------------------------

# TODO: read ANTLR visitor stuff ?


# FMap
# ------------------------------------------------------------------------------

# Here we would like to specify a function that does some elementary
# pandoc elt to "something" transformation, but that does not encode
# the recursion part, that would be taken care of by fmap.

# Wait a minute, is it going to be simpler? To really factor out the
# code that is repeated to allow the user to express its transformations
# more easily? Yeah, if something has to be done here, it should be
# pragmatic: we are just uneasy in the current code because unpack_divs_2
# is copying so much of the code of 'copy' without reuse. Solve this
# first and everything will be ok. Right?

# Nota: in the fmap / tree examples out there,

# Not sure fmap is the right wording here, but nevermind, we will
# solve this pb later. To begin with, the fmap thingy signature is
# fmap: (a -> b) -> (f a -> f b), so to begin with, the structures
# before and after are the same ("of type f") which is not what we
# want here: we may be willing to transform a Pandoc tree into
# plain text for example.

# The prototype of f would be? Could it be a type to type transformation?
# Too abstract? (Nota: if 'type' is taken to be factory, yeah, it's as
# powerful as we want, but it may be a bit mind-boggling)

def fmap(f, elt):
    pass

    
# Div Unpacking
# ------------------------------------------------------------------------------
def unpack_divs(doc):
    "Unpack Divs - Two-pass, In-Place Algorithm"

    # Locate the divs and extract the relevant data
    matches = []
    for elt, path in pandoc.iter(doc, path=True):
        if isinstance(elt, Div):
            div = elt
            parent, index = path[-1]
            contents = div[1]
            # Blocks are always held in lists (cf. the document model).
            assert isinstance(parent, list)
            matches.append((parent, index, contents))

    # We need to unpack the divs in reverse document order 
    # not to invalidate the remaining matches.
    for parent, index, contents in reversed(matches):
        del parent[index]
        parent[index:index] = contents

    return doc

# Can we make "copy" more general, "fmap"-like? So that we can use it
# in unpack_div instead of hard-copying it?
def copy(elt):
    "Copy the document (or document fragment) recursively"
    # List, tuple, map and (non-primitive) Pandoc types
    if hasattr(elt, "__iter__") and not isinstance(elt, String):
        type_ = type(elt)
        if type_ is map:
            args = list(elt.items())
        else:
            args = elt[:]
        new_args = [copy(arg) for arg in args]
        if issubclass(type_, (list, tuple, map)):
            return type_(new_args)
        else: # Pandoc types
            return type_(*new_args)
    else: # Python atomic (immutable) types
        return elt 

def is_blocks(elt):
    "Identify (non-empty) lists of blocks"
    return isinstance(elt, list) and \
           len(elt)!=0 and \
           isinstance(elt[0], Block)

def unpack_divs_2(elt):
    "Unpack Divs - One-Pass, Recursive, Non-Destructive Algorithm"
    # Find the list of blocks and their div children and unpack them
    if is_blocks(elt):
        blocks = elt
        new_blocks = []
        for block in blocks:
            if isinstance(block, Div):
                div = block
                contents = div[1]
                new_blocks.extend(unpack_divs_2(contents))
            else:
                new_blocks.append(unpack_divs_2(block))
        assert not any([isinstance(block, Div) for block in new_blocks])
        return new_blocks
    # List, tuple, map and (non-primitive) Pandoc types
    elif hasattr(elt, "__iter__") and not isinstance(elt, String):
        type_ = type(elt)
        if type_ is map:
            args = list(elt.items())
        else:
            args = elt[:]
        new_args = [unpack_divs_2(arg) for arg in args]
        if issubclass(type_, (list, tuple, map)):
            return type_(new_args)
        else: # Pandoc types
            return type_(*new_args)
    else: # Python atomic (immutable) types
        return elt 


# Main Content Extraction
# ------------------------------------------------------------------------------
def remove_preamble(doc):
    "Remove everything before the first real paragraph"
    blocks = doc[1]
    for i, block in enumerate(blocks):
        if isinstance(block, Para):
            para = block
            inlines = para[0]
            if len(inlines) > 0 and isinstance(inlines[0], Str):
                break
    doc[1] = blocks[i:]
    return doc


# Simplify
# ------------------------------------------------------------------------------
def simplify(doc):
    doc = unpack_divs(doc)
    # doc = unpack_divs_2(doc)
    doc = remove_preamble(doc)
    return doc


# Entry Point
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    url = 'https://pandoc.org/getting-started.html'
    src = urllib.request.urlopen(url).read()
    doc = pandoc.read(src, format="html")
    doc = simplify(doc)
    print(pandoc.write(doc, format="markdown", options=["-s"]))

