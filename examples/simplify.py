#!/usr/bin/env python

import urllib

import pandoc
from pandoc.types import *

# NOTA: the delete scheme is a bit different: sure we *could* do exactly
# the same, but it makes more sense to iterate "search-pattern-then-transform"
# since we may get rid of some parts of the document in the process and
# therefore decrease the amount of work needed. In other words the iteration
# and mutation process are much more intertwined if we "do it right"...
#
# NOTA: does the delete scheme suggest a more general "iterate, then
# do stuff (produce, transform), then iterate on something else I am
# giving you? A much more flexible/interactive iteration scheme?
#
# NOTA: sometimes it is much more handy to match not the top-lvl elt 
# involved in a pattern but the childs and afterwards get the parent.
# For example to find a div and get its holder, working at that parent
# level requires to know (and test) the list of types that hold a 
# list of blocks. But if we search divs directly, we don't care ...

# ------------------------------------------------------------------------------

# TODO: consider "immutable" schemes here. Are they simpler ?
# Have a look at classic patterns (fmaps for trees? monads ? etc.)
# Have a look at Haskell management of trees AND the example of pandoc
# (e.g. the pandoc/markdown to HTML translation)
# <https://github.com/jgm/pandoc/blob/master/src/Text/Pandoc/Writers/HTML.hs> 
# OK, I have looked at that, the looks of it is very imperative actually;
# this is a mix of Monads with a big Options & State system, some
# basic pattern matching (type-based mostly) and some limited use of
# recursion ...
# Shit, I really wouldn't know how to implement the one-pass,
# recursive, immutable (copy-based) version of unpack_divs ...
# Yeah, actually i know, but i don't like it at all since it involves
# listing all the Block holders ... and "where" (positionally)
# they hold blocks.

# TODO: read ANTLR visitor stuff.

# TODO: find by id / class / k-v pattern ?



def is_navbar(elt):
    if isinstance(elt, Div):
        _, classes, _ = elt[0]
        for cls in classes:
            if cls.startswith('navbar'):
                return True
    return False

def remove_navbar(doc):
    navs = []
    for path in pandoc.iter_path(doc):
        elt = path[-1]
        if is_navbar(elt):
            nav = elt
            holder = path[-2]
            navs.append((holder, nav))

    for holder, navs in navs:
        for i, elt in enumerate(holder):
            if elt is nav:
                del holder[i]
                break

def add_toc_header(doc):
    toc = None
    for elt in pandoc.iter(doc):
        if isinstance(elt, Div):
            id_, _, _ = elt[0]
            if id_ == 'toc':
                toc = elt
                break
    contents = toc[1]

    level = 1
    attr = ("", [], [])
    # alternatively, use a string and "read":
    # title = pandoc.read("Table of Contents")[1][0][0]
    title = [Str("Table"), Space(), Str("of"), Space(), Str("Contents")]
    header = Header(level, attr, title)
    contents.insert(0, header)

# Div Unpacking
# ------------------------------------------------------------------------------
# TODO: document this 2-pass "match-then-transform" mutable algorithm structure.
def unpack_divs(doc):
    # Locate divs and extract the relevant data for the mutation step
    matches = []
    for elt, path in pandoc.iter(doc, path=True):
        if isinstance(elt, Div):
            div = elt
            parent, index = path[-1]
            contents = div[1]
            # Blocks are always held in lists (cf. the document model).
            assert isinstance(parent, list)
            matches.append((parent, index, contents))

    # We iterate the div matches in reverse order. 
    # Like this we can mutate the document in the for loop 
    # and have the remaining matches remain valid.
    for parent, index, contents in reversed(matches):
        del parent[index]
        parent[index:index] = contents

# Pandoc Block Holders:
#
# Pandoc Meta [Block]
# MetaBlocks [Block]
# TableCell [Block]
# BlockQuote [Block]
# BulletList [[Blocks]]
# OrderedList ListAttributes [[Block]]
# DefinitionList [([Inline], [[Block]])]    # FUCK ME!
# Div Attr [Block]
# Note [Block]

# In the recursive (immutable) version, we need to search for any
# block holder (at the pandoc type level) and update the children
# at this level. Unless we just track lists and see if they hold
# blocks and everything works?

def is_blocks(elt): # (non-empty) list of blocks
    return isinstance(elt, list) and \
           len(elt)!=0 and \
           isinstance(elt[0], Block)

def unpack_divs_2(elt):
    # find list of blocks, look out for divs and unpack them
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
    # list, tuple, map and (non-primitive) Pandoc types
    elif hasattr(elt, "__iter__") and not isinstance(elt, String):
        type_ = type(elt)
        if type_ is map:
            args = list(elt.items())
        else:
            args = elt[:]
        new_args = [unpack_divs_2(arg) for arg in args]
        if issubclass(type_, (list, tuple, map)):
            return type_(new_args)
        else: # Pandoc type
            return type_(*new_args)
    else: # Python atomic (immutable) types
        return elt 

 

# ------------------------------------------------------------------------------

def cleanup_header(doc):
    blocks = doc[1]
    for i, block in enumerate(blocks):
        if isinstance(block, Header):
            break
    doc[1] = blocks[i:]

def add_title(doc):
    title = "Pandoc -- A Universal Document Converter"
    metadata = pandoc.read("%" + title)[0]
    doc[0] = metadata

# focus mainly on the unpack divs and add a minor cleanup: 
# is getting rid of everything before the first paragraph 
# is good enough? Do something with the span sub-title here?
# Arf the subtitle is common to all pages, it has to go
# 
# The cleanup is actually easier BEFORE the div purge since
# we have more data then.
# The easiest thing to do is probably to locate the table of
# contents and get rid of everything before it?
# Well this is slightly messy since we are already nested
# in divs, so how do we do that? Ouch, this is a MASSIVE pain ...
# The toc (and the rest of the document) is at a level 4 nesting.
# It would be VERY suspicious to have some code getting rid of
# everything BUT THE DIVS, just to have another one get rid of
# the divs afterwards ...
# The easiest way to go would be to insert a marker (header?)
# in the document to locate our first paragraph once the stuff
# is flattened, but this is slightly hackish and requires a 
# pre and post step. Mmmm.

def prettify(doc):
    #remove_navbar(doc)
    #add_toc_header(doc)
    #unpack_divs(doc)
    doc = unpack_divs_2(doc)
    #cleanup_header(doc)
    #add_title(doc)
    return doc

if __name__ == "__main__":
    url = 'https://pandoc.org/getting-started.html'
    src = urllib.request.urlopen(url).read()
    doc = pandoc.read(src, format="html")
    doc = prettify(doc)
    print(pandoc.write(doc, format="markdown", options=["-s"]))

