from . import COMMAND
from . import SEGMENT_REGISTER_MAPPING
from . import SEGMENT_BASE_ADDR_MAPPING
from utils import log_debug


class CodeWriter:
    def __init__(self, output_file):
        self.output = open(output_file, 'w')
        self.__vm_filename = ''
        self.__increase_num = 0

    def _write_lines(self, lines):
        self.output.writelines(lines)

    def _write_line(self, line="\n"):
        self.output.write(line)

    def write_end(self):
        # 写入标准结尾
        lines = [
            "(END)\n",
            "@END\n",
            "0; JMP\n",
        ]
        self._write_lines(lines)

    def _write_increase_sp(self):
        # SP 自增1
        lines = [
            "@SP\n",
            "M=M+1\n",
        ]
        self._write_lines(lines)

    def _write_push(self):
        lines = [
            "@SP\n",
            "A=M\n",
            "M=D\n",
        ]
        self._write_lines(lines)
        self._write_increase_sp()

    def _write_pop(self):
        # pop 只需要 SP 自减1
        lines = [
            "@SP\n",
            "M=M-1\n",
            "A=M\n",
        ]
        self._write_lines(lines)

    def _write_boolean(self):
        # 通过跳转的方法写入布尔值
        lines = [
            "(TRUE_{})\n".format(self.__increase_num),
            "D=-1\n",
            "@POP_{}\n".format(self.__increase_num),
            "0;JMP\n",
            "\n"
            "(FALSE_{})\n".format(self.__increase_num),
            "D=0\n",
            "@POP_{}\n".format(self.__increase_num),
            "0;JMP\n",
            "\n",
            "(POP_{})\n".format(self.__increase_num),
        ]
        self._write_lines(lines)
        self._write_push()

        self.__increase_num += 1

    def _handle_arithmetic_or_logic(self, line):
        # 处理算术和逻辑运算的抽象方法
        self._write_pop()
        self._write_line("D=M\n")
        self._write_pop()

        self._write_line(line)
        self._write_increase_sp()

    def _handle_add(self):
        self._handle_arithmetic_or_logic("M=D+M\n")

    def _handle_sub(self):
        self._handle_arithmetic_or_logic("M=M-D\n")

    def _handle_and(self):
        self._handle_arithmetic_or_logic("M=D&M\n")

    def _handle_or(self):
        self._handle_arithmetic_or_logic("M=D|M\n")

    def _handle_comparison(self, comparison):
        # 处理比较运算的抽象方法
        self._write_pop()
        self._write_line("D=M\n")
        self._write_pop()

        lines = [
            "D=M-D\n",
            "\n"
            "@TRUE_{}\n".format(self.__increase_num),
            "D;{}\n".format(comparison),
            "@FALSE_{}\n".format(self.__increase_num),
            "0;JMP\n",
            "\n",
        ]
        self._write_lines(lines)
        self._write_boolean()

    def _handle_eq(self):
        self._handle_comparison("JEQ")

    def _handle_gt(self):
        self._handle_comparison("JGT")

    def _handle_lt(self):
        self._handle_comparison("JLT")

    def _handle_unary_command(self, line):
        # 处理一元命令的抽象方法
        self._write_pop()
        self._write_line(line)
        self._write_increase_sp()

    def _handle_neg(self):
        self._handle_unary_command("M=-M\n")

    def _handle_not(self):
        self._handle_unary_command("M=!M\n")

    def _save_static_value_to_d_register(self, index):
        # 将static段对应的值存入D存储器
        lines = [
            "@{}.{}\n".format(self.__vm_filename, index),
            "D=M\n",
        ]
        self._write_lines(lines)

    def _save_value_to_d_register(self, segment, index):
        # 通过index, 拿到对应段的值，存储到D寄存器
        lines = [
            "@{}\n".format(index),
            "D=A\n",
        ]

        if segment != 'constant':
            if segment in SEGMENT_REGISTER_MAPPING:
                register = SEGMENT_REGISTER_MAPPING[segment]
                lines += [
                    "@{}\n".format(register),
                    "A=D+M\n",
                ]
            elif segment in SEGMENT_BASE_ADDR_MAPPING:
                base_addr = SEGMENT_BASE_ADDR_MAPPING[segment]
                lines += [
                    "@{}\n".format(base_addr),
                    "A=D+A\n",
                ]
            else:
                raise Exception("Unexpected segment - {}".format(segment))
            lines.append("D=M\n")

        self._write_lines(lines)

    def _handle_push(self, segment, index):
        # 处理 push 命令
        if segment == 'static':
            self._save_static_value_to_d_register(index)
        else:
            self._save_value_to_d_register(segment, index)
        self._write_push()

    def _save_ram_addr_to_temp(self, segment, index):
        # 通过index, 拿到对应段的地址，存储到TEMP中
        lines = [
            "@{}\n".format(index),
            "D=A\n",
        ]

        if segment in SEGMENT_REGISTER_MAPPING:
            register = SEGMENT_REGISTER_MAPPING[segment]
            lines += [
                "@{}\n".format(register),
                "D=D+M\n",
            ]
        elif segment in SEGMENT_BASE_ADDR_MAPPING:
            base_addr = SEGMENT_BASE_ADDR_MAPPING[segment]
            lines += [
                "@{}\n".format(base_addr),
                "D=D+A\n",
            ]
        else:
            raise Exception("Unexpected segment - {}".format(segment))

        lines.append("@TEMP\n")
        lines.append("M=D\n")

        self._write_lines(lines)

    def _save_value_to_ram(self):
        # 把 退栈得到的值 存储到 TEMP中存储的地址对应的RAM中
        lines = [
            "D=M\n",
            "@TEMP\n",
            "A=M\n",
            "M=D\n",
        ]
        self._write_lines(lines)

    def _save_value_to_static(self, index):
        lines = [
            "D=M\n",
            "@{}.{}\n".format(self.__vm_filename, index),
            "M=D\n",
        ]
        self._write_lines(lines)

    def _handle_pop(self, segment, index):
        # 处理 pop 命令
        if segment != 'static':
            self._save_ram_addr_to_temp(segment, index)
            self._write_pop()
            self._save_value_to_ram()
        else:
            self._write_pop()
            self._save_value_to_static(index)

    # 告知CodeWriter当前处理文件是什么，为了方便处理static段
    def set_filename(self, filename):
        self.__vm_filename = filename

    def write_arithmetic(self, command):
        log_debug("command - {}".format(command))

        handle_func = getattr(self, "_handle_{}".format(command))
        handle_func()

        self._write_line()

    def write_push_or_pop(self, command, segment, index):
        log_debug("command_type - {}, segment - {}, index - {}".format(command, segment, index))
        if command == COMMAND.C_PUSH:
            self._handle_push(segment, index)
        elif command == COMMAND.C_POP:
            self._handle_pop(segment, index)
        else:
            raise Exception("Unexpected command type - {}".format(command))
        self._write_line()

    def close(self):
        self.output.close()
