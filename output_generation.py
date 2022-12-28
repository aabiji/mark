from mark.parser import Node

tags = {
    "HORIZANTAL RULE": "<hr>",
    "PARAGRAPH": "<p>",
    "BOLD": "<strong>",
    "ITALIC": "<em>",
    "MONOSPACE": "<code>",
    "CODEBLOCK": "<code>",
    "UNORDERED LIST": "<ul>",
    "ORDERED LIST": "<ol>",
    "LIST ITEM": "<li>",
    "CODEBLOCK": "<code>",
    "BLOCKQUOTE": "<blockquote>",
    "HEADER": lambda level: f"<h{level}>",
    "LINK": lambda href: f"<a href='{href}'>",
    "IMAGE": lambda path, alt: f"<img src='{path}' alt='{alt}' title='{alt}'>"
}

class OutputGenerator:
    def __init__(self, ast: list, should_prettify_html: bool):
        self.ast = ast
        self.html_output = ""
        self.prettify = should_prettify_html

    def url_builder(self, url_str: str) -> str:
        if "https://" not in url_str or "http://" not in url_str:
            url_str = f"https://{url_str}"
        url_str = url_str.replace("\\", "/")
        return url_str

    def output(self, node: Node, indent: int) -> str:
        insert_indent = lambda: (" " * 4) * indent if self.prettify else ""
        closing_stack = []
        out = insert_indent()

        if node.type == "TEXT":
            text = node.element_data['value']
            out += text

        elif node.type == "HEADER":
            t = tags['HEADER'](node.element_data['level'])
            out += t
            closing_stack.append(t[0] + "/" + t[1:])

        elif node.type == "LINK":
            url = self.url_builder(node.element_data['href'])
            out += tags['LINK'](url)
            closing_stack.append("</a>")

        elif node.type == "IMAGE":
            out += tags['IMAGE'](node.element_data['path'], node.element_data['alt'])

        elif node.type == "REFERENCE":
            url = node.children[0].element_data['value']
            out += f"<a href='{url}'>"
            closing_stack.append("</a>")

        elif node.type == "CODEBLOCK":
            out += "<pre>\n" + insert_indent() + "<code>\n"
            code = node.children[0].element_data['value']
            code = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            code = code.replace("\t", "    ").split("\n")

            for i in code:
                out += insert_indent()
                out += i
                out += "\n"

            # Remove the extra \n
            out = ''.join(list(out)[:len(list(out)) - 1])

            closing_stack.append("</code>")
            closing_stack.append("</pre>")
        elif node.type == "HORIZANTAL RULE":
            out += "<hr/>"
        else:
            t = tags[node.type]
            out += t
            closing_stack.append(''.join(t[0] + "/" + t[1:]))
        
        out += "\n" if self.prettify else ""

        if node.type != "CODEBLOCK":
            for n in node.children:
                out += self.output(n, indent + 1)

        for i in closing_stack:
            out += insert_indent()
            out += i
            out += "\n" if self.prettify else ""

        return out

    # @base_indent: int -> Perhaps useful if embedding in existing html that's
    #                      already tabbed.
    def compile(self, base_indent: int):
        self.html_output = ""
        for node in self.ast:
            self.html_output += self.output(node, base_indent)
        return self.html_output
