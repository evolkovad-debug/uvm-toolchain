"""Командная строка ассемблера УВМ (этап 1)."""

import argparse
import sys

from src import assembler

EXIT_OK = 0
EXIT_ERROR = 1


def build_parser():
    """Создать разборщик параметров командной строки."""
    parser = argparse.ArgumentParser(
        description="Ассемблер учебной виртуальной машины (УВМ)."
    )
    parser.add_argument("source", help="путь к исходному файлу (JSON)")
    parser.add_argument("output", help="путь к двоичному файлу-результату")
    parser.add_argument(
        "--test", action="store_true",
        help="режим тестирования: вывести результат на экран",
    )
    return parser


def format_fields(instruction):
    """Записать поля команды в виде «A=0, B=1009»."""
    return ", ".join(f"{name}={value}" for name, value in instruction.items())


def main(argv=None):
    """Точка входа: ассемблировать программу и вывести результат."""
    args = build_parser().parse_args(argv)
    try:
        program = assembler.assemble_file(args.source)
    except assembler.AsmError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    if args.test:
        for instruction in program:
            print(format_fields(instruction))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
