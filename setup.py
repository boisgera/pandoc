#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
from __future__ import absolute_import
import os
import shutil
import sys
import tempfile
import warnings

# Pip Package Manager
# ------------------------------------------------------------------------------
try:
    import pip
    import setuptools
    import pkg_resources
except ImportError:
    error = "pip is not installed, refer to <{url}> for instructions."
    raise ImportError(error.format(url="http://pip.readthedocs.org"))

# Local Libraries
# ------------------------------------------------------------------------------


# Pandoc Metadata
# ------------------------------------------------------------------------------
def local(path):
    return os.path.join(os.path.dirname(__file__), path)
sys.path.insert(0, local(".lib"))
import about
tmp_dir = tempfile.mkdtemp()
source = local("src/pandoc/about.py")
target = os.path.join(tmp_dir, "about_pandoc.py")
shutil.copyfile(source, target)
sys.path.insert(0, tmp_dir)
import about_pandoc
del sys.path[0]
shutil.rmtree(tmp_dir)
metadata = about.get_metadata(about_pandoc)

# Setup Configuration
# ------------------------------------------------------------------------------

contents = {
  "packages": setuptools.find_packages("src"),
  "package_dir": {"": "src"},
  "package_data": {"pandoc": ["pandoc-types.js", "tests.md"]},
}
requirements = {
  "install_requires": ["plumbum", "ply"],
}
tests = {
  "test_suite": "pandoc.tests.suite"
}

info = {}
info.update(metadata)
info.update(contents)
info.update(requirements)
info.update(tests)

# Pypi fails to render the ReStructuredText content, override the README.
info["long_description"] = "GitHub: https://github.com/boisgera/pandoc"

if __name__ == "__main__":
    setuptools.setup(**info)

