import pdb
from enum import Enum

# HOMEWORK: For each AST node you will need
# to write a "three_addr_code" function which
# writes the three address code instruction
# for each node.

# HOMEWORK: For each AST node you should also
# write a "linearize" function which provides
# a list of 3 address instructions for the node
# and its descendants.

# Hint: you may want to utilize the class hierarchy
# to avoid redundant code.

# enum for data types in ClassIeR
class Types(Enum):
    INT = 1
    FLOAT = 2

# base class for an AST node. Each node
# has a type and a VR
class ASTNode():
    def __init__(self):
        self.node_type = None
        self.vr = None
    def set_type(self, t):
        self.node_type = t
    def get_type(self):
        return self.node_type

# AST leaf nodes
class ASTLeafNode(ASTNode):
    def __init__(self, value):
        self.value = value
        super().__init__()

######
# A number leaf node

# The value passed in should be a number
# (probably as a string).

# HOMEWORK: Determine if the number is a float
# or int and set the type
######
class ASTNumNode(ASTLeafNode):
    def __init__(self, value):        
        super().__init__(value)
        if self.is_int(value):
            self.set_type(Types.INT)
        else:
            self.set_type(Types.FLOAT)

    def is_int(self, numstring):
        if "." in numstring:
            return False
        else: 
            return True 
    # converts to 3address code. 
    # converts int and float to virtual registers
    def three_addr_code(self):
        if self.get_type() == Types.FLOAT:
            return "%s = float2vr(%s);" % (self.vr, self.value)
        if self.get_type() == Types.INT:
            return "%s = int2vr(%s);" % (self.vr, self.value)

######
# A program variable leaf node

# The value passed in should be an id name
# eventually it should be the new name generated
# by the symbol table to handle scopes.

# When you create this node, you will also need
# to provide its data type
######
class ASTVarIDNode(ASTLeafNode):
    def __init__(self, value, value_type):
        super().__init__(value)
        self.node_type = value_type
        self.vr = self.value
    #no conversion needed.
    #sets virtual register to value 
    def three_addr_code(self):
        return  ""  # was "%s = %s;" % (self.vr, self.value)
                    # now returns empty string

######
# An IO leaf node

# The value passed in should be an id name.
# Because it is an IO node, you do not need
# to get a new name for it.

# When you create this node, you will also need
# to provide its data type. It is recorded in
# the symbol table
######
class ASTIOIDNode(ASTLeafNode):
    def __init__(self, value, value_type):
        super().__init__(value)
        self.node_type = value_type
    def three_addr_code(self):
        if self.get_type() == Types.FLOAT:
            return "%s = float2vr(%s);" % (self.vr, self.value)
        if self.get_type() == Types.INT:
            return "%s = int2vr(%s);" % (self.vr, self.value)



######
# Binary operation AST Nodes

# These nodes require their left and right children to be
# provided on creation
######
class ASTBinOpNode(ASTNode):
    def __init__(self, l_child, r_child):
        self.l_child = l_child
        self.r_child = r_child
        super().__init__()
    def three_addr_code(self):
       
        return "%s = %s(%s,%s);" % (self.vr, self.get_op(), self.l_child.vr, self.r_child.vr)

class ASTPlusNode(ASTBinOpNode):
    def __init__(self, l_child, r_child):
        super().__init__(l_child,r_child)
    def get_op(self):
        if self.node_type == Types.FLOAT:
            return "addf"
        elif self.node_type == Types.INT:
            return "addi"

class ASTMultNode(ASTBinOpNode):
    def __init__(self, l_child, r_child):
        super().__init__(l_child,r_child)
    def get_op(self):
        if self.node_type == Types.FLOAT:
            return "multf"
        elif self.node_type == Types.INT:
            return "multi"
    

class ASTMinusNode(ASTBinOpNode):
    def __init__(self, l_child, r_child):
        super().__init__(l_child,r_child)
    def get_op(self):
        if self.node_type == Types.FLOAT:
            return "subf"
        elif self.node_type == Types.INT:
            return "subi"

class ASTDivNode(ASTBinOpNode):
    def __init__(self, l_child, r_child):
        super().__init__(l_child,r_child)
    def get_op(self):
        if self.node_type == Types.FLOAT:
            return "divf"
        elif self.node_type == Types.INT:
            return "divi"

######
# Special BinOp nodes for comparisons

# These operations always return an int value
# (as an untyped register):
# 0 for false and 1 for true.

# Because of this, their node type is always
# an int. However, the operations (eq and lt)
# still need to be typed depending
# on their inputs. If their children are floats
# then you need to use eqf, ltf, etc.
######
class ASTEqNode(ASTBinOpNode):
    def __init__(self, l_child, r_child):
        self.node_type = Types.INT
        super().__init__(l_child,r_child)
    def get_op(self):
        if self.node_type == Types.FLOAT:
            return "eqf"
        elif self.node_type == Types.INT:
            return "eqi"

class ASTLtNode(ASTBinOpNode):
    def __init__(self, l_child, r_child):
        self.node_type = Types.INT
        super().__init__(l_child,r_child)
    def get_op(self):
        if self.l_child.get_type() == Types.FLOAT:
            return "ltf"
        elif self.l_child.get_type() == Types.INT:
            return "lti"

######
# Unary operation AST Nodes

# The only operations here are converting
# the bits in a virtual register to another
# virtual register of a different type,
# i.e. corresponding to the CLASSIeR instructions:
# vr_int2float and vr_float2int
######
class ASTUnOpNode(ASTNode):
    def __init__(self, child):
        self.child = child
        super().__init__()

    def three_addr_code(self):
        return "%s = %s(%s);" % (self.vr, self.get_op(), self.child.vr)
        
 # added get_op() to both converters. To get the correct classIeR function name for the operation       
class ASTIntToFloatNode(ASTUnOpNode):
    def __init__(self, child):
        self.set_type(Types.FLOAT) # setting type because its known
        assert(child.get_type() == Types.INT)
        super().__init__(child)

    def get_op(self):
        return "vr_int2float"

class ASTFloatToIntNode(ASTUnOpNode):
    def __init__(self, child):
        self.set_type(Types.INT)# setting type because its known
        assert(child.get_type() == Types.FLOAT)
        super().__init__(child)
    
    def get_op(self):
        return "vr_float2int"
