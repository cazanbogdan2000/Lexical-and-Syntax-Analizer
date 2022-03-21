import sys

class REGEX:
    # unicode for epsilon
    epsilon = '\u03B5'

    #constructor for regex
    def __init__(self, prenex):
        self.prenex = prenex
        self.prenex = self.prenex.split(" ")
        i = 0
        while i < len(self.prenex) - 1:
            if self.prenex[i] == '' and self.prenex[i + 1] == '':
                self.prenex.pop(i)
                self.prenex.pop(i)
                self.prenex.insert(i, " ")
            i += 1
        if self.prenex == []:
            self.prenex.append(" ")
    
    #function that converts a prenex to NFA
    def PrenexToNFA(self):
        stack = []
        stateIndex = 0
        # create a stack and append / pop elements, simulating the parsing tree
        for i in range(0, len(self.prenex)):
            if self.prenex[i] == "STAR":
                stack.append("STAR")
            elif self.prenex[i] == "PLUS":
                stack.append("PLUS")
            elif self.prenex[i] == "UNION":
                stack.append("UNION")
            elif self.prenex[i] == "CONCAT":
                stack.append("CONCAT")
            else:
                lexem = Lexem(self.prenex[i])
                partialNFA = lexem.getNFA(stateIndex)
                stateIndex += 2
                stack.append((lexem, partialNFA))
                while(len(stack) > 1):
                    if stack[-2] == "STAR":
                        prevObj = stack[-1][0]
                        obj = Star(prevObj)
                        oldNFA = stack[-1][1]
                        partialNFA = obj.getNFA(stateIndex, oldNFA)
                        stack = stack[0:-2]
                        stack.append((obj, partialNFA))
                        stateIndex += 2
                    elif stack[-2] == "PLUS":
                        prevObj = stack[-1][0]
                        obj = Plus(prevObj)
                        oldNFA = stack[-1][1]
                        partialNFA = obj.getNFA(stateIndex, oldNFA)
                        stack = stack[0:-2]
                        stack.append((obj, partialNFA))
                        stateIndex += 3
                    elif not isinstance(stack[-2][0], REGEX):
                        break
                    elif stack[-3] == "UNION":
                        prevObj1 = stack[-1][0]
                        prevObj2 = stack[-2][0]
                        obj = Union(prevObj1, prevObj2)
                        oldNFA1 = stack[-2][1]
                        oldNFA2 = stack[-1][1]
                        partialNFA = obj.getNFA(stateIndex, oldNFA1, oldNFA2)
                        stack = stack[0:-3]
                        stack.append((obj, partialNFA))
                        stateIndex += 2
                    elif stack[-3] == "CONCAT":
                        prevObj1 = stack[-1][0]
                        prevObj2 = stack[-2][0]
                        obj = Concat(prevObj1, prevObj2)
                        oldNFA1 = stack[-2][1]
                        oldNFA2 = stack[-1][1]
                        partialNFA = obj.getNFA(stateIndex, oldNFA1, oldNFA2)
                        stack = stack[0:-3]
                        stack.append((obj, partialNFA))
        return stack[0]
    
    # function to convert a regex from PRENEX to simple regex
    def __str__(self):
        stack = []
        # create a stack and append / pop elements, simulating the parsing tree
        for i in range(0, len(self.prenex)):
            if self.prenex[i] == "CONCAT":
                stack.append("CONCAT")
            elif self.prenex[i] == "STAR":
                stack.append("STAR")
            elif self.prenex[i] == "PLUS":
                stack.append("PLUS")
            elif self.prenex[i] == "UNION":
                stack.append("UNION")
            else:
                stack.append(Lexem(self.prenex[i]))
                while(len(stack) > 1):
                    if stack[-2] == "STAR":
                        obj = Star(stack[-1])
                        stack = stack[0:-2]
                        stack.append(obj)
                    elif stack[-2] == "PLUS":
                        obj = Plus(stack[-1])
                        stack = stack[0:-2]
                        stack.append(obj)
                    elif not isinstance(stack[-2], REGEX):
                        break
                    elif stack[-3] == "UNION":
                        obj = Union(stack[-2], stack[-1])
                        stack = stack[0:-3]
                        stack.append(obj)
                    elif stack[-3] == "CONCAT":
                        obj = Concat(stack[-2], stack[-1])
                        stack = stack[0:-3]
                        stack.append(obj)
        return str(stack[0])

    # function that converts a NFA to a DFA
    # It applies the subset construct algorithm
    def NFAtoDFA(self):
        nfa = self.PrenexToNFA()[1]
        delta = nfa[0]
        initialState = nfa[1][0]
        finalState = nfa[1][1]
        alphabet = set()
        states = set()
        # find direct epsilon enclosures
        eps_enclosures = {}
        init = []
        init.append(initialState)
        eps_enclosures[initialState] = init
        fin = []
        fin.append(finalState)
        eps_enclosures[finalState] = fin
        # make the tuples which will represent the new states after the convetion
        # always starts with the first tuple, which will be the initial state
        for transition in delta:
            alphabet.add(transition[1])
            if transition[0] not in eps_enclosures:
                value = []
                value.append(transition[0])
                eps_enclosures[transition[0]] = value
            if transition[1] == REGEX.epsilon:
                curr_enclosure = eps_enclosures[transition[0]]
                curr_enclosure.append(transition[2])
                eps_enclosures[transition[0]] = curr_enclosure
        if REGEX.epsilon in alphabet:
            alphabet.remove(REGEX.epsilon)
        for state in eps_enclosures:
            visited = []
            visited.append(state)
            queue = eps_enclosures[state][:]
            while queue:
                elem = queue.pop(0)
                if elem not in visited:
                    curr_enclosure = eps_enclosures[state][:]
                    curr_enclosure += eps_enclosures[elem]
                    eps_enclosures[state] = curr_enclosure[:]
                    visited.append(elem)
                    queue += eps_enclosures[elem]
            eps_enclosures[state] = list(set(eps_enclosures[state]))
        queue = []
        visited = set()
        for enclosure in eps_enclosures:
            if initialState in eps_enclosures[enclosure]:
                queue.append(tuple(eps_enclosures[enclosure]))
                visited.add(tuple(eps_enclosures[enclosure])) 

        new_delta = {}
        alphabet = list(alphabet)
        alphabet.sort()
        # creating the new states and the new delta
        while queue:
            current_state = queue.pop(0)
            for char in alphabet:
                new_state = []
                for state in current_state:
                    for transition in delta:
                        if transition[1] == char and transition[0] == state:
                            new_state += eps_enclosures[transition[2]]
                new_state = list(set(new_state))
                new_state.sort()
                new_state = tuple(new_state)
                if new_state not in visited and new_state != ():
                    queue.append(new_state)
                    visited.add(new_state)
                if new_state != ():
                    new_delta[(current_state, char)] = new_state
        
        # matching for each tuple of states a number, which will represent
        # basically the new states, in normal form (tuple -> number) 
        DFA_StateIndex = 0
        DFA_InitialState = []
        DFA_FinalStates = []
        DFA_States = []
        DFA_Alphabet = alphabet[:]
        DFA_Delta = {}
        tuple_to_newState = {}
        for transition in new_delta:
            if transition[0] not in tuple_to_newState:
                tuple_to_newState[transition[0]] = DFA_StateIndex
                DFA_States.append(DFA_StateIndex)
                DFA_StateIndex += 1
            if new_delta[transition] not in tuple_to_newState:
                tuple_to_newState[new_delta[transition]] = DFA_StateIndex
                DFA_States.append(DFA_StateIndex)
                DFA_StateIndex += 1
            if initialState in transition[0]:
                DFA_InitialState = [tuple_to_newState[transition[0]]]
            if finalState in transition[0]:
                DFA_FinalStates += [tuple_to_newState[transition[0]]]
            if finalState in new_delta[transition]:
                DFA_FinalStates += [tuple_to_newState[new_delta[transition]]]

            DFA_Delta[(tuple_to_newState[transition[0]], transition[1])] = tuple_to_newState[new_delta[transition]]
        DFA_FinalStates = list(set(DFA_FinalStates))
        # Adding a sink state to our program and also transitions required
        sink_state = DFA_StateIndex
        DFA_States.append(sink_state)
        for state in DFA_States:
            for char in DFA_Alphabet:
                if (state, char) not in DFA_Delta:
                    DFA_Delta[(state, char)] = sink_state

        return (DFA_Delta, DFA_Alphabet, DFA_InitialState, DFA_FinalStates, DFA_States)

