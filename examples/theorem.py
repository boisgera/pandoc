#!/usr/bin/env python
"""
Pandoc filter to convert divs with class="theorem" to LaTeX
theorem environments in LaTeX output, and to numbered theorems
in HTML output.
"""

# Python 2.7 Standard Library
import sys

# Third-Party Libraries
import pandoc

# Errrrr ... the html div stuff is not even picked up as Div in a html to
# html conversion ? WTF ? Oh, fuck this is kind of pandoc 1.13 specific,
# read more in the changelog.

theoremcount = 0

def LATEX(x):
  return RawBlock("latex",x)

def HTML(x):
  return RawBlock("html", x)

_count = 0

def theorem(mode):
    def transform(item):
        global _count
        if isinstance(item, pandoc.Div):
            attrs, contents = item.args
            if mode == "html":
                new_contents = [HTML("<dt>Theorem " + str(_count) + "</dt>"),
                                HTML("<dd>")] + contents + [HTML("</dd>\n</dl>")]
                _count = _count + 1
                return pandoc.Div(attrs, new_contents)
            elif mode == "latex":
                pass
        else:
            return item
    return transform


def to_html(item):
    if isinstance(item, pandoc.Div):
        pass
    else:
        return item

def to_latex(item):
    if isinstance(item, pandoc.Div):
        pass
    else:
        return item



if __name__ == "__main__":
    input = sys.stdin.read()
    args = sys.argv
    if "--latex" in args:
        f = theorem("latex")
    elif "--html" in args:
        f = theorem("html")
    else:
        raise ValueError("unspecified mode (--latex or --html)")

    doc = pandoc.read(input)
    print pandoc.to_json(pandoc.fold(f, doc))


