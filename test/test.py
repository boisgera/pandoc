#!/usr/bin/env python

# Python 2.7 Standard Library
import json
import os
import os.path
import sys

# Third-Party Libraries (local)
sys.path.insert(0, "../lib")
import path
import sh

# Pandoc (local)
sys.path.insert(0, "..")
import pandoc

def main():
    src = path.path("src")

    dst = path.path("dst")
    if not dst.exists():
        dst.mkdir()
    for file in dst.files():
        file.remove()

    md_files = [file for file in src.listdir() if file.ext in [".txt", ".md"]]
    md_files.sort(key=lambda file: file.getsize())
    for md_file in md_files:
        namebase = md_file.namebase
        print "{0:20} ...".format(namebase[:20]), 
        js_file = namebase + ".js"

        error = False
        try:
            sh.pandoc("-t", "json", "-o", dst / js_file, md_file)
            json1 = json.load(open(dst / js_file), object_pairs_hook=pandoc.Map)
            doc = pandoc.to_pandoc(json1)
            py_file = namebase + ".py"
            output = open(dst / py_file, "w")
            output.write(repr(doc))
            js2_file = namebase + "2" + ".js"
            json2 = pandoc.to_json(doc)
            json.dump(json2, open(dst /js2_file, "w"))
            sh.pandoc("-t", "markdown", "-o", dst / namebase + ".txt", 
                      "-f", "json", dst / js2_file)
        except Exception:
            error = True        

        if not error and json1 == json2:
            print "OK"
        else:
            print "FAIL"

# TODO: use argparse
# TODO: verbose mode
# TODO: select the name of a test (for full error diagnostic)
if __name__ == "__main__":
    main()

