import Lexer
import PrenexToDfa
import ast

# function that converts an input of type Regex to type Prenex
def RegexToPrenex(regex):
    regex = list(regex)
    i = 0
    # treat the special case, when +,*,() are characters
    while i < len(regex):
        if regex[i] == "'":
            regex.pop(i)
            el = regex.pop(i)
            regex.pop(i)
            regex.insert(i, "'" + el + "'")
        i += 1
    stack = []
    char = 0
    # parse regex
    for char in regex:
        while True:
            # if current char is an character, a '|', a '(' or simple string:
            if char not in [')', '+', '*']:
                # analyse previous elements on stack;
                # based on that do different things
                if len(stack) >= 2:
                    res = ConcatOrUnion(stack)
                    if res[0] == False:
                        continue
                    # if we have just a set of brackets on the stack that are
                    # besides a single variable, then erase them
                    elif stack[-1] == ')' and stack[-3] == '(':
                        aux = stack[-2]
                        stack.pop()
                        stack.pop()
                        stack.pop()
                        stack.append(aux)
                    else:
                        break
                else:
                    break
            # if the current character is ')'
            elif char == ')':
                if len(stack) >= 2:
                    res = ConcatOrUnion(stack)
                    if res[0] == False:
                        continue
                    # if we have just a set of brackets on the stack that are
                    # besides a single variable, then erase them
                    elif stack[-1] == ')' and stack[-3] == '(':
                        aux = stack[-2]
                        stack.pop()
                        stack.pop()
                        stack.pop()
                        stack.append(aux)
                    else:
                        break
                else:
                    break
            # the case when we have a star or plus, the procedure is the same
            elif char in ['*', '+']:
                wordToAdd = ''
                if char == '*':
                    wordToAdd = 'STAR'
                else:
                    wordToAdd = 'PLUS'
                if stack[-1] != ')':
                    stack[-1] = wordToAdd + " " + stack[-1]
                    if len(stack) >= 2:
                       res = ConcatOrUnion(stack)
                # if we have just a set of brackets on the stack that are
                # besides a single variable, then erase them
                elif stack[-1] == ')' and stack[-3] == '(':
                    aux = wordToAdd + " " + stack[-2]
                    stack.pop()
                    stack.pop()
                    stack.pop()
                    stack.append(aux)
                break
        # add the char in the stack, except
        if char not in ['*', '+']:
            stack.append(char)
    return getPrenexFromStack(stack)

# after we have parsed the regex, there are a few components remained on the
# stack; get the final Prenex form them
def getPrenexFromStack(stack):
    while len(stack) > 1:
        if stack[-1] == ')':
            stack.pop()
            if stack[-2] != '(' and len(stack) > 1:
                if stack[-2] != '|':
                    aux = "CONCAT " + stack[-2] + " " + stack[-1]
                    stack.pop()
                    stack.pop()
                    stack.append(aux)
                else:
                    aux = "UNION " + stack[-3] + " " + stack[-1]
                    stack.pop()
                    stack.pop()
                    stack.pop()
                    stack.append(aux)
            aux = stack[-1]
            stack.pop()
            stack.pop()
            stack.append(aux)
        elif stack[-2] != '|':
            aux = "CONCAT " + stack[-2] + " " + stack[-1]
            stack.pop()
            stack.pop()
            stack.append(aux)
        else:
            aux = "UNION " + stack[-3] + " " + stack[-1]
            stack.pop()
            stack.pop()
            stack.pop()
            stack.append(aux)
    return stack[0]

# the case when we need to do CONCAT or UNION, depending on the elements on
# stack; updates stack, return ok if we had one of those two
def ConcatOrUnion(stack):
    ok = False
    # if previous elements are chars and need to CONCAT them
    if stack[-1] not in ['(', ')', '|', '+', '*']\
            and stack[-2] not in ['(', ')', '|', '+', '*']:
        if len(stack[-1]) == 3:
            stack[-1] = stack[-1][1:2]
        if len(stack[-2]) == 3:
            stack[-2] = stack[-1][1:2]
        aux = "CONCAT " + stack[-2] + " " + stack[-1]
        stack.pop()
        stack.pop()
        stack.append(aux)
    # if previous elements are chars and need to UNION them
    elif stack[-2] == '|' and stack[-1] not in \
            ['(', ')', '|', '+', '*'] and stack[-3] not in\
            ['(', ')', '|', '+', '*']:
        if len(stack[-1]) == 3:
            stack[-1] = stack[-1][1:2]
        if len(stack[-2]) == 3:
            stack[-2] = stack[-1][1:2]
        aux = "UNION " + stack[-3] + " " + stack[-1]
        stack.pop()
        stack.pop()
        stack.pop()
        stack.append(aux)
    else:
        ok = True
    return (ok, stack)

# the function that will write in a file the complete output by parsing a file
# using a given lexer
def runcompletelexer(lexer, finput, foutput):
    lexer = open(lexer, 'r').read()
    lexerList = lexer.split(";")
    lexerList.pop()
    for i in range(0, len(lexerList)):
        if lexerList[i][0] == '\n':
            lexerList[i] = lexerList[i][1:]
        lexerList[i] = lexerList[i]\
            .replace("'", "")\
            .replace("\\n", "\n")\
            .split(" ", 1)
        obj = PrenexToDfa.REGEX(RegexToPrenex(lexerList[i][1]))
        lexerList[i] = PrenexToDfa.printDFA(obj.NFAtoDFA(),\
            lexerList[i][0]).replace("'\n'", "'\\n'")
    lexer = "\n".join(lexerList)
    Lexer.runlexer(lexer, finput, foutput)

