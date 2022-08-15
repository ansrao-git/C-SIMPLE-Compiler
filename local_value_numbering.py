import re


global_counter = 0

# MIGHT HAVE TO REMOVE WHITESPACE BEFORE REGEX

def is_label(s):
    s.strip() # removes whitespace
    return ":" in s

def is_instr(s):
    s.strip() # removes whitespace
    return not is_label(s)
def is_assign_statement(s):# eg. vr1 = vr0 or _new_name = vr0
    #return re.match("(^(vr\S+)|^(_new_name\S+))=(([a-zA-z0-9;]+)$)",s)!=None
    return re.match("(\S+)=(\S+)",s)
    
def is_one_arg_instr(s):
    s.strip() # removes whitespace
    return re.match("(\S+)=(int2vr|float2vr|vr_int2float|vr_float2int|vr2int|vr2float)\((\S+)\)",s) != None
            
def is_two_arg_instr(s):
    s.strip() # removes whitespace
    return re.match("(\S+)=(\S+)\((\S+),(\S+)\)",s) != None
                
                
def is_three_arg_branch(s):
    s.strip() # removes whitespace
    return re.match("(\S+)\((\S+),(\S+),(\S+)\)", s) !=None
def is_one_arg_branch(s):
    s.strip() # removes whitespace
    return re.match("^(branch)\((\S+)\)",s) != None
def is_comm(s):
    return re.match("^(mult)|^(div)",s) != None

def is_program_var(s):
    s.strip()
    return re.match("^(vr)|^(_new_name)", s) != None

def stitch_blocks(block_list):
    prog = []
   
    for block in block_list:
        
        block.append("")
        prog = prog + block
    return prog
            
def split_bb(program):
    basic_blocks = []
    bb = []
    count = 0
    for i in program:
       # print(bb)
        
        rep = i.replace(" ","")
        if is_label(rep):
            if bb:    # if bb is not empty
                basic_blocks.append(bb)
                bb = []
                bb.append(rep) # adds label or 3 arg brach to next basic block
            else:
                bb.append(rep)        
            
        elif is_one_arg_branch(rep) or is_three_arg_branch(rep):
           # print (rep)
            bb.append(rep) # if its a 1 arg branch. Add to the same basic block instead of the next one
            basic_blocks.append(bb)
           
            bb = []
        else:
            bb.append(rep)
    if bb: #if label is last line, append to block list
        basic_blocks.append(bb)

   
    
    return basic_blocks
    

