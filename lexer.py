import re

#fixed tokens
keywds = {"Let", "be", "maps", "to", "if", "then", "else", "Compute", "num", "bool"}
puncs = {",","." ,"(" , ")"}
arithOps = {"+", "*"}
relaOps =  {"=", "<"}
type = {">>"}

num_lit = re.compile(r"^-?(0|[1-9][0-9]*)$")
bool_lit = {"true", "false"}
id = re.compile(r"^[a-z]+$")

class Token:
    # Your implementation
    def __init__(self, name: str, lexeme: str):
        self.name = name
        self.lexeme = lexeme
    

class Lexer:
    # Your implementation
    # This is only an example, you can modify it as you like
    def __init__(self, source_code: str):
        self.source_code = source_code

    def tokens(self) -> list[Token] | None:
        #split by whitespace
        clips = self.source_code.split()
        #result
        r = []
        for s in clips:
            #1.fixed tokens
            if (s in keywds or s in puncs or s in arithOps or s in relaOps or s in relaOps or s in type):
                r.append(Token(name=s, lexeme=s))
            #2.bool lit
            elif s in bool_lit:
                r.append(Token(name="bool_lit", lexeme=s))
            #3.number lit
            elif num_lit.match(s):
                r.append(Token(name="num_lit", lexeme=s))
            #4.id
            elif id.match(s) and (s not in keywds):
                r.append(Token(name="identifier", lexeme=s))
            #lexical error
            else: 
                return None
        return r