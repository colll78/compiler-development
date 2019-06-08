import sys
import collections
from Parser import Tokenizer
from Parser import SyntaxAnalyzer
from Parser.Tokenizer import lex
from Parser.SyntaxAnalyzer import Parser

#testFile = sys.argv[1]
testFile = input()
rStr = ''''''

with open(testFile) as f:
    for line in f:
        rStr = rStr + line

parseObj = Parser()
parseObj.parse(rStr)