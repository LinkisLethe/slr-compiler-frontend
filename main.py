from lexer import Lexer
from lexer import Token
from parser import Parser
import sys
import json

# WARNING:
# - You are not allowed to use any external libraries other than the standard library
# - Please do not modify the file name of the entry file 'main.py'
# - Our autograder will test your code by runing 'python main.py <test_file>'
#   The current directory will be the same directory as the entry file
#   So please make sure your import statement is correct

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python main.py <test_file>")
        sys.exit(1)

    file_name = sys.argv[1]

    with open(file_name, 'r', encoding="utf-8") as f:
        source_code = f.read()
    #outputs
    lexer_out = file_name + "_lexer.json"
    parse_out = file_name + "_parse.json"
    type_out = file_name + "_type.json"
    ast_out = file_name + "_ast.json"

    #-------------lexer--------------
    lexer = Lexer(source_code)
    tokens = lexer.tokens()

    #lexer output
    with open(lexer_out, 'w') as o:
        if tokens is None:
            o.write("Lexical error")
        else:
            result = []
            for t in tokens:
                result.append({"name": t.name,"lexeme": t.lexeme})
            json.dump(result, o, indent=2)

    #if lexical error,following phases are also lexical error
    if tokens is None:
        with open(parse_out, 'w') as o:
            o.write("Lexical error")
        with open(type_out, 'w') as o:
            o.write("Lexical error")
        with open(ast_out, 'w') as o:
            o.write("Lexical error")
        sys.exit(0)

    #append eof
    tokens.append(Token("$", "$"))

    #-------------parser+semantic--------------
    parser = Parser(tokens)
    ret = parser.parse()

    #syntax error, current and following phases are syntax error
    if ret is None or ret is False:
        with open(parse_out, 'w') as o:
            o.write("Syntax error")
        with open(type_out, 'w') as o:
            o.write("Syntax error")
        with open(ast_out, 'w') as o:
            o.write("Syntax error")
        sys.exit(0)

    parse_tree, type_tree, ast_forest = ret

    #parse output
    with open(parse_out, 'w') as o:
        json.dump(parse_tree, o, indent=2)

    #type error
    if parser.type_error:
        with open(type_out, 'w') as o:
            o.write("Type error")
        with open(ast_out, 'w') as o:
            o.write("Type error")
        sys.exit(0)

    #type+ast output
    with open(type_out, 'w') as o:
        json.dump(type_tree, o, indent=2)

    with open(ast_out, 'w') as o:
        json.dump(ast_forest, o, indent=2)
