                
mappings = {
    "#":  "HASH",
    "-":  "HYPHEN",
    "+":  "PLUS",
    "*":  "ASTRIX",
    "`":  "BACKTICK",
    "!":  "EXCLAMATION",
    "[":  "OPEN BACKET",
    "]":  "CLOSED BRACKET",
    "(":  "OPEN PARENTHESES",
    ")":  "CLOSED PARENTHESES",
    "<":  "OPEN ANGLER BRACKET",
    ">":  "CLOSED ANGLER BRACKET",
    "\r": "CARRIAGE RETURN",
    "\n": "NEWLINE",
    "\t": "TAB"
}

class Token:
    def __init__(self, token_type: str, raw: str):
        self.type = token_type
        self.raw = raw

    def debug(self):
        print(f"{self.type}  ->  {self.raw}")

class Lexer:
    def __init__(self, source: str, should_debug: bool):
        source = source.replace(" " * 4, "\t")
        source = source.replace(" " * 2, "\r")
        source = source.replace(" & ", "&amp;")
        source = source.replace("&<", "&lt;")
        source = source.replace("&>", "&gt;")
        self.source = list(source)

        self.tokens = []
        self.index = -1
        self._tokenize()
        
        self.should_debug = should_debug
        self.debug()

    def debug(self) -> None:
        if self.should_debug:
            for i in self.tokens:
                i.debug()
            print("\n", "=" * 25, end="\n\n")

    def _read(self, amount=1) -> str:
        stop = self.index + amount
        stream = []
        while self.index < stop:
            self.index += 1
            
            if self.index >= len(self.source):
                break

            stream.append(self.source[self.index])
        return ''.join(stream)

    def _tokenize(self) -> None:
        if self.source[-1] != "\n":
            self.source.append("\n")

        text_buffer = ""
        while self.index < len(self.source):
            char = self._read()

            if char == "\\":
                char = self._read()

            # Is a keyword and is not escaped.
            if char in mappings.keys() and self.source[self.index - 1] != "\\":
                if len(text_buffer) > 0:
                    self.tokens.append(Token("TEXT", text_buffer))
                    text_buffer = ""

                self.tokens.append(Token(mappings[char], char))
            else:
                text_buffer += char