def numbering(block):
    global global_counter
    
    seen_vars = {}
    varDict = {}
    patchTop=[]
    patchBot=[]
    
    for idx, instr in enumerate(block):
        
        instr = instr.replace(" ","")
        #print(instr)
        if is_assign_statement(instr):
            
            if not is_two_arg_instr(instr) and not is_one_arg_instr(instr):
                
                match_obj = re.match("(\S+)=(\S+);",instr)
                assign = match_obj.group(1)
                arg1 = match_obj.group(2)
                if(arg1 not in seen_vars and is_program_var(arg1)):
                    seen_vars[arg1] = arg1+"_"+str(global_counter)
                    patchTop.append("%s=%s;"%(seen_vars[arg1],arg1))# if new var, assign it to origingal name

                    block[idx] = block[idx].replace(arg1,seen_vars[arg1])#add counter to var name    
                    global_counter+=1
                elif(arg1 in seen_vars and is_program_var(arg1)):
                    block[idx] = block[idx].replace(arg1,seen_vars[arg1])
                if is_program_var(assign):
                    if assign in seen_vars :
                        varDict[assign] = (seen_vars[assign])
                    seen_vars[assign] = assign+"_"+str(global_counter)               
                    block[idx] = block[idx].replace(assign,seen_vars[assign])         
                    global_counter+=1

                
        if is_two_arg_instr(instr):
           # print(block[idx])
            match_obj = re.match("(\S+)=(\S+)\((\S+),(\S+)\)",instr)
            assign = match_obj.group(1)
            arg1 = match_obj.group(3)
            arg2 = match_obj.group(4)
            if(arg1 not in seen_vars and is_program_var(arg1)): # first encounter of a var
                
                seen_vars[arg1] = arg1+"_"+str(global_counter)
                patchTop.append("%s=%s;"%(seen_vars[arg1],arg1))# if new var, assign it to origingal name

                block[idx] = block[idx].replace(arg1,seen_vars[arg1])#add counter to var name
                #print(block[idx])
                global_counter+=1
            elif(arg1 in seen_vars and is_program_var(arg1)): # if seen the var before, use latest name
                block[idx] = block[idx].replace(arg1,seen_vars[arg1])#add counter from seen_vars to var name

            if(arg2 not in seen_vars and is_program_var(arg2)):
                seen_vars[arg2] = arg2+"_"+str(global_counter)
                patchTop.append("%s=%s;"%(seen_vars[arg2],arg2))# if new var, assign it to origingal name

                block[idx] = block[idx].replace(arg2,seen_vars[arg2])#add counter to var name
                
                global_counter+=1
            elif(arg2 in seen_vars and is_program_var(arg2)):
                block[idx] = block[idx].replace(arg2,seen_vars[arg2])#add counter from seen_vars to var name
            if is_program_var(assign):# adds counter to assignment var. Everytime
                if assign in seen_vars :
                    varDict[assign] = (seen_vars[assign])
                seen_vars[assign] = assign+"_"+str(global_counter)
                #print (seen_vars[assign])
                block[idx] = block[idx].replace(assign,seen_vars[assign])
               # print(block[idx])
                global_counter+=1
                
        elif is_one_arg_instr(instr):
            match_obj = re.match("(\S+)=(\S+)\((\S+)\)", instr)
            
            assign = match_obj.group(1)
            #print(assign)
            arg1 = match_obj.group(3)
            
            if(arg1 not in seen_vars and is_program_var(arg1)):# first encounter of a var
                seen_vars[arg1] = arg1+"_"+str(global_counter)
                patchTop.append("%s=%s;"%(seen_vars[arg1],arg1))# if new var, assign it to origingal name
                block[idx] = block[idx].replace(arg1,seen_vars[arg1])
                global_counter+=1
            elif arg1 in seen_vars and is_program_var(arg1):# use latest name if exists
                
                block[idx] = "%s = %s(%s);"%(match_obj.group(1),match_obj.group(2),seen_vars[arg1])
                #block[idx] = block[idx].replace(arg1,seen_vars[arg1])
            if is_program_var(assign):
                if assign in seen_vars :
                    varDict[assign] = (seen_vars[assign])
                seen_vars[assign] = assign+"_"+str(global_counter)
                block[idx] = block[idx].replace(assign,seen_vars[assign])
                global_counter+=1

        elif is_three_arg_branch(instr):
            match_obj = re.match("(\S+)\((\S+),(\S+),(\S+)\)", instr)
            arg1 = match_obj.group(2)
            arg2 = match_obj.group(3)
            arg3 = match_obj.group(4)
            if(arg1 not in seen_vars and is_program_var(arg1)):
                seen_vars[arg1] = arg1+"_"+str(global_counter)
                patchTop.append("%s=%s;"%(seen_vars[arg1],arg1))# if new var, assign it to origingal name
                block[idx] = block[idx].replace(arg1,seen_vars[arg1])#add counter to var name
                global_counter+=1

            elif(arg1 in seen_vars and is_program_var(arg1)):
                block[idx] = block[idx].replace(arg1,seen_vars[arg1]) 

            if(arg2 not in seen_vars and is_program_var(arg2)):
                seen_vars[arg2] = arg2+"_"+str(global_counter)
                patchTop.append("%s=%s;"%(seen_vars[arg2],arg2))# if new var, assign it to origingal name
                block[idx] = block[idx].replace(arg2,seen_vars[arg2])#add counter to var name
                global_counter+=1

            elif(arg2 in seen_vars and is_program_var(arg2)):
                block[idx] = block[idx].replace(arg2,seen_vars[arg2])

            if(arg3 not in seen_vars and is_program_var(arg3)):
                seen_vars[arg3] = arg3+"_"+str(global_counter)
                patchTop.append("%s=%s;"%(seen_vars[arg3],arg3))# if new var, assign it to origingal name
                block[idx] = block[idx].replace(arg3,seen_vars[arg3])#add counter to var name
                global_counter+=1

            elif(arg3 in seen_vars and is_program_var(arg3)):
                block[idx] = block[idx].replace(arg3,seen_vars[arg3])
        
    
   # for s in patchTop:
        #print(s)

    
    returnList = list(seen_vars.values())
    values = list(varDict.values())
    returnList = returnList+values


    
    
    for key in seen_vars.keys():
        patchBot.append("%s=%s;"%(key,seen_vars[key]))

   
    new_block = add_patchTop(block,patchTop)
    new_block = add_patchBot(new_block,patchBot)

             
    
               

   # for idx, instr in enumerate(block):#patchbot
       
    #block = patchTop+block+patchBot
    
    
    return new_block,returnList
            

        
