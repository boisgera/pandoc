#!/usr/bin/env python

# Python 3.7 Standard Library
import json
import io
import pathlib
import re
import sys

# Third-Party Libraries
import bs4
import requests
import sh

# Helpers
# ------------------------------------------------------------------------------
def version_key(string):
    return [int(s) for s in string.split(".")]


# Pandoc to Pandoc Types Version Mapping
# ------------------------------------------------------------------------------
#
# We browse the Hackage page for existing pandoc versions,
# get the pandoc.cabal file for every version we're interested in
# (we start at pandoc 1.8 since it is when JSON was introduced)
# "grep" the pandoc-types line inside them, get the dependency spec,
# and write the stuff as JSON.


def update_version_mapping(pandoc_types):
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

    # start with 1.8 (no pandoc JSON support before)
    versions = [v for v in versions if version_key(v) >= [1, 8]]

    # fetch the data only for unregistered versions
    version_mapping = pandoc_types["version_mapping"]
    versions = [v for v in versions if v not in version_mapping]

    for i, version in enumerate(versions):
        print(version + ": ", end="")
        url = "http://hackage.haskell.org/package/pandoc-{0}/src/pandoc.cabal"
        url = url.format(version)
        cabal_file = requests.get(url).content.decode("utf-8")
        for line in cabal_file.splitlines():
            line = line.strip()
            if "pandoc-types" in line:
                vdep = line[13:-1]
                vdep = [c.strip().split(" ") for c in vdep.split("&&")]
                print(vdep)
                version_mapping[version] = vdep
                break


# Type Definitions Fetcher
# ------------------------------------------------------------------------------

GHCI_SCRIPT = """
import Data.Map (Map)
:load Text.Pandoc.Definition
putStrLn ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
:browse Text.Pandoc.Definition
putStrLn "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
"""


def setup():
    # clone the pandoc-types repository
    sh.rm("-rf", "pandoc-types")
    sh.git("clone", "https://github.com/jgm/pandoc-types.git")
    sh.cd("pandoc-types")

    # install the GHCI script
    script = open(".ghci", "w")
    script.write(GHCI_SCRIPT)
    script.close()

    # conform to stack requirements
    sh.chmod("go-w", "../pandoc-types")
    sh.chmod("go-w", ".ghci")

    sh.cd("..")


def collect_ghci_script_output():
    print("running GHCI script ...")
    collect = False
    lines = []
    for line in sh.stack("ghci", _iter=True):
        if line.startswith(">>>>>>>>>>"):
            collect = True
        elif line.startswith("<<<<<<<<<<"):
            collect = False
            break
        elif collect == True:
            lines.append(line)
    definitions = "".join(lines)
    return definitions


def update_type_definitions(pandoc_types):
    # registered definitions
    type_definitions = pandoc_types["definitions"]

    # create the error log and logger function
    sh.rm("-rf", "log.txt")
    logfile = open("log.txt", "w", encoding="utf-8")

    def log(message):
        if isinstance(message, bytes):
            ansi_escape = re.compile(rb"\x1b[^m]*m")
            message = ansi_escape.sub(b"", message)
            message = message.decode("utf-8")
        print(message)
        logfile.write(message + "\n")

    # fetch the pandoc git repo and get into it
    setup()
    sh.cd("pandoc-types")

    # get the version tags, write the (ordered) list down
    versions = str(sh.git("tag")).split()
    versions.sort(key=version_key)
    # start with 1.8 (no pandoc JSON support before)
    versions = [v for v in versions if version_key(v) >= [1, 8]]
    # only fetch the data for unregistered versions
    versions = [v for v in versions if v not in type_definitions]

    typedefs = {}
    for i, version in enumerate(versions):
        log(80 * "-")
        log(f"version: {version}")
        log("")

        try:
            sh.git("checkout", "-f", version)
            if pathlib.Path("stack.yaml").exists():
                log("found stack.yaml file")
            else:
                log("no stack.yaml file found")
                try:
                    sh.stack("init", "--solver")
                except sh.ErrorReturnCode as error:
                    log(error.stderr)
                    log("ABORT")
                    continue

            try:
                print("setting up stack ...")
                for line in sh.stack("setup", _iter=True, _err_to_out=True):
                    print("   ", line, end="")
                print("building ...")
                for line in sh.stack("build", _iter=True, _err_to_out=True):
                    print("   ", line, end="")
            except Exception as error:
                log(error.stdout)
                log("ABORT")
                continue

            # if we've gone so far
            log("OK")
            definitions = collect_ghci_script_output()
            type_definitions[version] = definitions
        finally:
            sh.rm("-rf", "stack.yaml")
    sh.cd("..")


# Main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    pandoc_types = json.load(open("../src/pandoc/pandoc-types.js"))
    update_type_definitions(pandoc_types)
    update_version_mapping(pandoc_types)
    output = open("pandoc-types.js", "w")
    json.dump(pandoc_types, output, indent=2)
