#!/usr/bin/env python

# Python 2.7 Standard Library
import argparse
import json
import sys

# Third-Party Libraries
import sh
from pandoc import *

def as_doc(inline_or_block):
    if isinstance(inline_or_block, (Inline, Block)):
        inline_or_block = [inline_or_block]
    if len(inline_or_block)!=0 and isinstance(inline_or_block[0], Inline):
        inline_or_block = [Plain(inline_or_block)]
    doc = Pandoc(unMeta(Map()), inline_or_block)
    return doc

def node_map(node):
    return node

def type_map(type_):

    def unwrap(*args):
        return args[0]

    def to_text(args):
        doc = as_doc(args[0])
        return to_markdown(doc)

    if issubclass(type_, Meta):
        return unwrap
    elif issubclass(type_, MetaValue):
        if type_ is MetaMap:
            return unwrap
        elif type_ is MetaList:
            return unwrap
        elif type_ is MetaBool:
            return unwrap
        elif type_ is MetaString:
            return unwrap
        elif type_ is MetaInlines:
            return to_text
        elif type_ is MetaBlocks:
            return to_text
        else:
            raise AssertionError("invalid Meta type")
    else:
        return type_

def main():
    description = "get metadata as JSON from a markdown document"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("input", nargs='?', 
                         type = argparse.FileType("r"),
                         default = sys.stdin,
                         help = "input file (default: standard input)")
    parser.add_argument("-o", "--output", 
                        type = argparse.FileType("w"),
                        default = sys.stdout,
                        help = "output file (default: standard output)")
    args = parser.parse_args()

    src = args.input.read()
    if args.input != sys.stdin:
        args.input.close()

    doc = from_markdown(src)

    meta = doc[0] # ok. The DOM is borked already, some 't', 'c' stuff is still there.
    args.output.write(repr(meta) + 2*"\n") 
    meta = transform(meta, node_map, type_map)
    args.output.write(repr(meta) + 2*"\n")
    json_ = json.dumps(meta)
    args.output.write(json_ + "\n")

if __name__ == "__main__":
    main()


