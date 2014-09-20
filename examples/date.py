#!/usr/bin/env python

# Python 2.7 Standard Library
import datetime
import sys

# Third-Party Libraries
import sh
from pandoc import *

def add_date(doc, date):
    date_doc = from_markdown(date)
    date_inlines = date_doc[1][0][0]
    map = doc[0][0]
    map["date"] = MetaInlines(date_inlines)    

def help():
    print """
usage: date.py FILENAME

Insert the current date into a markdown file.
"""

def main():
    args = sys.argv
    try:
        filename = args[1]
    except IndexError:
        help()
        sys.exit(1)

    input = open(filename)
    src = input.read()
    input.close()
    doc = from_markdown(src)
    date = datetime.datetime.now().strftime("%A, %d %B %Y")
    add_date(doc, date)
    dst = to_markdown(doc)
    output = open(filename, "w")
    output.write(dst)
    output.close()

if __name__ == "__main__":
    main()

