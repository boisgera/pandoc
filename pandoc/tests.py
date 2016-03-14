
# Python 2.7 Standard Library
import doctest
import unittest

# Third-Party Libraries
import pkg_resources


path = pkg_resources.resource_filename("pandoc", "tests.txt")
suite = doctest.DocFileSuite(path, module_relative=False)

def run():
    result = {}
    suite.run(result)
    return result

