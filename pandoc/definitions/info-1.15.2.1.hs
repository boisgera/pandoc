data Alignment
  = AlignLeft | AlignRight | AlignCenter | AlignDefault
type Attr = (String, [String], [(String, String)])
data Block
  = Plain [Inline]
  | Para [Inline]
  | CodeBlock Attr String
  | RawBlock Format String
  | BlockQuote [Block]
  | OrderedList ListAttributes [[Block]]
  | BulletList [[Block]]
  | DefinitionList [([Inline], [[Block]])]
  | Header Int Attr [Inline]
  | HorizontalRule
  | Table [Inline] [Alignment] [Double] [TableCell] [[TableCell]]
  | Div Attr [Block]
  | Null
data Citation
  = Citation {citationId :: String,
              citationPrefix :: [Inline],
              citationSuffix :: [Inline],
              citationMode :: CitationMode,
              citationNoteNum :: Int,
              citationHash :: Int}
data CitationMode = AuthorInText | SuppressAuthor | NormalCitation
newtype Format = Format String
data Inline
  = Str String
  | Emph [Inline]
  | Strong [Inline]
  | Strikeout [Inline]
  | Superscript [Inline]
  | Subscript [Inline]
  | SmallCaps [Inline]
  | Quoted QuoteType [Inline]
  | Cite [Citation] [Inline]
  | Code Attr String
  | Space
  | LineBreak
  | Math MathType String
  | RawInline Format String
  | Link [Inline] Target
  | Image [Inline] Target
  | Note [Block]
  | Span Attr [Inline]
type ListAttributes = (Int, ListNumberStyle, ListNumberDelim)
data ListNumberDelim = DefaultDelim | Period | OneParen | TwoParens
data ListNumberStyle
  = DefaultStyle
  | Example
  | Decimal
  | LowerRoman
  | UpperRoman
  | LowerAlpha
  | UpperAlpha
data MathType = DisplayMath | InlineMath
newtype Meta = Meta {unMeta :: Map String MetaValue}
data MetaValue
  = MetaMap (Map String MetaValue)
  | MetaList [MetaValue]
  | MetaBool Bool
  | MetaString String
  | MetaInlines [Inline]
  | MetaBlocks [Block]
data Pandoc = Pandoc Meta [Block]
data QuoteType = SingleQuote | DoubleQuote
type TableCell = [Block]
type Target = (String, String)
docAuthors :: Meta -> [[Inline]]
docDate :: Meta -> [Inline]
docTitle :: Meta -> [Inline]
isNullMeta :: Meta -> Bool
lookupMeta :: String -> Meta -> Maybe MetaValue
nullAttr :: Attr
nullMeta :: Meta
