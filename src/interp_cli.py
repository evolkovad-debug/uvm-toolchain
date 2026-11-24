"""Командная строка интерпретатора УВМ (этап 3).

Аргументы:
  binary   — путь к бинарному файлу с ассемблированной программой
  dump     — путь к файлу, куда будет сохранён дамп памяти
  range    — диапазон адресов памяти в формате START:END

Опционально:
  --init FILE  — файл с начальными значениями памяти данных
                 (формат: адрес значение  — по одному на строку)
"""

import argparse
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom

from src import vm


EXIT_OK = 0
EXIT_ERROR = 1


def build_parser():
    parser = argparse.ArgumentParser(
        description="Интерпретатор учебной виртуальной машины (УВМ)."
    )
    parser.add_argument("binary", help="путь к бинарному файлу с программой")
    parser.add_argument("dump", help="путь к файлу дампа памяти (XML)")
    parser.add_argument(
        "range",
        help="диапазон адресов памяти для дампа в формате START:END",
    )
    parser.add_argument(
        "--init",
        metavar="FILE",
        help="файл с начальными значениями памяти данных "
             "(строки вида: адрес значение)",
    )
    return parser


def parse_range(text: str):
    """Разобрать диапазон вида 0:10 → (0, 10)."""
    try:
        start_str, end_str = text.split(":")
        start = int(start_str)
        end = int(end_str)
    except ValueError as error:
        raise vm.VMError(
            f"некорректный диапазон {text!r}, ожидается START:END"
        ) from error
    if start < 0 or end <= start:
        raise vm.VMError(f"некорректный диапазон: {start}..{end}")
    return start, end


def load_init(path: str, machine: vm.VirtualMachine) -> None:
    """Загрузить начальные значения памяти данных из текстового файла."""
    try:
        with open(path, encoding="utf-8") as handle:
            for lineno, line in enumerate(handle, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) != 2:
                    raise vm.VMError(
                        f"{path}:{lineno}: ожидается «адрес значение»"
                    )
                try:
                    address = int(parts[0])
                    value = int(parts[1])
                except ValueError as error:
                    raise vm.VMError(
                        f"{path}:{lineno}: адрес и значение должны быть числами"
                    ) from error
                if not (0 <= address < len(machine.data)):
                    raise vm.VMError(
                        f"{path}:{lineno}: адрес {address} вне памяти данных"
                    )
                machine.data[address] = value & 0xFFFFFFFF
    except OSError as error:
        raise vm.VMError(f"не удалось прочитать {path!r}: {error}") from error


def write_xml_dump(path: str, values: list, start: int) -> None:
    """Записать дамп памяти данных в формате XML."""
    root = ET.Element("memory")
    root.set("start", str(start))
    root.set("end", str(start + len(values)))

    for offset, value in enumerate(values):
        cell = ET.SubElement(root, "cell")
        cell.set("address", str(start + offset))
        cell.set("value", str(value))

    rough = ET.tostring(root, encoding="unicode")
    pretty = minidom.parseString(rough).toprettyxml(indent="  ")

    lines = pretty.splitlines()
    if lines and lines[0].startswith("<?xml"):
        content = "\n".join(lines[1:]).lstrip("\n") + "\n"
    else:
        content = pretty

    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
    except OSError as error:
        raise vm.VMError(f"не удалось записать дамп {path!r}: {error}") from error


def main(argv=None):
    args = build_parser().parse_args(argv)

    try:
        start, end = parse_range(args.range)

        with open(args.binary, "rb") as handle:
            binary = handle.read()

        machine = vm.VirtualMachine()
        machine.load_program(binary)

        if args.init:
            load_init(args.init, machine)

        machine.run()

        values = machine.dump_data(start, end)
        write_xml_dump(args.dump, values, start)

    except (OSError, vm.VMError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR

    print(f"Выполнение завершено. Дамп памяти [{start}:{end}] записан в {args.dump}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
