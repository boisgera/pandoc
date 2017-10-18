data Pandoc = Pandoc Meta [Block]
data Meta
  = Meta {docTitle :: [Inline],
          docAuthors :: [[Inline]],
          docDate :: [Inline]}
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
type TableCell = [Block]
data Block
  = Plain [Inline]
  | Para [Inline]
  | CodeBlock Attr String
  | RawHtml String
  | BlockQuote [Block]
  | OrderedList ListAttributes [[Block]]
  | BulletList [[Block]]
  | DefinitionList [([Inline], [[Block]])]
  | Header Int [Inline]
  | HorizontalRule
  | Table [Inline] [Alignment] [Double] [TableCell] [[TableCell]]
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
  | Code String
  | Space
  | EmDash
  | EnDash
  | Apostrophe
  | Ellipses
  | LineBreak
  | Math MathType String
  | TeX String
  | HtmlInline String
  | Link [Inline] Target
  | Image [Inline] Target
  | Note [Block]
data Citation
  = Citation {citationId :: String,
              citationPrefix :: [Inline],
              citationSuffix :: [Inline],
              citationMode :: CitationMode,
              citationNoteNum :: Int,
              citationHash :: Int}
data CitationMode = AuthorInText | SuppressAuthor | NormalCitation
