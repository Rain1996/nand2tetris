from enum import IntEnum

COMMAND = IntEnum("COMMAND", "A_COMMAND C_COMMAND L_COMMAND")

PREDEFINED_SYMBOL_TABLE = {
    "SP":     0,
    "LCL":    1,
    "ARG":    2,
    "THIS":   3,
    "THAT":   4,
    "SCREEN": 16384,
    "KBD":    24576,
    "R0":     0,
    "R1":     1,
    "R2":     2,
    "R3":     3,
    "R4":     4,
    "R5":     5,
    "R6":     6,
    "R7":     7,
    "R8":     8,
    "R9":     9,
    "R10":    10,
    "R11":    11,
    "R12":    12,
    "R13":    13,
    "R14":    14,
    "R15":    15,
}

DEST_SYMBOL_TABLE = {
    "M": 0b001,
    "D": 0b010,
    "A": 0b100,
}

JUMP_SYMBOL_TABLE = {
    "null": 0b000,
    "JGT":  0b001,
    "JEQ":  0b010,
    "JGE":  0b011,
    "JLT":  0b100,
    "JNE":  0b101,
    "JLE":  0b110,
    "JMP":  0b111,
}

COMP_SYMBOL_TABLE = {      # a-bits and c-bits
    "0":   0b0101010,
    "1":   0b0111111,
    "-1":  0b0111010,
    "D":   0b0001100,
    "A":   0b0110000,
    "M":   0b1110000,
    "!D":  0b0001101,
    "!A":  0b0110001,
    "!M":  0b1110001,
    "-D":  0b0001111,
    "-A":  0b0110011,
    "-M":  0b1110011,
    "D+1": 0b0011111,
    "A+1": 0b0110111,
    "M+1": 0b1110111,
    "D-1": 0b0001110,
    "A-1": 0b0110010,
    "M-1": 0b1110010,
    "D+A": 0b0000010,
    "D+M": 0b1000010,
    "D-A": 0b0010011,
    "D-M": 0b1010011,
    "A-D": 0b0000111,
    "M-D": 0b1000111,
    "D&A": 0b0000000,
    "D&M": 0b1000000,
    "D|A": 0b0010101,
    "D|M": 0b1010101,
}
