from . import Command
from .code import Code
from .parser import Parser
from utils import log_debug


class Assembler:
    def __init__(self, file_name):
        self.file_name = file_name
        self.input = open(self.file_name, 'rb')
        self.parser = Parser(self.input)
        self.code = Code()
        self.output = []

    def output_filename(self):
        if self.file_name.endswith(".asm"):
            filename = self.file_name.replace(".asm", ".hack")
        else:
            filename = self.file_name + ".hack"
        return filename

    def parse_asm_program(self):
        parser = self.parser
        while parser.has_more_commands():
            line = ''
            parser.advance()
            command_type = parser.command_type()
            if command_type == Command.A_COMMAND:
                symbol = parser.symbol()
                log_debug("A_COMMAND, symbol - {}".format(symbol))

                line = "0{:015b}\n".format(int(symbol))
            elif command_type == Command.L_COMMAND:
                symbol = parser.symbol()
                log_debug("L_COMMAND, symbol - {}".format(symbol))
            elif command_type == Command.C_COMMAND:
                # dest_str = parser.dest()
                # comp_str = parser.comp()
                # jump_str = parser.jump()
                dest_str, comp_str, jump_str = parser.parse_c_command()
                log_debug("C_COMMAND, dest - {!r}, comp - {!r}, jump - {!r}".format(dest_str, comp_str, jump_str))

                dest = self.code.dest(dest_str)
                comp = self.code.comp(comp_str)
                jump = self.code.jump(jump_str)

                line = '111{:07b}{:03b}{:03b}\n'.format(comp, dest, jump)
            else:
                raise Exception("Unexpected command - {}".format(command_type))

            log_debug("line - {}".format(line))
            self.output.append(line)

    def write_output_to_hack_file(self):
        output_hack_filename = self.output_filename()
        with open(output_hack_filename, 'w') as file:
            file.writelines(self.output)
