import sys
import os.path
from utils import log
from utils import log_debug
from utils import log_error
from vmtranslator.code_writer import CodeWriter
from vmtranslator.translator import Translator

help_msg = """usage:
    python main.py <vm_file>|<dir>
example:
    python main.py source.vm
or:
    python main.py dir
"""

VM_SUFFIX = ".vm"
ASM_SUFFIX = ".asm"


# 处理单个vm文件
def translate_single_vm_file(filename):
    log_debug('handle_single_vm_file')

    output = filename.replace(VM_SUFFIX, ASM_SUFFIX)
    code_writer = CodeWriter(output)
    translator = Translator(code_writer)

    translator.translate(filename)

    code_writer.close()


# 通过路径得到文件名
def filename_by_path(path):
    sep = '/' if '/' in path else '\\'
    log_debug("sep - {}".format(sep))
    dir_list = path.split(sep)
    log_debug("dir_list - {}".format(dir_list))
    filename = dir_list[-1] if dir_list[-1] != '' else dir_list[-2]
    return "{}{}".format(filename, ASM_SUFFIX)


# 处理多个vm文件
def translate_multi_vm_file(path):
    log_debug('handle_multi_vm_file')
    filename = filename_by_path(path)

    output = os.path.join(path, filename)
    log_debug("output - {}".format(output))
    code_writer = CodeWriter(output)
    translator = Translator(code_writer)
    code_writer.bootstrap()

    for f in os.listdir(path):
        filename = os.path.join(path, f)
        if os.path.isfile(filename) and filename.endswith(VM_SUFFIX):
            translator.translate(filename)

    # code_writer.write_end()          # 写入asm文件标准结尾
    code_writer.close()


# 解析命令行参数
def parse_sys_arg(sys_argv):
    path = sys_argv[1]
    if os.path.isfile(path):
        if path.endswith(VM_SUFFIX):
            translate_single_vm_file(path)
        else:
            log_error("{} is not a vm file".format(path))
    elif os.path.isdir(path):
        translate_multi_vm_file(path)
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
