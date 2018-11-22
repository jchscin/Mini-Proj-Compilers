import sys
from antlr4 import *
from CymbolLexer import CymbolLexer
from CymbolParser import CymbolParser
from MyVisitor import MyVisitor
 
def main(argv):
    input = FileStream("teste.c")
    lexer = CymbolLexer(input)                           #lexer pega input e gera tokens
    stream = CommonTokenStream(lexer)                    #acho que pega tokens e transforma numa sequencia pra entrar no parser
    parser = CymbolParser(stream)                        #pega a sequencia de tokens e transforma através do parser
    tree = parser.file()                                 #cria árvore sintática
    visitor = MyVisitor()
    visitor.visit(tree)

if __name__ == '__main__':
    main(sys.argv)