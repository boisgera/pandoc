#!/usr/bin/env python

# Python 2.7 Standard Library
import json
import io
import re
import sys

# Third-Party Libraries
from bs4 import BeautifulSoup
import requests
import sh


# Constants & Helpers
# ------------------------------------------------------------------------------
GHCI_SCRIPT = """
import Data.Map (Map)
:load Text.Pandoc.Definition
putStrLn ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
:browse Text.Pandoc.Definition
putStrLn "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
"""


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

def version_info():
    pandoc_url = "http://hackage.haskell.org/package/pandoc"
    html = requests.get(pandoc_url).content
    soup = BeautifulSoup(html, "html.parser")
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

    info = {}
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
                info[version] = vdep
                break
    return info

# Type Definitions Fetcher
# ------------------------------------------------------------------------------
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


def type_definitions():
    # Create/enter the pandoc-types project directory
    setup()
    sh.cd("pandoc-types")

    # get the version tags, write the (ordered) list down
    versions = str(sh.git("tag")).split()
    versions.sort(key=version_key)

    # start with 1.8 (no pandoc JSON support before)
    versions = [v for v in versions if version_key(v) >= [1, 8]]

    stack_not_found = False

    sh.rm("-rf", "stack.yaml")
    sh.git("checkout", ".")

    typedefs = {}
    log = open("log.txt", "w")

    for i, version in enumerate(versions):
        # cleanup
        if stack_not_found:
            sh.rm("-rf", "stack.yaml")
            stack_not_found = False
        sh.git("checkout", ".")

        print(80 * "-")

        sh.git("checkout", version)

        try:
            stack_not_found = False
            sh.ls("stack.yaml")
            print("{0}: found stack.yaml file".format(version))
        except:
            stack_not_found = True
            print("{0}: no stack.yaml file found".format(version))
            try:
                sh.stack("init", "--solver")
            #        stack_file = open("stack.yaml", "w")
            #        stack_file.write(STACK_YAML)
            #        stack_file.close()
            except sh.ErrorReturnCode as error:
                print(error.stderr)

        builder_src = str(sh.cat("Text/Pandoc/Builder.hs"))
        builder_src = (
            """
          {-# LANGUAGE TypeSynonymInstances, FlexibleInstances,  
          MultiParamTypeClasses,
          DeriveDataTypeable, GeneralizedNewtypeDeriving, CPP, StandaloneDeriving,
          DeriveGeneric, DeriveTraversable, AllowAmbiguousTypes #-}
          """
            + builder_src
        )

        #    if "FlexibleInstances" not in builder_src:
        #        print "didn't find flexible instances"
        #        lines = builder_src.split("\n")
        #        lines[0] = "{-# LANGUAGE TypeSynonymInstances, FlexibleInstances #-}"
        #        builder_src = "\n".join(lines)

        fragment = "(<>) :: Monoid a => a -> a -> a\n(<>) = mappend"
        builder_src = builder_src.replace(fragment, "")

        #    builder_src = "{-# LANGUAGE AllowAmbiguousTypes #-}\n" + builder_src

        b = open("Text/Pandoc/Builder.hs", "w")
        b.write(builder_src)
        b.close()

        try:
            print("setting up stack ...")
            for line in sh.stack("setup", _iter=True, _err_to_out=True):
                print("   ", line, end="")
            print("building ...")
            for line in sh.stack("build", _iter=True, _err_to_out=True):
                print("   ", line, end="")
        except Exception as error:
            message = error.stdout
            for line in message.splitlines():
                print("    ", line, file=sys.stderr)
            # TODO: print error to file (.error instead of .hs)
            # this filter here is not good enough

            ansi_escape = re.compile(rb"\x1b[^m]*m")
            message = ansi_escape.sub(b"", message)

            # message = "".join(char for char in message if isprint(char))
            # open("../definitions/{0}.error".format(version), "w").write(message)
            # continue

            print("FAIL:", message.decode("utf-8"))
            log.write(message.decode("utf-8"))
            continue
            # raise RuntimeError(message.decode("utf-8"))

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
        definition = "".join(lines)
        typedefs[version] = definition

    sh.cd("..")
    return typedefs


