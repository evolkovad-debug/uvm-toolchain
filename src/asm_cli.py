"""Командная строка ассемблера УВМ (этапы 1–2)."""

import argparse
import sys

from src import assembler, codec

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
        help="режим тестирования: вывести байты команд на экран",
    )
    return parser


def write_binary(path, data):
    """Записать результат ассемблирования в двоичный файл."""
    try:
        with open(path, "wb") as handle:
            handle.write(data)
    except OSError as error:
        raise assembler.AsmError(
            f"не удалось записать {path!r}: {error}"
        ) from error


def main(argv=None):
    """Точка входа: ассемблировать программу и записать результат."""
    args = build_parser().parse_args(argv)
    try:
        program = assembler.assemble_file(args.source)
        chunks = codec.encode_program(program)
        write_binary(args.output, b"".join(chunks))
    except assembler.AsmError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    print(f"Ассемблировано команд: {len(program)}")
    if args.test:
        for chunk in chunks:
            print(codec.format_bytes(chunk))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
