#!/usr/bin/env python
# coding: utf-8

import setuptools

# Pandoc Metadata
# ------------------------------------------------------------------------------
m = {}
exec(open("src/pandoc/about.py").read(), m)
metadata = dict((k, v) for (k, v) in m.items() if not k.startswith("_"))

# Setup Configuration
# ------------------------------------------------------------------------------
contents = {
    "packages": setuptools.find_packages("src"),
    "package_dir": {"": "src"},
    "package_data": {"pandoc": ["pandoc-types.json", "tests.md"]},
}
requirements = {
    "install_requires": ["plumbum", "ply"],
}

info = {}
info.update(metadata)
info.update(contents)
info.update(requirements)

info["long_description"] = open("README.md", encoding="utf-8").read()
info["long_description_content_type"] = "text/markdown"

if __name__ == "__main__":
    setuptools.setup(**info)
