#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
from __future__ import absolute_import
import distutils
import os.path
import re
import subprocess
import types

# Third-Party Libraries
import pkg_resources

# About Metadata
from .about import *

# Markdown to ReStructuredText
# ------------------------------------------------------------------------------
def to_rst(markdown):
    pandoc = distutils.spawn.find_executable("pandoc")
    if pandoc:
        args = [pandoc, "-f", "markdown", "-t", "rst"]
        options = {"stdin":subprocess.PIPE, "stdout":subprocess.PIPE}
        p = subprocess.Popen(args, **options)
        p.stdin.write(markdown.encode("utf-8"))
        return p.communicate()[0].decode("utf-8")

# Generation of Metadata for Setuptools
# ------------------------------------------------------------------------------
trove = None

def clean(text):
    text = text.replace("(", "").replace(")", "")
    text = text.replace("/", " ")
    text = text.replace(" - ", " ")
    return text.lower()

def generate_trove():
    global trove
    if trove is None:
        trove = []
        load = pkg_resources.resource_string
        trove_text = load("about", "Trove-classifiers.txt")
        if hasattr(trove_text, "decode"):
            trove_text = trove_text.decode("utf-8")
        for trove_id in trove_text.splitlines():
            parts = trove_id.split(u" :: ")
            context = clean(" ".join(parts[:-1])).split()
            name = clean(parts[-1]).split()
            trove.append({"id": trove_id, "name": name, "context": context})

def match_score(items, ref_items, trove=trove):
    matches = [item in ref_items for item in items].count(True)
    score = float(matches) / (len(items) + len(ref_items) - matches)
    return score

def trove_search(keyword):
    generate_trove()
    parts = [p.strip().lower() for p in keyword.split(u"/")]
    try:
        name = parts[-1].split() 
        if len(parts) == 2:
            context = parts[0].split()
        else:
            context = None
    except:
        error = u"Invalid keyword {keyword!r}"
        raise ValueError(error.format(keyword=keyword))
    matches = {}
    for item in trove:
        score = match_score(name, item["name"])
        matches.setdefault(score, []).append(item)
    max_ = sorted(matches.keys())[-1]
    if len(matches[max_]) == 1:
        return matches[max_][0]["id"]
    elif context:
        submatches = {}
        subtrove = matches[max_]
        for item in subtrove:
            score = match_score(item["context"], context)
            submatches.setdefault(score, []).append(item)
        max_ = sorted(submatches.keys())[-1]
        if len(submatches[max_]) == 1:
            return submatches[max_][0]["id"]

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
        email_pattern = u"<([^>]+@[^>]+)>"
        match = re.search(email_pattern, author)
        if match is not None:
            setuptools_kwargs["author_email"] = email = match.groups()[0]
            setuptools_kwargs["author"] = author.replace(u"<" + email + u">", u"").strip()
        else:
            setuptools_kwargs["author"] = author

    # Get the module summary.
    summary = metadata.get("__summary__")
    if summary is not None:
        setuptools_kwargs["description"] = summary

    # Get and process the module README.
    README_filenames = ["README.md", "README.txt", "README"]
    for filename in README_filenames:
        if os.path.isfile(filename):
            README = open(filename).read()
            if hasattr(README, "decode"):
                README = README.decode("utf-8")
            README_rst = to_rst(README)
            setuptools_kwargs["long_description"] = README_rst or README
            break

    # Process keywords that match trove classifiers.
    keywords = metadata.get("__keywords__")
    if keywords is not None:
        classifiers = []
        keywords = [k.strip() for k in keywords.split(",")]
        for keyword in keywords:
            trove_id = trove_search(keyword)
            if trove_id is not None:
                classifiers.append(trove_id)
        classifiers = sorted(list(set(classifiers)))
        setuptools_kwargs["classifiers"] = classifiers

    return setuptools_kwargs

