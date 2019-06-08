from Parser.Tokenizer import lex
from Parser import Tokenizer
import sys
import warnings
import collections

class Parser:
    '''
      Recursive descent syntax. Each method
      accounts for a single grammar rule.  The ._accept() method is used to compare(check)
      actual versus expected and if the pass checks then accept the lookahead token.
      Use the ._expect() method to exactly match and discard the next token on on the input
      using the ._accept() method (or raise a SyntaxError if it doesn't match).
    '''

    def parse(self, programToParse):
        self.tokens = lex(programToParse)
        self.tok = None  # Last symbol consumed
        self.nexttok = None  # Next symbol lexed
        self._advance()  # Prepare first lookahead token
        return self.program()

    # Move(advance) one token ahead
    def _advance(self):
        self.tok, self.nexttok = self.nexttok, next(self.tokens, None)
        if self.nexttok != None:
            while(self.nexttok.type == 'ILLEGAL'):
                self.tok, self.nexttok = self.nexttok, next(self.tokens, None)
        if self.nexttok == None :
            self.nexttok = Tokenizer.Token('PARSINGCOMPLETE', 'PARSECOMPLETEDATA', 'EOF')
            self.tok = Tokenizer.Token('PARSINGCOMPLETE', 'PARSECOMPLETEDATA', 'EOF')

    def _accept(self, toktype):
        #check if next token matches toktype, if so then advance to next token
        if self.nexttok and self.nexttok.type == toktype:
            self._advance()
            return True
        else:
            return False

    def _expect(self, expTok):
        #will call accept method to test, and either advance to next token or raise SyntaxError
        if not self._accept(expTok):
            if self.nexttok != None:
                warnings.warn('Expected ' + expTok + ' but saw ' + self.nexttok.value  + ' at line ' + str(self.nexttok.lineNumber))


    #Grammar portion

    def program(self):
        #<program> ::= program <progname> <compound stmt>
        self._expect('PROGRAM')
        if(self._accept('PROGNAME')):
            program = self.compoundStmt()
            if self.nexttok.type != 'PARSINGCOMPLETE':
                warnings.warn('Code beyond the expected end of the outermost compound statement')
                exit()
        else:
            warnings.warn('Expected a PROGNAME, saw ' + self.nexttok.value + ' at line ' + str(self.nexttok.lineNumber))
            program = self.compoundStmt()
            if self.nexttok.type != 'PARSINGCOMPLETE':
                warnings.warn('Code beyond the end of the outermost compound statement')
                exit()

    def compoundStmt(self):
        # <compoundStmt> ::= begin <stmt> {; <stmt>} end
        if self.nexttok and self.nexttok.type != 'BEGIN':
            warnings.warn(
                'Expected BEGIN, saw ' + self.nexttok.value + ' at line ' + str(self.nexttok.lineNumber))
        if(self._accept('BEGIN')):
            compoundStmt = self.stmt()
            while (self._accept('SEMICOLON')):
                compoundStmt = self.stmt()
            self._expect('END')
            if self.nexttok.type == 'PARSINGCOMPLETE':
                print('Parsing complete')
                exit()

    def stmt(self):
        #<stmt> ::= <simpleStmt> | <structuredStmt>
        if self.nexttok.type == 'IF' or self.nexttok.type == 'WHILE' or self.nexttok.type == 'BEGIN':
            stmt = self.structStmt()
        elif self.nexttok.type == 'READ' or self.nexttok.type == 'WRITE' or self.nexttok.type == 'VARIABLE':
            stmt = self.simpleStmt()

    def structStmt(self):
        #<structured stmt> ::= <compoundStmt> | <ifStmt> | <whileStmt>
        if self.nexttok.type == 'BEGIN':
            structStmtData = self.compoundStmt()
            return structStmtData
        elif self.nexttok.type == 'IF':
            structStmtData = self.ifStmt()
            return structStmtData
        elif self.nexttok.type == 'WHILE':
            structStmtData = self.whileStmt()

    def ifStmt(self):
        #<if stmt> ::= if <expression> then <stmt> | if <expression> then <stmt> else <stmt>
        if self._accept('IF'):
            ifStmtData = self.expr()
            self._expect('THEN')
            ifStmtData = self.stmt()
            if self._accept('ELSE'):
                ifStmtData = self.stmt()

    def simpleStmt(self):
        # <simpleStmt> ::= <assignStmt> | <readStmt> | <writeStmt>
        if self.nexttok.type == 'VARIABLE':
            stmt = self.assignStmt()
        elif self.nexttok.type == 'READ':
            stmt = self.readStmt()
        elif self.nexttok.type == 'WRITE':
            stmt = self.writeStmt()

    def assignStmt(self):
        #<expr> ::= <variable> <assignment_op> <expression>
        if self._accept('VARIABLE'):
            if self._accept('ASSIGNMENT_OP'):
                assignStmt = self.expr()
            else:
                self._expect('ASSIGNMENT_OP')
                assignStmt = self.expr()

    def readStmt(self):
        # <readStmt> ::= read ( <variable> {,<variable>})
        if self._accept('READ'):
            self._expect('LEFT_PAREN')
            self._expect('VARIABLE')
            while (self._accept('COMMA')):
                readStmt = self._expect('VARIABLE')
            self._expect('RIGHT_PAREN')

    def writeStmt(self):
        #<writeStmt> ::= write ( <expr> {,<expr>})
        if self._accept('WRITE'):
            self._expect('LEFT_PAREN')
            writeData = self.expr()
            while(self._accept('COMMA')):
                writeData = self.expr()
            self._expect('RIGHT_PAREN')

    def whileStmt(self):
        #<whileStmt> ::= while<expr> do <stmt>
        if self._accept('WHILE'):
            whileStmtData = self.expr()
            self._expect('DO')
            whileStmtData = self.stmt()

    def expr(self):
        #<expr> ::= <simpleExpr> | <simpleExpr><relational_operator><simpleExpr>
        exprdata = self.simpleExpr()
        if self._accept('RELATIONAL_OPERATOR'):
            right = self.simpleExpr()

    def simpleExpr(self):
        #<expr> ::= [<signaddingop>] <term> {<signaddingop><term>}
        if self._accept('SIGNADDINGOP'):
            simexprdata = self.term()
        else:
            simexprdata = self.term()
        while self._accept('SIGNADDINGOP'):
                right = self.term()

    def term(self):
        #<term> ::= <factor> {<multiplying_operator> <factor>}
        termdata = self.factor()
        while self._accept('MULTIPLYING_OPERATOR'):
            self.factor()

    def factor(self):
        #<factor> ::= <variable> | <constant> | (<expr>)
        if self._accept('VARIABLE'):
            x = self.tok.value
        elif self._accept('CONSTANT'):
            x = self.tok.value
        elif self._accept('LEFT_PAREN'):
            exprdata = self.expr()
            self._expect('RIGHT_PAREN')
        else:
            if self.tok != None:
                warnings.warn('Expected a CONSTANT, VARIABLE, or LEFT_PAREN got ' + self.nexttok.type  + ' at line ' + str(self.nexttok.lineNumber))
