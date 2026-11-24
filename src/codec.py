"""Машинный код УВМ: перевод команд в байты."""

from src import isa

BYTE_FORMAT = "0x{:02X}"


def encode_instruction(instruction):
    """Перевести одну команду (словарь полей) в байты."""
    command = isa.BY_OPCODE[instruction[isa.OPCODE_NAME]]
    value = instruction[isa.OPCODE_NAME] << isa.OPCODE_START
    for field in command.fields:
        value |= instruction[field.name] << field.start
    return value.to_bytes(command.size, isa.BYTE_ORDER)


def encode_program(program):
    """Перевести программу в список байтовых строк (по одной на команду)."""
    return [encode_instruction(instruction) for instruction in program]


def format_bytes(chunk):
    """Записать байты команды в виде «0x40, 0xFC, 0x00, 0x00»."""
    return ", ".join(BYTE_FORMAT.format(byte) for byte in chunk)
