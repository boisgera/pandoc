
from ._types import defs

def find(name):
    for def_ in defs:
        if name == def_[1][0]:
            return def_

# TODO: def to string (string to def ? bootstrapping issue ?).

