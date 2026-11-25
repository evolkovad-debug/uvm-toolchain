"""Тесты команды сдвига вправо shr (этап 4)."""

import os
import unittest

from src import vm
from tests.test_vm import compile_text, run_text

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")
SHR_FILE = os.path.join(EXAMPLES, "shr_test.json")


def shift_text(base, amount, source, offset):
    """Текст программы: сдвиг ячейки source на amount бит."""
    return (
        f'[{{"op": "load_const", "value": {base}}},'
        f' {{"op": "load_const", "value": {amount}}},'
        f' {{"op": "shr", "address": {source}, "offset": {offset}}}]'
    )


def run_shift(value, amount, base=20, offset=0):
    """Выполнить сдвиг числа value в ячейке 5; вернуть машину."""
    machine = vm.Machine(compile_text(shift_text(base, amount, 5, offset)))
    machine.data[5] = value
    machine.run()
    return machine


class ShiftTests(unittest.TestCase):
    """Проверка вычислений команды shr."""

    def test_basic_shift(self):
        """1024 >> 3 = 128, результат по адресу из стека."""
        machine = run_shift(1024, 3)
        self.assertEqual(machine.data[20], 128)

    def test_zero_shift(self):
        """Сдвиг на 0 не меняет число."""
        self.assertEqual(run_shift(77, 0).data[20], 77)

    def test_shift_to_zero(self):
        """Сдвиг на число бит, большее длины числа, даёт 0."""
        self.assertEqual(run_shift(255, 8).data[20], 0)
        self.assertEqual(run_shift(255, 100).data[20], 0)

    def test_result_address_uses_offset(self):
        """Адрес результата — адрес со стека плюс смещение C."""
        machine = run_shift(64, 2, base=30, offset=4)
        self.assertEqual(machine.data[34], 16)
        self.assertEqual(machine.data[30], 0)

    def test_source_unchanged(self):
        """Исходная ячейка B не меняется."""
        self.assertEqual(run_shift(64, 2).data[5], 64)

    def test_stack_empty_after(self):
        """Оба элемента со стека сняты."""
        self.assertEqual(run_shift(64, 2).stack, [])

    def test_empty_stack_error(self):
        """Сдвиг при пустом стеке — ошибка."""
        text = '[{"op": "shr", "address": 5, "offset": 0}]'
        with self.assertRaises(vm.VMError):
            run_text(text)

    def test_address_out_of_range(self):
        """Адрес результата за памятью данных — ошибка."""
        with self.assertRaises(vm.VMError):
            run_shift(64, 2, base=262143, offset=5)


class ExampleProgramTests(unittest.TestCase):
    """Проверка тестовой программы examples/shr_test.json."""

    def test_results_in_memory(self):
        """Результаты сдвигов сохранены в память."""
        with open(SHR_FILE, encoding="utf-8") as handle:
            machine = run_text(handle.read())
        self.assertEqual(machine.data[0:3], [1024, 255, 67108863])
        self.assertEqual(machine.data[10], 128)
        self.assertEqual(machine.data[11], 15)
        self.assertEqual(machine.data[13], 1024)
        self.assertEqual(machine.data[14], 63)
        self.assertEqual(machine.data[15], 0)
        self.assertEqual(machine.executed, 24)


if __name__ == "__main__":
    unittest.main()
