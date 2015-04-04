
import __builtin__
import collections
import json
import sys

import pandoc.types
import pandoc.types.defs

class map(collections.OrderedDict):
    pass

def load(json_obj, type_): # TODO: rename typedef ? Dunno.
    if isinstance(type_, str):
        py_type = pandoc.types.types[type_]
        if py_type in __builtin__.__dict__.values():
            return py_type(json_obj)
        elif isinstance(py_type, pandoc.types.Type):
            return py_type
        else:
            return load(json_obj, pandoc.types.defs.find(type_))

    if type_[0] == "type":
        return load(json_obj, type_[1][1])
    elif type_[0] == "list":
        list_type = type_[1][0]
        return list([load(item, list_type) for item in json_obj])
    elif type_[0] == "tuple":
        tuple_types = type_[1]
        return tuple([load(item, item_type) 
                      for item, item_type in zip(json_obj, tuple_types)])
    elif type_[0] == "map":
        key_type, value_type = type_[1]
        return map([(load(k, key_type), load(v, value_type)) 
                   for k, v in json_obj.items()])
    elif type_[0] in ("data", "newtype"):
        # deal with the "normal case" and the "record one" or "newtype"
        constructors = type_[1][1]
        if len(constructors) == 1 and constructors[0][1][0] == "record":
            constructor = constructors[0]
            type_name = constructor[0]
            key_types = constructor[1][1]
            key_value_types = [(k, json_obj[k], t) for k, t in key_types]
            kwargs = map([(k, load(v, t)) for k, v, t in key_value_types])
            return pandoc.types.types[type_name](**kwargs) 
        elif len(constructors) == 1 and type_[0] == "newtype":
            # Concretely, only one occurence: Format. Not sure what Aeson
            # would produce in general ...
            constructor = constructors[0]
            type_name = constructor[0]
            if len(constructor[1]) == 1:
                objs = [json_obj]
            else:
                objs = json_obj
            items = []
            for item, item_type in zip(objs, constructor[1]):
                items.append(load(item, item_type))
            return pandoc.types.types[type_name](*items)
        else:
#            print "TYPE", type_
#            print "JSON OBJ", json_obj
            for constructor in constructors:
                name = constructor[0]
                if name == json_obj["t"]:
                    break
            if constructor[1]:
                if len(constructor[1]) == 1:
                    objs = [json_obj["c"]]
                else:
                    objs = json_obj["c"]
                # TODO: need to add an extra list level when there is a solo
                #       argument to a constructor. (try on doc1.txt). Fuck, 
                #       where am I supposed to do that ?
                items = []
                for item, item_type in zip(objs, constructor[1]):
                    items.append(load(item, item_type))
                return getattr(types, name)(*items)
            else:
                return getattr(types, name)

def alt_repr(item, depth=0):
    pad = 2 * u" "
    tab = depth * pad

    if isinstance(item, types.Data):
        if item.args:
            out = [tab, unicode(type(item).__name__), u"("]
            for arg in item.args:
                out += [u"\n", alt_repr(arg, depth + 1), u"\n", tab, pad, u","]
            if len(item.args):
                out = out[:-2] + [")"]
            else:
                out = out + [")"]
        else: # singleton
            out = [tab, item.name]
    elif isinstance(item, types.Record):
        out = [tab, unicode(type(item).__name__), u"("]
        for k, v in item.kwargs.items():
            out += [u"\n", tab + pad, k, "=", u"\n", alt_repr(v, depth + 1), u"\n", tab, pad, u","]
        if len(item.kwargs):
            out = out[:-2] + [")"]
        else:
            out = out + [")"]
    elif isinstance(item, list):
        out = [tab, u"["]
        for child in item:
            out += [u"\n", alt_repr(child, depth + 1), u"\n", tab, pad, u","]
        if len(item):
            out = out[:-2] + ["]"]
        else:
            out += ["]"] 
    elif isinstance(item, tuple):
        out = [tab, u"("]
        for child in item:
            out += [u"\n", alt_repr(child, depth + 1), u"\n", tab, pad, u","]
        if len(item):
            out = out[:-2] + [")"]
        else:
            out += [")"] 
    elif isinstance(item, map):
        out = [tab, u"map("]
        if len(item):
            out += [u"\n", alt_repr(list(item.items()), depth + 1), u"\n"]
        out += [u")"]
    else: # ?
        try:
            string = unicode(item)
        except (UnicodeEncodeError, UnicodeDecodeError):
            string = item.decode("utf-8")
        out = [tab, repr(string)]
    return u"".join(out) 


