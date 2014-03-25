# coding: utf-8
"""
About - Metadata for Setuptools
"""

# Python 2.7 Standard Library
import importlib
import inspect
import os
import re
import sys

# Third-Party Libraries
import setuptools

# Metadata
__project__ = "about"
__author__  = u"Sébastien Boisgérault <Sebastien.Boisgerault@gmail.com>"
__version__ = "0.2.1"
__license__ = "MIT License"


def get_metadata(name, path=None):
    """
    Return metadata for setuptools `setup`.
    """

    if path is None:
        path = os.getcwd()
    sys.path.insert(0, path)
    about_data = importlib.import_module(name).__dict__
    if path is not None:
        del sys.path[0]
    metadata = {}

    # read the relevant __*__ module attributes
    for name in "project name author version license doc url classifiers".split():
        value = about_data.get("__" + name + "__")
        if value is not None:
            metadata[name] = value

    # when "project" is here, it overrides the (generated) "name" attribute
    project = metadata.get("project")
    if project is not None:
        metadata["name"] = project
        del metadata["project"]

    # search for author email with <...@...> syntax in the author field
    author = metadata.get("author")
    if author is not None:
        email_pattern = r"<([^>]+@[^>]+)>"
        match = re.search(email_pattern, author)
        if match is not None:
            metadata["author_email"] = email = match.groups()[0]
            metadata["author"] = author.replace("<" + email + ">", "").strip()

    # get the module short description from the docstring
    doc = metadata.get("doc")
    if doc is not None:
        lines = [line for line in doc.splitlines() if line.strip()]
        metadata["description"] = lines[0].strip()
        del metadata["doc"]

    # process trove classifiers
    classifiers = metadata.get("classifiers")
    if classifiers and isinstance(classifiers, str):
        classifiers = [l.strip() for l in classifiers.splitlines() if l.strip()]
        metadata["classifiers"] = classifiers

    return metadata

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
        # TODO: clean up unused fields, add some setuptools fields
        #       (install requires, entry_points, etc.)
        attrs = [
            ("name", metadata.get_name()),
            ("version", metadata.get_version()),
            ("summary", metadata.get_description()),
            ("home page", metadata.get_url()),
            ("author", metadata.get_contact()),
            ("author_email", metadata.get_contact_email()),
            ("license", metadata.get_licence()),
            ("description", metadata.get_long_description()),
            ("keywords", metadata.get_keywords()),
            ("platform", metadata.get_platforms()),
            ("classifiers", metadata.get_classifiers()),
            ("download url", metadata.get_download_url()),
            # PEP 314
            ("provides", metadata.get_provides()),
            ("requires", metadata.get_requires()),
            ("obsoletes", metadata.get_obsoletes()),
        ]
        print
        for name, value in attrs:
            print "  - " + name + ":", value
        print

if __name__ == "__main__":
    import about
    local = open("about.py", "w")
    local.write(open(inspect.getsourcefile(about)).read())
    local.close()
    
