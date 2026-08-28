#!/usr/bin/env python3
"""Диагностика: где реально стоит гачек над буквой в собранном шрифте.

Показывает для каждой целевой буквы:
  - геометрический центр bbox буквы
  - центр «верхней зоны» (то, по чему считался якорь)
  - куда фактически попадает центр гачека при текущем BaseAnchor
  - смещение факт-центра гачека относительно центра bbox и верхней зоны
"""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen

TARGETS = [0x3BE, 0x3B6, 0x3C7, 0x3C8, 0x3C3, 0x3C2, 0x3BA, 0x3B3,
           0x3A3, 0x39E, 0x396, 0x3A7, 0x3A8, 0x39A, 0x393]

# Буквы, по которым носитель языка просит сдвиг вправо
COMPLAINTS = set('ξζχψΣΞΖΧΨ')


def bounds(font, gn):
    gs = font.getGlyphSet()
    bp = BoundsPen(gs)
    gs[gn].draw(bp)
    return bp.bounds


def iter_markbase(font):
    gpos = font['GPOS'].table
    for lu in gpos.LookupList.Lookup:
        if lu.LookupType == 4:
            for sub in lu.SubTable:
                yield sub
        elif lu.LookupType == 9:
            for sub in lu.SubTable:
                if sub.ExtensionLookupType == 4:
                    yield sub.ExtSubTable


def find_markbase(font, caron):
    for sub in iter_markbase(font):
        if caron in sub.MarkCoverage.glyphs:
            return sub
    return None


def main(path):
    font = TTFont(path)
    cmap = font.getBestCmap()
    caron = cmap.get(0x30C)
    sub = find_markbase(font, caron)

    mi = sub.MarkCoverage.glyphs.index(caron)
    mrec = sub.MarkArray.MarkRecord[mi]
    mclass = mrec.Class
    manchor_x = mrec.MarkAnchor.XCoordinate
    cb = bounds(font, caron)
    caron_center = (cb[0] + cb[2]) / 2
    offset = caron_center - manchor_x

    print(f"\n=== {path} ===")
    print(f"гачек: bbox={cb}, MarkAnchor.X={manchor_x}, "
          f"центр={caron_center:.1f}, offset={offset:.1f}, class={mclass}")
    print(f"{'бкв':<4}{'bbox':<22}{'ц.bbox':>8}{'BaseAnchor':>12}"
          f"{'ц.гачека':>10}{'Δ к ц.bbox':>12}")

    cover = dict(zip(sub.BaseCoverage.glyphs, sub.BaseArray.BaseRecord))
    for cp in TARGETS:
        gn = cmap.get(cp)
        if not gn or gn not in cover:
            print(f"{chr(cp):<4}— нет якоря")
            continue
        rec = cover[gn]
        a = rec.BaseAnchor[mclass] if mclass < len(rec.BaseAnchor) else None
        if a is None:
            print(f"{chr(cp):<4}— якорь класса {mclass} пуст")
            continue
        b = bounds(font, gn)
        bc = (b[0] + b[2]) / 2
        actual = a.XCoordinate + offset
        mark = '  <-- жалоба' if chr(cp) in COMPLAINTS else ''
        print(f"{chr(cp):<4}{str(tuple(round(v) for v in b)):<22}"
              f"{bc:>8.0f}{a.XCoordinate:>12}{actual:>10.0f}"
              f"{actual - bc:>12.0f}{mark}")


if __name__ == '__main__':
    for p in sys.argv[1:]:
        main(p)
