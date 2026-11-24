"""Интерпретатор учебной виртуальной машины (УВМ), вариант 5.

Память команд и память данных разделены.
Машина стековая.
"""

from src import isa


class VMError(Exception):
    """Ошибка во время выполнения программы."""


class VirtualMachine:
    """Стековая УВМ с разделённой памятью команд и данных."""

    def __init__(self, code_size=8192, data_size=8192):
        # Память команд и память данных разделены (требование этапа 3)
        self.code = bytearray(code_size)
        self.data = [0] * data_size
        self.stack = []
        self.pc = 0  # счётчик команд (в байтах)

    def load_program(self, binary: bytes) -> None:
        """Загрузить бинарную программу в память команд."""
        if len(binary) > len(self.code):
            raise VMError("программа слишком большая для памяти команд")
        self.code[:len(binary)] = binary
        self.pc = 0

    def push(self, value: int) -> None:
        self.stack.append(value & 0xFFFFFFFF)

    def pop(self) -> int:
        if not self.stack:
            raise VMError("попытка снять значение с пустого стека")
        return self.stack.pop()

    def fetch_decode(self):
        """
        Прочитать следующую команду из памяти команд
        и перевести её во внутреннее представление (словарь полей).
        """
        if self.pc >= len(self.code):
            return None

        first = self.code[self.pc]
        opcode = first & 0x3F  # биты 0—5

        if opcode not in isa.BY_OPCODE:
            raise VMError(
                f"неизвестная команда с кодом {opcode} по адресу {self.pc}"
            )

        command = isa.BY_OPCODE[opcode]
        size = command.size

        if self.pc + size > len(self.code):
            raise VMError(f"неполный код команды по адресу {self.pc}")

        raw = int.from_bytes(self.code[self.pc : self.pc + size], isa.BYTE_ORDER)
        self.pc += size

        # Внутреннее представление — словарь полей (как на этапе 1)
        instruction = {isa.OPCODE_NAME: opcode}
        for field in command.fields:
            mask = (1 << field.width) - 1
            instruction[field.name] = (raw >> field.start) & mask

        return instruction

    def execute(self, instruction: dict) -> None:
        """Выполнить одну команду."""
        opcode = instruction[isa.OPCODE_NAME]

        if opcode == 0:  # load_const
            # Операнд: поле B. Результат: новый элемент на стеке.
            self.push(instruction["B"])

        elif opcode == 36:  # read
            # Операнд: значение в памяти по адресу, которым является поле B.
            # Результат: новый элемент на стеке.
            address = instruction["B"]
            if not (0 <= address < len(self.data)):
                raise VMError(f"чтение по недопустимому адресу {address}")
            self.push(self.data[address])

        elif opcode == 38:  # write
            # Операнд: элемент, снятый с вершины стека.
            # Результат: значение в памяти по адресу =
            # сумма адреса (элемент, снятый с вершины стека) и смещения (поле B).
            offset = instruction["B"]
            value = self.pop()
            address = self.pop()
            target = address + offset
            if not (0 <= target < len(self.data)):
                raise VMError(f"запись по недопустимому адресу {target}")
            self.data[target] = value & 0xFFFFFFFF

        else:
            raise VMError(f"команда с кодом {opcode} ещё не реализована")

    def run(self, max_steps: int = 100_000) -> None:
        """Основной цикл интерпретатора."""
        steps = 0
        while steps < max_steps:
            instruction = self.fetch_decode()
            if instruction is None:
                break
            self.execute(instruction)
            steps += 1
        else:
            raise VMError("превышено максимальное число шагов выполнения")

    def dump_data(self, start: int, end: int) -> list:
        """Вернуть срез памяти данных [start; end)."""
        if start < 0 or end > len(self.data) or start >= end:
            raise VMError(f"некорректный диапазон дампа: {start}..{end}")
        return self.data[start:end]