def _type_definitions():
    # Create/enter the pandoc-types project directory
    setup()
    sh.cd("pandoc-types")

    # get the version tags, write the (ordered) list down
    versions = str(sh.git("tag")).split()
    versions.sort(key=version_key)

    # start with 1.8 (no pandoc JSON support before)
    versions = [v for v in versions if version_key(v) >= [1, 8]]

    typedefs = {}
    log = open("log.txt", "w")

    for i, version in enumerate(versions):
        print(80 * "-")
        # cleanup from the previous round
        sh.rm("-rf", "stack.yaml")
        stack_enabled = False
        sh.git("checkout", version)

        try:
            stack_enabled = True
            sh.ls("stack.yaml")
            print("{0}: found stack.yaml file".format(version))
        except:
            stack_not_found = True
            print("{0}: no stack.yaml file found".format(version))
            try:
                sh.stack("init", "--solver")
            #        stack_file = open("stack.yaml", "w")
            #        stack_file.write(STACK_YAML)
            #        stack_file.close()
            except sh.ErrorReturnCode as error:
                print(error.stderr)
                log.write(80*"-")
                log.write(version + "\n")
                log.write(error.stderr)
                continue

        builder_src = str(sh.cat("Text/Pandoc/Builder.hs"))
        builder_src = (
            """
          {-# LANGUAGE TypeSynonymInstances, FlexibleInstances,  
          MultiParamTypeClasses,
          DeriveDataTypeable, GeneralizedNewtypeDeriving, CPP, StandaloneDeriving,
          DeriveGeneric, DeriveTraversable, AllowAmbiguousTypes #-}
          """
            + builder_src
        )

        #    if "FlexibleInstances" not in builder_src:
        #        print "didn't find flexible instances"
        #        lines = builder_src.split("\n")
        #        lines[0] = "{-# LANGUAGE TypeSynonymInstances, FlexibleInstances #-}"
        #        builder_src = "\n".join(lines)

        fragment = "(<>) :: Monoid a => a -> a -> a\n(<>) = mappend"
        builder_src = builder_src.replace(fragment, "")

        #    builder_src = "{-# LANGUAGE AllowAmbiguousTypes #-}\n" + builder_src

        b = open("Text/Pandoc/Builder.hs", "w")
        b.write(builder_src)
        b.close()

        try:
            print("setting up stack ...")
            for line in sh.stack("setup", _iter=True, _err_to_out=True):
                print("   ", line, end="")
            print("building ...")
            for line in sh.stack("build", _iter=True, _err_to_out=True):
                print("   ", line, end="")
        except Exception as error:
            message = error.stdout
            for line in message.splitlines():
                print("    ", line, file=sys.stderr)
            # TODO: print error to file (.error instead of .hs)
            # this filter here is not good enough

            ansi_escape = re.compile(rb"\x1b[^m]*m")
            message = ansi_escape.sub(b"", message)

            # message = "".join(char for char in message if isprint(char))
            # open("../definitions/{0}.error".format(version), "w").write(message)
            # continue

            print("FAIL:", message.decode("utf-8"))

            log.write(80*"-")
            log.write(version + "\n")
            log.write(message.decode("utf-8"))
            continue
            # raise RuntimeError(message.decode("utf-8"))

        print("running GHCI script ...")
        collect = False
        lines = []
        try:
            for line in sh.stack("ghci", _iter=True):
                if line.startswith(">>>>>>>>>>"):
                    collect = True
                elif line.startswith("<<<<<<<<<<"):
                    collect = False
                    break
                elif collect == True:
                    lines.append(line)
            definition = "".join(lines)
            typedefs[version] = definition
        except sh.ErrorReturnCode as error:
            log.write(80*"-")
            log.write(version + "\n")
            log.write(error.stdout)

    sh.cd("..")
    return typedefs


# Main
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    js = {}
    # temporary outcomment
    js["version_mapping"] = version_info()
    js["definitions"] = type_definitions()
    output = open("pandoc-types.js", "w")
    json.dump(js, output)
