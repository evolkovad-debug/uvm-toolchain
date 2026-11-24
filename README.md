# Ассемблер и интерпретатор УВМ

## 1. Общее описание

Учебная виртуальная машина (УВМ): стековая машина с **разделённой** памятью команд и памятью данных.  
Проект содержит ассемблер (JSON → машинный код) и интерпретатор.

Реализованы этапы 1–3:
- перевод программы из JSON во внутреннее представление и в машинный код;
- интерпретатор с командами `load_const`, `read`, `write`;
- дамп памяти данных в формате XML;
- тестовая программа копирования массива.

## 2. Язык ассемблера и настройки

Программа — JSON-список команд. Каждая команда — объект с полем `op` и операндами:

| op          | Операнды              | Что делает                                      |
|-------------|-----------------------|-------------------------------------------------|
| load_const  | value                 | положить value на стек                          |
| read        | address               | положить на стек память[address]                |
| write       | offset                | снять значение и адрес со стека, записать значение по адресу+offset |
| shr         | address, offset       | логический сдвиг вправо (этап 4)                |

Все операнды — целые числа в допустимом диапазоне поля.

Пример:

```json
[
  {"op": "load_const", "value": 50},
  {"op": "read", "address": 10},
  {"op": "write", "offset": 0}
]
./run.sh asm ИСХОДНИК ВЫХОД [--test]
./run.sh run БИНАРНИК ДАМП START:END [--init FILE]
# Ассемблирование
./run.sh asm examples/spec_tests.json out.bin --test

# Копирование массива (этап 3)
./run.sh asm examples/copy_array.json examples/copy_array.bin
./run.sh run examples/copy_array.bin dump.xml 50:54 --init examples/copy_array_init.txt

# Unit-тесты
python3 -m unittest discover -s tests -t .
./run.sh asm examples/spec_tests.json out.bin --test
./run.sh run examples/copy_array.bin dump.xml 50:54 --init examples/copy_array_init.txt
cat dump.xml
