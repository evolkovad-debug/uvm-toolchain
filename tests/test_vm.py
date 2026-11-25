"""Тесты интерпретатора УВМ (этап 3): память, стек, команды, дамп."""

import contextlib
import io
import os
import tempfile
import unittest
from xml.dom import minidom

from src import assembler, codec, dump, vm, vm_cli

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")
COPY_FILE = os.path.join(EXAMPLES, "copy_array.json")


def compile_text(text):
    """Ассемблировать программу из текста JSON в байты."""
    program = assembler.assemble(text)
    return b"".join(codec.encode_program(program))


def run_text(text):
    """Выполнить программу из текста JSON; вернуть машину."""
    machine = vm.Machine(compile_text(text))
    machine.run()
    return machine


class DecodeTests(unittest.TestCase):
    """Проверка чтения машинного кода."""

    def test_decode_spec_bytes(self):
        """Байты из спецификации превращаются в поля A, B, C."""
        code = bytes([0x3D, 0x34, 0x00, 0x82, 0x01])
        fields, size = codec.decode_instruction(code, 0)
        self.assertEqual(fields, {"A": 61, "B": 208, "C": 386})
        self.assertEqual(size, 5)

    def test_decode_with_offset(self):
        """Команда читается с заданного смещения."""
        code = bytes([0x40, 0xFC, 0x00, 0x00, 0x24, 0x35, 0x00])
        fields, size = codec.decode_instruction(code, 4)
        self.assertEqual(fields, {"A": 36, "B": 212})
        self.assertEqual(size, 3)

    def test_unknown_opcode(self):
        """Неизвестный код команды — ошибка."""
        with self.assertRaises(codec.DecodeError):
            codec.decode_instruction(bytes([0x01, 0x00]), 0)

    def test_truncated_command(self):
        """Обрезанная команда — ошибка."""
        with self.assertRaises(codec.DecodeError):
            codec.decode_instruction(bytes([0x40, 0xFC]), 0)


class MachineTests(unittest.TestCase):
    """Проверка выполнения команд."""

    def test_load_const(self):
        """Константа попадает на стек."""
        machine = run_text('[{"op": "load_const", "value": 1009}]')
        self.assertEqual(machine.stack, [1009])

    def test_read(self):
        """Чтение кладёт значение памяти на стек."""
        machine = vm.Machine(compile_text('[{"op": "read", "address": 7}]'))
        machine.data[7] = 42
        machine.run()
        self.assertEqual(machine.stack, [42])

    def test_write_uses_stack_and_offset(self):
        """Запись: значение сверху, под ним адрес, плюс смещение."""
        text = (
            '[{"op": "load_const", "value": 100},'
            ' {"op": "load_const", "value": 7},'
            ' {"op": "write", "offset": 5}]'
        )
        machine = run_text(text)
        self.assertEqual(machine.data[105], 7)
        self.assertEqual(machine.stack, [])

    def test_empty_program(self):
        """Пустая программа ничего не делает."""
        machine = vm.Machine(b"")
        machine.run()
        self.assertEqual(machine.executed, 0)

    def test_empty_stack_error(self):
        """Запись при пустом стеке — ошибка."""
        with self.assertRaises(vm.VMError):
            run_text('[{"op": "write", "offset": 0}]')

    def test_address_out_of_range(self):
        """Адрес за пределами памяти данных — ошибка."""
        text = (
            '[{"op": "load_const", "value": 262143},'
            ' {"op": "load_const", "value": 1},'
            ' {"op": "write", "offset": 1}]'
        )
        with self.assertRaises(vm.VMError):
            run_text(text)

    def test_instruction_and_data_memory_separate(self):
        """Память команд и память данных — разные объекты."""
        machine = run_text('[{"op": "load_const", "value": 1}]')
        self.assertIsInstance(machine.code, bytes)
        self.assertIsInstance(machine.data, list)


class CopyProgramTests(unittest.TestCase):
    """Проверка тестовой программы: копирование массива."""

    def test_array_copied(self):
        """Массив из ячеек 0–4 скопирован в ячейки 20–24."""
        with open(COPY_FILE, encoding="utf-8") as handle:
            machine = run_text(handle.read())
        self.assertEqual(machine.data[0:5], [11, 22, 33, 44, 55])
        self.assertEqual(machine.data[20:25], [11, 22, 33, 44, 55])
        self.assertEqual(machine.executed, 30)


class DumpTests(unittest.TestCase):
    """Проверка формата XML."""

    def test_dump_cells(self):
        """В дампе нужные ячейки с адресами и значениями."""
        data = [0] * 10
        data[3] = 99
        document = minidom.parseString(dump.build_dump(data, 2, 4))
        root = document.documentElement
        cells = [
            (cell.getAttribute("address"), cell.firstChild.data)
            for cell in root.getElementsByTagName("cell")
        ]
        self.assertEqual(cells, [("2", "0"), ("3", "99"), ("4", "0")])
        self.assertEqual(root.getAttribute("first"), "2")
        self.assertEqual(root.getAttribute("last"), "4")


class CliTests(unittest.TestCase):
    """Проверка командной строки интерпретатора."""

    def run_cli(self, argv):
        """Запустить CLI; вернуть код возврата и вывод."""
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            with contextlib.redirect_stderr(io.StringIO()):
                code = vm_cli.main(argv)
        return code, buffer.getvalue()

    def test_end_to_end(self):
        """Программа выполняется, дамп записывается в XML."""
        with open(COPY_FILE, encoding="utf-8") as handle:
            binary = compile_text(handle.read())
        with tempfile.TemporaryDirectory() as folder:
            program = os.path.join(folder, "copy.bin")
            target = os.path.join(folder, "dump.xml")
            with open(program, "wb") as handle:
                handle.write(binary)
            code, output = self.run_cli([program, target, "--range", "20:24"])
            root = minidom.parse(target).documentElement
        values = [
            cell.firstChild.data for cell in root.getElementsByTagName("cell")
        ]
        self.assertEqual(code, vm_cli.EXIT_OK)
        self.assertEqual(values, ["11", "22", "33", "44", "55"])
        self.assertIn("Выполнено команд: 30", output)

    def test_bad_range(self):
        """Некорректный диапазон даёт код 1."""
        for text in ["5", "a:b", "10:5", "0:999999"]:
            code, _ = self.run_cli(["x.bin", "d.xml", "--range", text])
            self.assertEqual(code, vm_cli.EXIT_ERROR)

    def test_missing_program(self):
        """Нет файла с программой — код 1."""
        code, _ = self.run_cli(["no_such.bin", "d.xml", "--range", "0:1"])
        self.assertEqual(code, vm_cli.EXIT_ERROR)


if __name__ == "__main__":
    unittest.main()
