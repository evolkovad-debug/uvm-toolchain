"""Командная строка интерпретатора УВМ (этап 3)."""

import argparse
import sys

from src import codec, dump, vm

EXIT_OK = 0
EXIT_ERROR = 1
RANGE_PARTS = 2


def build_parser():
    """Создать разборщик параметров командной строки."""
    parser = argparse.ArgumentParser(
        description="Интерпретатор учебной виртуальной машины (УВМ)."
    )
    parser.add_argument("program", help="путь к двоичному файлу программы")
    parser.add_argument("dump", help="путь к XML-файлу с дампом памяти")
    parser.add_argument(
        "--range", required=True, metavar="ПЕРВЫЙ:ПОСЛЕДНИЙ",
        help="диапазон адресов памяти для дампа (включительно)",
    )
    return parser


def parse_range(text):
    """Разобрать диапазон адресов вида «0:24»."""
    parts = text.split(":")
    try:
        if len(parts) != RANGE_PARTS:
            raise ValueError(text)
        first, last = (int(part) for part in parts)
    except ValueError as error:
        message = "диапазон должен иметь вид ПЕРВЫЙ:ПОСЛЕДНИЙ"
        raise vm.VMError(message) from error
    if first < vm.MIN_ADDRESS or last >= vm.DATA_MEMORY_SIZE or first > last:
        raise vm.VMError(f"недопустимый диапазон адресов {text!r}")
    return first, last


def read_binary(path):
    """Прочитать двоичный файл с программой."""
    try:
        with open(path, "rb") as handle:
            return handle.read()
    except OSError as error:
        raise vm.VMError(f"не удалось прочитать {path!r}: {error}") from error


def write_text(path, text):
    """Записать текст дампа в файл."""
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
    except OSError as error:
        raise vm.VMError(f"не удалось записать {path!r}: {error}") from error


def main(argv=None):
    """Точка входа: выполнить программу и сохранить дамп памяти."""
    args = build_parser().parse_args(argv)
    try:
        first, last = parse_range(args.range)
        machine = vm.Machine(read_binary(args.program))
        machine.run()
        write_text(args.dump, dump.build_dump(machine.data, first, last))
    except (vm.VMError, codec.DecodeError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    print(f"Выполнено команд: {machine.executed}")
    print(f"Дамп памяти сохранён: {args.dump}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
