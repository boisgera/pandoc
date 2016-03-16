
# Python 2.7 Directives
from __future__ import absolute_import

# Python 2.7 Standard Library
import doctest
import json
from subprocess import Popen, PIPE
import sys

# Local Library
import pandoc

# Declare a new doctest directive: PANDOC 
PANDOC = doctest.register_optionflag("PANDOC")
doctest.PANDOC = PANDOC
doctest.__all__.append("PANDOC")
doctest.COMPARISON_FLAGS = doctest.COMPARISON_FLAGS | PANDOC

# Helpers
from subprocess import Popen, PIPE
import json
def to_json(txt):
    p = Popen(["pandoc", "-tjson"], 
              stdout=PIPE, stdin=PIPE, stderr=PIPE)
    json_string = p.communicate(input=txt.encode("utf-8"))[0]
    json_doc = json.loads(json_string)
    return json_doc

def linebreak(text, length=80):
    text = text.replace(u"\n", "")
    chunks = [text[i:i+length] for i in range(0, len(text), length)]
    return "\n".join(chunks)

# Implement the pandoc output checker and monkey-patch doctest:
_doctest_OutputChecker = doctest.OutputChecker
class PandocOutputChecker(_doctest_OutputChecker):
    def check_output(self, want, got, optionflags):
        if optionflags & PANDOC:
            json_got = to_json(eval(got))
            doc_got = pandoc.read(json_got)
            got = linebreak(repr(doc_got))
            want = linebreak(want)
            # Should a failed roundtrip change want/got ?
#            if pandoc.write(doc_got) != json_got:
#                return False 
        super_check_output = _doctest_OutputChecker.check_output
        return super_check_output(self, want, got, optionflags)
    def output_difference(self, example, got, optionflags):
        if optionflags & PANDOC:
            json_got = to_json(eval(got))
            doc_got = pandoc.read(json_got)
            got = linebreak(repr(doc_got), length=80-4)
        super_output_difference = _doctest_OutputChecker.output_difference
        return super_output_difference(self, example, got, optionflags)

doctest.OutputChecker = PandocOutputChecker

