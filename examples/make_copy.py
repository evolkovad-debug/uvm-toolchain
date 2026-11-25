"""Создаёт программу copy_array.json: копирование массива в памяти УВМ."""

import json

SOURCE = 0
TARGET = 20
VALUES = [11, 22, 33, 44, 55]
OUTPUT = "examples/copy_array.json"


def build_program():
    """Собрать список команд: заполнить массив и скопировать его."""
    program = []
    for index, value in enumerate(VALUES):
        program.append({"op": "load_const", "value": SOURCE})
        program.append({"op": "load_const", "value": value})
        program.append({"op": "write", "offset": index})
    for index in range(len(VALUES)):
        program.append({"op": "load_const", "value": TARGET})
        program.append({"op": "read", "address": SOURCE + index})
        program.append({"op": "write", "offset": index})
    return program


def main():
    """Записать программу в файл, по одной команде на строку."""
    lines = ["  " + json.dumps(command) for command in build_program()]
    with open(OUTPUT, "w", encoding="utf-8") as handle:
        handle.write("[\n" + ",\n".join(lines) + "\n]\n")
    print(f"Создан файл {OUTPUT}")


if __name__ == "__main__":
    main()
