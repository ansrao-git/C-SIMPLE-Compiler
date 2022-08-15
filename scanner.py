import re
import pdb

# simple implementation of the EM Scanner from HW 1

class ScannerException(Exception):

    # Report the line number in the exception
    def __init__(self, lineno):
        message = "Scanner error on line: " + str(lineno)
        super().__init__(message)

class Scanner:
    def __init__(self):
        self.lineno = 1
        self.tokens = None

    def set_tokens(self, tokens):
        self.tokens = tokens

    def input_string(self, input_string):
        self.istring = input_string

    # Get the scanner line number, needed for the parser exception
    def get_lineno(self):
        return self.lineno

    # You can use your scanner implementation here if you'd like
    # it is just the EMScanner right now
    def token(self):
        
        # Loop until we find a token we can
        # return (or until the string is empty)
        while True:
            if len(self.istring) == 0:
                return None

            # For each substring
            for l in range(len(self.istring),0,-1):
                matches = []

                # Check each token
                for t in self.tokens:                    
                    # Create a tuple for each token:
                    # * first element is the token name
                    # * second is the possible match
                    # * third is the token action
                    matches.append((t[0],
                                    re.fullmatch(t[1],self.istring[:l]),
                                    t[2]))

                # Check if there is any token that returned a match
                # If so break out of the substring loop
                matches = [m for m in matches if m[1] is not None]
                if len(matches) > 0:
                    break
                
            if len(matches) == 0:
                raise ScannerException(self.lineno);
            
            # since we are exact matching on the substring, we can
            # arbitrarily take the first match as the longest one            
            longest = matches[0]

            # apply the token action
            lexeme = longest[2]((longest[0],longest[1][0]))

            # figure how much we need to chop from our input string
            chop = len(lexeme[1])
            self.istring = self.istring[chop:]

            # if we did not match an IGNORE token, then we can
            # return the lexeme
            if lexeme[0] != "IGNORE":
                return lexeme


keywords = [("IF", "if"), ("ELSE", "else"), ("FOR", "for"), ("INT", "int"), ("FLOAT", "float"), ("VOID", "void")]

def find_keywords(x):
    values = [k[1] for k in keywords]
    if x[1] in values:
        i = values.index(x[1])
        return keywords[i]
    return x

def idy(x):
    return x

tokens = [ ("MUL", "\*", idy),
           ("PLUS", "\+", idy),
           ("MINUS", "-", idy),
           ("DIV", "/", idy),
           ("EQ", "==", idy), 
           ("LT", "<", idy),
           ("LBRACE", "{", idy),
           ("RBRACE", "}", idy),
           ("LPAR", "\(", idy),
           ("RPAR", "\)", idy),
           ("SEMI", ";", idy),
           ("ASSIGN", "=", idy),
           ("AMP", "&", idy),
           ("COMMA", ",", idy), 
           ("NUM", "([0-9]+(\.[0-9]+)?)|(\.[0-9]+)", idy), 
           ("ID", "[a-zA-Z]+[a-zA-Z0-9]*", find_keywords)
          ]
