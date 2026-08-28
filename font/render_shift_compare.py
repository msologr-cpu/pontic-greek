#!/usr/bin/env python3
"""Рисует сравнение вариантов сдвига гачека: 0 / +15 / +25 / +35.

Только буквы из замечания носитель языка, крупным кеглем, с вертикальной линией
по геометрическому центру буквы — чтобы сдвиг было видно объективно.
"""
import os
import tempfile

from PIL import Image, ImageChops, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
import uharfbuzz as hb

from optical_shift import make_shifted_copy

FLATNESS = 10


class PolygonPen(BasePen):
    def __init__(self, glyphSet, scale, ox, oy):
        super().__init__(glyphSet)
        self.scale = scale
        self.ox = ox
        self.oy = oy
        self.contours = []
        self._cur = []

    def _pt(self, p):
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
            x = u**3*p0[0] + 3*u*u*t*a[0] + 3*u*t*t*b[0] + t**3*c[0]
            y = u**3*p0[1] + 3*u*u*t*a[1] + 3*u*t*t*b[1] + t**3*c[1]
            self._cur.append((x, y))

    def _qCurveToOne(self, p1, p2):
        p0 = self._cur[-1]
        a, b = self._pt(p1), self._pt(p2)
        for i in range(1, FLATNESS + 1):
            t = i / FLATNESS
            u = 1 - t
            x = u*u*p0[0] + 2*u*t*a[0] + t*t*b[0]
            y = u*u*p0[1] + 2*u*t*a[1] + t*t*b[1]
            self._cur.append((x, y))

    def _closePath(self):
        if len(self._cur) > 2:
            self.contours.append(self._cur)
        self._cur = []

    def _endPath(self):
        self._closePath()

    def done(self):
        if len(self._cur) > 2:
            self.contours.append(self._cur)
        return self.contours


def shape(path, text):
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


def draw_text(img, ttf_path, tt, text, x, y, size, color=(0, 0, 0)):
    """Рисует текст, возвращает итоговую ширину в пикселях."""
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
            mask = Image.new('1', img.size, 0)
            for contour in contours:
                one = Image.new('1', img.size, 0)
                ImageDraw.Draw(one).polygon(contour, fill=1)
                mask = ImageChops.logical_xor(mask, one)
            img.paste(color, (0, 0), mask)
        pen_x += adv
    return pen_x * scale


# Буквы из замечания носитель языка, по одной в ячейке (с гачеком U+030C)
LETTERS = ['ξ̌', 'ζ̌', 'χ̌', 'ψ̌', 'Σ̌', 'Ξ̌', 'Ζ̌', 'Χ̌', 'Ψ̌']

SHIFTS = [0, 15, 25, 35]
LABELS = ['сейчас (v5.0)', '+15', '+25', '+35']

SOURCES = [
    ('Pontic Serif', 'font/PonticSerif-Regular.ttf'),
    ('Pontic Sans', 'font/PonticSans-Regular.ttf'),
]


def build_variants(src, tmpdir):
    """Готовит по копии шрифта на каждый вариант сдвига."""
    paths = []
    base = os.path.basename(src).replace('.ttf', '')
    for sh in SHIFTS:
        dst = os.path.join(tmpdir, f'{base}-shift{sh}.ttf')
        make_shifted_copy(src, dst, sh)
        paths.append(dst)
    return paths


def render_family(title, src, out_path):
    tmpdir = tempfile.mkdtemp()
    variants = build_variants(src, tmpdir)

    SIZE = 96
    cell_w = 150
    row_h = 190
    left = 210
    top = 110

    W = left + cell_w * len(LETTERS) + 40
    H = top + row_h * len(SHIFTS) + 40

    img = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(img)

    ui = ImageFont.truetype(src, 30)
    small = ImageFont.truetype(src, 21)

    d.text((40, 34), title, font=ui, fill='black')
    d.line([(40, 84), (W - 40, 84)], fill='#cccccc', width=2)

    for row, (sh, label) in enumerate(zip(SHIFTS, LABELS)):
        y = top + row * row_h
        colour = '#c00000' if sh == 0 else '#0a7a0a'
        d.text((40, y + 78), label, font=small, fill=colour)

        # фон текущей (неисправленной) строки — чтобы отделить визуально
        if sh == 0:
            d.rectangle([left - 12, y - 8, W - 28, y + row_h - 30],
                        fill='#fbf3f3')

        tt = TTFont(variants[row])
        for col, letter in enumerate(LETTERS):
            cx = left + col * cell_w
            baseline = y + 118
            # вертикаль по центру ячейки как опорная линия для глаза
            d.line([(cx + 46, y + 4), (cx + 46, y + 138)],
                   fill='#e3e3e3', width=1)
            draw_text(img, variants[row], tt, letter, cx, baseline, SIZE)

        d.line([(40, y + row_h - 22), (W - 40, y + row_h - 22)],
               fill='#eeeeee', width=1)

    img.save(out_path)
    print(f'Сохранено: {out_path}')


def main():
    for title, src in SOURCES:
        name = 'serif' if 'Serif' in src else 'sans'
        render_family(f'{title} — варианты сдвига гачека',
                      src, f'font/shift_compare_{name}.png')


if __name__ == '__main__':
    main()
