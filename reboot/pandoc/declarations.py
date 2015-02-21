type_declarations = [

# data Alignment
#   = AlignLeft | AlignRight | AlignCenter | AlignDefault
[ 'data',
  [ 'Alignment',
    [ ['AlignLeft', []],
      ['AlignRight', []],
      ['AlignCenter', []],
      ['AlignDefault', []]]]]
,

# type Attr = (String, [String], [(String, String)])
[ 'type',
  [ 'Attr',
    [ 'tuple',
      [ 'String',
        ['list', ['String']],
        ['list', [['tuple', ['String', 'String']]]]]]]]
,

# data Block
#   = Plain [Inline]
#   | Para [Inline]
#   | CodeBlock Attr String
#   | RawBlock Format String
#   | BlockQuote [Block]
#   | OrderedList ListAttributes [[Block]]
#   | BulletList [[Block]]
#   | DefinitionList [([Inline], [[Block]])]
#   | Header Int Attr [Inline]
#   | HorizontalRule
#   | Table [Inline] [Alignment] [Double] [TableCell] [[TableCell]]
#   | Div Attr [Block]
#   | Null
[ 'data',
  [ 'Block',
    [ ['Plain', [['list', ['Inline']]]],
      ['Para', [['list', ['Inline']]]],
      ['CodeBlock', ['Attr', 'String']],
      ['RawBlock', ['Format', 'String']],
      ['BlockQuote', [['list', ['Block']]]],
      ['OrderedList', ['ListAttributes', ['list', [['list', ['Block']]]]]],
      ['BulletList', [['list', [['list', ['Block']]]]]],
      [ 'DefinitionList',
        [ [ 'list',
            [ [ 'tuple',
                [['list', ['Inline']], ['list', [['list', ['Block']]]]]]]]]],
      ['Header', ['Int', 'Attr', ['list', ['Inline']]]],
      ['HorizontalRule', []],
      [ 'Table',
        [ ['list', ['Inline']],
          ['list', ['Alignment']],
          ['list', ['Double']],
          ['list', ['TableCell']],
          ['list', [['list', ['TableCell']]]]]],
      ['Div', ['Attr', ['list', ['Block']]]],
      ['Null', []]]]]
,

# data Citation
#   = Citation {citationId :: String,
#               citationPrefix :: [Inline],
#               citationSuffix :: [Inline],
#               citationMode :: CitationMode,
#               citationNoteNum :: Int,
#               citationHash :: Int}
[ 'data',
  [ 'Citation',
    [ [ 'Citation',
        [ 'struct',
          [ ['citationId', 'String'],
            ['citationPrefix', ['list', ['Inline']]],
            ['citationSuffix', ['list', ['Inline']]],
            ['citationMode', 'CitationMode'],
            ['citationNoteNum', 'Int'],
            ['citationHash', 'Int']]]]]]]
,

# data CitationMode = AuthorInText | SuppressAuthor | NormalCitation
[ 'data',
  [ 'CitationMode',
    [['AuthorInText', []], ['SuppressAuthor', []], ['NormalCitation', []]]]]
,

# newtype Format = Format String
['newtype', ['Format', [['Format', ['String']]]]]
,

# data Inline
#   = Str String
#   | Emph [Inline]
#   | Strong [Inline]
#   | Strikeout [Inline]
#   | Superscript [Inline]
#   | Subscript [Inline]
#   | SmallCaps [Inline]
#   | Quoted QuoteType [Inline]
#   | Cite [Citation] [Inline]
#   | Code Attr String
#   | Space
#   | LineBreak
#   | Math MathType String
#   | RawInline Format String
#   | Link [Inline] Target
#   | Image [Inline] Target
#   | Note [Block]
#   | Span Attr [Inline]
[ 'data',
  [ 'Inline',
    [ ['Str', ['String']],
      ['Emph', [['list', ['Inline']]]],
      ['Strong', [['list', ['Inline']]]],
      ['Strikeout', [['list', ['Inline']]]],
      ['Superscript', [['list', ['Inline']]]],
      ['Subscript', [['list', ['Inline']]]],
      ['SmallCaps', [['list', ['Inline']]]],
      ['Quoted', ['QuoteType', ['list', ['Inline']]]],
      ['Cite', [['list', ['Citation']], ['list', ['Inline']]]],
      ['Code', ['Attr', 'String']],
      ['Space', []],
      ['LineBreak', []],
      ['Math', ['MathType', 'String']],
      ['RawInline', ['Format', 'String']],
      ['Link', [['list', ['Inline']], 'Target']],
      ['Image', [['list', ['Inline']], 'Target']],
      ['Note', [['list', ['Block']]]],
      ['Span', ['Attr', ['list', ['Inline']]]]]]]
,

# type ListAttributes = (Int, ListNumberStyle, ListNumberDelim)
[ 'type',
  ['ListAttributes', ['tuple', ['Int', 'ListNumberStyle', 'ListNumberDelim']]]]
,

# data ListNumberDelim = DefaultDelim | Period | OneParen | TwoParens
[ 'data',
  [ 'ListNumberDelim',
    [ ['DefaultDelim', []],
      ['Period', []],
      ['OneParen', []],
      ['TwoParens', []]]]]
,

# data ListNumberStyle
#   = DefaultStyle
#   | Example
#   | Decimal
#   | LowerRoman
#   | UpperRoman
#   | LowerAlpha
#   | UpperAlpha
[ 'data',
  [ 'ListNumberStyle',
    [ ['DefaultStyle', []],
      ['Example', []],
      ['Decimal', []],
      ['LowerRoman', []],
      ['UpperRoman', []],
      ['LowerAlpha', []],
      ['UpperAlpha', []]]]]
,

# data MathType = DisplayMath | InlineMath
['data', ['MathType', [['DisplayMath', []], ['InlineMath', []]]]]
,

# newtype Meta
#   = Meta {unMeta :: Map
#                       String MetaValue}
[ 'newtype',
  [ 'Meta',
    [['Meta', ['struct', [['unMeta', ['map', ['String', 'MetaValue']]]]]]]]]
,

# data MetaValue
#   = MetaMap (Map String MetaValue)
#   | MetaList [MetaValue]
#   | MetaBool Bool
#   | MetaString String
#   | MetaInlines [Inline]
#   | MetaBlocks [Block]
[ 'data',
  [ 'MetaValue',
    [ ['MetaMap', [['map', ['String', 'MetaValue']]]],
      ['MetaList', [['list', ['MetaValue']]]],
      ['MetaBool', ['Bool']],
      ['MetaString', ['String']],
      ['MetaInlines', [['list', ['Inline']]]],
      ['MetaBlocks', [['list', ['Block']]]]]]]
,

# data Pandoc = Pandoc Meta [Block]
['data', ['Pandoc', [['Pandoc', ['Meta', ['list', ['Block']]]]]]]
,

# data QuoteType = SingleQuote | DoubleQuote
['data', ['QuoteType', [['SingleQuote', []], ['DoubleQuote', []]]]]
,

# type TableCell = [Block]
['type', ['TableCell', ['list', ['Block']]]]
,

# type Target = (String, String)
['type', ['Target', ['tuple', ['String', 'String']]]]
,

]
