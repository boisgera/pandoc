#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
import importlib
import inspect
import os
import pydoc
import re
import sys
import types

# Third-Party Libraries
from path import path
import pkg_resources
import setuptools
import sh
try:
    pandoc = sh.pandoc
except sh.CommandNotFound:
    pandoc = None
    warning  = "warning: "
    warning += "pandoc is not available, ReST content generation is disabled."
    print >> sys.stderr, warning


# Metadata
__main__ = (__name__ == "__main__")

def _open(filename):
    "Open a data file with the Resource Management API"
    requirement = pkg_resources.Requirement.parse(__name__)
    try:
        file = open(pkg_resources.resource_filename(requirement, filename))
    except (IOError, pkg_resources.DistributionNotFound):
        file = open(filename)
    return file

metadata = dict(
    __name__        = "about",
    __version__     = "3.0.0-alpha.4",
    __license__     = "MIT License",
    __author__      = u"Sébastien Boisgérault <Sebastien.Boisgerault@gmail.com>",
    __url__         = "https://warehouse.python.org/project/about",
    __summary__     = "Software Metadata for Humans",
    __readme__      = None,
    __doc__         = __doc__,
    __classifiers__ = ["Programming Language :: Python :: 2.7" ,
                       "Topic :: Software Development"         ,
                       "Operating System :: OS Independent"    ,
                       "Intended Audience :: Developers"       ,
                       "License :: OSI Approved :: MIT License",
                       "Development Status :: 3 - Alpha"       ]
)

globals().update(metadata)

def setup(source, **kwargs):
    setuptools_kwargs = get_metadata(source)
    setuptools_kwargs.update(kwargs)
    return setuptools.setup(**setuptools_kwargs)

def get_metadata(source):
    """
    Extract the metadata from the module or dict argument.

    It returns a `metadata` dictionary that provides keywords arguments
    for the setuptools `setup` function.
    """

    if isinstance(source, types.ModuleType):
        metadata = source.__dict__
    else:
        metadata = source

    setuptools_kwargs = {}

    for key in "name version url license".split():
        val = metadata.get("__" + key + "__")
        if val is not None:
            setuptools_kwargs[key] = val

    version = metadata.get("__version__")
    if version is not None:
        setuptools_kwargs["version"] = version

    # Search for author email with a <...@...> syntax in the author field.
    author = metadata.get("__author__")
    if author is not None:
        author = author.encode("utf-8")
        email_pattern = r"<([^>]+@[^>]+)>"
        match = re.search(email_pattern, author)
        if match is not None:
            setuptools_kwargs["author_email"] = email = match.groups()[0]
            setuptools_kwargs["author"] = author.replace("<" + email + ">", "").strip()
        else:
            setuptools_kwargs["author"] = author

    # Get the module summary and readme.
    summary = metadata.get("__summary__")
    if summary is not None:
        setuptools_kwargs["description"] = summary
    readme = metadata.get("__readme__")
    # The readme is supposed to be in markdown.
    if readme is not None:
        # Try to refresh the ReST documentation in 'doc/doc.rst'
        if pandoc:
            readme_rst = str(pandoc("-t", "rst", _in=readme))             
        else:
            warning = "warning: cannot generate the ReST documentation."
            print >> sys.stderr, warning
            rst = readme_rst # d'oh!
        setuptools_kwargs["long_description"] = readme_rst

    # Process trove classifiers.
    classifiers = metadata.get("__classifiers__")
    if classifiers and isinstance(classifiers, str):
        classifiers = [c.strip() for c in classifiers.splitlines() if c.strip()]
    setuptools_kwargs["classifiers"] = classifiers

    return setuptools_kwargs

def printer(line, stdin):
    print line,

class About(setuptools.Command):

    description = "Display Project Metadata"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        metadata = self.distribution.metadata

        attrs = [
            ("name"     , metadata.name       ),
            ("version"  , metadata.version    ),
            ("summary"  , metadata.description),
            ("home page", metadata.url        ),
            ("license"  , metadata.license    ),
        ]

        author = metadata.author
        maintainer = metadata.maintainer
        if author:
            attrs.extend([
                ("author", metadata.author      ),
                ("e-mail", metadata.author_email),
            ])
        if maintainer and maintainer != author:
            attrs.extend([
                ("maintainer", metadata.maintainer      ),
                ("e-mail"    , metadata.maintainer_email),
            ])

        desc = metadata.long_description
        if desc:
           line_count = len(desc)
           attrs.append(("description", "yes ({0} lines)".format(line_count)))
        else:
           attrs.append(("description", None))

        attrs.extend([
            # I am ditching "keywords" but keeping "classifiers".
            # (no one is declaring or using "keywords" AFAICT)
            ("classifiers" , metadata.classifiers     ),
            # How can we specify the platforms in the setup.py ?
            ("platforms"   , metadata.platforms       ),
            # Do we need a download url ?
            ("download url", metadata.download_url    ),
        ])

        # Get the mandatory, runtime, declarative dependencies 
        # (managed by setuptools).
        attrs.append(("requires", self.distribution.install_requires))

        print
        for name, value in attrs:
            print "  - " + name + ":",
            if isinstance(value, list):
                print
                for item in value:
                  print "      - " + str(item)
            elif isinstance(value, basestring):
                lines = value.splitlines()
                if len(lines) <= 1:
                    print value
                else:
                    print
                    for line in lines:
                        print "      | " + line
            else:
                print "undefined"
        print


if __main__:
    import about # this, my dear, is buggy if about exist locally.
    local = open("about.py", "w")
    local.write(open(inspect.getsourcefile(about)).read())
    local.close()

