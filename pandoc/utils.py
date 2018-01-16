
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

def docstring(decl):
    if isinstance(decl, str):
        return decl
    else:
        assert isinstance(decl, list)
        if decl[0] == "data" or decl[0] == "newtype":
            type_name = decl[1][0]
            constructors = decl[1][1]
            _docstring = ""
            for i, constructor in enumerate(constructors):
                if i == 0:
                    prefix = type_name + " = "
                else:
                    prefix = " " * len(type_name) + " | "
                if i > 0:
                    _docstring += "\n"
                _docstring += prefix + docstring(constructor)
            return _docstring 
        elif decl[0] == "type":
            return "{0} = {1}".format(decl[1][0], docstring(decl[1][1]))
        elif decl[0] == "list":
<<<<<<< HEAD
            return "[{0}]".format(docstring(decl[1][0]))
=======
            child = signature(decl[1][0])
            node = Node([child], before="[", between="", after="]")
>>>>>>> 819336e... add 2.0 roadmap sketch
        elif decl[0] == "tuple":
            _types = [docstring(_type) for _type in decl[1]]
            _types = ", ".join(_types)
            return "({0})".format(_types)
        elif decl[0] == "map":
<<<<<<< HEAD
            #print(">>>", decl)
            key_type, value_type = decl[1]
            return "{{{0}: {1}}}".format(docstring(key_type), docstring(value_type))
        else: # constructor, distinguish normal and record types
=======
            children = [signature(_decl) for _decl in decl[1]] # key, value decl
            node = Node(children, before="{", between=": ", after="}")
        else: # constructor
>>>>>>> 819336e... add 2.0 roadmap sketch
            type_name = decl[0]
            args_type = decl[1][0]
            args = decl[1][1]
            if args_type == "list":
<<<<<<< HEAD
                return "{0}({1})".format(type_name, ", ".join(docstring(t) for t in args))
            else: 
                assert args_type == "map"
                args = [item for _, item in args]
                return "{0}({1})".format(type_name, ", ".join(docstring(t) for t in args))    
=======
                children = [signature(arg) for arg in args]
            else: 
                assert args_type == "map"
                children = [signature(arg) for _, arg in args]
            node = Node(children, before=type_name + "(", between=", ", after=")")
    return node

>>>>>>> 819336e... add 2.0 roadmap sketch

