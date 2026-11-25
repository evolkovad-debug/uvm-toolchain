"""Создаёт программу shr_test.json: проверка команды сдвига вправо."""

import json

OUTPUT = "examples/shr_test.json"
INPUTS = {0: 1024, 1: 255, 2: 67108863}
CASES = [
    (10, 0, 3, 0),
    (11, 1, 4, 0),
    (12, 0, 0, 1),
    (14, 2, 20, 0),
    (15, 1, 8, 0),
]


def store(address, value):
    """Команды записи числа value в ячейку address."""
    return [
        {"op": "load_const", "value": address},
        {"op": "load_const", "value": value},
        {"op": "write", "offset": 0},
    ]


def shift(base, source, amount, offset):
    """Команды сдвига ячейки source вправо на amount бит.

    Результат попадает в ячейку base + offset.
    """
    return [
        {"op": "load_const", "value": base},
        {"op": "load_const", "value": amount},
        {"op": "shr", "address": source, "offset": offset},
    ]


def build_program():
    """Собрать программу: заполнить память и выполнить сдвиги."""
    program = []
    for address, value in INPUTS.items():
        program.extend(store(address, value))
    for case in CASES:
        program.extend(shift(*case))
    return program


def main():
    """Записать программу в файл, по одной команде на строку."""
    lines = ["  " + json.dumps(command) for command in build_program()]
    with open(OUTPUT, "w", encoding="utf-8") as handle:
        handle.write("[\n" + ",\n".join(lines) + "\n]\n")
    print(f"Создан файл {OUTPUT}")


if __name__ == "__main__":
    main()
