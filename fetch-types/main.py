#!/usr/bin/env python

# Python Standard Library
import json
import logging
import os

# Third-Party Libraries
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
    logging.info("Getting version mappings")

    pandoc_url = "https://hackage.haskell.org/package/pandoc"
    headers = {"accept": "application/json"}
    r = requests.get(pandoc_url, headers=headers)
    r.raise_for_status()

    versions = []
    for k, v in sorted(r.json().items(), key=lambda x: version_key(x[0])):
        if v == "normal" and len(k) > 1 and k[0].isdigit():
            versions.append(k)

    # start with 1.8 (no pandoc JSON support before)
    versions = [v for v in versions if version_key(v) >= [1, 8]]

    # fetch the data only for unregistered versions
    version_mapping = pandoc_types["version_mapping"]
    versions = [v for v in versions if v not in version_mapping]
    # remove 2.10.x (see https://github.com/boisgera/pandoc/issues/22)
    versions = [v for v in versions if v != "2.10" and not v.startswith("2.10.")]

    for version in versions:
        logging.info(f"Getting version mapping for version {version}")
        url = f"http://hackage.haskell.org/package/pandoc-{version}/src/pandoc.cabal"
        cabal_file = requests.get(url).content.decode("utf-8")
        for line in cabal_file.splitlines():
            if "pandoc-types" in line:
                vdep = line.strip()[13:-1]
                vdep = [c.strip().split(" ") for c in vdep.split("&&")]
                logging.info(f"Setting mapping for version {version}: {vdep}")
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
    if not os.path.isdir("pandoc-types"):
        logging.info("Cloning pandoc-types repository")
        sh.git("clone", "https://github.com/jgm/pandoc-types.git")
    else:
        logging.info("pandoc-types repository already cloned")

    os.chdir("pandoc-types")

    # sh.rm("-rf", ".git") # don't want to see the folder as a git submodule

    # install the GHCI script
    with open(".ghci", "w") as f:
        f.write(GHCI_SCRIPT)

    # conform to stack requirements
    sh.chmod("go-w", "./")
    sh.chmod("go-w", ".ghci")

    os.chdir("..")


def collect_ghci_script_output():
    logging.info("Running GHCI script ...")
    collect = False
    lines = []
    for line in sh.stack("ghci", _iter=True):
        if line.startswith(">>>>>>>>>>"):
            collect = True
        elif line.startswith("<<<<<<<<<<"):
            collect = False
            break
        elif collect:
            sline = line.strip()
            if not (
                sline.startswith("type") and sline.endswith(":: *")
            ):  # e.g. "type ListNumberStyle :: *"
                lines.append(line)
    definitions = "".join(lines)
    return definitions


# def ansi_escape(string):
#     ansi_escape_8bit = re.compile(
#       r'(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])'
#     )
#     return re.compile(ansi_escape_8bit).sub("", string)


def update_type_definitions(pandoc_types):
    # registered definitions
    type_definitions = pandoc_types["definitions"]

    # fetch the pandoc git repo and get into it
    setup()
    os.chdir("pandoc-types")

    # get the version tags, write the (ordered) list down
    version_string = str(sh.git("--no-pager", "tag"))  # no ANSI escape codes
    versions = version_string.split()
    versions.sort(key=version_key)
    # start with 1.8 (no pandoc JSON support before)
    versions = [v for v in versions if version_key(v) >= [1, 8]]
    # remove 1.21.x from the list (see https://github.com/boisgera/pandoc/issues/22)
    versions = [v for v in versions if v != "1.21" and not v.startswith("1.21.x")]
    # only fetch the data for unregistered versions
    versions = [v for v in versions if v not in type_definitions]

    for version in versions:
        logging.info(f"Getting type definitions - version {version}")

        try:
            sh.git("--no-pager", "checkout", "-f", version)
            if os.path.isfile("stack.yaml"):
                logging.info("Found stack.yaml file")
            else:
                logging.info("No stack.yaml file found")
                try:
                    sh.stack("init", "--solver")
                except sh.ErrorReturnCode as error:
                    logging.error(error.stderr)
                    continue

            try:
                print("setting up stack ...")
                for line in sh.stack("setup", _iter=True, _err_to_out=True):
                    print("   ", line, end="")
                print("building ...")
                for line in sh.stack("build", _iter=True, _err_to_out=True):
                    print("   ", line, end="")
            except sh.ErrorReturnCode as error:
                logging.error(error.stdout)
                continue

            definitions = collect_ghci_script_output()
            type_definitions[version] = definitions
            logging.info(f"Set type definitions - version {version}")
        finally:
            sh.rm("stack.yaml")
    os.chdir("..")


# Main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    pandoc_types_path = os.path.join(
        os.path.dirname(__file__), "../src/pandoc/pandoc-types.json"
    )
    pandoc_types = json.load(open(pandoc_types_path))

    update_type_definitions(pandoc_types)
    update_version_mapping(pandoc_types)

    with open("pandoc-types.json", "w") as f:
        json.dump(pandoc_types, f, indent=2)
