'''
TODO: !, (), newtype, 

Type Synonyms, List, Tuple, Map & Maybe
---------------------------------------

>>> parse("type Text = String")
['type', ['Text', 'String']]

>>> parse("type Text = (String)")
['type', ['Text', 'String']]

>>> parse("type Text = ((String))")
['type', ['Text', 'String']]

>>> parse("type Numbers = [Int]")
['type', ['Numbers', ['list', ['Int']]]]

>>> parse("type Sequences = [[Int]]")
['type', ['Sequences', ['list', [['list', ['Int']]]]]]

>>> parse("type Pair = (String, Int)")
['type', ['Pair', ['tuple', ['String', 'Int']]]]

>>> parse("type Count = Map String Int")
['type', ['Count', ['map', ['String', 'Int']]]]

>>> parse("type OptionalText = Maybe String")
['type', ['OptionalText', ['maybe', ['String']]]]

These patterns may be nested; a real-life Pandoc example would be:

>>> parse("type Attr = (String, [String], [(String, String)])") == \\
... ['type', 
...     ['Attr', 
...         ['tuple', 
...             [
...                 'String', 
...                 ['list', ['String']], 
...                 ['list', [['tuple', ['String', 'String']]]]
...             ]
...         ]
...     ]
... ]
True

Data Types
----------

New data types are defined with the `data` keyword.  
For example in Pandoc, documents are instances of the top-level `Pandoc` data type;
they are built with `Pandoc` constructor given metadata and a list of blocks.

>>> parse("data Pandoc = Pandoc Meta [Block]") == \\
... ['data', 
...     ['Pandoc', 
...         [
...             ['Pandoc', 
...                 ['list', 
...                     [
...                         'Meta', 
...                         ['list', ['Block']]
...                     ]
...                 ]
...             ]
...         ]
...     ]
... ]
True

Data types may have several constructors, separated by a `|`. 

>>> parse("data Color = RGB Int Int Int | Hex String") == \\
... ['data', 
...    ['Color', 
...        [
...            ['RGB', ['list', ['Int', 'Int', 'Int']]], 
...            ['Hex', ['list', ['String']]]
...        ]
...    ]
... ]
True

Such data types are often defined on several lines.

>>> parse(
... """
... data Color
...   = RGB Int Int Int
...   | Hex String
... """) == \\
... ['data', 
...    ['Color', 
...        [
...            ['RGB', ['list', ['Int', 'Int', 'Int']]], 
...            ['Hex', ['list', ['String']]]
...        ]
...    ]
... ]
True

"Enums" can be defined as datatypes with only constructors with no arguments; 
they are handled exactly like that by the parser.

>>> parse("data QuoteType = SingleQuote | DoubleQuote") == \\
... ['data', 
...     ['QuoteType', 
...         [
...             ['SingleQuote', ['list', []]], 
...             ['DoubleQuote', ['list', []]]
...         ]
...     ]
... ]
True

A real-life data type: in Pandoc the `Block` data type used to be defined as:

>>> parse("""
... data Block
...   = Plain [Inline]
...   | Para [Inline]
...   | CodeBlock Attr String
...   | RawBlock Format String
...   | BlockQuote [Block]
...   | OrderedList ListAttributes [[Block]]
...   | BulletList [[Block]]
...   | DefinitionList [([Inline], [[Block]])]
...   | Header Int [Inline]
...   | HorizontalRule
...   | Table [Inline] [Alignment] [Double] [TableCell] [[TableCell]]
...   | Null
... """) == \\
... ['data', 
...    ['Block', 
...        [
...            ['Plain', ['list', [['list', ['Inline']]]]], 
...            ['Para', ['list', [['list', ['Inline']]]]], 
...            ['CodeBlock', ['list', ['Attr', 'String']]], 
...            ['RawBlock', ['list', ['Format', 'String']]], 
...            ['BlockQuote', ['list', [['list', ['Block']]]]], 
...            ['OrderedList', ['list', ['ListAttributes', ['list', [['list', ['Block']]]]]]], 
...            ['BulletList', ['list', [['list', [['list', ['Block']]]]]]], 
...            ['DefinitionList', ['list', [['list', [['tuple', [['list', ['Inline']], ['list', [['list', ['Block']]]]]]]]]]], 
...            ['Header', ['list', ['Int', ['list', ['Inline']]]]], 
...            ['HorizontalRule', ['list', []]], 
...            ['Table', ['list', [['list', ['Inline']], ['list', ['Alignment']], ['list', ['Double']], ['list', ['TableCell']], ['list', [['list', ['TableCell']]]]]]], 
...            ['Null', ['list', []]]
...        ]
...     ]
... ]
True

Record data types are defined with braces

>>> parse("data Person = Person { name :: String, age :: Int}") == \\
... ['data', 
...     ['Person', 
...         [
...             ['Person', 
...                 ['map', 
...                     [
...                         ['name', 'String'], 
...                         ['age', 'Int']
...                     ]
...                 ]
...             ]
...         ]
...     ]
... ]
True

Pandoc only defines a few records

>>> parse("""
... data Citation
...   = Citation {citationId :: Text,
...               citationPrefix :: [Inline],
...               citationSuffix :: [Inline],
...               citationMode :: CitationMode,
...               citationNoteNum :: Int,
...               citationHash :: Int}
... """) == \\
... ['data', 
...     ['Citation', 
...         [
...             ['Citation', 
...                 ['map', 
...                     [
...                         ['citationId', 'Text'], 
...                         ['citationPrefix', ['list', ['Inline']]], 
...                         ['citationSuffix', ['list', ['Inline']]], 
...                         ['citationMode', 'CitationMode'], 
...                         ['citationNoteNum', 'Int'], 
...                         ['citationHash', 'Int']
...                     ]
...                 ]
...             ]
...         ]
...     ]
... ]
True

>>> parse("newtype Meta = Meta {unMeta :: Map Text MetaValue}") == \\
... ['newtype', 
...    ['Meta', 
...        [
...            ['Meta', 
...                ['map', 
...                    [
...                        ['unMeta', ['map', ['Text', 'MetaValue']]]
...                    ]
...                ]
...            ]
...        ]
...    ]
... ]
True



Pandoc-types introduced some strictness flags ("!") in version 1.23. 
Since this information is meaningless for Python, we do not keep this information;
this flags will not change the results of the parser:

>>> parse("data Pandoc = Pandoc Meta [Block]")
['data', ['Pandoc', [['Pandoc', ['list', ['Meta', ['list', ['Block']]]]]]]]

>>> parse ("data Pandoc = Pandoc !Meta ![Block]")
['data', ['Pandoc', [['Pandoc', ['list', ['Meta', ['list', ['Block']]]]]]]]



>>> parse("newtype Format = Format Text") == \\
... ['newtype', 
...     ['Format', 
...         [
...            ['Format', 
...               ['list', 
...                   ['Text']
...               ]
...            ]
...         ]
...     ]
... ]
True

>>> parse("data Caption = Caption (Maybe ShortCaption) [Block]") == \\
... ['data', 
...     ['Caption', 
...         [
...             ['Caption', 
...                 ['list', 
...                     [
...                         ['maybe', ['ShortCaption']], 
...                         ['list', ['Block']]
...                     ]
...                 ]
...             ]
...         ]
...    ]
... ]
True
'''

