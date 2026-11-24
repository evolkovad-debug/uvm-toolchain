"""Тесты машинного кода и ассемблера (этап 2): байты из спецификации."""

import contextlib
import io
import os
import tempfile
import unittest

from src import asm_cli, assembler, codec

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")
SPEC_FILE = os.path.join(EXAMPLES, "spec_tests.json")
SPEC_BYTES = [
    bytes([0x40, 0xFC, 0x00, 0x00]),
    bytes([0x24, 0x35, 0x00]),
    bytes([0xE6, 0xA9, 0x00]),
    bytes([0x3D, 0x34, 0x00, 0x82, 0x01]),
]


def encode(text):
    """Ассемблировать и закодировать одну команду из JSON."""
    return codec.encode_program(assembler.assemble(f"[{text}]"))[0]


class SpecificationBytesTests(unittest.TestCase):
    """Тесты из спецификации: байтовые последовательности."""

    def test_load_const(self):
        """Загрузка константы (A=0, B=1009)."""
        result = encode('{"op": "load_const", "value": 1009}')
        self.assertEqual(result, SPEC_BYTES[0])

    def test_read(self):
        """Чтение из памяти (A=36, B=212)."""
        result = encode('{"op": "read", "address": 212}')
        self.assertEqual(result, SPEC_BYTES[1])

    def test_write(self):
        """Запись в память (A=38, B=679)."""
        result = encode('{"op": "write", "offset": 679}')
        self.assertEqual(result, SPEC_BYTES[2])

    def test_shr(self):
        """Сдвиг вправо (A=61, B=208, C=386)."""
        result = encode('{"op": "shr", "address": 208, "offset": 386}')
        self.assertEqual(result, SPEC_BYTES[3])

    def test_example_file(self):
        """Файл spec_tests.json даёт все четыре последовательности."""
        program = assembler.assemble_file(SPEC_FILE)
        self.assertEqual(codec.encode_program(program), SPEC_BYTES)

    def test_format_bytes(self):
        """Байты печатаются как в спецификации."""
        text = codec.format_bytes(SPEC_BYTES[3])
        self.assertEqual(text, "0x3D, 0x34, 0x00, 0x82, 0x01")

    def test_max_values_fit(self):
        """Максимальные значения полей помещаются в команду shr."""
        text = '{"op": "shr", "address": 262143, "offset": 32767}'
        result = encode(text)
        self.assertEqual(len(result), 5)
        self.assertLess(int.from_bytes(result, "little"), 1 << 39)


class CliTests(unittest.TestCase):
    """Проверка командной строки ассемблера."""

    def run_cli(self, argv):
        """Запустить CLI; вернуть код возврата и вывод."""
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            with contextlib.redirect_stderr(io.StringIO()):
                code = asm_cli.main(argv)
        return code, buffer.getvalue()

    def test_binary_file_written(self):
        """В двоичный файл записаны байты всех команд."""
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "out.bin")
            code, _ = self.run_cli([SPEC_FILE, target])
            with open(target, "rb") as handle:
                data = handle.read()
        self.assertEqual(code, asm_cli.EXIT_OK)
        self.assertEqual(data, b"".join(SPEC_BYTES))

    def test_count_printed(self):
        """Выводится число ассемблированных команд."""
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "out.bin")
            _, output = self.run_cli([SPEC_FILE, target])
        self.assertEqual(output, "Ассемблировано команд: 4\n")

    def test_test_mode_prints_bytes(self):
        """В режиме --test печатаются байты как в спецификации."""
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "out.bin")
            _, output = self.run_cli([SPEC_FILE, target, "--test"])
        lines = output.splitlines()
        self.assertEqual(lines[1], "0x40, 0xFC, 0x00, 0x00")
        self.assertEqual(lines[2], "0x24, 0x35, 0x00")
        self.assertEqual(lines[3], "0xE6, 0xA9, 0x00")
        self.assertEqual(lines[4], "0x3D, 0x34, 0x00, 0x82, 0x01")

    def test_source_error(self):
        """Ошибка в исходном файле даёт код 1."""
        code, _ = self.run_cli(["no_such_file.json", "out.bin"])
        self.assertEqual(code, asm_cli.EXIT_ERROR)

    def test_cannot_write_output(self):
        """Недоступная папка результата даёт код 1."""
        target = os.path.join("no_such_dir", "out.bin")
        code, _ = self.run_cli([SPEC_FILE, target])
        self.assertEqual(code, asm_cli.EXIT_ERROR)


if __name__ == "__main__":
    unittest.main()
