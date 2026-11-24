"""Ассемблер УВМ: разбор программы в формате JSON во внутреннее
представление (список словарей «поле -> значение»)."""

import json

from src import isa

MIN_FIELD_VALUE = 0
KEY_OPERATION = "op"


class AsmError(Exception):
    """Ошибка в тексте программы на языке ассемблера."""


def parse_json(text):
    """Разобрать JSON и убедиться, что это список команд."""
    try:
        data = json.loads(text)
    except ValueError as error:
        raise AsmError(f"некорректный JSON: {error}") from error
    if not isinstance(data, list):
        raise AsmError("программа должна быть JSON-списком команд")
    return data


def find_command(entry, where):
    """Найти описание команды по полю op."""
    mnemonic = entry.get(KEY_OPERATION)
    command = None
    if isinstance(mnemonic, str):
        command = isa.BY_MNEMONIC.get(mnemonic)
    if command is None:
        raise AsmError(f"{where}: неизвестная команда {mnemonic!r}")
    return command


def check_number(value, field, where):
    """Проверить, что значение поля — целое число допустимого размера."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise AsmError(f"{where}: поле {field.key!r} должно быть числом")
    max_value = (1 << field.width) - 1
    if value < MIN_FIELD_VALUE or value > max_value:
        raise AsmError(
            f"{where}: поле {field.key!r} вне диапазона "
            f"{MIN_FIELD_VALUE}..{max_value}"
        )
    return value


def translate_entry(entry, number):
    """Перевести одну команду из JSON во внутреннее представление."""
    where = f"команда {number}"
    if not isinstance(entry, dict):
        raise AsmError(f"{where}: ожидался JSON-объект")
    command = find_command(entry, where)
    allowed = {KEY_OPERATION} | {field.key for field in command.fields}
    extra = sorted(set(entry) - allowed)
    if extra:
        raise AsmError(f"{where}: лишние поля {extra}")
    result = {isa.OPCODE_NAME: command.opcode}
    for field in command.fields:
        if field.key not in entry:
            raise AsmError(f"{where}: не указано поле {field.key!r}")
        result[field.name] = check_number(entry[field.key], field, where)
    return result


def assemble(text):
    """Перевести текст программы во внутреннее представление."""
    entries = parse_json(text)
    return [
        translate_entry(entry, number)
        for number, entry in enumerate(entries, start=1)
    ]


def assemble_file(path):
    """Прочитать файл с программой и перевести его."""
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except (OSError, UnicodeDecodeError) as error:
        raise AsmError(f"не удалось прочитать {path!r}: {error}") from error
    return assemble(text)