"""
    The following objects inherits REGEX, which means it will be a part of the
    final regex. Each object will contain a method called getNFA, which will
    take as an input the previous nfa on the stack (or lexem, if it is the case)
    and:
    1) if lexem, will create a new nfa, which will be stored
    2) if star or plus, will complete the nfa received with 2 other states and
    corresponding transitions
    3) Concat will take 2 nfas and will combine them, obtaining only one new
    nfa just by simply adding a new transition.
    4) Union will also take 2 nfas and will combine them and will add 2 new
    states and corresponding transitions.
"""

class Lexem(REGEX):
    def __init__(self, word):
        self.word = str(word)

    def __str__(self):
        return self.word
    
    def getNFA(self, indexState):
        importantStates = [indexState, indexState + 1]
        delta = set()
        delta.add((indexState, self.word, indexState + 1))
        return (delta, importantStates)

class Star(REGEX):
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        if  len(str(self.expr)) > 1 and str(self.expr)[-1] != ")":
            return "(" + str(self.expr) + ")*"
        else:
            return str(self.expr) + "*"

    def getNFA(self, indexState, oldNFA):
        delta = oldNFA[0]
        importantStates = oldNFA[1]
        initialState = importantStates[0]
        finalState = importantStates[1]
        importantStates = [indexState, indexState + 1]
        delta.add((indexState, REGEX.epsilon, initialState))
        delta.add((finalState, REGEX.epsilon, indexState + 1))
        delta.add((finalState, REGEX.epsilon, initialState))
        delta.add((indexState, REGEX.epsilon, indexState + 1))
        return (delta, importantStates)   

