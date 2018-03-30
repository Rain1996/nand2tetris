import sys
import os.path
from utils import log
from utils import log_debug
from utils import log_error
from vmtranslator import COMMAND
from vmtranslator.parser import Parser
from vmtranslator.code_writer import CodeWriter

help_msg = """usage:
    python main.py <vm_file>|<dir>
example:
    python main.py source.vm
or:
    python main.py dir
"""


# 翻译vm文件
def translate_vm_to_asm(code_writer, filename):
    log_debug("filename - {}".format(filename))
    input_ = open(filename, 'rb')
    parser = Parser(input_)
    base_name = os.path.basename(filename[:-3])     # \c\xxx.vm -> xxx or /c/c/xxx.vm -> xxx
    code_writer.set_filename(base_name)

    while parser.has_more_commands():
        parser.advance()
        command_type = parser.command_type()
        if command_type in (COMMAND.C_PUSH, COMMAND.C_POP):
            segment, index = parser.arg1(), parser.arg2()
            code_writer.write_push_or_pop(command_type, segment, index)
        elif command_type == COMMAND.C_ARITHMETIC:
            command = parser.arg1()
            code_writer.write_arithmetic(command)
        else:
            Exception("Unexpected command - {}".format(command_type))


# 处理单个vm文件
def handle_single_vm_file(filename):
    log_debug('handle_single_vm_file')

    output = filename.replace(".vm", ".asm")
    code_writer = CodeWriter(output)

    translate_vm_to_asm(code_writer, filename)

    code_writer.write_end()         # 写入asm文件标准结尾


# 处理多个vm文件
def handle_multi_vm_file(path):
    log_debug('handle_multi_vm_file')

    output = os.path.join(path, 'out.asm')
    code_writer = CodeWriter(output)

    for f in os.listdir(path):
        filename = os.path.join(path, f)
        if os.path.isfile(filename) and filename.endswith(".vm"):
            translate_vm_to_asm(code_writer, filename)

    code_writer.write_end()          # 写入asm文件标准结尾


# 解析命令行参数
def parse_sys_arg(sys_argv):
    path = sys_argv[1]
    if os.path.isfile(path):
        if path.endswith(".vm"):
            handle_single_vm_file(path)
        else:
            log_error("{} is not a vm file".format(path))
    elif os.path.isdir(path):
        handle_multi_vm_file(path)
    else:
        abspath = os.path.abspath(path)
        log_error("{} is not exists".format(abspath))
        log(help_msg)


if __name__ == '__main__':
    log_debug("sys.argv - {}".format(sys.argv))
    if len(sys.argv) == 2:
        parse_sys_arg(sys.argv)
    else:
        log(help_msg)
