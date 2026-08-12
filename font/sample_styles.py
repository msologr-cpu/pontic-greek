#!/usr/bin/env python3
"""
Рисует образец всех четырёх начертаний одного семейства в одну картинку:
Regular, Italic, Bold, Bold Italic — чтобы был виден контраст между обычным
и полужирным и настоящий курсив (просьба Д.И.).

Как и sample.py, рисует через HarfBuzz + ручную отрисовку контуров, чтобы
показать именно то, что даёт движок (с правильным GPOS-позиционированием
понтийских знаков).
"""
import sys
from PIL import Image, ImageChops, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
import uharfbuzz as hb

# переиспользуем PolygonPen и shape из sample.py
from sample import PolygonPen, shape, SIZE

FAMILY = sys.argv[1] if len(sys.argv) > 1 else 'serif'
FAM_NAME = 'Pontic Serif' if FAMILY == 'serif' else 'Pontic Sans'
PREFIX = 'PonticSerif' if FAMILY == 'serif' else 'PonticSans'

STYLES = [
    ('Regular',    'Обычный'),
    ('Italic',     'Курсив'),
    ('Bold',       'Полужирный'),
    ('BoldItalic', 'Полужирный курсив'),
]

# Понтийская строка со всеми диакритиками
TEXT = 'ζ̌ ξ̌ ψ̌ σ̌ ς̌ χ̌ κ̌ Σ̌ Ξ̌ Ψ̌ γ̆ α̤ ό̤'


def draw_text(img, ttf_path, tt, text, x, y, size=SIZE):
    gs = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    upem = tt['head'].unitsPerEm
    scale = size / upem
    pen_x = 0
    for gid, dx, dy, adv in shape(ttf_path, text):
        name = order[gid]
        pen = PolygonPen(gs, scale, x + (pen_x + dx) * scale, y - dy * scale)
        gs[name].draw(pen)
        contours = pen.done()
        if contours:
            glyph_mask = Image.new('1', img.size, 0)
            for contour in contours:
                one = Image.new('1', img.size, 0)
                ImageDraw.Draw(one).polygon(contour, fill=1)
                glyph_mask = ImageChops.logical_xor(glyph_mask, one)
            img.paste((0, 0, 0), (0, 0), glyph_mask)
        pen_x += adv


def main():
    W = 1150
    H = 130 + len(STYLES) * 108
    img = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(img)

    reg_path = f'font/{PREFIX}-Regular.ttf'
    ui = ImageFont.truetype(reg_path, 30)
    small = ImageFont.truetype(reg_path, 17)

    d.text((40, 30), f'{FAM_NAME} — четыре начертания', font=ui, fill='black')
    d.line([(40, 90), (W - 40, 90)], fill='#ddd', width=1)

    baseline = 175
    for style, label in STYLES:
        path = f'font/{PREFIX}-{style}.ttf'
        tt = TTFont(path)
        d.text((40, baseline - 34), label, font=small, fill='#555')
        draw_text(img, path, tt, TEXT, 330, baseline)
        baseline += 108

    out = f'font/sample_{FAMILY}_styles.png'
    img.save(out)
    print('Сохранено:', out)


if __name__ == '__main__':
    main()
