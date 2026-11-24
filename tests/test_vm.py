"""Тесты интерпретатора УВМ (этап 3)."""

import os
import tempfile
import unittest
import xml.etree.ElementTree as ET

from src import assembler, codec, vm
from src.interp_cli import main as interp_main


EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")


class ArrayCopyTest(unittest.TestCase):
    """Тестовая программа: копирование массива (требование этапа 3)."""

    def test_copy_array(self):
        """Копирование массива [111, 222, 333, 444] с адреса 10 на адрес 50."""
        # Ассемблируем программу
        program = assembler.assemble_file(
            os.path.join(EXAMPLES, "copy_array.json")
        )
        binary = b"".join(codec.encode_program(program))

        # Создаём машину и инициализируем память данных
        machine = vm.VirtualMachine()
        machine.load_program(binary)
        machine.data[10] = 111
        machine.data[11] = 222
        machine.data[12] = 333
        machine.data[13] = 444

        machine.run()

        # Проверяем результат копирования
        self.assertEqual(machine.data[50], 111)
        self.assertEqual(machine.data[51], 222)
        self.assertEqual(machine.data[52], 333)
        self.assertEqual(machine.data[53], 444)

    def test_xml_dump_format(self):
        """Дамп памяти сохраняется в формате XML."""
        with tempfile.TemporaryDirectory() as folder:
            bin_path = os.path.join(folder, "prog.bin")
            dump_path = os.path.join(folder, "dump.xml")
            init_path = os.path.join(folder, "init.txt")

            # Готовим бинарник
            program = assembler.assemble_file(
                os.path.join(EXAMPLES, "copy_array.json")
            )
            with open(bin_path, "wb") as f:
                f.write(b"".join(codec.encode_program(program)))

            # Файл инициализации
            with open(init_path, "w", encoding="utf-8") as f:
                f.write("10 111\n11 222\n12 333\n13 444\n")

            # Запускаем интерпретатор
            code = interp_main([bin_path, dump_path, "50:54", "--init", init_path])
            self.assertEqual(code, 0)

            # Проверяем XML
            tree = ET.parse(dump_path)
            root = tree.getroot()
            self.assertEqual(root.tag, "memory")
            self.assertEqual(root.get("start"), "50")
            self.assertEqual(root.get("end"), "54")

            cells = root.findall("cell")
            self.assertEqual(len(cells), 4)
            self.assertEqual(cells[0].get("value"), "111")
            self.assertEqual(cells[1].get("value"), "222")
            self.assertEqual(cells[2].get("value"), "333")
            self.assertEqual(cells[3].get("value"), "444")


if __name__ == "__main__":
    unittest.main()
