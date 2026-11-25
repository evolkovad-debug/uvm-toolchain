"""Создаёт три программы: поэлементный сдвиг вправо двух векторов."""

import json

FIRST = 100
SECOND = 110
EXAMPLES = {
    "examples/vectors_1.json": (
        [256, 1024, 7, 100, 65535],
        [4, 3, 1, 2, 8],
    ),
    "examples/vectors_2.json": (
        [1, 2, 4, 8, 16],
        [0, 1, 2, 3, 4],
    ),
    "examples/vectors_3.json": (
        [1000000, 500, 33, 1048576, 12345],
        [10, 5, 0, 20, 3],
    ),
}


def store(address, value):
    """Команды записи числа value в ячейку address."""
    return [
        {"op": "load_const", "value": address},
        {"op": "load_const", "value": value},
        {"op": "write", "offset": 0},
    ]


def shift_element(index):
    """Команды: first[index] = first[index] >> second[index]."""
    return [
        {"op": "load_const", "value": FIRST},
        {"op": "read", "address": SECOND + index},
        {"op": "shr", "address": FIRST + index, "offset": index},
    ]


def build_program(first, second):
    """Собрать программу: заполнить векторы и сдвинуть первый."""
    program = []
    for index, value in enumerate(first):
        program.extend(store(FIRST + index, value))
    for index, value in enumerate(second):
        program.extend(store(SECOND + index, value))
    for index in range(len(first)):
        program.extend(shift_element(index))
    return program


def main():
    """Записать три программы в файлы, по одной команде на строку."""
    for path, (first, second) in EXAMPLES.items():
        commands = build_program(first, second)
        lines = ["  " + json.dumps(command) for command in commands]
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("[\n" + ",\n".join(lines) + "\n]\n")
        print(f"Создан файл {path}")


if __name__ == "__main__":
    main()
