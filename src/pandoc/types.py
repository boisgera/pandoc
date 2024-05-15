# coding: utf-8

# Python 3 Standard Library
import dataclasses
import re

from abc import ABCMeta
from collections import Counter
from collections.abc import Sequence
from functools import partial
from typing import Any, Dict, List, Optional, Tuple

# Pandoc
import pandoc
import pandoc.utils


def _to_snake_case(x: str):
    # https://stackoverflow.com/questions/1175208
    return re.sub(r"(?<!^)(?=[A-Z])", "_", x).lower()


def _to_plural(word: str):
    # https://en.wikipedia.org/wiki/English_plurals
    if word.endswith("y") and len(word) > 1 and word[-2] not in "aeiou":
        return word[:-1] + "ies"
    elif word.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"
    else:
        return word + "s"


def _rename_duplicate_fields(fields: List[str]):
    counter = Counter(fields)

    counter_max = 0
    for k, v in counter.items():
        if v > counter_max:
            counter_max = v
        if v == 1:
            # We set to 0 the entries we do not want to process
            counter[k] = 0

    if counter_max == 1:
        return fields

    # For each duplicated entry concatenate and decrease the counter value
    ret = list(fields)
    for i, r in reversed(list(enumerate(ret))):
        if (c := counter.get(r, 0)) > 0:
            ret[i] += str(c)
            counter[r] -= 1

    return ret


def _field_type_name(field_type, field):
    if (
        isinstance(field, list)
        and field[0] == field_type
        and isinstance(field[1], list)
        and len(field[1]) == 1
        and isinstance(field[1][0], str)
    ):
        return field[1][0]
    else:
        return None


def _rename_fields(fields: List[str], names: Dict[str, str]) -> List[str]:
    result = fields.copy()

    for old_name, new_name in names.items():
        try:
            result[result.index(old_name)] = new_name
        except ValueError:
            pass

    return result


def _get_data_fields(decl: List[Any]) -> List[Field]:
    type_name = decl[0]
    type_def = decl[1]
    fields = []

    if type_def[0] == "map":
        for x in type_def[1]:
            field = _to_snake_case(x[0]).lower()
            field = field.removeprefix(type_name.lower()).lstrip("_")
            fields.append(field)
    else:
        for x in type_def[1]:
            if isinstance(x, str):
                if x == "Int" or x == "Double":
                    field = "value"
                else:
                    field = _to_snake_case(x.removeprefix(type_name))
            elif field := _field_type_name("maybe", x):
                field = _to_snake_case(field).lower()
                field = field.removeprefix(type_name.lower()).lstrip("_")
            elif field := _field_type_name("list", x):
                if (
                    type_name != "Pandoc"
                    and not type_name.startswith("Meta")
                    and (field == "Block" or field == "Inline")
                ):
                    field = "content"
                else:
                    field = _to_snake_case(field).lower()
                    field = field.removeprefix(type_name.lower()).lstrip("_")
                    field = _to_plural(field)
            else:
                field = "content"

            fields.append(field)

    fields = _rename_duplicate_fields(fields)

    # Handle special cases
    if type_name == "Meta":
        fields = _rename_fields(fields, {"un_meta": "map"})
    elif type_name == "Header":
        fields = _rename_fields(fields, {"value": "level"})
    elif type_name == "TableBody":
        fields = _rename_fields(fields, {"rows1": "head", "rows2": "body"})

    return fields


# Haskell Type Constructs
# ------------------------------------------------------------------------------
def _fail_init(self, *args, **kwargs):
    type_name = type(self).__name__
    error = "Can't instantiate abstract class {type}"
    raise TypeError(error.format(type=type_name))


class MetaType(ABCMeta):
    def __repr__(cls):
        doc = getattr(cls, "__doc__", None)
        if doc is not None:
            return doc
        else:
            return type.__repr__(cls)


Type = MetaType("Type", (object,), {"__init__": _fail_init})


class Data(Type):
    pass


class TypeDef(Type):
    pass


class Constructor(Sequence):
    pass


def _data_get_attr(self, key):
    return self.attr[key]


def _data_set_attr(self, value, key):
    self.attr = self.attr[:key] + (value,) + self.attr[key + 1 :]


_data_property_identifier = property(
    partial(_data_get_attr, key=0), partial(_data_set_attr, key=0)
)
_data_property_classes = property(
    partial(_data_get_attr, key=1), partial(_data_set_attr, key=1)
)
_data_property_attributes = property(
    partial(_data_get_attr, key=2), partial(_data_set_attr, key=2)
)


def _data_getitem(self, key):
    if isinstance(key, int):
        return getattr(self, self._fields[key])
    elif isinstance(key, slice):
        return [
            getattr(self, self._fields[i])
            for i in range(*key.indices(len(self._fields)))
        ]
    else:
        raise ValueError("Invalid argument type.")


def _data_setitem(self, key, value):
    if isinstance(key, int):
        setattr(self, self._fields[key], value)
    elif isinstance(key, slice):
        if not isinstance(value, Sequence):
            raise ValueError("Can only assign a sequence.")
        else:
            slice_indices = list(range(*key.indices(len(self._fields))))
            if len(slice_indices) != len(value):
                raise ValueError(
                    "The number of elements to assign must be the same as "
                    "the number of elements of the slice."
                )
            for i in slice_indices:
                setattr(self, self._fields[i], value[i])
    else:
        raise ValueError("Invalid argument type.")


