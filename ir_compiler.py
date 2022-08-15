import local_value_numbering

class IRCompiler():
    def __init__(self, p):
        self.parser = p

    def print_program(self,program,lvn_new_variables,lvn_replaced):
        args = ["%s &%s" % (a[1], a[0]) for a in self.parser.function_args]
        arg_string = ",".join(reversed(args))
        program_str = "\n".join(program)
        vrs = self.parser.vra.declare_variables()
        vrs_str = "\n".join(vrs)
        new_names = "\n".join(["virtual_reg %s;" % n for n in self.parser.nng.new_names])
        lvn_names = "\n".join(["virtual_reg %s;" % n for n in lvn_new_variables])
        return """
// LVN replaced %s arithmetic instructions
#include "../../classir.h"
void %s(%s){
%s
%s
%s
%s
return;
}
        """ % (str(lvn_replaced), self.parser.function_name, arg_string, vrs_str, new_names, lvn_names, program_str)
        

    def compile2ir(self, s, lvn, uf):
        program = self.parser.parse(s,uf)
        program = [p for p in program if p != '']
        if lvn:
            program,lvn_new_names,lvn_replaced = local_value_numbering.LVN(program)
        else:
            lvn_new_names = []
            lvn_replaced = 0
        self.ir_program = self.print_program(program,lvn_new_names,lvn_replaced)
