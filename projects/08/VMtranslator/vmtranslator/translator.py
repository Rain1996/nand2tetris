import os.path
from . import COMMAND
from .parser import Parser
from utils import log_debug
from functools import partialmethod


class Translator:
    def __init__(self, code_writer):
        self.code_writer = code_writer
        self.parser = None
        self.__command_translate_methods = [
            self._translate_unexpected_command,
            self._translate_arithmetic,
            self._translate_push,
            self._translate_pop,
            self._translate_label,
            self._translate_goto,
            self._translate_function,
            self._translate_if,
            self._translate_return,
            self._translate_call,
        ]

    def _translate_unexpected_command(self, command_type):
        raise Exception("Unexpected command - {}".format(command_type))

    def _translate_arithmetic(self):
        command = self.parser.arg1()
        self.code_writer.write_arithmetic(command)

    def _translate_push_or_pop(self, command_type):
        segment, index = self.parser.arg1(), self.parser.arg2()
        self.code_writer.write_push_or_pop(command_type, segment, index)

    _translate_push = partialmethod(_translate_push_or_pop, COMMAND.C_PUSH)
    _translate_pop = partialmethod(_translate_push_or_pop, COMMAND.C_POP)

    def _translate_label(self):
        label = self.parser.arg1()
        self.code_writer.write_label(label)

    def _translate_goto(self):
        label = self.parser.arg1()
        self.code_writer.write_goto(label)

    def _translate_function(self):
        func_name = self.parser.arg1()
        n = int(self.parser.arg2())
        self.code_writer.write_function(func_name, n)

    def _translate_if(self):
        label = self.parser.arg1()
        self.code_writer.write_if(label)

    def _translate_return(self):
        self.code_writer.write_return()

    def _translate_call(self):
        func_name = self.parser.arg1()
        n = int(self.parser.arg2())
        self.code_writer.write_call(func_name, n)

    def _translator_update(self, filename):
        log_debug("filename - {}".format(filename))
        input_ = open(filename, 'rb')
        self.parser = Parser(input_)

        base_name = os.path.basename(filename[:-3])  # \c\xxx.vm -> xxx or /c/c/xxx.vm -> xxx
        self.code_writer.set_filename(base_name)

    def translate(self, filename):
        self._translator_update(filename)

        parser = self.parser

        while parser.has_more_commands():
            parser.advance()
            command_type = parser.command_type()
            if command_type == 0 or command_type >= len(self.__command_translate_methods):
                self._translate_unexpected_command(command_type)
            else:
                translate_func = self.__command_translate_methods[command_type]
                translate_func()
