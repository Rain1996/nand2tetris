from . import Command
# from utils import log_debug


class Parser:
    def __init__(self, input):
        self.input = input
        self.command = ''

    def reset(self):
        """
        @description: 由于需要两次读取，所以提供重置文件读取指针到开头
        """
        self.input.seek(0, 0)
        self.command = ''

    def has_more_commands(self):
        if self.input.read(1):
            self.input.seek(-1, 1)
            return True
        else:
            return False

    def advance(self):
        command = self.input.readline().decode('utf-8')
        # log_debug("raw command: {!r}".format(command))
        if "//" in command:
            command = command.split("//", 1)[0]
        if command:
            self.command = "".join(command.split())
            if self.command == '':
                self.advance()
        else:
            self.advance()

    def _check_symbol(self, symbol):
        """
        @description:
            检查该符号是否符合A_COMMAND的要求的格式
            格式要求为:
                1.常数必须是非负的，用十进制标识
                2.用户自定义的符号可以由字母，数字，下划线，点，美元符号合冒号组成，且不能以数字开头
        @parameter:
            symbol - 需检查的符号
        @return:
            符合返回True, 否则False
        """
        allowed_symbol = ('_', '.', '$', ':')
        if symbol.isdigit():
            return True
        elif symbol[0].isdigit():
            return False
        return all(ch.isalnum() or ch in allowed_symbol for ch in symbol)

    def command_type(self):
        # log_debug("command_type - command: {}".format(self.command))
        first_ch = self.command[0]
        rest = self.command[1:]
        last_ch = self.command[-1]
        if first_ch == '@' and self._check_symbol(rest):
            return Command.A_COMMAND
        elif first_ch == '(' and last_ch == ')':
            return Command.L_COMMAND
        else:
            return Command.C_COMMAND

    def symbol(self):
        # log_debug("symbol - command: {}".format(self.command))
        if self.command[0] == '@':
            return self.command[1:]
        elif self.command[0] == '(' and self.command[-1] == ')':
            return self.command[1:-1]
        else:
            raise Exception("Unexpected command - {}".format(self.command))

    def dest(self):
        if '=' in self.command:
            return self.command.split('=', 1)[0]
        return 'null'

    def comp(self):
        c = self.command
        if '=' in c:
            c = c.split('=', 1)[1]

        if ';' in c:
            c = c.split(';', 1)[0]

        return c

    def jump(self):
        if ';' in self.command:
            return self.command.split(';', 1)[1]
        return 'null'

    def parse_c_command(self):
        """
        @description: 解析 C_COMMAND, 返回 dest, comp以及jump的tuple
        """
        dest_str, comp_str, jump_str = 'null', '', 'null'
        c = self.command

        if '=' in c:
            c_split_list = c.split('=', 1)
            dest_str = c_split_list[0]
            comp_str = c = c_split_list[1]
        if ';' in c:
            split_list = c.split(';', 1)
            comp_str = split_list[0]
            jump_str = split_list[1]

        return dest_str, comp_str, jump_str
