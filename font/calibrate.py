#!/usr/bin/env python3
"""Калибровка: какая метрика центра лучше предсказывает выбор дизайнера?

В Noto у ~25 греческих букв якорь для U+030C поставлен ВРУЧНУЮ дизайнерами.
Это наш эталон. Пробуем разные способы вычислить «центр буквы» и смотрим,
какой ближе к руке дизайнера. Победивший применяем к буквам без родного якоря.
"""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.basePen import BasePen

FLAT = 12


class Flattener(BasePen):
    """Разбивает контуры на полилинии для расчёта площади."""

    def __init__(self, glyphSet):
        super().__init__(glyphSet)
        self.contours = []
        self._cur = []

    def _moveTo(self, p):
        self._flush()
        self._cur = [p]

    def _lineTo(self, p):
        self._cur.append(p)

    def _curveToOne(self, p1, p2, p3):
        p0 = self._cur[-1]
        for i in range(1, FLAT + 1):
            t = i / FLAT
            u = 1 - t
            x = u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0]
            y = u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]
            self._cur.append((x, y))

    def _qCurveToOne(self, p1, p2):
        p0 = self._cur[-1]
        for i in range(1, FLAT + 1):
            t = i / FLAT
            u = 1 - t
            x = u*u*p0[0] + 2*u*t*p1[0] + t*t*p2[0]
            y = u*u*p0[1] + 2*u*t*p1[1] + t*t*p2[1]
            self._cur.append((x, y))

    def _flush(self):
        if len(self._cur) > 2:
            self.contours.append(self._cur)
        self._cur = []

    def _closePath(self):
        self._flush()

    def _endPath(self):
        self._flush()

    def done(self):
        self._flush()
        return self.contours


def get_contours(font, gn):
    gs = font.getGlyphSet()
    f = Flattener(gs)
    gs[gn].draw(f)
    return f.done()


def bounds(font, gn):
    gs = font.getGlyphSet()
    bp = BoundsPen(gs)
    gs[gn].draw(bp)
    return bp.bounds


# --------------------------------------------------------------------------
# Метрики «где центр буквы»
# --------------------------------------------------------------------------

def m_bbox(font, gn, b, contours):
    return (b[0] + b[2]) / 2


def _extreme_center(contours, ymin, ymax):
    xs = [p[0] for c in contours for p in c if ymin <= p[1] <= ymax]
    if not xs:
        return None
    return (min(xs) + max(xs)) / 2


def make_topN(frac):
    def f(font, gn, b, contours):
        h = b[3] - b[1]
        return _extreme_center(contours, b[1] + h * frac, b[3] + 1)
    return f


def m_above_baseline(font, gn, b, contours):
    """Центр по части буквы выше базовой линии (отбрасываем нижние хвосты)."""
    xs = [p[0] for c in contours for p in c if p[1] >= 0]
    if not xs:
        return (b[0] + b[2]) / 2
    return (min(xs) + max(xs)) / 2


def _ink_centroid_slice(contours, ylo, yhi, steps=60):
    """Центр масс «чернил» в горизонтальной полосе [ylo, yhi].

    Сканируем полосу горизонтальными линиями, находим закрашенные интервалы
    (even-odd) и считаем взвешенный по площади центр.
    """
    total_a = 0.0
    total_ax = 0.0
    step = (yhi - ylo) / steps
    if step <= 0:
        return None
    for i in range(steps):
        ymid = ylo + (i + 0.5) * step
        xs = []
        for c in contours:
            n = len(c)
            for j in range(n):
                ax, ay = c[j]
                bx, by = c[(j + 1) % n]
                if (ay <= ymid < by) or (by <= ymid < ay):
                    t = (ymid - ay) / (by - ay)
                    xs.append(ax + t * (bx - ax))
        if len(xs) < 2:
            continue
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            w = xs[k + 1] - xs[k]
            if w <= 0:
                continue
            a = w * step
            total_a += a
            total_ax += a * (xs[k] + xs[k + 1]) / 2
    if total_a == 0:
        return None
    return total_ax / total_a


def make_ink_top(frac):
    def f(font, gn, b, contours):
        h = b[3] - b[1]
        return _ink_centroid_slice(contours, b[1] + h * frac, b[3])
    return f


