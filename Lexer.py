# class used to create an object of type DFA (basically it's a DFA)
class Dfa:
    # DFA constructor
    def __init__(self, inputString):
        # split the inout of DFA on lines
        parser = inputString.splitlines()
        self.alphabet = set()
        # create the alphabet, which is a set
        for i in range(1, len(parser) - 1):
            self.alphabet.add(parser[i].split()[1])
        # declare initial state and final states
        self.initial = int(parser[0])
        self.final = list(map(int, parser[len(parser) - 1].split()))
        # create the states and the delta function (a.k.a transitions)
        self.delta = {}
        self.states = set()
        for i in range(1, len(parser) - 1):
            elem = parser[i].split()
            # special case for " " character
            if (len(elem) == 2):
                elem.insert(1, ' ')
                self.alphabet.add(' ')
            # delta is a dictionary with the key a tuple (curr_state, pos_char)
            self.delta[(int(elem[0]), elem[1])] = int(elem[2])
            self.states.add(int(elem[0]))
            self.states.add(int(elem[2]))
        # find the sink states of the DFA
        self.sink_states = self.find_sink_states()

    # function used to find the sink states of our given DFA
    def find_sink_states(self):
        visited = set(self.final)
        # calculate the reveresed delta function
        reversed_delta = self.revDelta()
        # apply BFS from final states on the reversed delta
        for final_state in self.final:
            q = [final_state]
            while q:
                el = q.pop(0)
                for elem in reversed_delta:
                    if elem[2] not in visited and elem[0] == el:
                        visited.add(elem[2])
                        q.append(elem[2])
        # nonvisited states are sink states (you can't get in a final state
        # from a sink state)
        return self.states - visited

    # function which executes a single step on a given input, based on the 
    # current configuration
    def singleStep(self, configuration):
        state = configuration[0]
        word = configuration[1]
        # end of word or empty word
        if word == '':
            if state in self.final:
                return True
            else:
                return False
        # special case for '\n' threated here, implementation reasons, not
        # logic ones
        if word[0] == '\n':
            if (state, '\\n') not in self.delta:
                return (-1, word)
            return (self.delta[(state, '\\n')], word[1:])
        # meeting a configuration which is not in our delta function (kinda
        # errorish)
        if (state, word[0]) not in self.delta:
            return (-1, word)
        return (self.delta[(state, word[0])], word[1:])

    # this is the function that computes the reverse of our delta function
    def revDelta(self):
        result = set()
        for key in self.delta:
            result.add((self.delta[key], key[1], key[0]))
        return result

    # the function which computes the longest prefix accepted by this DFA,
    # depending on a given input("word")
    def longestPrefixAccepted(self, word):
        #extract the configuration
        configuration = (self.initial, word)
        # maximum sequence that this DFA can reach (not necesary accepting that
        # sequence)
        maximum = 0
        # maximum accepted sequence
        longestToReturn = 0
        while configuration != True and configuration != False and \
            configuration[0] not in self.sink_states and configuration[0] != -1:
            configuration = self.singleStep(configuration)
            maximum += 1
            if configuration == True:
                maximum = 0
                break
            elif configuration == False:
                break
            if configuration[0] in self.final:
                longestToReturn = maximum
        return (longestToReturn, maximum)

# The class that constructs an object of type lexer, which contains a bunch of
# DFA's; run an input on the lexer and obtain the lexemes
class Lexer:
    # constructor for a lexer object
    def __init__(self, DFA_list):
        self.DFA_list = DFA_list

    # this function generates the lexemes based on the lexer
    def lexical_analysis(self, myWord):
        #myWord == initial word
        result = []

        #word == the remaining part of the word, at some given time
        word = myWord
        # parse the input
        while word != "":            
            maximumLen = -1
            prefix = []
            Dfa_index = ""
            maximum = 0
            # iterate through lexer's DFAs and see the best sequence
            for dfa in self.DFA_list:
                longestPrefix = dfa[1].longestPrefixAccepted(word)
                if maximum < longestPrefix[1]:
                    maximum = longestPrefix[1]
                else:
                    maximum
                longestPrefix = longestPrefix[0]
                if longestPrefix > maximumLen:
                    maximumLen = longestPrefix
                    prefix = word[:longestPrefix]
                    Dfa_index = dfa[0]
            else:
                result += [(Dfa_index, prefix)]
            word = word[maximumLen:]
            # special case: no DFA reaches a final state; parse error
            if maximumLen == 0:
                if len(myWord) - len(word) + maximum > len(myWord):
                    return "No viable alternative at character EOF, line 0"
                return "No viable alternative at character " + str(len(myWord)
                - len(word) + maximum - 1) + ", line 0"
        return result

# function to run the homework
# the lexer class is from previous labs, i took the input and adapted it to
# the already implemented lexer
def runlexer(lexer, finput, foutput):
    lexer = lexer.split('\n\n')
    dfa = []
    for i in range(0, len(lexer)):
        new_dfa = lexer[i].splitlines()
        new_dfa = new_dfa[3:-1]
        new_dfa = list(map(lambda word: word.replace(',', ' '), new_dfa))
        new_dfa = list(map(lambda word: word.replace('\'', ''), new_dfa))
        new_dfa = [lexer[i].splitlines()[2]] + new_dfa + [lexer[i].splitlines()[-1]]
        new_dfa = '\n'.join(new_dfa)
        dfa.append((lexer[i].splitlines()[1], Dfa(new_dfa)))
    lexer = Lexer(dfa)
    finput = open(finput, "r").read()
    result = lexer.lexical_analysis(finput)
    foutput = open(foutput, "w")
    if isinstance(result, str):
        foutput.write(result)
    else:
        for i in range(0, len(result) - 1):
            foutput.write(result[i][0] + ' ' + result[i][1].replace('\n', '\\n') + '\n')
        foutput.write(result[-1][0] + ' ' + result[-1][1].replace('\n', '\\n'))

if __name__ == "__main__":
    runlexer("tests/T1/T1.11/T1.11.lex", "tests/T1/T1.11/input/T1.11.1.in",
        "tests/T1/T1.4/out/T1.11.1.out")