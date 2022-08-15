import pdb
from ast import *

# Extra classes:

# Keeps track of the type of an ID,
# i.e. whether it is a program variable
# or an IO variable
class IDTypes(Enum):
    IO = 1
    VAR = 2

# The data to be stored for each ID in the symbol table
class SymbolTableData:
    def __init__(self, id_type, data_type, new_name):
        self.id_type = id_type      # if the variable is input/output
                                    # or variable
                                    
        self.data_type = data_type  # if the variable is an int or
                                    # float
                                    
        self.new_name = new_name    # a new name to resolve collisions
                                    # in scoping

    # Getters for each of the elements
    def get_id_type(self):
        return self.id_type

    def get_data_type(self):
        return self.data_type

    def get_new_name(self):
        return self.new_name

# Symbol Table exception, requires a line number and ID
class SymbolTableException(Exception):
    def __init__(self, lineno, ID):
        message = "Symbol table error on line: " + str(lineno) + "\nUndeclared ID: " + str(ID)
        super().__init__(message)

class TypeException(Exception): # added type exception
    def __init__(self, message):
        message = "\n" + message
        super().__init__(message)

# Generates a new label when needed
class NewLabelGenerator():
    def __init__(self):
        self.counter = 0
        
    def mk_new_label(self):
        new_label = "label" + str(self.counter)
        self.counter += 1
        return new_label

# Generates a new name (e.g. for program variables)
# when needed
class NewNameGenerator():
    def __init__(self):
        self.counter = 0
        self.new_names = []

    # You may want to make a better renaming scheme
    def mk_new_name(self):
        new_name = "_new_name" + str(self.counter)
        self.counter += 1
        self.new_names.append(new_name)
        return new_name
    
# Allocates virtual registers
class VRAllocator():
    def __init__(self):
        self.counter = 0
        
    def mk_new_vr(self):
        vr = "vr" + str(self.counter)
        self.counter += 1
        return vr

    # get variable declarations (needed for the C++ wrapper)
    def declare_variables(self):
        ret = []
        for i in range(self.counter):
            ret.append("virtual_reg vr%d;" % i)

        return ret

# Symbol table class
class SymbolTable:
    def __init__(self,nng):
        # stack of hashtables
        self.ht_stack = [dict()]
        self.nng = nng # newname object

    def insert(self, ID, id_type, data_type):
        
        # Create the data to store for the ID
        
        # if its a program variable, make new name - Anish
        if id_type == IDTypes.VAR:
           newname = self.nng.mk_new_name()
           info = SymbolTableData(id_type, data_type, newname)
           self.ht_stack[-1][ID] = info
        
        # HOMEWORK: make sure this is storing the 
        # right information! You may need to use
        # the new name generator to make new names
        # for some ids
        else:
            info = SymbolTableData(id_type, data_type, ID)
            self.ht_stack[-1][ID] = info        

    # Lookup the symbol. If it is there, return the
    # info, otherwise return Noney
    def lookup(self, ID):
        for ht in reversed(self.ht_stack):
            if ID in ht:
                return ht[ID]
        return None

    def push_scope(self):
        self.ht_stack.append(dict())

    def pop_scope(self):
        self.ht_stack.pop()

# Parser Exception
class ParserException(Exception):
    
    # Pass a line number, current lexeme, and what tokens are expected
    def __init__(self, lineno, lexeme, tokens):
        message = "Parser error on line: " + str(lineno) + "\nExpected one of: " + str(tokens) + "\nGot: " + str(lexeme)
        super().__init__(message)

