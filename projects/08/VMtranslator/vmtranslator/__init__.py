from enum import IntEnum

commands = (
    "C_ARITHMETIC "
    "C_PUSH C_POP "
    "C_LABEL "
    "C_GOTO "
    "C_FUNCTION "
    "C_IF "
    "C_RETURN "
    "C_CALL "
)

COMMAND = IntEnum("COMMAND", commands)

WORD_COMMAND_TYPE_MAPPING = {
    "push":     COMMAND.C_PUSH,
    "pop":      COMMAND.C_POP,
    "label":    COMMAND.C_LABEL,
    "goto":     COMMAND.C_GOTO,
    "if-goto":  COMMAND.C_IF,
    "function": COMMAND.C_FUNCTION,
    "call":     COMMAND.C_CALL,
    "return":   COMMAND.C_RETURN,
    "add":      COMMAND.C_ARITHMETIC,
    "sub":      COMMAND.C_ARITHMETIC,
    "neg":      COMMAND.C_ARITHMETIC,
    "eq":       COMMAND.C_ARITHMETIC,
    "gt":       COMMAND.C_ARITHMETIC,
    "lt":       COMMAND.C_ARITHMETIC,
    "and":      COMMAND.C_ARITHMETIC,
    "or":       COMMAND.C_ARITHMETIC,
    "not":      COMMAND.C_ARITHMETIC,
}

SEGMENT_REGISTER_MAPPING = {
    "local":    "LCL",
    "argument": "ARG",
    "this":     "THIS",
    "that":     "THAT",
}

SEGMENT_BASE_ADDR_MAPPING = {
    "pointer": 3,
    "temp":    5,
}
