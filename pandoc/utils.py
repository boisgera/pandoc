
# Python 2.7 Standard Library
from __future__ import absolute_import
from __future__ import print_function

# PLY
import ply.lex as lex
import ply.yacc as yacc


# Lexer
# ------------------------------------------------------------------------------
tokens = [
   "CONID",
   "VARID",
   "COMMA",
   "BAR",
   "EQUAL",
   "DCOLON", 
   "LPAREN",
   "RPAREN",
   "LBRACKET",
   "RBRACKET",
   "LBRACE",
   "RBRACE",
]
keywords = {
   "data"    : "DATA",
   "type"    : "TYPE",
   "newtype" : "NEWTYPE",
   "Map"     : "MAP",
}
tokens = tokens + list(keywords.values())

def t_CONID(t):
    r"[A-Z][a-zA-Z_0-9`']*"
    t.type = keywords.get(t.value, "CONID")
    return t
def t_VARID(t):
    r"[a-z][a-zA-Z_0-9`']*"
    t.type = keywords.get(t.value, "VARID")
    return t
t_COMMA      = r"\,"
t_BAR        = r"\|"
t_EQUAL      = r"\="
t_DCOLON     = r"\:\:" 
t_LPAREN     = r"\("
t_RPAREN     = r"\)"
t_LBRACKET   = r"\["
t_RBRACKET   = r"\]"
t_LBRACE     = r"\{"
t_RBRACE     = r"\}"

t_ignore     = " \t\n"

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()

# Parser
# ------------------------------------------------------------------------------
def p_typedecl(p):
    """typedecl : typetypedecl
                | datatypedecl
                | newtypedecl"""
    p[0] = p[1]

def p_typetypedecl(p):
    "typetypedecl : TYPE CONID EQUAL type"
    p[0] = [p[1], [p[2], p[4]]]

def p_type_paren(p):
    "type : LPAREN type RPAREN"
    p[0] = p[2]

def p_type_conid(p):
    "type : CONID"
    p[0] = p[1]

def p_type_list(p):
    "type : LBRACKET type RBRACKET"
    p[0] = ["list", [p[2]]]

def p_comma_separated_types_2(p):
    "comma_separated_types : type COMMA type"
    p[0] = [p[1]] + [p[3]]

def p_comma_separated_types_more(p):
    "comma_separated_types : type COMMA comma_separated_types"
    p[0] = [p[1]] + p[3]
                             
def p_type_tuple(p):
    "type : LPAREN comma_separated_types RPAREN" 
    p[0] = ["tuple", p[2]]        

def p_type_map(p):
    "type : MAP type type"
    p[0] = ["map", [p[2], p[3]]]
    
def p_assignment(p):
    """
    assignment : VARID DCOLON type
    """
    p[0] = [p[1], p[3]]

def p_assignments(p):
    """
    assignments : assignment
                | assignment COMMA assignments
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else: 
        p[0] = [p[1]] + p[3]

def p_record(p):
    """type_record : LBRACE RBRACE
                   | LBRACE assignments RBRACE
    """
    if len(p) == 3:
       p[0] = ["map", []]
    else:
       p[0] = ["map", p[2]]

def p_types(p):
    """types : type
             | type types
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]
    
def p_constructor(p):
    """constructor : CONID types
                   | CONID
                   | CONID type_record
    """
    if len(p) == 3 and p[2][0] == "map":
        p[0] = [p[1], p[2]]
    else:
        if len(p) == 2:
            p[0] = [p[1], ["list", []]]
        else:
            p[0] = [p[1], ["list", p[2]]]

