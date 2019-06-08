import re
import collections
import warnings
import sys
#Define and group regex patterns as ordered pairs, set up for VERBOSE
token_pattern = r"""
(?P<RELATIONAL_OPERATOR>==|<>|<=|>=|>|<)
|(?P<MULTIPLYING_OPERATOR>[*/])
|(?P<SIGNADDINGOP>[+-])
|(?P<LEFT_PAREN>[(])
|(?P<RIGHT_PAREN>[)])
|(?P<COMMA>[,])
|(?P<ASSIGNMENT_OP>:=)
|(?P<SEMICOLON>[;])
|(?P<PROGRAM>program)
|(?P<DO>do)
|(?P<WHILE>while)
|(?P<ELSE>else)
|(?P<THEN>then)
|(?P<IF>if)
|(?P<WRITE>write)
|(?P<READ>read)
|(?P<END>end)
|(?P<BEGIN>begin)
|(?P<CONSTANT>[0-9]+)
|(?P<PROGNAME>[A-Z][a-zA-Z0-9]*)
|(?P<VARIABLE>[a-zA-Z][a-zA-Z0-9]*)
|(?P<NEWLINE>[\n])
|(?P<SKIP>[\s+\t])
|(?P<COMMENT> [#].*)
|(?P<ILLEGAL> .)
"""
#
#re.VERBOSE for cleaner regex, the <SKIP> pattern to use to avoid lexing whitespace
#and tabs, comment pattern to avoid lexing comments
token_re = re.compile(token_pattern, re.VERBOSE)
Token = collections.namedtuple('Token', ['type','value', 'lineNumber'])
#just for some debugging help
class TokenizerException(Exception): pass


def lex(text):
    pos = 0
    llineCount = 0
    progNameExists = False;
    while True:
        tokMatch = token_re.match(text, pos)
        if not tokMatch: break
        pos = tokMatch.end()
        tokIdent = tokMatch.lastgroup
        tokValue = tokMatch.group(tokIdent)
        #Keep track of the current line.
        if tokIdent == 'ILLEGAL':
            warnings.warn("Lexical Analyzer detected illegal token " + tokValue)
        if tokIdent == 'NEWLINE':
            llineCount = llineCount + 1
        if tokIdent == 'PROGNAME' and progNameExists == True:
            tokIdent = 'VARIABLE'
        if tokIdent !=  'SKIP' and tokIdent != 'COMMENT' and tokIdent != 'NEWLINE':
            # Make sure that PROGNAME only appears once
            if tokIdent == 'PROGNAME' and progNameExists == False:
                progNameExists = True
            yield Token(tokIdent, tokValue, llineCount)  # similar to return, but returns a generator
        if pos == len(text): break
    if pos != len(text):
        #to give me the position at which the error occured.
        raise TokenizerException('tokenizer stopped at pos %r of %r' % (
            pos, len(text)))

