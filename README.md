# Ассемблер и интерпретатор УВМ (вариант 5)

## 1. Общее описание

Учебная виртуальная машина (УВМ) — стековая машина с **разделённой** памятью команд и памятью данных.

Реализованы все этапы практической работы:

- **Этап 1–2**: ассемблер (JSON → промежуточное представление → машинный код)
- **Этап 3**: интерпретатор + команды `load_const`, `read`, `write` + дамп XML
- **Этап 4**: команда `shr` (логический сдвиг вправо)
- **Этап 5**: поэлементный `shr` над двумя векторами длины 5 + 3 примера

## 2. Язык ассемблера

Программа — JSON-список команд:

| op          | Операнды        | Описание |
|-------------|-----------------|----------|
| load_const  | value           | положить константу на стек |
| read        | address         | положить на стек `memory[address]` |
| write       | offset          | снять значение и адрес, записать значение по `address + offset` |
| shr         | address, offset | `memory[dest + offset] = memory[address] >> shift` |

Пример:

```json
[
  {"op": "load_const", "value": 100},
  {"op": "read", "address": 200},
  {"op": "shr", "address": 100, "offset": 0}
]
./run.sh asm ИСХОДНИК ВЫХОД [--test]
./run.sh run БИНАРНИК ДАМП START:END [--init FILE]
python3 -m unittest discover -s tests -t .
./run.sh asm examples/stage5_main.json examples/stage5_main.bin
./run.sh run examples/stage5_main.bin dump.xml 100:105 --init examples/stage5_main_init.txt