import ply.lex as lex
import ply.yacc as yacc

type Decl = str | list["Decl"]
type Token = lex.LexToken
type Production = yacc.YaccProduction

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
    "EXCLAMATION",
]
keywords = {
    "data": "DATA",
    "type": "TYPE",
    "newtype": "NEWTYPE",
    "Map": "MAP",
    "Maybe": "MAYBE",
}
tokens = tokens + list(keywords.values())


def t_CONID(t: Token) -> None:
    r"[A-Z][a-zA-Z_0-9`']*"
    t.type = keywords.get(t.value, "CONID")
    return t


def t_VARID(t: Token) -> None:
    r"[a-z][a-zA-Z_0-9`']*"
    t.type = keywords.get(t.value, "VARID")
    return t


t_COMMA = r"\,"
t_BAR = r"\|"
t_EQUAL = r"\="
t_DCOLON = r"\:\:"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACKET = r"\["
t_RBRACKET = r"\]"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_EXCLAMATION = r"\!"

t_ignore = " \t\n"


def t_error(t: Token) -> None:
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()


# Parser
# ------------------------------------------------------------------------------
def p_typedecl(p: Production) -> None:
    """typedecl : typetypedecl
    | datatypedecl
    | newtypedecl"""
    p[0] = p[1]


def p_typetypedecl(p: Production) -> None:
    "typetypedecl : TYPE CONID EQUAL type"
    p[0] = [p[1], [p[2], p[4]]]


def p_type_paren(p: Production) -> None:
    "type : LPAREN type RPAREN"
    p[0] = p[2]


