#!/usr/bin/env python

import pandoc
import pandoc.types
from pandoc.types import *

with open("api.md.template", encoding="utf-8") as file:
    src = file.read()


doc = ""


def indent(text):
    return "\n".join(4 * " " + line for line in text.splitlines())


def list_types(type_):
    _def = type_._def
    types_ = set()
    for elt in pandoc.iter(_def):
        if isinstance(elt, str) and elt[0].isupper():
            types_.add(elt)
    return sorted([x for x in types_ if x != type_.__name__])


def see_also(type_):
    ts = list_types(type_)
    if ts:
        s = "<h5>See also</h5>\n\n"
        for t in ts:
            s += f'<a href="#{t}"><code>{t}</code></a>, '
        s = s[:-2] + "."
        return indent(s)
    else:
        return ""


td = pandoc.types._types_dict

for key in sorted(td):
    if key[0].isupper():
        type_ = td[key]
        if issubclass(type_, Data):
            if issubclass(type_, Constructor):
                type_doc = "Concrete data type"
                type_sig = indent(repr(type_))
                see_also_ = see_also(type_)

            else:
                type_doc = "Abstract data type"
                type_sig = indent(repr(type_))
                see_also_ = see_also(type_)
        elif issubclass(type_, TypeDef):
            type_doc = "Typedef"
            type_sig = indent(repr(type_))
            see_also_ = see_also(type_)
        else:
            type_doc = "Primitive type"
            type_sig = 4 * " " + type_.__name__
            see_also_ = ""
        doc += f"""
<div id="{key}"></div>

??? note "`{key}`"

    {type_doc}

    <h5>Signature</h5>

    ``` skip
{type_sig}
    ```

{see_also_}
"""


src = src.replace("${types_documentation}", doc)
with open("api.md", "w") as file:
    file.write(src)
