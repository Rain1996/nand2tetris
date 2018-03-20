import sys
from utils import log, log_debug
from assembler.assembler import Assembler


if __name__ == '__main__':
    log_debug("sys.argv - {}".format(sys.argv))
    if len(sys.argv) == 2:
        file_name = sys.argv[1]
        assembler = Assembler(file_name)
        assembler.parse_asm_program()
        assembler.write_output_to_hack_file()
    else:
        log("usage: ")
        log("    python assembler.py <asm_file>")
        log("example: ")
        log("    python assembler.py prog.asm")
