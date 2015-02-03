#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
import os
import sys
import warnings

# Pip Package Manager
try:
    import pip
    import setuptools
    import pkg_resources
except ImportError:
    error = "pip is not installed, refer to <{url}> for instructions."
    raise ImportError(error.format(url="http://pip.readthedocs.org"))

def local(path):
    return os.path.join(os.path.dirname(__file__), path)

# Extra Third-Party Libraries
sys.path.insert(1, local(".lib"))
try:
    setup_requires = ["about>=4.0.0", "sh"]
    require = lambda *r: pkg_resources.WorkingSet().require(*r)
    require(*setup_requires)
    import about
except pkg_resources.DistributionNotFound:
    error = """{req!r} not found; install it locally with:

    pip install --target=.lib --ignore-installed {req}
"""
    raise ImportError(error.format(req=" ".join(setup_requires)))
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

