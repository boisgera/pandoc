data Pandoc = Pandoc Meta [Block]
newtype Meta = Meta {unMeta :: Map String MetaValue}
data MetaValue
  = MetaMap (Map String MetaValue)
  | MetaList [MetaValue]
  | MetaBool Bool
  | MetaString String
  | MetaInlines [Inline]
  | MetaBlocks [Block]
nullMeta :: Meta
isNullMeta :: Meta -> Bool
lookupMeta :: String -> Meta -> Maybe MetaValue
docTitle :: Meta -> [Inline]
docAuthors :: Meta -> [[Inline]]
docDate :: Meta -> [Inline]
data Alignment
  = AlignLeft | AlignRight | AlignCenter | AlignDefault
type ListAttributes = (Int, ListNumberStyle, ListNumberDelim)
data ListNumberStyle
  = DefaultStyle
  | Example
  | Decimal
  | LowerRoman
  | UpperRoman
  | LowerAlpha
  | UpperAlpha
data ListNumberDelim = DefaultDelim | Period | OneParen | TwoParens
type Attr = (String, [String], [(String, String)])
nullAttr :: Attr
type TableCell = [Block]
newtype Format = Format String
data Block
  = Plain [Inline]
  | Para [Inline]
  | LineBlock [[Inline]]
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
data QuoteType = SingleQuote | DoubleQuote
type Target = (String, String)
data MathType = DisplayMath | InlineMath
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
  | SoftBreak
  | LineBreak
  | Math MathType String
  | RawInline Format String
  | Link Attr [Inline] Target
  | Image Attr [Inline] Target
  | Note [Block]
  | Span Attr [Inline]
data Citation
  = Citation {citationId :: String,
              citationPrefix :: [Inline],
              citationSuffix :: [Inline],
              citationMode :: CitationMode,
              citationNoteNum :: Int,
              citationHash :: Int}
data CitationMode = AuthorInText | SuppressAuthor | NormalCitation
pandocTypesVersion :: Version