def p_type_exclamation(p: Production) -> None:
    "type : EXCLAMATION type"
    p[0] = p[2]


def p_type_conid(p: Production) -> None:
    "type : CONID"
    p[0] = p[1]


def p_type_list(p: Production) -> None:
    "type : LBRACKET type RBRACKET"
    p[0] = ["list", [p[2]]]


def p_comma_separated_types_2(p: Production) -> None:
    "comma_separated_types : type COMMA type"
    p[0] = [p[1]] + [p[3]]


def p_comma_separated_types_more(p: Production) -> None:
    "comma_separated_types : type COMMA comma_separated_types"
    p[0] = [p[1]] + p[3]


def p_type_tuple(p: Production) -> None:
    "type : LPAREN comma_separated_types RPAREN"
    p[0] = ["tuple", p[2]]


def p_type_map(p: Production) -> None:
    "type : MAP type type"
    p[0] = ["map", [p[2], p[3]]]


def p_type_maybe(p: Production) -> None:
    "type : MAYBE type"
    p[0] = ["maybe", [p[2]]]


def p_assignment(p: Production) -> None:
    """
    assignment : VARID DCOLON type
    """
    p[0] = [p[1], p[3]]


def p_assignments(p: Production) -> None:
    """
    assignments : assignment
                | assignment COMMA assignments
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]


def p_record(p: Production) -> None:
    """type_record : LBRACE RBRACE
    | LBRACE assignments RBRACE
    """
    if len(p) == 3:
        p[0] = ["map", []]
    else:
        p[0] = ["map", p[2]]


def p_types(p: Production) -> None:
    """types : type
    | type types
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]


def p_constructor(p: Production) -> None:
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


def p_constructors(p: Production) -> None:
    """constructors : constructor
    | constructor BAR constructors
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]


def p_datatypedecl(p: Production) -> None:
    "datatypedecl : DATA CONID EQUAL constructors"
    p[0] = [p[1], [p[2], p[4]]]


def p_newtypedecl(p: Production) -> None:
    "newtypedecl : NEWTYPE CONID EQUAL constructor"
    p[0] = [p[1], [p[2], [p[4]]]]


# Error rule for syntax errors
def p_error(p: Production) -> None:
    print("Syntax error in input.")


parser = yacc.yacc(debug=0, write_tables=0)


# Type Declarations
# ------------------------------------------------------------------------------
def split(src: str) -> list[str]:
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

def parse(text: str) -> Decl:
    return parser.parse(text)

def parse_defs(src: str) -> list[Decl]:
    """
    >>> parse_defs("data Color = Red | Green | Blue") == [
    ...     ['data', 
    ...         ['Color', 
    ...             [
    ...                 ['Red', ['list', []]], 
    ...                 ['Green', ['list', []]], 
    ...                 ['Blue', ['list', []]]
    ...             ]
    ...         ]
    ...     ]
    ... ]
    True

    >>> parse_defs("data Alignment = AlignLeft | AlignRight | AlignCenter | AlignDefault") == [
    ...     ['data', 
    ...         ['Alignment', 
    ...             [
    ...                 ['AlignLeft', ['list', []]], 
    ...                 ['AlignRight', ['list', []]], 
    ...                 ['AlignCenter', ['list', []]], 
    ...                 ['AlignDefault', ['list', []]]
    ...             ]
    ...         ]
    ...     ]
    ... ]
    True
    >>> parse_defs("data Pandoc = Pandoc Meta [Block]") # doctest: +NORMALIZE_WHITESPACE
    [['data', 
        ['Pandoc', 
        [['Pandoc', 
            ['list', 
                ['Meta', 
                ['list', ['Block']]]]]]]]]
    >>> parse_defs("data Meta = Meta {docTitle :: [Inline], docAuthors :: [[Inline]], docDate :: [Inline]}") # doctest: +NORMALIZE_WHITESPACE
    [['data', 
        ['Meta', 
        [['Meta', ['map', 
            [['docTitle', ['list', ['Inline']]], 
             ['docAuthors', ['list', [['list', ['Inline']]]]], 
             ['docDate', ['list', ['Inline']]]]]]]]]]
    >>> parse_defs("type Attr = (String, [String], [(String, String)])") # doctest: +NORMALIZE_WHITESPACE
    [['type', 
        ['Attr', 
        ['tuple', 
            ['String', 
             ['list', ['String']], 
             ['list', [['tuple', ['String', 'String']]]]]]]]]
    >>>
    """
    return [parse(type_decl) for type_decl in split(src)]