# the function that will take an imperative programming language, will parse it
# using the ProgLexer.lex file, written by us (DO NOT DELETE THAT FILE, AT ANY
# COST!!!) and using the ast.py file, we'll obtain the final output
def runparser(finput, foutput):
    lexer = open("ProgLexer.lex", 'r').read()
    lexerList = lexer.split(";")
    lexerList.pop()
    for i in range(0, len(lexerList)):
        if lexerList[i][0] == '\n':
            lexerList[i] = lexerList[i][1:]
        lexerList[i] = lexerList[i]\
            .replace("'\\n'", "\n")\
            .replace("'\\t'", "\t")\
            .split(" ", 1)
        obj = PrenexToDfa.REGEX(RegexToPrenex(lexerList[i][1]))
        lexerList[i] = PrenexToDfa.printDFA(obj.NFAtoDFA(),\
             lexerList[i][0]).replace("'\n'", "'\\n'")
    lexer = "\n".join(lexerList)
    auxOut = "out.txt"
    Lexer.runlexer(lexer, finput, auxOut)
    GenerateParsedObject(auxOut, foutput)

# check if we have met an operand or not
def Operand(elem, height):
    if isinstance(elem, ast.Expr):
        return elem
    if elem[0] == "VARIABLE":
        return ast.Expr(height, 'v', elem[1])
    if elem[0] == "VALUE":
        return ast.Expr(height, 'i', int(elem[1]))

# Function that generates the parsed object, using a stack; the logic of this
# algorithm is recursively, but we used a stack instead (due to the possible
# big length of our program, the height of the tree could grow considerably)
def GenerateParsedObject(fin, fout):
    inp = open(fin, 'r').read().split('\n')
    for i in range(0, len(inp)):
        inp[i] = inp[i].split(' ', 1)
    stack = []
    height = 0
    hasAssign = False
    # after we parsed the program, we will obtain in a file named out.txt
    # where we have the result after applying our lexer
    for elem in inp:
        # add to stack, nothing major
        if elem[0] == "BEGIN" or elem[0] == "VARIABLE" or elem[0] == "VALUE"\
                or elem[0] == "BRACKETS_OPEN":
            stack.append(elem)
        # increase the height in your tree
        elif elem[0] == "OPERATORS" or elem[0] == "IF"\
                or elem[0] == "WHILE":
            stack.append(elem)
            height += 1
        # if there is an assign, we will have to do something when we meet
        # NEWLINE
        elif elem[0] == "ASSIGN":
            stack.append(elem)
            hasAssign = True
            height += 1
        # Comparators are always in some brackets; deal with them!
        elif elem[0] == "COMPARATORS":
            while stack[-2][0] != "BRACKETS_OPEN":
                operand2 = Operand(stack.pop(), height)
                operator = stack.pop()
                operand1 = Operand(stack.pop(), height)
                stack.append(ast.Expr(height - 1, operator[1], operand1, operand2))
            height -= 1
            stack.append(elem)
        # closed brackets means that we end some sort of condition
        elif elem[0] == "BRACKETS_CLOSE":
            while stack[-2][0] != "BRACKETS_OPEN":
                operand2 = Operand(stack.pop(), height)
                operator = stack.pop()
                operand1 = Operand(stack.pop(), height)
                stack.append(ast.Expr(height - 1, operator[1], operand1, operand2))
            height -= 1
            stack.pop(-2)
        # just increase the height of the tree
        elif elem[0] == "THEN" or elem[0] == "DO" or elem[0] == "ELSE":
            height += 1
        # fi means the end of an if block
        elif elem[0] == "FI":
            my_else = stack.pop()
            then = stack.pop()
            condition = stack.pop()
            stack.pop()
            height -= 2
            stack.append(ast.If(height, condition, then, my_else))
        # same does od, just for while
        elif elem[0] == "OD":
            body = stack.pop()
            condition = stack.pop()
            stack.pop()
            height -= 2
            stack.append(ast.While(height, condition, body))
        # in some cases, newline doesn't do much; but in other cases, such as
        # assign, then it means that we have to do an assignment of a value to
        # a given variable, all found on the stack
        # There are also cases when we could also have even some operations,
        # before attribution
        elif elem[0] == "NEWLINE":
            if hasAssign == True:
                hasAssign = False
                while stack[-2][0] != "ASSIGN":
                    operand2 = Operand(stack.pop(), height)
                    operator = stack.pop()
                    operand1 = Operand(stack.pop(), height)
                    stack.append(ast.Expr(height, operator[1], operand1, operand2))
                operand2 = Operand(stack.pop(), height)
                operator = stack.pop()
                operand1 = Operand(stack.pop(), height)
                height -= 1
                stack.append(ast.Assign(height, operand1, operand2))
        # end marks the end of a begin--end block
        # There we make a list of all objects found on the stack, until we meet
        # the BEGIN keyword
        elif elem[0] == "END":
            l = []
            while isinstance(stack[-1], ast.Assign) or\
                    isinstance(stack[-1], ast.If) or\
                    isinstance(stack[-1], ast.While) or\
                    isinstance(stack[-1], ast.InstructionList):
                l.insert(0, stack.pop())
            stack.pop()
            stack.append(ast.InstructionList(height, l))
            height -= 1       
    f = open(fout, 'w')
    f.write(str(stack[0]))