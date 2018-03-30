from . import COMMAND
from . import WORD_COMMAND_TYPE_MAPPING
from utils import log_debug


class Parser:
    def __init__(self, input_):
        self.input = input_
        self.command = ''

    def has_more_commands(self):
        if self.input.read(1):
            self.input.seek(-1, 1)
            return True
        else:
            return False

    def advance(self):
        command = self.input.readline().decode('utf-8')
        log_debug("raw command: {!r}".format(command))
        if "//" in command:
            command = command.split("//", 1)[0]
        if command:
            self.command = command.strip()
            if self.command == '':
                self.advance()
        else:
            self.advance()

    def command_type(self):
        log_debug("command: {}".format(self.command))
        first_word = self.command.split()[0]
        try:
            command_type = WORD_COMMAND_TYPE_MAPPING[first_word]
            return command_type
        except KeyError:
            raise Exception("Unexpected command - {}".format(self.command))

    def arg1(self):
        command_type = self.command_type()
        if command_type == COMMAND.C_ARITHMETIC:
            return self.command
        elif command_type == COMMAND.C_RETURN:
            raise Exception("function arg1: Unexpected command - {}".format(self.command))
        else:
            return self.command.split()[1]

    def arg2(self):
        command_type = self.command_type()
        allow_commands = (COMMAND.C_PUSH, COMMAND.C_POP, COMMAND.C_FUNCTION, COMMAND.C_CALL)
        if command_type in allow_commands:
            return self.command.split()[2]
        else:
            raise Exception("function arg2: Unexpected command - {}".format(self.command))
