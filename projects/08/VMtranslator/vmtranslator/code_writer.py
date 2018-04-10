from . import COMMAND
from . import SEGMENT_REGISTER_MAPPING
from . import SEGMENT_BASE_ADDR_MAPPING
from utils import log_debug
from functools import partialmethod
from uuid import uuid1


class CodeWriter:
    def __init__(self, output_file):
        self._output = open(output_file, 'w')
        self._vm_filename = ''
        self._current_func = ''

    def _write_empty_line(self):
        self._output.write("\n")

    def _write(self, string):
        self._output.write(string)

    def _write_increase_sp(self):
        # SP 自增1
        lines = (
            "@SP\n"
            "M=M+1\n"
        )
        self._write(lines)

    def _write_push(self):
        # 将D寄存器存储的值存入栈中
        lines = (
            "@SP\n"
            "A=M\n"
            "M=D\n"
        )
        self._write(lines)
        self._write_increase_sp()

    def _write_pop(self):
        # pop 只需要 SP 自减1
        # M 寄存器的值为 pop 出的值
        lines = (
            "@SP\n"
            "M=M-1\n"
            "A=M\n"
        )
        self._write(lines)

    def _write_boolean(self, uuid):
        # 通过跳转的方法写入布尔值
        lines = (
            "({func}$TRUE${uuid})\n"
            "D=-1\n"
            "@{func}$POP${uuid}\n"
            "0;JMP\n"
            "\n"
            "({func}$FALSE${uuid})\n"
            "D=0\n"
            "@{func}$POP${uuid}\n"
            "0;JMP\n"
            "\n"
            "({func}$POP${uuid})\n"
        ).format(func=self._current_func, uuid=uuid)
        self._write(lines)
        self._write_push()

    def _handle_arithmetic_or_logic(self, line):
        # 处理算术和逻辑运算的抽象方法
        self._write_pop()
        self._write("D=M\n")
        self._write_pop()

        self._write(line)
        self._write_increase_sp()

    _handle_add = partialmethod(_handle_arithmetic_or_logic, "M=D+M\n")
    _handle_sub = partialmethod(_handle_arithmetic_or_logic, "M=M-D\n")
    _handle_and = partialmethod(_handle_arithmetic_or_logic, "M=D&M\n")
    _handle_or = partialmethod(_handle_arithmetic_or_logic, "M=D|M\n")

    def _handle_comparison(self, comparison):
        # 处理比较运算的抽象方法
        self._write_pop()
        self._write("D=M\n")
        self._write_pop()

        uuid = uuid1()
        lines = (
            "D=M-D\n"
            "\n"
            "@{func}$TRUE${uuid}\n"
            "D;{comp}\n"
            "@{func}$FALSE${uuid}\n"
            "0;JMP\n"
            "\n"
        ).format(func=self._current_func, uuid=uuid, comp=comparison)
        self._write(lines)
        self._write_boolean(uuid)

    _handle_eq = partialmethod(_handle_comparison, "JEQ")
    _handle_gt = partialmethod(_handle_comparison, "JGT")
    _handle_lt = partialmethod(_handle_comparison, "JLT")

    def _handle_unary_command(self, line):
        # 处理一元命令的抽象方法
        self._write_pop()
        self._write(line)
        self._write_increase_sp()

    _handle_neg = partialmethod(_handle_unary_command, "M=-M\n")
    _handle_not = partialmethod(_handle_unary_command, "M=!M\n")

    def _save_static_value_to_d_register(self, index):
        # 将static段对应的值存入D存储器
        lines = (
            "@{filename}.{index}\n"
            "D=M\n"
        ).format(filename=self._vm_filename, index=index)
        self._write(lines)

    def _save_value_to_d_register(self, segment, index):
        # 通过index, 拿到对应段的值，存储到D寄存器
        lines = (
            "@{index}\n"
            "D=A\n"
        ).format(index=index)

        if segment != 'constant':
            if segment in SEGMENT_REGISTER_MAPPING:
                register = SEGMENT_REGISTER_MAPPING[segment]
                lines += (
                    "@{register}\n"
                    "A=D+M\n"
                ).format(register=register)
            elif segment in SEGMENT_BASE_ADDR_MAPPING:
                base_addr = SEGMENT_BASE_ADDR_MAPPING[segment]
                lines += (
                    "@{base_addr}\n"
                    "A=D+A\n"
                ).format(base_addr=base_addr)
            else:
                raise Exception("Unexpected segment - {}".format(segment))
            lines += "D=M\n"

        self._write(lines)

    def _handle_push(self, segment, index):
        # 处理 push 命令
        if segment == 'static':
            self._save_static_value_to_d_register(index)
        else:
            self._save_value_to_d_register(segment, index)
        self._write_push()

    def _save_ram_addr_to_temp(self, segment, index):
        # 通过index, 拿到对应段的地址，存储到TEMP中
        lines = (
            "@{index}\n"
            "D=A\n"
        ).format(index=index)

        if segment in SEGMENT_REGISTER_MAPPING:
            register = SEGMENT_REGISTER_MAPPING[segment]
            lines += (
                "@{register}\n"
                "D=D+M\n"
            ).format(register=register)
        elif segment in SEGMENT_BASE_ADDR_MAPPING:
            base_addr = SEGMENT_BASE_ADDR_MAPPING[segment]
            lines += (
                "@{base_addr}\n"
                "D=D+A\n"
            ).format(base_addr=base_addr)
        else:
            raise Exception("Unexpected segment - {}".format(segment))

        lines += (
            "@TEMP\n"
            "M=D\n"
        )

        self._write(lines)

    def _save_value_to_ram(self):
        # 把 退栈得到的值 存储到 TEMP中存储的地址对应的RAM中
        lines = (
            "D=M\n"
            "@TEMP\n"
            "A=M\n"
            "M=D\n"
        )
        self._write(lines)

    def _save_value_to_static(self, index):
        lines = (
            "D=M\n"
            "@{filename}.{index}\n"
            "M=D\n"
        ).format(filename=self._vm_filename, index=index)
        self._write(lines)

    def _handle_pop(self, segment, index):
        # 处理 pop 命令
        if segment != 'static':
            self._save_ram_addr_to_temp(segment, index)
            self._write_pop()
            self._save_value_to_ram()
        else:
            self._write_pop()
            self._save_value_to_static(index)

    def _save_segment_point(self):
        # 函数调用时，存储四个段的所存储的指针
        segments = ["LCL", "ARG", "THIS", "THAT"]

        for segment in segments:
            lines = (
                "@{segment}\n"
                "D=M\n"
            ).format(segment=segment)
            self._write(lines)
            self._write_push()

    def _return_address(self):
        uuid = uuid1()
        return "{}$return${}".format(self._current_func, uuid)

    def _push_return_address(self, label):
        lines = (
            "@{label}\n"
            "D=A\n"
        ).format(label=label)
        self._write(lines)
        self._write_push()

    def _recover(self):
        # 恢复调用者的SP以及其他段的指针
        self._write_pop()
        lines = (
            "D=M\n"
            "@ARG\n"
            "A=M\n"
            "M=D\n"
            "D=A\n"
            "@SP\n"
            "M=D+1\n"
        )
        self._write(lines)

        segments = ["THAT", "THIS", "ARG", "LCL"]
        for i, segment in enumerate(segments, start=1):
            lines = (
                "@FRAME\n"
                "D=M\n"
                "@{i}\n"
                "A=D-A\n"
                "D=M\n"
                "@{segment}\n"
                "M=D\n"
            ).format(i=i, segment=segment)
            self._write(lines)

    def _reset_arg_and_lcl(self, num_args):
        # 重置 ARG 和 LCL
        push_num = 5

        lines = (
            "@SP\n"
            "D=M\n"
            "@LCL\n"
            "M=D\n"
            "@{num_args}\n"
            "D=D-A\n"
            "@{push_num}\n"
            "D=D-A\n"
            "@ARG\n"
            "M=D\n"
        ).format(num_args=num_args, push_num=push_num)
        self._write(lines)

    def _save_address_into_temp(self):
        # 将返回地址放入临时变量中
        push_num = 5

        lines = (
            "@LCL\n"
            "D=M\n"
            "@FRAME\n"
            "M=D\n"
            "@{push_num}\n"
            "D=A\n"
            "@FRAME\n"
            "A=M-D\n"
            "D=M\n"
            "@RET\n"
            "M=D\n"
        ).format(push_num=push_num)
        self._write(lines)

    def bootstrap(self):
        # 引导程序
        lines = (
            "@256\n"
            "D=A\n"
            "@SP\n"
            "M=D\n"
        )
        self._write(lines)
        self._write_empty_line()
        self.write_call("Sys.init", 0)

    def set_filename(self, filename):
        # 告知CodeWriter当前处理文件名(无.vm后缀)，方便处理static段
        self._vm_filename = filename

    def write_arithmetic(self, command):
        log_debug("command - {}".format(command))

        handle_func = getattr(self, "_handle_{}".format(command))
        handle_func()

        self._write_empty_line()

    def write_push_or_pop(self, command, segment, index):
        log_debug("command_type - {}, segment - {}, index - {}".format(command, segment, index))
        if command == COMMAND.C_PUSH:
            self._handle_push(segment, index)
        elif command == COMMAND.C_POP:
            self._handle_pop(segment, index)
        else:
            raise Exception("Unexpected command type - {}".format(command))
        self._write_empty_line()

    def write_call(self, func_name, num_args):
        label = self._return_address()
        self._push_return_address(label)

        self._save_segment_point()
        self._reset_arg_and_lcl(num_args)
        self.write_goto(func_name, prefix=False)
        self.write_label(label, prefix=False)
        self._write_empty_line()

    def write_return(self):
        self._save_address_into_temp()
        self._recover()
        lines = (
            "@RET\n"
            "A=M\n"
            "0;JMP\n"
        )
        self._write(lines)

    def write_function(self, func_name, num_locals):
        self._current_func = func_name
        self.write_label(func_name, prefix=False)
        for i in range(num_locals):
            self._write("D=0\n")
            self._write_push()
            self._write_empty_line()

    def write_label(self, label, prefix=True):
        if prefix:
            label = "{}${}".format(self._current_func, label)
        self._write("({})\n".format(label))

    def write_goto(self, label, prefix=True):
        if prefix:
            label = "{}${}".format(self._current_func, label)

        lines = (
            "@{label}\n"
            "0;JMP\n"
        ).format(label=label)
        self._write(lines)
        self._write_empty_line()

    def write_if(self, label):
        self._write_pop()
        self._write("D=M\n")
        label = "{}${}".format(self._current_func, label)

        lines = (
            "@{label}\n"
            "D;JNE\n"
            "\n"
        ).format(label=label)
        self._write(lines)

    def close(self):
        self._output.close()
