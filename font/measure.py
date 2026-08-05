#!/usr/bin/env python3
"""Измеряет положение букв и комбинируемых знаков в шрифте."""
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen

f = TTFont('font/work/NotoSans.ttf')
cmap = f.getBestCmap()
gs = f.getGlyphSet()

LETTERS = {
    0x3BE: 'xi', 0x3B6: 'zeta', 0x3C3: 'sigma', 0x3C2: 'sigmafinal',
    0x3C8: 'psi', 0x3BA: 'kappa', 0x3C7: 'chi', 0x3B3: 'gamma',
    0x3A3: 'SIGMA', 0x39E: 'XI', 0x3A8: 'PSI', 0x396: 'ZETA',
    0x3A7: 'CHI', 0x39A: 'KAPPA', 0x393: 'GAMMA',
    0x3B1: 'alpha', 0x3BF: 'omicron',
}
MARKS = {0x30C: 'caron', 0x306: 'breve', 0x324: 'dieresisbelow'}


def bounds(cp):
    gn = cmap.get(cp)
    if not gn:
        return gn, None
    bp = BoundsPen(gs)
    gs[gn].draw(bp)
    return gn, bp.bounds


print("unitsPerEm:", f['head'].unitsPerEm)
print("\n=== БУКВЫ ===")
print(f"{'name':12} {'glyph':16} {'yMax':>6} {'xMin':>6} {'xMax':>6}")
for cp, name in LETTERS.items():
    gn, b = bounds(cp)
    if b:
        print(f"{name:12} {gn:16} {b[3]:6.0f} {b[0]:6.0f} {b[2]:6.0f}")

print("\n=== КОМБИНИРУЕМЫЕ ЗНАКИ ===")
for cp, name in MARKS.items():
    gn, b = bounds(cp)
    print(f"{name:16} {gn:16} bounds={tuple(round(v) for v in b) if b else None}")

# Проверяем, есть ли GPOS mark-attachment для этих знаков
print("\n=== GPOS ===")
gpos = f.get('GPOS')
if gpos:
    feats = sorted({fr.FeatureTag for fr in gpos.table.FeatureList.FeatureRecord})
    print("features:", ' '.join(feats))
