"""Интерпретатор УВМ: память команд, память данных, стек."""

from src import codec, isa

DATA_MEMORY_SIZE = 1 << 18
WORD_MASK = (1 << 32) - 1
MIN_ADDRESS = 0


class VMError(Exception):
    """Ошибка выполнения программы на УВМ."""


class Machine:
    """Учебная виртуальная машина.

    Память команд (code) и память данных (data) разделены.
    """

    def __init__(self, code):
        """Создать машину с программой code (байты) и пустой памятью."""
        self.code = bytes(code)
        self.data = [0] * DATA_MEMORY_SIZE
        self.stack = []
        self.position = 0
        self.executed = 0
        self.handlers = {
            isa.LOAD_CONST.opcode: self.load_const,
            isa.READ.opcode: self.read,
            isa.WRITE.opcode: self.write,
        }

    def pop(self):
        """Снять элемент с вершины стека."""
        if not self.stack:
            raise VMError("стек пуст")
        return self.stack.pop()

    def check_address(self, address):
        """Проверить, что адрес лежит в памяти данных."""
        if address < MIN_ADDRESS or address >= DATA_MEMORY_SIZE:
            raise VMError(f"адрес {address} вне памяти данных")
        return address

    def load_const(self, fields):
        """Загрузка константы: новый элемент на стеке."""
        self.stack.append(fields["B"])

    def read(self, fields):
        """Чтение из памяти по адресу B: новый элемент на стеке."""
        address = self.check_address(fields["B"])
        self.stack.append(self.data[address])

    def write(self, fields):
        """Запись: значение и адрес снимаются со стека, смещение — B."""
        value = self.pop()
        address = self.check_address(self.pop() + fields["B"])
        self.data[address] = value & WORD_MASK

    def step(self):
        """Выполнить одну команду: прочитать, декодировать, исполнить."""
        start = self.position
        instruction, size = codec.decode_instruction(self.code, start)
        self.position += size
        try:
            self.handlers[instruction[isa.OPCODE_NAME]](instruction)
        except VMError as error:
            raise VMError(f"по смещению {start}: {error}") from error
        self.executed += 1

    def run(self):
        """Выполнить всю программу от начала до конца."""
        while self.position < len(self.code):
            self.step()
