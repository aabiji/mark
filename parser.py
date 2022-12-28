from mark.lexer import Token

class Node:
    def __init__(self, node_type: str):
        self.type = node_type
        self.element_data = {}
        self.children = []

def debug_node(node, nest_level):
    indent = "   " * nest_level if nest_level > 0 else ""
    data = f"| {node.element_data}" if node.element_data != {} else ""
    print(indent, node.type, data)
    for n in node.children:
        debug_node(n, nest_level + 1)

class Parser:
    def __init__(self, tokens: list, should_debug: bool):
        self.tokens = tokens
        self.index = -1
        self.document = self._parse()

        self.should_debug = should_debug
        self.debug()
    
    def debug(self):
        if self.should_debug:
            for node in self.document:
                debug_node(node, 0)
                print()

    def _read(self, amount=1) -> list:
        tokens = []
        stop = self.index + amount
        while self.index < stop:
            self.index += 1
        
            if not self.index < len(self.tokens):
                break

            tokens.append(self.tokens[self.index])
        return tokens

    def _peek(self, amount=1) -> list:
        tokens = []
        temp_index = self.index
        stop = self.index + amount
        while temp_index < stop:
            temp_index += 1

            if not temp_index < len(self.tokens):
                break

            tokens.append(self.tokens[temp_index])
        return tokens
    
    def _parse_text(self) -> Node:
        node = Node("TEXT")
        node.element_data = {"value": self.tokens[self.index].raw}
        return node

    def _parse_horizantal_rule(self) -> Node:
        node = Node("HORIZANTAL RULE")

        while self.tokens[self.index].type == "HYPHEN":
            self.index += 1

        return node

    def _parse_link(self) -> Node:
        self.index += 1 # Skip the open bracket
        node = Node("LINK")
        child_nodes = self._parse_inline("CLOSED PARENTHESES")

        node.children = child_nodes[: len(child_nodes) - 1]
        node.element_data['href'] = child_nodes[-1].element_data['value']

        return node

    # Images are not nestable -> ![ALT](path) both the ALT and path must be TEXT nodes
    def _parse_img(self) -> Node:
        node = Node("IMAGE")
        self.index += 2 # Skip the exclamation point and the open bracket
        child_nodes = self._parse_inline("CLOSED PARENTHESES")

        node.element_data['alt'] = child_nodes[0].element_data['value']
        node.element_data['path'] = child_nodes[1].element_data['value']

        return node

    # References must contain text and nothing else
    def _parse_reference(self) -> Node:
        node = Node("REFERENCE")

        self.index += 1 # Skipping the opening <
        node.children.append(self._parse_text())
        self.index += 1 # Skipping the closing >

        return node

    def _parse_monospace(self) -> Node:
        node = Node("MONOSPACE")
        self.index += 1 # Skipping the `
        node.children = self._parse_inline("BACKTICK")
        return node

    def _parse_italic(self) -> Node:
        end_literal = self.tokens[self.index].type
        node = Node("ITALIC")
        self.index += 1 # Skip the closing *
        node.children = self._parse_inline(end_literal)
        return node

    def _parse_bold(self) -> Node:
        end_literal = self.tokens[self.index].type
        node = Node("BOLD")
        self.index += 2 # Skip the current * and the next *

        # nested text styling
        t = self.tokens[self.index].type
        if t == "ASTRIX":
            node.children.append(self._parse_italic())

            t = self.tokens[self.index + 1].type
            if t != "ASTRIX":
                self.index += 1 # Skip the current token
                for i in self._parse_inline(end_literal):
                    node.children.append(i)
                self.index += 1 # Skip the ending *
                return node

            self.index += 2 # Skip the two trailing *
            return node

        node.children = self._parse_inline(end_literal)
        self.index += 1 # Skip the trailing *

        return node

    def _parse_codeblock(self) -> Node:
        node = Node("CODEBLOCK")
    
        # Potentially getting the codeblock language, ex: ```py\n THE CODE \n```
        self.index += 3
        lang = self._parse_inline("NEWLINE")
        lang = None if len(lang) == 0 else lang[0].element_data['value']
        node.element_data = {"type": lang}

        code = [] # Tokens have no special meaning inside code blocks
        while self.tokens[self.index].type != "BACKTICK":
            code.append(self._read()[0].raw)
        code = ''.join(code[:len(code) - 2]) # Removing the trailing backtick and newline

        code_node = Node("TEXT")
        code_node.element_data = {"value": code}
        node.children.append(code_node)

        self.index += 2 # Skipping the 2 ``
        return node

    def _parse_header(self) -> Node:
        node = Node("HEADER")
        header_type = 0
        t = self.tokens[self.index]
        
        # Get header level, h1, h2, etc...
        while t.type == "HASH":
            header_type += 1
            t = self._read()[0]
        header_type = 1 if header_type == 0 else header_type
        
        node.element_data = {"level": header_type}
        node.children = self._parse_inline("NEWLINE")

        return node

    def _parse_paragraph(self):
        node = Node("PARAGRAPH")

        stops = ["HASH", "PLUS", "BACKTICK", "TAB", "HYPHEN",
                 "CLOSED ANGLER BRACKET"]
        while True:
            for i in self._parse_inline("NEWLINE"):
                node.children.append(i)

            if self.index + 1 >= len(self.tokens):
                next_token = Token("NEWLINE", "\n")
            else:
                next_token = self.tokens[self.index + 1]

            # A new line break
            if self.tokens[self.index].type == next_token.type:
                break
            elif next_token.type in stops:
                break
            
            if self.tokens[self.index - 1].type == "CARRIAGE RETURN":
                break

            self.index += 1

        return node

    def _parse_list_item(self, indent: int) -> Node:
        if self.tokens[self.index].type != "\t" :
            t = self.tokens[self.index]
        else:
            t = self.tokens[self.index + 1]
        list_item_type = "ORDERED LIST" if t.raw == '+' else "UNORDERED LIST"

        list_item = Node("LIST ITEM")
        list_item.element_data = {"indent": indent}
        list_item.element_data['type'] = list_item_type

        t = self.tokens[self.index]
        if t.raw == ' ' or t.raw == '-':
            self.index += 1
            t = self.tokens[self.index]

        if t.type == "HASH":
            list_item.children.append(self._parse_header())

        elif self._peek()[0].type == "CLOSED ANGLER BRACKET":
            self.index += 1
            list_item.children.append(self._parse_blockquote())

        elif t.type != "NEWLINE":
            list_item.children.append(self._parse_paragraph())

        return list_item

    def _parse_list_items(self) -> list:
        indent = 0
        list_items = []
        while len(self._peek()) > 0 and self._peek()[0].type != "NEWLINE":
            t = self.tokens[self.index]
            if t.type == "NEWLINE" or t.type == "HYPHEN":
                self.index += 1

            t = self.tokens[self.index]
            if t.type == "TAB":
                i = 0
                while self.tokens[self.index].type == "TAB":
                    self.index += 1
                    i += 1
                indent = i
            
            # 'Reset'
            ending_token_types = ["HYPHEN", "PLUS"]
            if t.type in ending_token_types and self.tokens[self.index - 1].type == "NEWLINE":
                indent = 0
                self.index += 1

            list_items.append(self._parse_list_item(indent))

        return list_items

    # Parsing all the list items first, then assembling them into a tree with a bottom up approach	
    def _assemble_list(self, list_type: str) -> Node:
        node = Node(list_type)

        # List (tree building)
        list_items = self._parse_list_items()
        i = len(list_items) - 1
        has_seen = []
        while i > 0:
            indent = list_items[i].element_data['indent']
            same_indent = []
            start = i
            while list_items[i].element_data['indent'] == indent:
                same_indent.append(list_items[i])
                i -= 1
                if i == 0: break
            i = 0 if i < 0 else i
            same_indent = same_indent[::-1] # Since it was read back to front

            if indent > list_items[i].element_data['indent']:
                head = same_indent[0].element_data['type']
                list_type = "UNORDERED LIST" if head == "UNORDERED LIST" else "ORDERED LIST"

                child = Node(list_type)
                for c in same_indent:
                    c.element_data = {}
                    child.children.append(c)

                list_items[i].children.append(child)

                list_items = [l for x, l in enumerate(list_items) if x not in range(i + 1, start + 1)]
                i = len(list_items) - 1

        for c in list_items:
            c.element_data = {}
            node.children.append(c)
        return node

    def _parse_blockquote(self) -> Node:
        node = Node("BLOCKQUOTE")

        while len(self._peek()) > 0 and self._peek()[0].type != "NEWLINE":
            # Skipping unnessary whitespcae
            if self.tokens[self.index + 1].raw == " ":
                self.index += 1

            block = self._parse_block()
            node.children.append(block)

            # Continuing blockquotes
            if self.tokens[self.index].type == "NEWLINE":
                if len(self._peek()) > 0 and self._peek()[0].raw == ">":
                    self.index += 1
                if len(self._peek()) > 0 and self._peek()[0].type == "TAB":
                    temp_index = self.index
                    while self._peek()[0].type == "TAB":
                        self.index += 1
                        
                    if self._peek()[0].type == "PLUS" or self._peek()[0].type == "HYPHEN":
                        self.index = temp_index
                        break

        return node

    # Inline nodes are nodes that can't self nest: BOLD, ITALIC, LINK, IMAGE, TEXT
    def _parse_inline(self, end_delim: str) -> list:
        inline_nodes = []
        token = self.tokens[self.index].type

        while token != end_delim:
            if token == "OPEN BACKET":
                inline_nodes.append(self._parse_link())

            elif token == "ASTRIX":
                if self._peek()[0].type == "ASTRIX":
                    inline_nodes.append(self._parse_bold())
                else:
                    inline_nodes.append(self._parse_italic())

            elif token == "EXCLAMATION" and self._peek()[0].type == "OPEN BACKET":
                inline_nodes.append(self._parse_img())

            elif token == "BACKTICK" and self._peek()[0].type == "TEXT":
                inline_nodes.append(self._parse_monospace())
            
            elif token == "OPEN ANGLER BRACKET":
                inline_nodes.append(self._parse_reference())

            elif token == "TEXT":
                inline_nodes.append(self._parse_text())

            token = self._read()[0].type

        return inline_nodes
    
    # Blocks are the 'parent' elements and can contain the inline elements and themeselves
    # PARAGRAPHS, HEADERS, CODEBLOCKS, LISTS (ORDERED and UNORDERED), HORIZANTAL RULES, BLOCKQUOTES
    def _parse_block(self) -> Node:
        current_token = self._read()
        previous_token = self.tokens[self.index - 1]

        if len(current_token) == 0:
            return "EOF"
        else:
            current_token = current_token[0]

        if current_token.type == "HASH":
            return self._parse_header()

        elif current_token.type == "BACKTICK" and self._peek()[0].type == "BACKTICK":
            return self._parse_codeblock()

        elif current_token.type == "HYPHEN" and self._peek()[0].type == "HYPHEN":
            return self._parse_horizantal_rule()

        elif current_token.type == "HYPHEN":
            return self._assemble_list("UNORDERED LIST")

        elif current_token.type == "PLUS":
            return self._assemble_list("ORDERED LIST")

        elif current_token.type == "CLOSED ANGLER BRACKET" and \
            (previous_token.type == "NEWLINE" or previous_token.raw == ' '):
            return self._parse_blockquote()

        else:
            if current_token.type != "NEWLINE":
                return self._parse_paragraph()
            else:
                return "NEWLINE"

    def _parse(self):
        document = []
        while self.index < len(self.tokens):
            block = self._parse_block()

            if block == "NEWLINE":
                continue
            elif block == "EOF":
                break

            document.append(block)
        return document
