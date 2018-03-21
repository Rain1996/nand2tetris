from copy import deepcopy
from . import PREDEFINED_SYMBOL_TABLE


class SymbolTable:
    def __init__(self):
        self._table = deepcopy(PREDEFINED_SYMBOL_TABLE)

    def add_entry(self, symbol, address):
        self._table[symbol] = address

    def contains(self, symbol):
        return symbol in self._table

    def get_address(self, symbol):
        return self._table[symbol]

    def __repr__(self):
        return repr(self._table)

    def __str__(self):
        return str(self._table)