# Parser class
class Parser:

    # Creating the parser requires a scanner
    def __init__(self, scanner):
        
        self.scanner = scanner

       
        # objects to create virtual registers,
        # labels, and new names
        self.vra = VRAllocator()
        self.nlg = NewLabelGenerator()
        self.nng = NewNameGenerator()


         # Create a symbol table
        self.symbol_table = SymbolTable(self.nng)  # added newnamegenerator object as argument to generate names inside symbol table


        # needed to create the C++ wrapper
        # You do not need to modify these for the
        # homework
        self.function_name = None
        self.function_args = []


    # assigning virtual registers
    def assign_registers(self, node):
        if is_leaf_node(node):
            if node.vr is None:
                node.vr = self.vra.mk_new_vr() # only make new vr if its empty
            return
        elif is_binop_node(node):
            self.assign_registers(node.l_child)
            self.assign_registers(node.r_child)
            node.vr = self.vra.mk_new_vr()
            return
        elif is_unop_node(node):
            node.vr = self.vra.mk_new_vr()
            self.assign_registers(node.child)

    # HOMEWORK: top level function:
    # This needs to return a list of 3 address instructions
    def parse(self, s, unroll_factor):

        # Set the scanner and get the first token
        self.scanner.input_string(s)
        self.to_match = self.scanner.token()
        self.unroll_factor = unroll_factor

        # start parsing. In your solution, p must contain a list of
        # three address instructions
        p = self.parse_function()
        self.eat(None)
        return p

    # Helper fuction: get the token ID
    def get_token_id(self, t):
        if t is None:
            return None
        return t[0]

    # Helper fuction: eat a token ID and advance
    # to the next token
    def eat(self, check):
        token_id = self.get_token_id(self.to_match)
        if token_id != check:
            raise ParserException(self.scanner.get_lineno(),
                                  self.to_match,
                                  [check])      
        self.to_match = self.scanner.token()

    # The top level parse_function
    def parse_function(self):

        # I am parsing the function header for you
        # You do not need to do anything with this.
        self.parse_function_header()    
        self.eat("LBRACE")

        # your solution should have p containing a list
        # of three address instructions
        p = self.parse_statement_list()        
        self.eat("RBRACE")
        return p

    # You do not need to modify this for your homework
    # but you can look :) 
    def parse_function_header(self):
        self.eat("VOID")
        function_name = self.to_match[1]
        self.eat("ID")        
        self.eat("LPAR")
        self.function_name = function_name
        args = self.parse_arg_list()
        self.function_args = args
        self.eat("RPAR")

    # You do not need to modify this for your homework
    # but you can look :) 
    def parse_arg_list(self):
        token_id = self.get_token_id(self.to_match)
        if token_id == "RPAR":
            return
        arg = self.parse_arg()
        token_id = self.get_token_id(self.to_match)
        if token_id == "RPAR":
            return [arg]
        self.eat("COMMA")
        arg_l = self.parse_arg_list()
        return arg_l + [arg]

    # You do not need to modify this for your homework
    # but you can look :) 
    def parse_arg(self):
        token_id = self.get_token_id(self.to_match)
        if token_id == "FLOAT":
            self.eat("FLOAT")
            data_type = Types.FLOAT
            data_type_str = "float"            
        elif token_id == "INT":
            self.eat("INT")
            data_type = Types.INT
            data_type_str = "int"
        else:
            raise ParserException(self.scanner.get_lineno(),
                              self.to_match,            
                              ["INT", "FLOAT"])
        self.eat("AMP")
        id_name = self.to_match[1]
        self.eat("ID")

        # storing an IO variable to the symbol table
        self.symbol_table.insert(id_name, IDTypes.IO, data_type)
        return (id_name, data_type_str)
        
    # The top level parsing function for your homework
    # This function needs to return a list of three address codes
    def parse_statement_list(self):
        token_id = self.get_token_id(self.to_match)
        if token_id in ["INT", "FLOAT", "ID", "IF", "LBRACE", "FOR"]:
            l1 = self.parse_statement() # assigning 3addr code to list
            l2 = self.parse_statement_list()
            return l1+l2 # concatenating lists
        if token_id in ["RBRACE"]:
            return []
        
    # you need to return a list of three address instructions
    # from the statement that gets parsed
    def parse_statement(self):
        token_id = self.get_token_id(self.to_match)
        if token_id in ["INT", "FLOAT"]:
            self.parse_declaration_statement()
            return []# returns empty list
        if token_id in ["ID"]:
            l = self.parse_assignment_statement()
            return l
        if token_id in ["IF"]:
            l = self.parse_if_else_statement()
            return l
        if token_id in ["LBRACE"]:
            l = self.parse_block_statement()
            return l
        if token_id in ["FOR"]:
            l = self.parse_for_statement()
            return l
        
        raise ParserException(self.scanner.get_lineno(),
                            self.to_match,            
                            ["FOR", "IF", "LBRACE", "INT", "FLOAT", "ID"])

    # you need to return a list of three address instructions
    def parse_declaration_statement(self):
        token_id = self.get_token_id(self.to_match)
        if token_id in ["INT"]:
            self.eat("INT")
            id_name = self.to_match[1]
            data_type = Types.INT
            # Think about what you want to insert into the symbol table
            # self.symbol_table.insert(...)
            self.symbol_table.insert(id_name, IDTypes.VAR, data_type)
            self.eat("ID")
            self.eat("SEMI")
            return
        if token_id in ["FLOAT"]:
            self.eat("FLOAT")
            id_name = self.to_match[1]
            data_type = Types.FLOAT
            # Think about what you want to insert into the symbol table
            # self.symbol_table.insert(...)
            self.symbol_table.insert(id_name, IDTypes.VAR, data_type)
            self.eat("ID")
            self.eat("SEMI")
            return
        
        raise ParserException(self.scanner.get_lineno(),
                              self.to_match,            
                              ["INT", "FLOAT"])

    # you need to return a list of three address instructions
    def parse_assignment_statement(self):
        l = self.parse_assignment_statement_base()
        self.eat("SEMI")
        return l

    # you need to return a list of three address instructions
    def parse_assignment_statement_base(self):
        id_name = self.to_match[1]
        id_data = self.symbol_table.lookup(id_name)
        if id_data == None:
            
            raise SymbolTableException(self.scanner.get_lineno(), id_name)
        self.eat("ID")
        self.eat("ASSIGN")

        ast = self.parse_expr()
        
        type_inference(ast)
     
       
        # checks if the assignment variable type is the same as the expression(the ast returned by parse_expr)
        # then changes the type of the AST (expression) depending on the assingment variable type
        if id_data.get_data_type() != ast.node_type:
            if id_data.data_type == Types.FLOAT:
                ast = ASTIntToFloatNode(ast)
            elif id_data.data_type == Types.INT:
                ast = ASTFloatToIntNode(ast)
            else:
                assert(False)

        
        self.assign_registers(ast) 
                       
        program = linearize(ast)
       
        
        

        # if id type is input/output, convert to int/float
        if id_data.get_id_type() == IDTypes.IO: 
            if id_data.get_data_type() == Types.INT:
                op = "vr2int"
            else:
                op = "vr2float"
            new_inst = ["%s = %s(%s);" % (id_name, op, ast.vr)]
        # if id type is program var   
        elif id_data.get_id_type() == IDTypes.VAR:
            new_inst = ["%s = %s;" % (id_data.new_name,ast.vr)]
            
        
        new_inst = program + new_inst
        # returns concatenated list
        return new_inst




        

    # you need to return a list of three address instructions
    def parse_if_else_statement(self):
        self.eat("IF")
        self.eat("LPAR")

        ast = self.parse_expr()
        type_inference(ast)
        self.assign_registers(ast)

        #assigning labels and register for 0
        zero = self.vra.mk_new_vr()
        else_label = self.nlg.mk_new_label()
        end_label = self.nlg.mk_new_label()

        program1 = linearize(ast)

        #converting to classIeR
        line1 = "%s = int2vr(0);" % (zero)
        line2 = "beq(%s,%s,%s);" % (zero, ast.vr, else_label)
        line3 = "branch(%s);" % (end_label)

        self.eat("RPAR")
        program2 = self.parse_statement()
        self.eat("ELSE")
        program3 = self.parse_statement()
        #concatenating lists
        finalProgram = program1 + [line1,line2] + program2 + [line3,else_label + ":"] + program3 + [end_label + ":"]
        return finalProgram
    
    # you need to return a list of three address instructions
    def parse_block_statement(self):
        self.eat("LBRACE")
        self.symbol_table.push_scope()
        program = self.parse_statement_list()
        self.symbol_table.pop_scope()
        self.eat("RBRACE")
        return program

    # you need to return a list of three address instructions
    def parse_for_statement(self):
        self.eat("FOR")
        self.eat("LPAR")
        program = self.parse_assignment_statement()

        if self.unroll_factor is not None:
            inc = self.unroll_factor-1 # if unrollfactor is 2, copy 1 extra time (unrollfactor-1)
      

        ast = self.parse_expr()
        type_inference(ast)
        self.assign_registers(ast)
        program1 = linearize(ast)

        self.eat("SEMI")
        program2 = self.parse_assignment_statement_base()
        
        self.eat("RPAR")
        program3 = self.parse_statement()

        #assigning labels and register for 0
        zero = self.vra.mk_new_vr()
        start_label = self.nlg.mk_new_label()
        end_label = self.nlg.mk_new_label() 
        
        loop_body = program3+program2
        
        if self.unroll_factor is not None:
            while(inc>0):
                loop_body += program3 + program2
                inc = inc - 1
            


        #converting to classIeR
        line1 = "%s = int2vr(0);" % (zero)
        line2 = "beq(%s,%s,%s)" % (zero, ast.vr, end_label)
        line3 = "branch(%s)" % start_label
        #concatenating lists
        finalProgram = program + [start_label+":"]+program1+[line1,line2]+loop_body+[line3,end_label+":"]
        return finalProgram

    # you need to build and return an AST
    def parse_expr(self): 
        node = self.parse_comp()
        return self.parse_expr2(node)
        

    # you need to build and return an AST
    def parse_expr2(self, lhs_node):
        token_id = self.get_token_id(self.to_match)
        if token_id in ["EQ"]:
            self.eat("EQ")
            rhs_node = self.parse_comp()
            node = ASTEqNode(lhs_node, rhs_node)
           
            
            
            
            return self.parse_expr2(node)
        if token_id in ["SEMI", "RPAR"]:
            return  lhs_node
        
        raise ParserException(self.scanner.get_lineno(),
                              self.to_match,            
                              ["EQ", "SEMI", "RPAR"])
    
    # you need to build and return an AST
    def parse_comp(self):
        node = self.parse_factor()
        return self.parse_comp2(node)

    # you need to build and return an AST
    def parse_comp2(self, lhs_node):
        token_id = self.get_token_id(self.to_match)
        if token_id in ["LT"]:
            self.eat("LT")
            rhs_node = self.parse_factor()
            node = ASTLtNode(lhs_node, rhs_node)
            node = self.parse_comp2(node)
            
            return node
        if token_id in ["SEMI", "RPAR", "EQ"]:
            return lhs_node
        
        raise ParserException(self.scanner.get_lineno(),
                              self.to_match,            
                              ["EQ", "SEMI", "RPAR", "LT"])

    # you need to build and return an AST
    def parse_factor(self):
        node = self.parse_term()
        return self.parse_factor2(node)

    # you need to build and return an AST
    def parse_factor2(self, lhs_node):
        token_id = self.get_token_id(self.to_match)
        if token_id in ["PLUS"]:
            self.eat("PLUS")
            rhs_node = self.parse_term()      
            plusnode = ASTPlusNode(lhs_node, rhs_node)      
            node = self.parse_factor2(plusnode)
            return node
        if token_id in ["MINUS"]:
            self.eat("MINUS")
            rhs_node = self.parse_term()      
            minusnode = ASTMinusNode(lhs_node, rhs_node)      
            node = self.parse_factor2(minusnode)
            
           
            
            return node
        if token_id in ["EQ", "SEMI", "RPAR", "LT"]:
            return lhs_node

        raise ParserException(self.scanner.get_linesno(),
                              self.to_match,            
                              ["EQ", "SEMI", "RPAR", "LT", "PLUS", "MINUS"])
    
    # you need to build and return an AST
    def parse_term(self):
        node = self.parse_unit()
        return self.parse_term2(node)
        

    # you need to build and return an AST
    def parse_term2(self, lhs_node):
        token_id = self.get_token_id(self.to_match)
        if token_id in ["DIV"]:
            self.eat("DIV")
            rhs_node = self.parse_unit()
            divnode = ASTDivNode(lhs_node, rhs_node)
            node = self.parse_term2(divnode)
            
            
            
            return node
        if token_id in ["MUL"]:
            self.eat("MUL")
            rhs_node = self.parse_unit()
            multnode = ASTMultNode(lhs_node, rhs_node)
            node = self.parse_term2(multnode)
            
        
            
            return node
        if token_id in ["EQ", "SEMI", "RPAR", "LT", "PLUS", "MINUS"]:
            return lhs_node

        raise ParserException(self.scanner.get_lineno(),
                              self.to_match,            
                              ["EQ", "SEMI", "RPAR", "LT", "PLUS", "MINUS", "MUL", "DIV"])

    # you need to build and return an AST
    def parse_unit(self):
        token_id = self.get_token_id(self.to_match)
        if token_id in ["NUM"]:
            number = self.to_match[1]
            
            self.eat("NUM")   
            num_node = ASTNumNode(number)
            
            return num_node
        if token_id in ["ID"]:
            id_name = self.to_match[1]
            
            id_data = self.symbol_table.lookup(id_name)
            if id_data == None:
                raise SymbolTableException(self.scanner.get_lineno(), id_name)
            self.eat("ID")

            if id_data.id_type == IDTypes.VAR: # if its a program variable
                id_node = ASTVarIDNode(id_data.new_name, id_data.data_type)
                
            elif id_data.id_type == IDTypes.IO: 
                id_node = ASTIOIDNode(id_name, id_data.data_type)
            else:
                assert(False)

            
            return id_node

        if token_id in ["LPAR"]:    
            self.eat("LPAR")
            ast = self.parse_expr()
            type_inference(ast)
            self.eat("RPAR") 
            return ast
            
        raise ParserException(self.scanner.get_lineno(),
                              self.to_match,            
                              ["NUM", "ID", "LPAR"])    