def _data_len(self):
    return len(self._fields)


def _data_iter(self):
    return (getattr(self, f) for f in self._fields)


def _make_constructor_class(
    name: str, fields: List[str], bases: Tuple[type, ...], attrs: Dict[str, Any]
):
    assert "tag" not in fields and "t" not in fields

    namespace = {
        "__getitem__": _data_getitem,
        "__iter__": _data_iter,
        "__len__": _data_len,
        "__setitem__": _data_setitem,
        "_fields": fields,
        "t": name,
        "tag": name,
    }

    namespace.update(attrs)

    if "attr" in fields:
        assert (
            "identifier" not in fields
            and "classes" not in fields
            and "attributes" not in fields
        )

        namespace.update(
            {
                "identifier": _data_property_identifier,
                "classes": _data_property_classes,
                "attributes": _data_property_attributes,
            }
        )

    c = dataclasses.make_dataclass(
        name, [(f, Any, None) for f in fields], bases=bases, namespace=namespace
    )

    # Save the __repr__ method in another field, so that we are able
    # to restore it we change the print options
    setattr(c, "_default_repr", c.__repr__)

    return c


# Pandoc Types
# ------------------------------------------------------------------------------

_types_version = None
_types_dict = {}


def _make_builtin_types():
    "Create Builtin Types"
    td = _types_dict
    td["Bool"] = bool
    td["Double"] = float
    td["Int"] = int
    td["String"] = str
    td["Text"] = str
    td["list"] = list
    td["tuple"] = tuple
    td["map"] = dict


def clear_types():
    """Uninstall Pandoc Types"""
    global _types_version
    global _types_dict
    globs = globals()

    # Uninstall registered types
    for type_name in _types_dict:
        del globs[type_name]
    _types_version = None
    _types_dict = {}


def make_types(version: str):
    """Create Pandoc Types"""

    global _types_version

    if version == _types_version:
        # types already initialized for the indicated version
        return

    global _types_dict
    globs = globals()

    # Uninstall existing types (if any)
    clear_types()

    # Create builtin types
    _make_builtin_types()

    # Load & parse the types definition
    defs_src = pandoc.utils.definitions[version]
    if not isinstance(defs_src, str):  # resource loaded as bytes in Python 3
        defs_src = defs_src.decode("utf-8")

    defs = pandoc.utils.parse(defs_src)

    # Create the types
    for decl in defs:
        decl_type = decl[0]
        type_name = decl[1][0]
        if decl_type in ("data", "newtype"):
            # Remark: when there is a constructor with the same name as its
            #         data type, the data type is shadowed.
            #         This was intentional, because in pandoc-types < 1.21,
            #         it used to happens only there is a single constructor.
            #         But, now we have ColWidth, which is either a ColWidth(Double)
            #         or a ColWidthDefault. So we need to adapt the model : we
            #         add a "_" to the end of the constructor and patch the decl
            constructors = decl[1][1]
            if len(constructors) > 1:
                for constructor in constructors:
                    constructor_name = constructor[0]
                    if constructor_name == type_name:
                        constructor[0] = constructor_name + "_"

            _dict = {"_def": decl, "__doc__": pandoc.utils.docstring(decl)}
            data_type = type(type_name, (Data,), _dict)
            _types_dict[type_name] = data_type

            for constructor in constructors:
                constructor_name = constructor[0]
                fields = _get_data_fields(constructor)
                bases = (Constructor, data_type)
                _dict = {
                    "_def": constructor,
                    "__doc__": pandoc.utils.docstring(constructor),
                }
                type_ = _make_constructor_class(constructor_name, fields, bases, _dict)

                _types_dict[constructor_name] = type_
        elif decl_type == "type":
            _dict = {"_def": decl, "__doc__": pandoc.utils.docstring(decl)}
            type_ = type(type_name, (TypeDef,), _dict)
            _types_dict[type_name] = type_

    # Install the types
    globs.update(_types_dict)
    _types_version = version


# Print options
# ------------------------------------------------------------------------------


def _dataclass_no_keyword_repr(self) -> str:
    field_repr = (repr(getattr(self, f.name)) for f in dataclasses.fields(self))
    return self.__class__.__name__ + "(" + ", ".join(field_repr) + ")"


def _dataclass_no_keyword_rich_repr(self):
    for f in (getattr(self, f.name) for f in dataclasses.fields(self)):
        yield f


def print_options(show_fields: bool = False, types: Optional[List[Type]] = None):
    types = types or [v for _, v in _types_dict.items()]
    for t in types:
        if issubclass(t, Constructor):
            if show_fields:
                if hasattr(t, "_default_repr"):
                    setattr(t, "__repr__", t._default_repr)
                if hasattr(t, "__rich_repr__"):
                    delattr(t, "__rich_repr__")
            else:
                setattr(t, "__repr__", _dataclass_no_keyword_repr)
                setattr(t, "__rich_repr__", _dataclass_no_keyword_rich_repr)


# Create Types
# ------------------------------------------------------------------------------
if pandoc.configure(read=True) is None:
    pandoc.configure(auto=True)
