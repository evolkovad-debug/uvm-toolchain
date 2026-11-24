# Ассемблер и интерпретатор УВМ (вариант 5)

## 1. Общее описание

Учебная виртуальная машина (УВМ) — стековая машина с разделённой памятью команд и памятью данных.

Реализованы все этапы практической работы:

- Этап 1–2: ассемблер (JSON → промежуточное представление → машинный код)
- Этап 3: интерпретатор + команды load_const, read, write + дамп XML
- Этап 4: команда shr (логический сдвиг вправо)
- Этап 5: поэлементный shr над двумя векторами длины 5 + 3 примера

## 2. Язык ассемблера

Программа — JSON-список команд.

| op         | Операнды        | Описание |
|------------|-----------------|----------|
| load_const | value           | положить константу на стек |
| read       | address         | положить на стек memory[address] |
| write      | offset          | снять значение и адрес, записать по address+offset |
| shr        | address, offset | memory[dest+offset] = memory[address] >> shift |

## 3. Запуск

Ассемблер:
./run.sh asm ИСХОДНИК ВЫХОД [--test]

Интерпретатор:
./run.sh run БИНАРНИК ДАМП START:END [--init FILE]

Тесты:
python3 -m unittest discover -s tests -t .

## 4. Примеры этапа 5

Основной пример:
./run.sh asm examples/stage5_main.json examples/stage5_main.bin
./run.sh run examples/stage5_main.bin dump.xml 100:105 --init examples/stage5_main_init.txt

Результат:
100: 240 >> 3 = 30
101: 200 >> 2 = 50
102: 128 >> 5 = 4
103: 255 >> 1 = 127
104:  64 >> 4 = 4

Ещё два примера: stage5_example2 и stage5_example3.
