
# Python 2.7 Standard Library
from __future__ import absolute_import, print_function
import argparse
import collections
import inspect
import json
import sys

# Third-Party Libraries
pass

# Pandoc
from .about import *
from . import utils
from . import types


# JSON Reader
# ------------------------------------------------------------------------------
def read(json_, type_=types.Pandoc):
    if isinstance(type_, str):
        type_ = getattr(types, type_)
    if not isinstance(type_, list): # not a type def (yet).
        if issubclass(type_, types.Type):
            type_ = type_._def
        else: # primitive type
            return type_(json_)

    if type_[0] == "type": # type alias
        type_ = type_[1][1]
        return read(json_, type_)
    if type_[0] == "list":
        item_type = type_[1][0]
        return [read(item, item_type) for item in json_]
    if type_[0] == "tuple":
        tuple_types = type_[1]
        return tuple(read(item, item_type) for (item, item_type) in zip(json_, tuple_types))
    if type_[0] == "map":
        key_type, value_type = type_[1]
        return types.map([(read(k, key_type), read(v, value_type)) for (k, v) in json_.items()])

    data_type = None
    constructor = None
    if type_[0] in ("data", "newtype"):
        data_type = type_
        constructors = data_type[1][1]
        if len(constructors) == 1:
            constructor = constructors[0]
        else:
            constructor = getattr(types, json_["t"])._def
    elif type_[0][0] == type_[0][0].upper():
        constructor = type_
        constructor_type = getattr(types, constructor[0])
        data_type = constructor_type.__mro__[2]._def

    single_type_constructor = (len(data_type[1][1]) == 1)
    single_constructor_argument = (len(constructor[1][1]) == 1)
    is_record = (constructor[1][0] == "map")

    json_args = None
    args = None
    if not is_record:
        if single_type_constructor:
            json_args = json_
        else:
            json_args = json_["c"]
        if single_constructor_argument:
            json_args = [json_args]
        args = [read(jarg, t) for jarg, t in zip(json_args, constructor[1][1])]
    else:
        keys = [k for k,t in constructor[1][1]]
        types_= [t for k, t in constructor[1][1]]
        json_args = [json_[k] for k in keys]
        args = [read(jarg, t) for jarg, t in zip(json_args, types_)]
    C = getattr(types, constructor[0])
    return C(*args)


# JSON Writer
# ------------------------------------------------------------------------------
def write(object_):
    odict = collections.OrderedDict
    type_ = type(object_)
    if not isinstance(object_, types.Type):
        if isinstance(object_, (list, tuple)):
            json_ = [write(item) for item in object_]
        elif isinstance(object_, dict):
            json_ = odict((k, write(v)) for k, v in object_.items())
        else: # primitive type
            json_ = object_
    else:
        constructor = type(object_)._def
        data_type = type(object_).__mro__[2]._def
        single_type_constructor = (len(data_type[1][1]) == 1)
        single_constructor_argument = (len(constructor[1][1]) == 1)
        is_record = (constructor[1][0] == "map")

        json_ = odict()
        if not single_type_constructor:
            json_["t"] = type(object_).__name__

        if not is_record:
            c = [write(arg) for arg in object_]
            if single_constructor_argument:
                c = c[0]
            if single_type_constructor:
                json_ = c
            else:
                json_["c"] = c
        else:
            keys = [kt[0] for kt in constructor[1][1]]
            for key, arg in zip(keys, object_):
                json_[key] = write(arg)
    return json_


# Iteration
# ------------------------------------------------------------------------------
def iter(elt, enter=None, exit=None):
    if enter is not None:
        enter(elt)
    yield elt
    if isinstance(elt, dict):
        elt = elt.items()
    if hasattr(elt, "__iter__") and not isinstance(elt, types.String):
        for child in elt:
             for subelt in iter(child, enter, exit):
                 yield subelt
    if exit is not None:
        exit(elt)

def iter_path(elt):
    path = []
    def enter(elt_):
        path.append(elt_)
    def exit(elt_):
        path.pop()
    for elt_ in iter(elt, enter, exit):
        yield path

def get_parent(doc, elt):
    for path in iter_path(doc):
        elt_ = path[-1]
        if elt is elt_:
             parent = path[-2] if len(path) >= 2 else None
             return parent


# Main Entry Point
# ------------------------------------------------------------------------------
def main():
    prog = "python -m pandoc"
    description = "Read/write pandoc JSON documents with Python"
    parser = argparse.ArgumentParser(prog=prog, description=description)

    try:
        stdin = sys.stdin.buffer
    except:
        stdin = sys.stdin
    parser.add_argument("input", 
                        nargs="?", metavar="INPUT",
                        type=argparse.FileType("rb"), default=stdin,
                        help="input file")
    try:
        stdout = sys.stdout.buffer
    except:
        stdout = sys.stdout
    parser.add_argument("-o", "--output", 
                        nargs="?", 
                        type=argparse.FileType("wb"), default=sys.stdout,
                        help="output file")
    args = parser.parse_args()

    input_text = args.input.read()
    if "b" in args.input.mode:
        # given the choice, we interpret the input as utf-8
        input_text = input_text.decode("utf-8")

    try: # try JSON content first
        json_ = json.loads(input_text, object_pairs_hook=collections.OrderedDict)
        doc = read(json_)
    except:
        pass # maybe it's a Python document?
    else:
        doc_repr = (repr(doc) + "\n") # this repr is 7-bit safe.
        if "b" in args.output.mode:
            # given the choice, we use utf-8.
            doc_repr = doc_repr.encode("utf-8")
        args.output.write(doc_repr)
        return
        
    globs = types.__dict__.copy()
    try:
        doc = eval(input_text, globs)
        json_ = write(doc)
    except:
        pass # not a Python document either ...
    else:
        json_repr = (json.dumps(json_) + "\n") # also 7-bit safe
        if "b" in args.output.mode:
            # given the choice, we use utf-8.
            json_repr = json_repr.encode("utf-8")
        args.output.write(json_repr)
        return

    sys.exit("pandoc (python): invalid input document")


