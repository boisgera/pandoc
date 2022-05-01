
🧪 Labs
================================================================================

``` python
import pandoc
from pandoc.types import *
from pandoc.labs import f
```


``` python
HELLOWORLD_DOC = pandoc.read("Hello world!")
```

``` python
from urllib.request import urlopen
PATH = "raw.githubusercontent.com/commonmark/commonmark-spec"
HASH = "499ebbad90163881f51498c4c620652d0c66fb2e" # pinned version
URL = f"https://{PATH}/{HASH}/spec.txt"
COMMONMARK_SPEC = urlopen(URL).read().decode("utf-8")
COMMONMARK_DOC = pandoc.read(COMMONMARK_SPEC)
```

<!--

``` pycon
#>>> f(HELLOWORLD_DOC, Meta)
[Meta({})]
#>>> f(HELLOWORLD_DOC, Para)
[Para([Str('Hello'), Space(), Str('world!')])]
#>>> f(HELLOWORLD_DOC, Str)
[Str('Hello'), Str('world!')]
#>>> f(HELLOWORLD_DOC, LineBreak)
[]
```

Types or multiple types can be specified (this is similar to what `isinstance`
does):

``` pycon
#>>> f(HELLOWORLD_DOC, (Str, Space))
[Str('Hello'), Space(), Str('world!')]
```

Complex conditions based on types and values can be factored out in 
a predicate function, such as `is_http_or_https_link`:

``` python
def get_url(link):
    target = link[2] # link: Link(Attr, [Inline], Target)
    url = target[0] # target: (Text, Text)
    return url

def is_http_or_https_link(elt):
    if isinstance(elt, Link):
        url = get_url(link=elt)
        return url.startswith("http:") or url.startswith("https:")
    else:
        return False
```

``` pycon
#>>> for link in f(COMMONMARK_DOC, is_http_or_https_link):
...     print(get_url(link))
http://creativecommons.org/licenses/by-sa/4.0/
http://daringfireball.net/projects/markdown/syntax
http://daringfireball.net/projects/markdown/
http://www.methods.co.nz/asciidoc/
http://daringfireball.net/projects/markdown/syntax
http://article.gmane.org/gmane.text.markdown.general/1997
http://article.gmane.org/gmane.text.markdown.general/2146
http://article.gmane.org/gmane.text.markdown.general/2554
https://html.spec.whatwg.org/entities.json
http://www.aaronsw.com/2002/atx/atx.py
http://docutils.sourceforge.net/rst.html
http://daringfireball.net/projects/markdown/syntax#em
http://www.vfmd.org/vfmd-spec/specification/#procedure-for-identifying-emphasis-tags
https://html.spec.whatwg.org/multipage/forms.html#e-mail-state-(type=email)
http://www.w3.org/TR/html5/syntax.html#comments
```


Calling the finder as a method works too:

``` pycon
#>>> HELLOWORLD_DOC.f(Meta)
[Meta({})]
#>>> HELLOWORLD_DOC.f(Para)
[Para([Str('Hello'), Space(), Str('world!')])]
#>>> HELLOWORLD_DOC.f(Str)
[Str('Hello'), Str('world!')]
#>>> HELLOWORLD_DOC.f(LineBreak)
[]
```

``` pycon
#>>> COMMONMARK_DOC.f(Meta)
[Meta({'author': MetaInlines([Str('John'), Space(), Str('MacFarlane')]), 'date': MetaInlines([Str('2021-06-19')]), 'license': MetaInlines([Link(('', [], []), [Str('CC-BY-SA'), Space(), Str('4.0')], ('http://creativecommons.org/licenses/by-sa/4.0/', ''))]), 'title': MetaInlines([Str('CommonMark'), Space(), Str('Spec')]), 'version': MetaInlines([Str('0.30')])})]
#>>> COMMONMARK_DOC.f(Meta)[0]
{'author': MetaInlines([Str('John'), Space(), Str('MacFarlane')]), 'date': MetaInlines([Str('2021-06-19')]), 'license': MetaInlines([Link(('', [], []), [Str('CC-BY-SA'), Space(), Str('4.0')], ('http://creativecommons.org/licenses/by-sa/4.0/', ''))]), 'title': MetaInlines([Str('CommonMark'), Space(), Str('Spec')]), 'version': MetaInlines([Str('0.30')])})
```

-->