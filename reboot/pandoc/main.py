#!/usr/bin/env python

# Python 2.7 Standard Library
import pprint ; pprint = pprint.PrettyPrinter(indent=2).pprint
import re
import sys

# PLY
import ply.lex as lex
import ply.yacc as yacc


# Command-Line Interface
# ------------------------------------------------------------------------------
if len(sys.argv) >= 2:
    filename = sys.argv[1]
else:
    filename = "types.hs"

# Pre-Processing
# ------------------------------------------------------------------------------
src = open(filename).read()
src = re.sub(r"[a-zA-Z0-9\-\.\:]+\.Map", "Map", src)

def keep(line):
    prefixes = [" ", "data ", "newtype ", "type "]
    return any(line.startswith(prefix) for prefix in prefixes)
src = "\n".join(line for line in src.splitlines() if keep(line))

typedecls = []
for line in src.splitlines():
    if not line.startswith(" "):
        typedecls.append(line)
    else:
        typedecls[-1] = typedecls[-1] + "\n" + line

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
    print "Illegal character '%s'" % t.value[0]
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

def p_type_record(p):
    """type_record : LBRACE RBRACE
                   | LBRACE assignments RBRACE
    """
    if len(p) == 3:
       p[0] = ["struct", []]
    else:
       p[0] = ["struct", p[2]]

def p_types(p):
    """types : type
             | type types
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_types_type_record(p):
    "types : type_record"
    p[0] = p[1]


def p_constructor(p):
    """constructor : CONID types
                   | CONID
    """
    if len(p) == 2:
        p[0] = [p[1], []]
    else:
        p[0] = p[1:]

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
    # The constructor -- despite being unique --  is wrapped in a list 
    # so that the `newtype` type declaration yields a structure similar
    # to the 'data' type declaration.
    p[0] = [p[1], [p[2], [p[4]]]]
 
# Error rule for syntax errors
def p_error(p):
    print "Syntax error in input."

parser = yacc.yacc()

# Main
# ------------------------------------------------------------------------------
print "type_declarations = ["
print
for typedecl in typedecls:
    for line in typedecl.splitlines():
        print "#", line
    lexer.input(typedecl)
    pprint(parser.parse(typedecl))
    print ","
    print
print "]"