def p_constructors(p):
    """constructors : constructor
                    | constructor BAR constructors
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else: 
        p[0] = [p[1]] + p[3]

def p_datatypedecl(p):
    "datatypedecl : DATA CONID EQUAL constructors"
    p[0] = [p[1], [p[2], p[4]]]

def p_newtypedecl(p):
    "newtypedecl : NEWTYPE CONID EQUAL constructor"
    p[0] = [p[1], [p[2], [p[4]]]]
 
# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input.")

parser = yacc.yacc(debug=0, write_tables=0)

# Type Declarations
# ------------------------------------------------------------------------------
def split(src):
    def keep(line):
        prefixes = [" ", "data ", "newtype ", "type "]
        return any(line.startswith(prefix) for prefix in prefixes)
    src = "\n".join(line for line in src.splitlines() if keep(line))
    type_decls = []
    for line in src.splitlines():
        if not line.startswith(" "):
            type_decls.append(line)
        else:
            type_decls[-1] = type_decls[-1] + "\n" + line
    return type_decls

def parse(src):
    return [parser.parse(type_decl) for type_decl in split(src)]

# find a better name: docstring is how we USE this stuff,
# but not what it IS and there are other uses (ex: error reporting)
# TODO: define signature_repr and docstring on top of that
#       (think of one-liner vs multiline issues, indentation, etc.)

# Nota: with the path option, the name of the function gets a little muddy.
# Q: do we need this for multi-line ? How could that help us? And it makes
#    things more complex.

# TODO: think the "nodes" stuff. Remember & study the use case:
#       The goal is to be able to pinpoint fragments in complex
#       types such as (String, [String], [(String, String)]).
#       So study how these types are checked and what API would
#       be appropriate (some info has to be conveyed by the exception
#       upwards).
#
#       One idea with the node stuff is to have a list of list ... etc.
#       such that we can locate the children, or the children children,
#       etc buy having says nodes[0][1] = (0,10) (start, past_the_end)
#       The root, well, it's (0, len(string)) ... Arf won't work:
#       we also need nodes[0] to return a value, not merely the children.

# TODO: at the very list, custom repr to see the attributes? 
#       Dunno how to represent this (yet)


# NOTA: alternate approach, probably much simpler:
#       build a list of strings or list (of the same kind)
#       whose flattening produces the signature.
#       The issue: with the separators & such, the indexing
#       would not be the one we think off.
#       But here the code is a pain in the ass.
#       Rework the stuff has a hierarchy of construct node with
#       children that know how to format themselves ?
#       Yeah why not but how do we handle the locations then?
#       This would be maybe a minor improvement of the initial
#       code (and even then i am not sure: that would be less 
#       compact)
#
#       Well, end the initial, BRUTAL and PAINFUL version first,
#       look for the patterns afterwards.
#
#       Maybe build the strings in a string-like with the option
#       to flag the node for insertion as a boundary effect.

# TODO: create "(Signature)Node" with before, after, separator fields and children;
#       some str() method, some getitem/iter/len and some locate method to
#       get the location of child i. Don't call the stuff signature_repr
#       but signature and let the use call str.
#       UPDATE: accept path as keys: lists of integers instead of integers.

class Node(object):
    def __init__(self, children, before, between, after):
        self.children = list(children)
        self.before = before
        self.between = between
        self.after = after
    def __str__(self):
        return self.before + \
               self.between.join(str(child) for child in self) + \
               self.after
    def __iter__(self):
        return iter(self.children)
    def __len__(self): # slightly misleading since we are also string-like ...
        return len(self.children)
    def __getitem__(self, index):
        return self.children[index]
    def locate(self, *indices):
        if len(indices) == 0:
            return (0, len(str(self)))
        elif len(indices) == 1:
            index = indices[0]
            start = len(self.before) + \
                    sum(len(str(child)) for child in self[0:index]) + \
                    index * len(self.between)
            end = start + len(str(self[index])) 
        else:
            inner = self
            for index in indices[:-1]:
                inner = inner[index]
            index = indices[-1]
            start, end = inner.locate(index)
            offset, _ = self.locate(*indices[:-1])
            start = offset + start
            end = offset + end
        return start, end

def signature(decl):
    if isinstance(decl, str):
        node = Node([decl], before="", between="", after="")
    else:
        assert isinstance(decl, list)
        if decl[0] == "data" or decl[0] == "newtype":
            type_name = decl[1][0]
            constructors = decl[1][1]
            children = [signature(constructor) for constructor in constructors]
            before = type_name + " = "
            between = "\n" + len(type_name) * " " + " | "
            after = "" # "\n" ?
            node = Node(children, before=before, between=between, after=after)
        elif decl[0] == "type":
            child = signature(decl[1][1])
            before = decl[1][0] + " = "
            node = Node([child], before=before, between="", after="")
        elif decl[0] == "list":
            child = signature(decl[1][0])
            node = Node(child, before="[", between="", after="]")
        elif decl[0] == "tuple":
            children = [signature(_decl) for _decl in decl[1]]
            node = Node(children, before="(", between=", ", after=")")
        elif decl[0] == "map":
            children = [signature(_decl) for _decl in decl[1]] # key, value decl
            node = Node(children, before="{", between=": ", after="}")
        else: # constructor, distinguish normal and record types
            type_name = decl[0]
            args_type = decl[1][0]
            args = decl[1][1]
            if args_type == "list":
                children = [signature(arg) for arg in args]
                node = Node(children, before=type_name + "(", between=", ", after=")")
            else: 
                assert args_type == "map"
                children = [signature(arg) for _, arg in args]
                node = Node(children, before=type_name + "(", between=", ", after=")")
    return node


