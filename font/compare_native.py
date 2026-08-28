#!/usr/bin/env python3
"""Сравнивает РОДНЫЕ якоря Noto с тем, что вычисляет наш алгоритм.

Идея: у части греческих букв Noto уже имеет якорь для U+030C, отрисованный
вручную дизайнерами. Если наш автоматический расчёт систематически расходится
с рукой дизайнера, эту разницу можно измерить и применить как поправку
к буквам, у которых родного якоря нет.
"""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.basePen import BasePen


class PointCollector(BasePen):
    def __init__(self, glyphSet):
        super().__init__(glyphSet)
        self.points = []

    def _moveTo(self, pt):
        self.points.append(pt)

    def _lineTo(self, pt):
        self.points.append(pt)

    def _curveToOne(self, p1, p2, p3):
        self.points.extend([p1, p2, p3])

    def _qCurveToOne(self, p1, p2):
        self.points.extend([p1, p2])

    def _closePath(self):
        pass

    def _endPath(self):
        pass


def bounds(font, gn):
    gs = font.getGlyphSet()
    bp = BoundsPen(gs)
    gs[gn].draw(bp)
    return bp.bounds


def top_zone_center(font, gn, frac=0.80):
    b = bounds(font, gn)
    if not b:
        return None
    gs = font.getGlyphSet()
    pc = PointCollector(gs)
    gs[gn].draw(pc)
    h = b[3] - b[1]
    thresh = b[1] + h * frac
    pts = [p for p in pc.points if p[1] >= thresh]
    if not pts:
        return (b[0] + b[2]) / 2
    return (min(p[0] for p in pts) + max(p[0] for p in pts)) / 2


def iter_markbase(font):
    gpos = font['GPOS'].table
    for lu in gpos.LookupList.Lookup:
        for sub in lu.SubTable:
            if lu.LookupType == 9:
                sub = sub.ExtSubTable
            if hasattr(sub, 'BaseCoverage') and hasattr(sub, 'MarkCoverage'):
                yield sub


# Все греческие буквы, которые нас интересуют + соседи для статистики
GREEK = list(range(0x391, 0x3AA)) + list(range(0x3B1, 0x3CA))


def main(path):
    font = TTFont(path)
    cmap = font.getBestCmap()
    caron = cmap.get(0x30C)
    print(f"\n=== {path} ===")

    sub = None
    for s in iter_markbase(font):
        if caron in s.MarkCoverage.glyphs:
            sub = s
            break
    if sub is None:
        print("нет подтаблицы с гачеком")
        return

    mi = sub.MarkCoverage.glyphs.index(caron)
    mrec = sub.MarkArray.MarkRecord[mi]
    mclass = mrec.Class
    manchor_x = mrec.MarkAnchor.XCoordinate
    cb = bounds(font, caron)
    caron_geom_center = (cb[0] + cb[2]) / 2
    offset = caron_geom_center - manchor_x

    print(f"гачек bbox={tuple(round(v) for v in cb)}  MarkAnchor.X={manchor_x}  "
          f"geom_center={caron_geom_center:.1f}  offset={offset:.1f}")

    cover = dict(zip(sub.BaseCoverage.glyphs, sub.BaseArray.BaseRecord))

    print(f"\n{'бкв':<5}{'родной BaseAnchor':>18}{'родной ц.гачека':>17}"
          f"{'наш top20%':>12}{'разница':>10}")
    diffs = []
    for cp in GREEK:
        gn = cmap.get(cp)
        if not gn or gn not in cover:
            continue
        rec = cover[gn]
        if mclass >= len(rec.BaseAnchor):
            continue
        a = rec.BaseAnchor[mclass]
        if a is None:
            continue
        native_caron_center = a.XCoordinate + offset
        ours = top_zone_center(font, gn)
        if ours is None:
            continue
        d = native_caron_center - ours
        diffs.append((chr(cp), d))
        print(f"{chr(cp):<5}{a.XCoordinate:>18}{native_caron_center:>17.0f}"
              f"{ours:>12.0f}{d:>10.1f}")

    if diffs:
        vals = [d for _, d in diffs]
        vals_sorted = sorted(vals)
        median = vals_sorted[len(vals_sorted) // 2]
        print(f"\nбукв с родным якорем: {len(vals)}")
        print(f"средняя разница (родной − наш): {sum(vals)/len(vals):+.1f}")
        print(f"медиана:                        {median:+.1f}")


if __name__ == '__main__':
    for p in sys.argv[1:]:
        main(p)
