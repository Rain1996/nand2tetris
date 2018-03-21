from . import DEST_SYMBOL_TABLE
from . import COMP_SYMBOL_TABLE
from . import JUMP_SYMBOL_TABLE
# from utils import log_debug


class Code:
    def __init__(self):
        self._DEST_SYMBOL_TABLE = DEST_SYMBOL_TABLE
        self._COMP_SYMBOL_TABLE = COMP_SYMBOL_TABLE
        self._JUMP_SYMBOL_TABLE = JUMP_SYMBOL_TABLE

    def dest(self, dest_str):
        # log_debug("dest_str - {}".format(dest_str))
        dest_byte = 0b000
        if dest_str != 'null':
            for d in dest_str:
                dest_byte |= self._DEST_SYMBOL_TABLE[d]
        return dest_byte

    def comp(self, comp_str):
        # log_debug("comp_str - {}".format(comp_str))
        return self._COMP_SYMBOL_TABLE[comp_str]

    def jump(self, jump_str):
        # log_debug("jump_str - {}".format(jump_str))
        return self._JUMP_SYMBOL_TABLE[jump_str]
