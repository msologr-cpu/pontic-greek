#!/usr/bin/env python3
"""
Рисует сравнение «было / стало».

ВАЖНО: Pillow без библиотеки libraqm НЕ применяет GPOS-таблицу шрифта,
поэтому его встроенный вывод текста показывал бы обе картинки одинаковыми
и вводил бы в заблуждение. Поэтому здесь мы сами:
  1) прогоняем текст через HarfBuzz (тот же движок, что в Android),
  2) получаем реальные позиции глифов,
  3) рисуем контуры глифов вручную.
Так картинка показывает именно то, что увидит телефон.
"""
from PIL import Image, ImageChops, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
import uharfbuzz as hb

import sys

# По умолчанию — Sans. Можно передать пресет 'serif' первым аргументом,
# либо явно указать BEFORE AFTER OUT.
PRESETS = {
    'sans': ('font/work/NotoSans.ttf', 'font/work/PonticSans-Regular.ttf',
             'font/sample_before_after.png', 'Noto Sans', 'Pontic Sans'),
    'serif': ('font/work/NotoSerif.ttf', 'font/work/PonticSerif-Regular.ttf',
              'font/sample_serif_before_after.png', 'Noto Serif', 'Pontic Serif'),
}
_preset = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in PRESETS else 'sans'
BEFORE, AFTER, OUT, BEFORE_NAME, AFTER_NAME = PRESETS[_preset]

ROWS = [
    ('ξ̌ ζ̌ ψ̌', 'строчные высокие'),
    ('σ̌ ς̌ χ̌ κ̌', 'строчные обычные'),
    ('Σ̌ Ξ̌ Ψ̌', 'заглавные — были сломаны'),
    ('Ζ̌ Χ̌ Κ̌', 'заглавные — были верны'),
    ('γ̆ Γ̆', 'бреве'),
    ('α̤ ο̤ ά̤ ό̤', 'две точки снизу'),
]

SIZE = 64          # кегль в пикселях
FLATNESS = 8       # на сколько отрезков дробим кривую


class PolygonPen(BasePen):
    """Собирает контуры глифа в списки точек для отрисовки в PIL."""

    def __init__(self, glyphSet, scale, ox, oy):
        super().__init__(glyphSet)
        self.scale = scale
        self.ox = ox
        self.oy = oy
        self.contours = []
        self._cur = []

    def _pt(self, p):
        # Y инвертируем: в шрифте ось вверх, в картинке — вниз
        return (self.ox + p[0] * self.scale, self.oy - p[1] * self.scale)

    def _moveTo(self, p):
        if len(self._cur) > 2:
            self.contours.append(self._cur)
        self._cur = [self._pt(p)]

    def _lineTo(self, p):
        self._cur.append(self._pt(p))

    def _curveToOne(self, p1, p2, p3):
        p0 = self._cur[-1]
        a, b, c = self._pt(p1), self._pt(p2), self._pt(p3)
        for i in range(1, FLATNESS + 1):
            t = i / FLATNESS
            u = 1 - t
            x = u**3 * p0[0] + 3*u*u*t * a[0] + 3*u*t*t * b[0] + t**3 * c[0]
            y = u**3 * p0[1] + 3*u*u*t * a[1] + 3*u*t*t * b[1] + t**3 * c[1]
            self._cur.append((x, y))

    def _qCurveToOne(self, p1, p2):
        p0 = self._cur[-1]
        a, b = self._pt(p1), self._pt(p2)
        for i in range(1, FLATNESS + 1):
            t = i / FLATNESS
            u = 1 - t
            x = u*u * p0[0] + 2*u*t * a[0] + t*t * b[0]
            y = u*u * p0[1] + 2*u*t * a[1] + t*t * b[1]
            self._cur.append((x, y))

    def _closePath(self):
        if len(self._cur) > 2:
            self.contours.append(self._cur)
        self._cur = []

    def done(self):
        if len(self._cur) > 2:
            self.contours.append(self._cur)
        return self.contours


def shape(path, text):
    """Возвращает [(glyph_id, x, y, advance)] по данным HarfBuzz."""
    with open(path, 'rb') as fh:
        blob = hb.Blob(fh.read())
    face = hb.Face(blob)
    font = hb.Font(face)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf)
    return [(i.codepoint, p.x_offset, p.y_offset, p.x_advance)
            for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


def draw_text(img, ttf_path, tt, text, x, y, size=SIZE):
    """
    Рисует строку с учётом GPOS-позиционирования от HarfBuzz.

    ВАЖНО про «дырки» в буквах: у σ, α, ο, Φ и др. есть внутренний контур.
    Если рисовать каждый контур обычной заливкой, внутренний контур
    закрашивается — и буква превращается в чёрное пятно.
    Поэтому контуры каждого глифа накладываются друг на друга через XOR:
    внешний контур заливает форму, внутренний — вычитает из неё дырку.
    """
    upem = tt['head'].unitsPerEm
    scale = size / upem
    gs = tt.getGlyphSet()
    order = tt.getGlyphOrder()

    pen_x = 0
    for gid, dx, dy, adv in shape(ttf_path, text):
        name = order[gid]
        pen = PolygonPen(gs, scale, x + (pen_x + dx) * scale, y - dy * scale)
        gs[name].draw(pen)
        contours = pen.done()

        if contours:
            # Маска глифа: каждый контур накладываем по XOR
            glyph_mask = Image.new('1', img.size, 0)
            for contour in contours:
                one = Image.new('1', img.size, 0)
                ImageDraw.Draw(one).polygon(contour, fill=1)
                glyph_mask = ImageChops.logical_xor(glyph_mask, one)
            img.paste((0, 0, 0), (0, 0), glyph_mask)

        pen_x += adv


def main():
    tt_before = TTFont(BEFORE)
    tt_after = TTFont(AFTER)

    W = 1180
    H = 150 + len(ROWS) * 112
    img = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(img)

    ui = ImageFont.truetype(AFTER, 28)
    small = ImageFont.truetype(AFTER, 16)

    d.text((40, 28), 'Понтийские знаки: было и стало', font=ui, fill='black')
    d.text((360, 92), f'БЫЛО ({BEFORE_NAME})', font=small, fill='#c00')
    d.text((760, 92), f'СТАЛО ({AFTER_NAME})', font=small, fill='#080')
    d.line([(40, 118), (W - 40, 118)], fill='#ddd', width=1)

    baseline = 205
    for text, note in ROWS:
        d.text((40, baseline - 30), note, font=small, fill='#555')
        draw_text(img, BEFORE, tt_before, text, 360, baseline)
        draw_text(img, AFTER, tt_after, text, 760, baseline)
        d.line([(720, baseline - 75), (720, baseline + 25)], fill='#eee', width=1)
        baseline += 112

    img.save(OUT)
    print('Сохранено:', OUT)


if __name__ == '__main__':
    main()