def add_patchTop(block,patchTop):
    new_block = []
    if(is_label(block[0])): 
        new_block.append(block[0])
        
        block.remove(block[0])
        
        for i in patchTop:
            new_block.append(i)  
         
        new_block = new_block+block        
        return new_block     
    elif not is_label(block[0]):
        new_block = patchTop+block
        return new_block

def add_patchBot(block, patchBot):
    if(is_one_arg_branch(block[-1])or is_three_arg_branch(block[-1])):
        br_instr = block[-1]
        block.remove(block[-1])
        block = block+patchBot
        block.append(br_instr)
    else:
        block = block+patchBot
    return block

def optimize(block):
    var_dict = {}
    count = 0
    for idx, instr in enumerate(block):
        if is_one_arg_instr(instr):
            line = re.match("(\S+)=(int2vr|float2vr|vr_int2float|vr_float2int|vr2int|vr2float)\((\S+)\)",instr)
            left = line.group(1)
            right = line.group(2)+line.group(3)
            
            if right in var_dict.keys():
                block[idx] = ("%s=%s;"%(left,var_dict[right]))
                count+=1
                
        if is_two_arg_instr(instr):
            line = re.match("(\S+)=(\S+)\((\S+),(\S+)\)",instr)
            left = line.group(1)
            right = line.group(2)+line.group(3)+line.group(4)
            if(is_comm(line.group(2))):
                sort_list = [line.group(3),line.group(4)]
                sort_list = sorted(sort_list)
                arg1 = sort_list[0]
                arg2 = sort_list[1]
                block[idx] = ("%s=%s(%s,%s);"%left,line.group(2),arg1,arg2)
                line = re.match("(\S+)=(\S+)\((\S+),(\S+)\)",instr)
                right = line.group(2)+line.group(3)
            if right in var_dict.keys():
                block[idx] = ("%s=%s;"%(left,var_dict[right]))
                count+=1
            var_dict[right] = left
    
    return block,count

# perform the local value numbering optimization
def LVN(program):
    full_count = 0
    global global_counter
    

    block_list = split_bb(program) # splits into basic blocks
    
    returnList = []
    for idx, block in enumerate(block_list):
        global_counter = 0
        block_list[idx],varList = numbering(block)
        
        returnList+=varList
        returnList = list(set(returnList))
    
    for idx, block in enumerate(block_list):
       block_list[idx],count = optimize(block)
       full_count+=count 
    program = stitch_blocks(block_list)
    

    # returns 3 items:
    
    # 1. a new program (list of classier instructions)
    # with the LVN optimization applied

    # 2. a list of new variables required (e.g. numbered virtual
    # registers and program variables)

    # 3. a number with how many instructions were replaced    
    return program,returnList,full_count
