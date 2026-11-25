"""Дамп памяти данных УВМ в формате XML."""

XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'


def build_dump(data, first, last):
    """Собрать XML с ячейками памяти от адреса first до last включительно."""
    lines = [XML_HEADER, f'<memory first="{first}" last="{last}">']
    for address in range(first, last + 1):
        lines.append(f'  <cell address="{address}">{data[address]}</cell>')
    lines.append("</memory>")
    return "\n".join(lines) + "\n"