class Plus(REGEX):
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        if  len(str(self.expr)) > 1 and str(self.expr)[-1] != ")":
            return "(" + str(self.expr) + ")+"
        else:
            return str(self.expr) + "+"

    def getNFA(self, indexState, oldNFA):
        delta = oldNFA[0]
        importantStates = oldNFA[1]
        initialState = importantStates[0]
        finalState = importantStates[1]
        importantStates = [indexState, indexState + 1]
        delta.add((indexState, REGEX.epsilon, initialState))
        delta.add((finalState, REGEX.epsilon, indexState + 1))
        delta.add((finalState, REGEX.epsilon, initialState))
        return (delta, importantStates)         

class Union(REGEX):
    def __init__(self, exp1, exp2):
        self.exp1 = exp1
        self.exp2 = exp2

    def __str__(self):
        return "(" + (str(self.exp1) + " U " + str(self.exp2)) + ")"

    def getNFA(self, stateIndex, oldNFA1, oldNFA2):
        delta1 = oldNFA1[0]
        delta2 = oldNFA2[0]
        importantStates1 = oldNFA1[1]
        importantStates2 = oldNFA2[1]
        initialState1 = importantStates1[0]
        initialState2 = importantStates2[0]
        finalState1 = importantStates1[1]
        finalState2 = importantStates2[1]
        importantStates = [stateIndex, stateIndex + 1]
        delta = delta1 | delta2
        delta.add((stateIndex, REGEX.epsilon, initialState1))
        delta.add((stateIndex, REGEX.epsilon, initialState2))
        delta.add((finalState1, REGEX.epsilon, stateIndex + 1))
        delta.add((finalState2, REGEX.epsilon, stateIndex + 1))

        return (delta, importantStates)

class Concat(REGEX):
    def __init__(self, exp1, exp2):
        self.exp1 = exp1
        self.exp2 = exp2

    def __str__(self):
        return str(self.exp1) + str(self.exp2)

    def getNFA(self, stateIndex, oldNFA1, oldNFA2):
        delta1 = oldNFA1[0]
        delta2 = oldNFA2[0]
        importantStates1 = oldNFA1[1]
        importantStates2 = oldNFA2[1]
        initialState1 = importantStates1[0]
        initialState2 = importantStates2[0]
        finalState1 = importantStates1[1]
        finalState2 = importantStates2[1]
        importantStates = [initialState1, finalState2]
        delta = delta1 | delta2
        delta.add((finalState1, REGEX.epsilon, initialState2))

        return (delta, importantStates)

# function which prints a DFA; puts the result in the 'file' object
def printDFA(dfa, token):
    #f = open(file, "w")
    f = []
    delta = dfa[0]
    alphabet = dfa[1]
    initialState = dfa[2]
    finalStates = dfa[3]
    states = dfa[4]
    f.append("".join(alphabet).replace('\n', '\\n'))
    f.append('\n')
    f.append(token)
    f.append('\n')
    for i in range(0, len(initialState) - 1):
        f.append(str(initialState[i]))
        f.append(' ')
    f.append(str(initialState[-1]))
    f.append('\n')
    dfa_list = []
    for transition in delta:
        dfa_list.append((transition[0], transition[1], delta[transition]))
    dfa_list.sort()
    for i in range(0, len(dfa_list)-1):
        f.append(str(dfa_list[i][0]))
        f.append(",")
        f.append("'")
        f.append(str(dfa_list[i][1]))
        f.append("'")
        f.append(",")
        f.append(str(dfa_list[i][2]))
        f.append('\n')

    f.append(str(dfa_list[-1][0]))
    f.append(",'")
    f.append(str(dfa_list[-1][1]))
    f.append("',")
    f.append(str(dfa_list[-1][2]))
    f.append('\n')

    finalStates.reverse()
    for i in range(0, len(finalStates) - 1):
        f.append(str(finalStates[i]))
        f.append(' ')
    f.append(str(finalStates[-1]))
    f.append('\n')
    f = "".join(f)
    return f

# call the main functions
def main():
    inp = sys.argv
    s = open(inp[1], "r").read()
    obj = REGEX(s)
    dfa = obj.NFAtoDFA()
    #printDFA(dfa, inp[2])

if __name__ == '__main__':
	main()

