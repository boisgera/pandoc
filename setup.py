#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
import os
import sys
import warnings

# Python Setup Dependencies
try:
    import setuptools
except ImportError:
    error  = "pip is not installed, "
    error += "refer to <http://www.pip-installer.org> for instructions."
    raise ImportError(error)
sys.path.insert(0, "lib")
import about
import sh

# Python Runtime Dependencies
requirements = dict(install_requires="sh")

# Local
sys.path.insert(0, "")
import about_pandoc

# Non-Python Runtime Dependencies 
try:
    pandoc = sh.pandoc
    magic, version = sh.pandoc("--version").splitlines()[0].split()
    assert magic == "pandoc"
    assert version.startswith("1.12") or version.startswith("1.13")
except:
    # if root runs the setup script, it's ok if pandoc is not available,
    # as long as the users have it. Hence we cannot raise an exception here,
    # we only produce a warning. 
    warnings.warn("cannot find pandoc 1.12 / 1.13")

# ------------------------------------------------------------------------------

contents = dict(py_modules=["pandoc", "about_pandoc"])
metadata = about.get_metadata(about_pandoc)
        
info = {}
info.update(contents)
info.update(metadata)
info.update(requirements)

# ------------------------------------------------------------------------------

if __name__ == "__main__":
    setuptools.setup(**info)

