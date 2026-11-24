"""Спецификация учебной виртуальной машины (УВМ), вариант 5."""

from collections import namedtuple

Field = namedtuple("Field", ["name", "key", "start", "width"])
Command = namedtuple("Command", ["mnemonic", "opcode", "size", "fields"])

OPCODE_NAME = "A"
OPCODE_START = 0
OPCODE_WIDTH = 6
BYTE_ORDER = "little"

LOAD_CONST = Command("load_const", 0, 4, (Field("B", "value", 6, 26),))
READ = Command("read", 36, 3, (Field("B", "address", 6, 18),))
WRITE = Command("write", 38, 3, (Field("B", "offset", 6, 15),))
SHR = Command(
    "shr", 61, 5,
    (Field("B", "address", 6, 18), Field("C", "offset", 24, 15)),
)

COMMANDS = (LOAD_CONST, READ, WRITE, SHR)
BY_MNEMONIC = {command.mnemonic: command for command in COMMANDS}
BY_OPCODE = {command.opcode: command for command in COMMANDS}
