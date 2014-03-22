#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
import os
import sys

# Setup Dependencies
import about
import setuptools
import sh
try:
    pandoc = sh.pandoc
    magic, version = sh.pandoc("--version").splitlines()[0].split()
    assert magic == "pandoc"
    assert version.startswith("1.12")
except:
    raise ImportError("cannot find pandoc 1.12")


contents = dict(py_modules=["pandoc", "about_pandoc"])
metadata = about.get_metadata("pandoc")
requirements = dict(install_requires="sh")

info = {}
info.update(contents)
info.update(metadata)
info.update(requirements)


if __name__ == "__main__":
    setuptools.setup(**info)

