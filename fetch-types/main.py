#!/usr/bin/env python

# Python 3.7 Standard Library
import json
import os
from pathlib import Path
import re
import sys
import typing

# Third-Party Libraries
import bs4
import requests
import sh


# Helpers
# ------------------------------------------------------------------------------
def version_key(version) -> list[int]:
    if version.startswith("v"):
        version = version[1:]
    try:
        return [int(s) for s in version.split(".")]
    except ValueError:  # alpha/beta versions, etc.
        return None


# Pandoc Types Info Schema
# ------------------------------------------------------------------------------
class PandocTypes(typing.TypedDict):
    version_mapping: dict[str, list[list[str]]]
    definitions: dict[str, str]


# Pandoc to Pandoc Types Version Mapping
# ------------------------------------------------------------------------------
def pandoc_versions() -> list[str]:
    """
    Get the existing pandoc versions from Hackage

    >>> pandoc_versions() # doctest: +ELLIPSIS
    ['0.4', '0.41', '0.42', '0.43', ...]
    """
    pandoc_url = "http://hackage.haskell.org/package/pandoc"
    html = requests.get(pandoc_url).content
    soup = bs4.BeautifulSoup(html, "html.parser")
    contents = soup.find(id="properties").table.tbody.tr.td.contents
    strings = []
    for content in contents:
        try:
            strings.append(content.string)
        except AttributeError:
            pass
    versions = []
    for string in strings:
        if len(string) >= 1 and string[0] in "0123456789":
            versions.append(string)
    return versions


def pandoc_types_dependency(pandoc_version: str) -> list[list[str]]:
    """
    Get the range of pandoc-types versions that match a given pandoc version.

    >>> pandoc_types_dependency("0.4")
    None
    >>> pandoc_types_dependency("1.8")
    [['==', '1.8.*']]
    >>> pandoc_types_dependency("3.8.1")
    [['>=', '1.23.1'], ['<', '1.24']]
    """
    url = "http://hackage.haskell.org/package/pandoc-{0}/src/pandoc.cabal"
    url = url.format(pandoc_version)
    cabal_file = requests.get(url).content.decode("utf-8")
    for line in cabal_file.splitlines():
        line = line.strip()
        if "pandoc-types" in line:
            vdep = line[13:-1]
            vdep = [c.strip().split(" ") for c in vdep.split("&&")]
            return vdep


def update_version_mapping(pandoc_types: PandocTypes) -> None:
    """
    Update the pandoc-types dependencies info
    """
    versions = pandoc_versions()

    # start with 1.8 (no pandoc JSON support before)
    versions = [v for v in versions if version_key(v) >= [1, 8]]

    # fetch the data only for unregistered versions
    version_mapping = pandoc_types["version_mapping"]
    versions = [v for v in versions if v not in version_mapping]
    # remove 2.10.x (see https://github.com/boisgera/pandoc/issues/22)
    versions = [v for v in versions if v != "2.10" and not v.startswith("2.10.")]

    for version in versions:
        vdep = pandoc_types_dependency(version)
        if vdep is not None:
            version_mapping[version] = vdep


# Type Definitions Fetcher
# ------------------------------------------------------------------------------

shopts = {"_out": sys.stderr, "_err_to_out": True}

def clone_pandoc_types() -> None:
    """
    Git clone the pandoc-types repository
    """
    sh.rm("-rf", "pandoc-types")
    sh.git("clone", "https://github.com/jgm/pandoc-types.git", **shopts)
    sh.chmod("go-w", "pandoc-types") # conform to stack requirements

def pandoc_types_versions() -> list[str]:
    """
    Return the ordered list of pandoc-types versions
    """
    try:
        os.chdir("pandoc-types")
        version_string = str(sh.git("--no-pager", "tag"))  # no ANSI escape codes
        versions = [
            version
            for version in version_string.split()
            if version_key(version) is not None
        ]
        versions.sort(key=version_key)
        # start with 1.8 (no pandoc JSON support before)
        versions = [v for v in versions if version_key(v) >= [1, 8]]
        return versions
    finally:
        os.chdir("..")


def stack_build(version) -> None:
    """
    Build pandoc-types with stack
    """
    # Note: this function only works for pandoc-types >= 1.20
    try:
        os.chdir("pandoc-types")
        print(f"*** Check out pandoc-types version {version}")
        sh.git("--no-pager", "checkout", "-f", version)
        print("*** Setting up stack", file=sys.stderr)
        sh.stack("setup", **shopts)
        print("*** Building pandoc-types", file=sys.stderr)
        sh.stack("build", **shopts)
    finally:
        os.chdir("..")

GHCI_SCRIPT = """
import Data.Map (Map)
:load Text.Pandoc.Definition
putStrLn ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
:browse Text.Pandoc.Definition
putStrLn "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
"""

def pandoc_types_type_definitions() -> str:
    """
    Return the pandoc-types type definitions
    """
    # Works only for pandoc-types >= 1.22.1
    try:
        os.chdir("pandoc-types")
        # install the GHCI script
        script = open(".ghci", "w")
        script.write(GHCI_SCRIPT)
        script.close()
        sh.chmod("go-w", ".ghci") # conform to stack requirements
        print("*** running GHCI script ...")
        collect = False
        lines = []
        for line in sh.stack("ghci", _iter=True):
            if line.startswith(">>>>>>>>>>"):
                collect = True
            elif line.startswith("<<<<<<<<<<"):
                collect = False
                break
            elif collect == True:
                sline = line.strip()
                if not (
                    sline.startswith("type") and sline.endswith(":: *")
                ):  # e.g. "type ListNumberStyle :: *"
                    lines.append(line)
        definitions = "".join(lines)
        return definitions
    finally:
        os.chdir("..")


def update_type_definitions(pandoc_types: PandocTypes) -> None:
    # Registered definitions
    type_definitions = pandoc_types["definitions"]
    versions = pandoc_types_versions()
    for version in versions:
        if version not in pandoc_types["definitions"]:
            try:
                stack_build(version)
                definitions = pandoc_types_type_definitions()
                type_definitions[version] = definitions
            except:
                error = f"❌ failed to get type defs for version {version}" 
                print(error, file=sys.stderr)

def main() -> None:
    # Load the pandoc types registry of the source tree
    with open("../src/pandoc/pandoc-types.js") as input:
        pandoc_types = json.load(input)
    clone_pandoc_types()
    # Update it with new version mapping and definitions
    update_version_mapping(pandoc_types)
    update_type_definitions(pandoc_types)
    # Dump the updated registry in the current directory
    with open("pandoc-types.js", "w") as output:
        json.dump(pandoc_types, output, indent=2)
    sh.rm("-rf", "pandoc-types")

if __name__ == "__main__":
    main()