def make_ink_band(frac_lo, frac_hi):
    """Центр масс в полосе от frac_lo до frac_hi высоты (от верха вниз)."""
    def f(font, gn, b, contours):
        h = b[3] - b[1]
        return _ink_centroid_slice(contours, b[3] - h * frac_hi,
                                   b[3] - h * frac_lo)
    return f


METRICS = {
    'bbox':       m_bbox,
    'above_bl':   m_above_baseline,
    'top10':      make_topN(0.90),
    'top20':      make_topN(0.80),
    'top30':      make_topN(0.70),
    'top50':      make_topN(0.50),
    'ink_top20':  make_ink_top(0.80),
    'ink_top30':  make_ink_top(0.70),
    'ink_top50':  make_ink_top(0.50),
    'ink_band15': make_ink_band(0.0, 0.15),
    'ink_band25': make_ink_band(0.0, 0.25),
}


# --------------------------------------------------------------------------
# Извлечение эталонных якорей
# --------------------------------------------------------------------------

def iter_markbase(font):
    gpos = font['GPOS'].table
    for lu in gpos.LookupList.Lookup:
        for sub in lu.SubTable:
            if lu.LookupType == 9:
                sub = sub.ExtSubTable
            if hasattr(sub, 'BaseCoverage') and hasattr(sub, 'MarkCoverage'):
                yield sub


GREEK = list(range(0x391, 0x3AA)) + list(range(0x3B1, 0x3CA))

# Буквы, на которые жалуется Д.И. (нужен сдвиг вправо)
COMPLAINTS = set('ξζχψΣΞΖΧΨ')


def collect(font):
    """Возвращает (rows, offset) где rows = [(символ, эталон_центра, метрики)]."""
    cmap = font.getBestCmap()
    caron = cmap.get(0x30C)

    sub = None
    for s in iter_markbase(font):
        if caron in s.MarkCoverage.glyphs:
            sub = s
            break
    if sub is None:
        return [], 0.0

    mi = sub.MarkCoverage.glyphs.index(caron)
    mrec = sub.MarkArray.MarkRecord[mi]
    mclass = mrec.Class
    cb = bounds(font, caron)
    offset = (cb[0] + cb[2]) / 2 - mrec.MarkAnchor.XCoordinate

    cover = dict(zip(sub.BaseCoverage.glyphs, sub.BaseArray.BaseRecord))

    rows = []
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
        b = bounds(font, gn)
        if not b:
            continue
        contours = get_contours(font, gn)
        vals = {}
        for name, fn in METRICS.items():
            try:
                vals[name] = fn(font, gn, b, contours)
            except Exception:
                vals[name] = None
        rows.append((chr(cp), a.XCoordinate + offset, vals))
    return rows, offset


def analyse(path):
    font = TTFont(path)
    rows, _ = collect(font)
    print(f"\n=== {path} ===")
    print(f"эталонных букв (якорь поставлен дизайнером Noto): {len(rows)}")
    if not rows:
        return

    print(f"\n{'метрика':<13}{'ср.|ошибка|':>12}{'макс':>8}{'смещение':>10}")
    results = []
    for name in METRICS:
        errs = [nat - v[name] for _, nat, v in rows if v.get(name) is not None]
        if not errs:
            continue
        ae = [abs(e) for e in errs]
        results.append((sum(ae) / len(ae), name, max(ae), sum(errs) / len(errs)))
    for mae, name, mx, bias in sorted(results):
        print(f"{name:<13}{mae:>12.1f}{mx:>8.1f}{bias:>+10.1f}")

    best = sorted(results)[0][1]
    print(f"\nЛучшая метрика: {best}")
    print(f"\nПобуквенно (эталон − метрика {best}):")
    for ch, nat, v in rows:
        if v.get(best) is None:
            continue
        mark = '  <-- жалоба' if ch in COMPLAINTS else ''
        print(f"  {ch}  эталон={nat:7.0f}  {best}={v[best]:7.0f}  "
              f"ошибка={nat - v[best]:+7.1f}{mark}")


if __name__ == '__main__':
    for p in sys.argv[1:]:
        analyse(p)
