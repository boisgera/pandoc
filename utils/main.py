#!/usr/bin/env python

# Python 2.7 Standard Library
import json
import re
import StringIO
import sys

# Third-Party Libraries
from bs4 import BeautifulSoup as BS
import requests
import sh


# Constants & Helpers
# ------------------------------------------------------------------------------
GHCI_SCRIPT = \
"""
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

def write_version_info(output):
    html = requests.get('http://hackage.haskell.org/package/pandoc').content
    soup = BS(html, 'html.parser')
    contents = soup.find(id='properties').table.tbody.tr.td.contents
    strings = []
    for content in contents:
        try:
             strings.append(content.string)
        except AttributeError:
            pass
    versions = []
    for string in strings:
        if len(string) >= 1 and string[0] in '0123456789':
            versions.append(string.encode('utf-8'))
    
    # 1.8 is good enough (JSON support starts there)
    versions = [v for v in versions if version_key(v) >= [1, 8]]

    output.write('{\n')
    for i, version in enumerate(versions):
        print version + ":",
        output.write('"' + str(version) + '": ') 
        url = 'http://hackage.haskell.org/package/pandoc-{0}/src/pandoc.cabal'
        url = url.format(version)
        cabal_file = requests.get(url).content
        for line in cabal_file.splitlines():
            line = line.strip()
            if 'pandoc-types' in line:
                vdep = line[13:-1]
                vdep = [c.strip().split(' ') for c in vdep.split('&&')]
                print vdep
                output.write(json.dumps(vdep))
                if i < len(versions) - 1:
                    output.write(',')
                output.write('\n')
                break
    output.write('}')

tmp = StringIO.StringIO()
write_version_info(tmp)
version_map = json.loads(tmp.getvalue())


# Type Definitions Fetcher
# ------------------------------------------------------------------------------
def setup():
    # create output directory
#    if not os.path.isdir("definitions"):
#        os.mkdir("definitions")

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

def write_type_definitions(output):
    # Create/enter the pandoc-types project directory
    setup()
    sh.cd("pandoc-types")

    # get the version tags, write the (ordered) list down
    versions = sh.git("tag").split()
    versions.sort(key=version_key)

    # 1.8 is good enough (JSON support starts there)
    versions = [v for v in versions if version_key(v) >= [1, 8]]

#    tags.sort(key=version_key)
#    versions_file = open("../definitions/versions", "w")
#    for tag in tags:
#      print >> versions_file, tag
#    versions_file.close()

    # TODO: single-tag from sys.argv
#    if len(sys.argv) == 2:
#        if sys.argv[1] in tags:
#            tags = [sys.argv[1]]
#        else:
#            print "error: unknown version {0}".format(tag)
#            sys.exit(1)

    stack_not_found = False

    sh.rm("-rf", "stack.yaml")
    sh.git("checkout", ".")

    output.write('{\n')
    for i, version in enumerate(versions):
        # cleanup
        if stack_not_found:
            sh.rm("-rf", "stack.yaml") 
            stack_not_found = False
        sh.git("checkout", ".")

        print 80*"-"

        sh.git("checkout", version)

        try:
            stack_not_found = False
            sh.ls("stack.yaml")
            print "{0}: found stack.yaml file".format(version)
        except:
            stack_not_found = True
            print "{0}: no stack.yaml file found".format(version)
            sh.stack("init", "--solver")
    #        stack_file = open("stack.yaml", "w")
    #        stack_file.write(STACK_YAML)
    #        stack_file.close()


        builder_src = str(sh.cat("Text/Pandoc/Builder.hs"))
        builder_src = """
          {-# LANGUAGE TypeSynonymInstances, FlexibleInstances,  
          MultiParamTypeClasses,
          DeriveDataTypeable, GeneralizedNewtypeDeriving, CPP, StandaloneDeriving,
          DeriveGeneric, DeriveTraversable, AllowAmbiguousTypes #-}
          """ + \
          builder_src

    #    if "FlexibleInstances" not in builder_src:
    #        print "didn't find flexible instances"
    #        lines = builder_src.split("\n")
    #        lines[0] = "{-# LANGUAGE TypeSynonymInstances, FlexibleInstances #-}"
    #        builder_src = "\n".join(lines)

        fragment = "(<>) :: Monoid a => a -> a -> a\n(<>) = mappend"
        builder_src = builder_src.replace(fragment, "")

    #    builder_src = "{-# LANGUAGE AllowAmbiguousTypes #-}\n" + builder_src 

        if not version.startswith("1.8") and \
            "import Data.Semigroup" not in builder_src:
            builder_src += """
#if MIN_VERSION_base(4,11,0)
instance Semigroup Inlines where
    (<>) = mappend
instance Semigroup Blocks where
    (<>) = mappend
#endif
"""

        b = open("Text/Pandoc/Builder.hs", "w")
        b.write(builder_src)
        b.close()

        try:
            print "setting up stack ..."
            for line in sh.stack("setup", _iter=True, _err_to_out=True):
                print "   ", line,
            print "building ..."
            for line in sh.stack("build", _iter=True, _err_to_out=True):
                print "   ", line,
        except Exception as error:
            message = error.stdout
            for line in message.splitlines():
                print >> sys.stderr, "    ", line
            # TODO: print error to file (.error instead of .hs)
            # this filter here is not good enough
            ansi_escape = re.compile(r'\x1b[^m]*m')
            message = ansi_escape.sub('', message)
            #message = "".join(char for char in message if isprint(char))
            #open("../definitions/{0}.error".format(version), "w").write(message)
            #continue
            raise RuntimeError(message)

        print "running GHCI script ..."
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
        definition = ''.join(lines)
        output.write(json.dumps(version) + ': ')
        output.write(json.dumps(definition)) 
        if i < len(versions) - 1:
            output.write(',')
        output.write('\n\n')

#        output_file = open("../definitions/{0}.hs".format(version), "w")
#        output_file.write(output)
#        output_file.close()
    output.write('}')
     
    sh.cd("..")




# Main
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    output = open('pandoc-types.js', 'w')
    output.write('{\n')
    output.write('"version_mapping":\n')
    write_version_info(output)
    output.write(',\n')
    output.write('"definitions":\n') 
    write_type_definitions(output)
    output.write('\n}')

