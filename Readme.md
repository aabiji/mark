### mark
A markdown compiler for a custom markdown flavor of mine. 

With zero dependencies, it compiles the markdown source to the html equivelant. 
See `supported_syntax.md` (in raw) to view the supported syntax.

What's supported:
- Paragraphs
- Headers
- Links
- Images
- Codeblocks
- Blockquotes
- Unordered lists
- Ordered lists
- Horizantal rules
- Character escaping
- References
- Bold and emphasis

Usage:
```py
from mark import  markdown

markdown_str = "Yeah mark\! Pretty **cool** right?"
c = markdown.Compiler(markdown_str,
	debug_lexer=True, debug_parser=True, prettify=True
)
print(c.compile(base_indent=0))
```

mark is liscensed under the MIT liscense. Feel free to look through 
the source, use it in your own projects and submit contributions via pull requests.
