#!/usr/bin/env python3
"""
Проверка результата: прогоняет понтийские сочетания через движок раскладки
(HarfBuzz) и сравнивает положение гачека ДО и ПОСЛЕ правки шрифта.

Так мы видим настоящие координаты, которые получит телефон, а не догадки.
"""
import sys

try:
    import uharfbuzz as hb
except ImportError:
    print("Нужен uharfbuzz:  pip3 install uharfbuzz")
    sys.exit(1)

PAIRS = [
    ('ζ̌', 'ζ + гачек'), ('ξ̌', 'ξ + гачек'), ('ψ̌', 'ψ + гачек'),
    ('σ̌', 'σ + гачек'), ('ς̌', 'ς + гачек'), ('χ̌', 'χ + гачек'),
    ('κ̌', 'κ + гачек'),
    ('Ζ̌', 'Ζ + гачек'), ('Ξ̌', 'Ξ + гачек'), ('Ψ̌', 'Ψ + гачек'),
    ('Σ̌', 'Σ + гачек'), ('Χ̌', 'Χ + гачек'), ('Κ̌', 'Κ + гачек'),
    ('γ̆', 'γ + бреве'), ('Γ̆', 'Γ + бреве'),
    ('α̤', 'α + 2 точки'), ('ο̤', 'ο + 2 точки'),
]


def shape(path, text):
    with open(path, 'rb') as fh:
        blob = hb.Blob(fh.read())
    face = hb.Face(blob)
    font = hb.Font(face)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf)
    return [(i.codepoint, p.x_offset, p.y_offset)
            for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


def mark_offset(path, text):
    """Возвращает вертикальное смещение комбинируемого знака."""
    out = shape(path, text)
    if len(out) < 2:
        return None
    return out[-1][2]  # y_offset последнего глифа (знака)


BEFORE = 'font/work/NotoSans.ttf'
AFTER = 'font/work/PonticSans-Regular.ttf'

print(f"{'сочетание':16} {'было':>8} {'стало':>8}   результат")
print("-" * 58)

fixed = same = 0
for text, label in PAIRS:
    b = mark_offset(BEFORE, text)
    a = mark_offset(AFTER, text)
    if b == a:
        verdict = "без изменений (и раньше было верно)"
        same += 1
    else:
        verdict = f"ИСПРАВЛЕНО: знак поднят на {a - b}"
        fixed += 1
    print(f"{label:16} {b:>8} {a:>8}   {verdict}")

print("-" * 58)
print(f"Исправлено сочетаний: {fixed}, было корректно изначально: {same}")
