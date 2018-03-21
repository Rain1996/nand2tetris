from . import Command
from .code import Code
from .parser import Parser
from .symbol_table import SymbolTable
# from utils import log_debug
from utils import log_info


class Assembler:
    def __init__(self, file_name):
        self.file_name = file_name
        self.input = open(self.file_name, 'rb')
        self.parser = Parser(self.input)
        self.code = Code()
        self._symbol_table = SymbolTable()
        self.output = []
        self._RAM_address = 16          # init RAM address

    def _output_filename(self):
        """
        @description: 返回输出的文件名
        """
        if self.file_name.endswith(".asm"):
            filename = self.file_name.replace(".asm", ".hack")
        else:
            filename = self.file_name + ".hack"
        return filename

    def _parse_address(self, symbol):
        """
        @description: 返回符号对应的地址
        """
        if symbol.isdigit():
            address = int(symbol)
        elif self._symbol_table.contains(symbol):
            address = self._symbol_table.get_address(symbol)
        else:
            address = self._RAM_address
            self._symbol_table.add_entry(symbol, address)
            self._RAM_address += 1
        return address

    def _first_parse(self):
        log_info('first_parse begin')
        parser = self.parser
        instruction = 0
        while parser.has_more_commands():
            # log_debug("instruction - {}".format(instruction))
            parser.advance()
            command_type = parser.command_type()
            if command_type in (Command.A_COMMAND, Command.C_COMMAND):
                instruction += 1
            elif command_type == Command.L_COMMAND:
                symbol = parser.symbol()
                # log_debug("L_COMMAND, symbol - {}".format(symbol))

                if not symbol.isdigit():
                    self._symbol_table.add_entry(symbol, instruction)
            else:
                raise Exception("Unexpected command - {}".format(command_type))

        # log_debug("symbol_table - {}".format(self._symbol_table))
        log_info('first_parse end')

    def _second_parse(self):
        log_info('second_parse begin')
        parser = self.parser
        while parser.has_more_commands():
            line = ''
            parser.advance()
            command_type = parser.command_type()
            if command_type == Command.A_COMMAND:
                symbol = parser.symbol()
                # log_debug("A_COMMAND, symbol - {}".format(symbol))

                address = self._parse_address(symbol)
                line = "0{:015b}\n".format(address)
            elif command_type == Command.L_COMMAND:
                symbol = parser.symbol()
                # log_debug("L_COMMAND, symbol - {}".format(symbol))
            elif command_type == Command.C_COMMAND:
                # dest_str = parser.dest()
                # comp_str = parser.comp()
                # jump_str = parser.jump()
                dest_str, comp_str, jump_str = parser.parse_c_command()
                # log_debug("C_COMMAND, dest - {!r}, comp - {!r}, jump - {!r}".format(dest_str, comp_str, jump_str))

                dest = self.code.dest(dest_str)
                comp = self.code.comp(comp_str)
                jump = self.code.jump(jump_str)

                line = '111{:07b}{:03b}{:03b}\n'.format(comp, dest, jump)
            else:
                raise Exception("Unexpected command - {}".format(command_type))

            # log_debug("line - {}".format(line))
            if line != '':
                self.output.append(line)
        log_info('second_parse end')
        # log_debug("symbol_table - {}".format(self._symbol_table))

    def parse_asm_program(self):
        self._first_parse()
        self.parser.reset()
        self._second_parse()

    def write_output_to_hack_file(self):
        output_hack_filename = self._output_filename()
        with open(output_hack_filename, 'w') as file:
            file.writelines(self.output)
