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


OPCODE_MASK = (1 << isa.OPCODE_WIDTH) - 1


class DecodeError(Exception):
    """Ошибка чтения машинного кода."""


def decode_instruction(code, position):
    """Прочитать команду из байтов code по смещению position.

    Возвращает пару (поля команды, размер команды в байтах).
    """
    opcode = code[position] & OPCODE_MASK
    command = isa.BY_OPCODE.get(opcode)
    if command is None:
        raise DecodeError(
            f"неизвестный код команды {opcode} по смещению {position}"
        )
    chunk = code[position:position + command.size]
    if len(chunk) < command.size:
        raise DecodeError(f"команда по смещению {position} обрезана")
    value = int.from_bytes(chunk, isa.BYTE_ORDER)
    instruction = {isa.OPCODE_NAME: opcode}
    for field in command.fields:
        mask = (1 << field.width) - 1
        instruction[field.name] = (value >> field.start) & mask
    return instruction, command.size
