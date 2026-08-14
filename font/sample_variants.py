#!/usr/bin/env python3
"""
Рисует все 4 начертания Pontic Serif / Pontic Sans для визуальной проверки.
"""
from PIL import Image, ImageChops, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
import uharfbuzz as hb
import sys

FLATNESS = 8

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


def draw_text(img, ttf_path, tt, text, x, y, size=52, color=(0, 0, 0)):
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
            glyph_mask = Image.new('1', img.size, 0)
            for contour in contours:
                one = Image.new('1', img.size, 0)
                ImageDraw.Draw(one).polygon(contour, fill=1)
                glyph_mask = ImageChops.logical_xor(glyph_mask, one)
            img.paste(color, (0, 0), glyph_mask)
        pen_x += adv


PRESETS = {
    'serif': {
        'title': 'Pontic Serif — все начертания',
        'variants': [
            ('Regular', 'font/work/PonticSerif-Regular.ttf'),
            ('Italic', 'font/work/PonticSerif-Italic.ttf'),
            ('Bold', 'font/work/PonticSerif-Bold.ttf'),
            ('Bold Italic', 'font/work/PonticSerif-BoldItalic.ttf'),
        ],
        'out': 'font/sample_serif_all_variants.png',
    },
    'sans': {
        'title': 'Pontic Sans — все начертания',
        'variants': [
            ('Regular', 'font/work/PonticSans-Regular.ttf'),
            ('Italic', 'font/work/PonticSans-Italic.ttf'),
            ('Bold', 'font/work/PonticSans-Bold.ttf'),
            ('Bold Italic', 'font/work/PonticSans-BoldItalic.ttf'),
        ],
        'out': 'font/sample_sans_all_variants.png',
    },
}

ROWS = [
    'ψ̌ ξ̌ ζ̌ σ̌ χ̌ κ̌',
    'Σ̌ Ξ̌ Ψ̌ Ζ̌ Χ̌ Κ̌',
    'γ̆ Γ̆ α̤ ο̤ ά̤ ό̤',
]


def main():
    preset_name = sys.argv[1] if len(sys.argv) > 1 else 'serif'
    preset = PRESETS[preset_name]

    W = 1200
    col_w = 280
    label_w = W - col_w * len(preset['variants'])

    row_h = 90
    header_h = 100
    H = header_h + len(ROWS) * row_h * len(preset['variants']) + len(ROWS) * 30

    # Simpler layout: one column per variant, all rows shown
    H = header_h + 40 + len(preset['variants']) * (30 + len(ROWS) * row_h + 20)
    img = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(img)

    # Use one of the fonts for UI text
    ui_path = preset['variants'][0][1]
    ui = ImageFont.truetype(ui_path, 24)
    small = ImageFont.truetype(ui_path, 16)

    d.text((40, 30), preset['title'], font=ui, fill='black')
    d.line([(40, 70), (W - 40, 70)], fill='#ddd', width=1)

    y_cursor = header_h

    for var_name, var_path in preset['variants']:
        tt = TTFont(var_path)

        # Variant label
        d.text((40, y_cursor), var_name, font=small, fill='#c00')
        y_cursor += 28

        for row_text in ROWS:
            draw_text(img, var_path, tt, row_text, 60, y_cursor + 60, size=52)
            y_cursor += row_h

        y_cursor += 15
        d.line([(40, y_cursor), (W - 40, y_cursor)], fill='#eee', width=1)
        y_cursor += 5

    img.save(preset['out'])
    print(f'Сохранено: {preset["out"]}')


if __name__ == '__main__':
    main()
