#!/usr/bin/env python

# Python Standard Library
import doctest
import platform
import sys
import re

# Third-Party Libraries
import strictyaml

# Test Files
# ------------------------------------------------------------------------------
mkdocs_pages = strictyaml.load(open("mkdocs.yml").read())["pages"].data
mkdocs_files = ["mkdocs/" + list(item.values())[0] for item in mkdocs_pages]
extra_testfiles = []
test_files = mkdocs_files + extra_testfiles

# Run the Tests
# ------------------------------------------------------------------------------
verbose = "-v" in sys.argv or "--verbose" in sys.argv

fails = 0
tests = 0
for filename in test_files:
    options = {"module_relative": False, "verbose": verbose}

    # Relax the tests to deal with test files that have a '\n' line break
    # (Linux flavor) which does not match the pandoc line break on Windows 
    # (Windows flavor : '\r\n').
    # The proper way to deal with this would be to convert the test files 
    # beforehand on Windows.
    if platform.system() == "Windows": 
        options["optionflags"] = doctest.NORMALIZE_WHITESPACE

    _fails, _tests = doctest.testfile(filename, **options)
    fails += _fails
    tests += _tests

if fails > 0 or verbose:
   print()
   print(60*"-")
   print("Test Suite Report:", end="")
   print("{0} failures / {1} tests".format(fails, tests))
   print(60*"-")
if fails:
    sys.exit(1)
 
