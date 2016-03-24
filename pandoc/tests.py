
# Python 2.7 Directives
from __future__ import absolute_import

# Python 2.7 Standard Library
import pandoc.doctest
import doctest
import unittest
import sys
import tempfile

# Third-Party Libraries
import pkg_resources


path = pkg_resources.resource_filename("pandoc", "tests.md")
suite = doctest.DocFileSuite(path, module_relative=False)

def run():
    # TODO: use doctest API instead.
    result = unittest.TestResult()
    suite.run(result)
    return result

