"""Тесты ассемблера УВМ (этап 1): примеры из спецификации."""

import contextlib
import io
import os
import tempfile
import unittest

from src import asm_cli, assembler

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")


def translate(text):
    """Ассемблировать одну команду, заданную JSON-объектом."""
    return assembler.assemble(f"[{text}]")[0]


class SpecificationTests(unittest.TestCase):
    """Тесты из спецификации: поля и их значения."""

    def test_load_const(self):
        """Загрузка константы: A=0, B=1009."""
        result = translate('{"op": "load_const", "value": 1009}')
        self.assertEqual(result, {"A": 0, "B": 1009})

    def test_read(self):
        """Чтение из памяти: A=36, B=212."""
        result = translate('{"op": "read", "address": 212}')
        self.assertEqual(result, {"A": 36, "B": 212})

    def test_write(self):
        """Запись в память: A=38, B=679."""
        result = translate('{"op": "write", "offset": 679}')
        self.assertEqual(result, {"A": 38, "B": 679})

    def test_shr(self):
        """Сдвиг вправо: A=61, B=208, C=386."""
        text = '{"op": "shr", "address": 208, "offset": 386}'
        self.assertEqual(translate(text), {"A": 61, "B": 208, "C": 386})

    def test_example_file(self):
        """Файл examples/spec_tests.json содержит все четыре теста."""
        path = os.path.join(EXAMPLES, "spec_tests.json")
        program = assembler.assemble_file(path)
        self.assertEqual([item["A"] for item in program], [0, 36, 38, 61])


class ErrorTests(unittest.TestCase):
    """Проверка сообщений об ошибках."""

    def assert_error(self, text):
        """Убедиться, что программа text отвергается."""
        with self.assertRaises(assembler.AsmError):
            assembler.assemble(text)

    def test_bad_json(self):
        """Некорректный JSON."""
        self.assert_error("[{")

    def test_not_a_list(self):
        """Программа не список."""
        self.assert_error('{"op": "read"}')

    def test_entry_not_object(self):
        """Команда не объект."""
        self.assert_error("[5]")

    def test_unknown_command(self):
        """Неизвестная команда."""
        self.assert_error('[{"op": "jump"}]')

    def test_missing_op(self):
        """Нет поля op."""
        self.assert_error('[{"address": 1}]')

    def test_missing_field(self):
        """Не указан операнд."""
        self.assert_error('[{"op": "read"}]')

    def test_extra_field(self):
        """Лишнее поле."""
        self.assert_error('[{"op": "read", "address": 1, "x": 2}]')

    def test_negative_value(self):
        """Отрицательное число."""
        self.assert_error('[{"op": "load_const", "value": -1}]')

    def test_value_too_large(self):
        """Число не помещается в поле (write: 15 бит)."""
        self.assert_error('[{"op": "write", "offset": 32768}]')

    def test_max_value_ok(self):
        """Максимальное число для поля допустимо."""
        result = translate('{"op": "write", "offset": 32767}')
        self.assertEqual(result["B"], 32767)

    def test_not_a_number(self):
        """Операнд не число."""
        self.assert_error('[{"op": "read", "address": "5"}]')

    def test_bool_is_not_number(self):
        """true не считается числом."""
        self.assert_error('[{"op": "read", "address": true}]')

    def test_missing_file(self):
        """Файла нет."""
        with self.assertRaises(assembler.AsmError):
            assembler.assemble_file("no_such_file.json")


class CliTests(unittest.TestCase):
    """Проверка командной строки."""

    def run_cli(self, argv):
        """Запустить CLI; вернуть код возврата и вывод."""
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            with contextlib.redirect_stderr(io.StringIO()):
                code = asm_cli.main(argv)
        return code, buffer.getvalue()

    def test_test_mode_output(self):
        """В режиме --test печатаются поля как в спецификации."""
        source = os.path.join(EXAMPLES, "spec_tests.json")
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "out.bin")
            code, output = self.run_cli([source, target, "--test"])
        expected = "A=0, B=1009\nA=36, B=212\nA=38, B=679\n"
        self.assertEqual(code, asm_cli.EXIT_OK)
        self.assertEqual(output, expected + "A=61, B=208, C=386\n")

    def test_no_output_without_test_mode(self):
        """Без --test поля на экран не выводятся."""
        source = os.path.join(EXAMPLES, "spec_tests.json")
        code, output = self.run_cli([source, "out.bin"])
        self.assertEqual(code, asm_cli.EXIT_OK)
        self.assertEqual(output, "")

    def test_error_code(self):
        """Ошибка в программе даёт код 1."""
        code, _ = self.run_cli(["no_such_file.json", "out.bin"])
        self.assertEqual(code, asm_cli.EXIT_ERROR)


if __name__ == "__main__":
    unittest.main()
