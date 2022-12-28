from mark.lexer import Lexer
from mark.parser import Parser
from mark.output_generation import OutputGenerator
import sys

class Compiler:
    def __init__(self, markdown_source: str, debug_lexer: bool, 
                       debug_parser: bool, prettify: bool):
        self.source = markdown_source
        if len(self.source) == 0:
            sys.exit("Length of markdown source is zero.")

        self.lexer = Lexer(self.source, debug_lexer)
        self.parser = Parser(self.lexer.tokens, debug_parser)
        self.output_gen = OutputGenerator(self.parser.document, prettify)

    def compile(self, base_indent: int) -> str:
        return self.output_gen.compile(base_indent)

    def compile_to_file(self, filename: str, base_indent: int):
        with open(filename, "w") as file:
            file.write(self.output_gen.compile(base_indent))