#linearizes ast
def linearize(ast):
    if is_leaf_node(ast):
        return [ast.three_addr_code()]
    elif is_binop_node(ast):
        l1 = linearize(ast.l_child)
        l2 = linearize(ast.r_child)
        return l1+l2+[ast.three_addr_code()]
    elif is_unop_node(ast):
        s = linearize(ast.child)
        return s + [ast.three_addr_code()]
    else:
        assert(False)


# Type inference start

# I suggest making functions like this to check
# what class a node belongs to.
def is_leaf_node(node):
    return issubclass(type(node), ASTLeafNode)

# checks if node is binop
def is_binop_node(node):
    return issubclass(type(node), ASTBinOpNode)

def is_unop_node(node):
    return issubclass(type(node), ASTUnOpNode)

def is_comp_node(node):
    return issubclass(type(node), ASTEqNode) or issubclass(type(node), ASTLtNode)

# Type inference top level
# Type_inference is called whenever parse_expr() returns an AST.
# Performs type inference on the ast. Based on the inference table for the appropriate operation. It infers the parents type depending on 
# the types of its children

def type_inference(node):
    
    if is_leaf_node(node):
        return node.get_type()
    elif is_unop_node(node):
        type_inference(node.child)
        return node.node_type

    elif is_comp_node(node):
        l_type = type_inference(node.l_child)
        r_type = type_inference(node.r_child)
        if (l_type == Types.FLOAT and r_type == Types.INT):
            conv = ASTIntToFloatNode(node.r_child)
            node.r_child = conv
        if (l_type == Types.INT and r_type == Types.FLOAT):
            conv = ASTIntToFloatNode(node.l_child)
            node.l_child = conv 
        return node.node_type

    elif is_binop_node(node):
        #print(node.get_type())
        l_type = type_inference(node.l_child)
        
        r_type = type_inference(node.r_child)

        if l_type== Types.INT and r_type == Types.FLOAT:
            conv = ASTIntToFloatNode(node.l_child)
            node.l_child = conv
        elif l_type == Types.FLOAT and r_type == Types.INT:
            conv = ASTIntToFloatNode(node.r_child)
            node.r_child = conv

        if l_type == Types.FLOAT: # if either of the children are float, the parent node's type is also float (implicit inference table)
            node.set_type(Types.FLOAT)
        if l_type == Types.INT:
            node.set_type(Types.INT) # else set type to int
        
         # converts the childrens type to the parent depending on case
        
        return node.get_type() #returns the type of the binop node
             

# Type conversion
# After the parent node's type has been infered, this fucntion performs the necessary conversions on the children if required

    

    
    # next check if it is a unary op, then a bin op.
    # remember that comparison operators (eq and lt)
    # are handled a bit differently
