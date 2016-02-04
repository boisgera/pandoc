#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
import os
import shutil
import sys
import tempfile
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
setup_requires = ["about==5.0.0a1"]
for req in setup_requires:
    try:
        require = lambda *r: pkg_resources.WorkingSet().require(*r)
        require(req)
    except pkg_resources.DistributionNotFound:
        error  = "{req!r} not found; install it locally with:"
        error += "\n"
        error += "pip install --target=.lib --ignore-installed {req!r}"
        raise ImportError(error.format(req=" ".join(setup_requires)))
import about

# Local Metadata
tmp_dir = tempfile.mkdtemp()
source = local("pandoc/about.py")
target = os.path.join(tmp_dir, "about_pandoc.py")
shutil.copyfile(source, target)
sys.path.insert(1, tmp_dir)
import about_pandoc
del sys.path[1]
shutil.rmtree(tmp_dir)

# ------------------------------------------------------------------------------
contents = {"packages": setuptools.find_packages()}
requirements = {}
metadata = about.get_metadata(about_pandoc)
        
info = {}
info.update(contents)
info.update(metadata)
info.update(requirements)

print info

# ------------------------------------------------------------------------------
if __name__ == "__main__":
    setuptools.setup(**info)

