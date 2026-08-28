#!/usr/bin/env python3
"""Картинка «до / после» для Д.И. — показывает результат правки v5.1.

Слева-направо по буквам, две строки: как было в v5.0 и как стало в v5.1.
Отдельной группой — ψ̌ и Ψ̌, которые намеренно не менялись.
"""
import os

from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

from render_shift_compare import draw_text

CHANGED = ['ξ̌', 'ζ̌', 'χ̌', 'Σ̌', 'Ξ̌', 'Ζ̌', 'Χ̌']
UNCHANGED = ['ψ̌', 'Ψ̌']

PAIRS = [
    ('Pontic Serif', '/tmp/before-serif.ttf', 'font/PonticSerif-Regular.ttf',
     'font/before_after_serif.png'),
    ('Pontic Sans', '/tmp/before-sans.ttf', 'font/PonticSans-Regular.ttf',
     'font/before_after_sans.png'),
]


def render(title, before, after, out):
    SIZE = 104
    cell = 160
    left = 250
    top = 120
    row_h = 200

    n = len(CHANGED) + 1 + len(UNCHANGED)
    W = left + cell * n + 50
    H = top + row_h * 2 + 70

    img = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(img)

    ui = ImageFont.truetype(after, 32)
    lbl = ImageFont.truetype(after, 23)
    small = ImageFont.truetype(after, 19)

    d.text((45, 36), f'{title} — гачек, было и стало', font=ui, fill='black')
    d.line([(45, 92), (W - 45, 92)], fill='#c8c8c8', width=2)

    sep_x = left + len(CHANGED) * cell + cell // 2

    for row, (path, label, colour) in enumerate([
        (before, 'было (v5.0)', '#b00000'),
        (after, 'стало (v5.1)', '#0a7a0a'),
    ]):
        y = top + row * row_h
        d.text((45, y + 84), label, font=lbl, fill=colour)
        tt = TTFont(path)

        for col, ch in enumerate(CHANGED):
            x = left + col * cell
            d.line([(x + 50, y + 6), (x + 50, y + 146)],
                   fill='#ebebeb', width=1)
            draw_text(img, path, tt, ch, x, y + 126, SIZE)

        for k, ch in enumerate(UNCHANGED):
            x = sep_x + 30 + k * cell
            d.line([(x + 50, y + 6), (x + 50, y + 146)],
                   fill='#ebebeb', width=1)
            draw_text(img, path, tt, ch, x, y + 126, SIZE)

    # разделитель между «исправлено» и «не менялось»
    d.line([(sep_x, top - 10), (sep_x, top + row_h * 2 - 40)],
           fill='#b8b8b8', width=2)
    d.text((left, top - 34), 'исправлено (сдвиг вправо)',
           font=small, fill='#0a7a0a')
    d.text((sep_x + 30, top - 34), 'не менялось', font=small, fill='#777777')

    img.save(out)
    print(f'Сохранено: {out}')


if __name__ == '__main__':
    for title, b, a, out in PAIRS:
        if os.path.exists(b):
            render(title, b, a, out)
        else:
            print(f'нет файла «до»: {b}')
