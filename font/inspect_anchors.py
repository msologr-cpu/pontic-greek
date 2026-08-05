#!/usr/bin/env python3
"""Показывает существующие GPOS mark-якоря для понтийских букв."""
from fontTools.ttLib import TTFont

f = TTFont('font/work/NotoSans.ttf')
cmap = f.getBestCmap()
gpos = f['GPOS'].table

TARGETS = {cmap[cp] for cp in
           [0x3BE, 0x3B6, 0x3C3, 0x3C2, 0x3C8, 0x3BA, 0x3C7, 0x3B3,
            0x3A3, 0x39E, 0x3A8, 0x396, 0x3A7, 0x39A, 0x393,
            0x3B1, 0x3BF, 0x391, 0x39F] if cp in cmap}
MARKS = {cmap[cp]: n for cp, n in
         [(0x30C, 'caron'), (0x306, 'breve'), (0x324, 'dbelow')] if cp in cmap}

print("Ищем MarkBasePos (тип 4) с нашими буквами...\n")

for li, lookup in enumerate(gpos.LookupList.Lookup):
    lt = lookup.LookupType
    for sub in lookup.SubTable:
        # Раскрываем extension
        if lt == 9:
            sub = sub.ExtSubTable
            real_type = sub.LookupType if hasattr(sub, 'LookupType') else None
        else:
            real_type = lt
        if not hasattr(sub, 'BaseCoverage'):
            continue
        bases = sub.BaseCoverage.glyphs
        marks = sub.MarkCoverage.glyphs
        hit_bases = TARGETS & set(bases)
        hit_marks = set(MARKS) & set(marks)
        if not (hit_bases and hit_marks):
            continue

        print(f"--- Lookup #{li} (MarkBasePos), классов: {sub.ClassCount} ---")
        # Классы марок
        for mn in sorted(hit_marks):
            mi = marks.index(mn)
            rec = sub.MarkArray.MarkRecord[mi]
            a = rec.MarkAnchor
            print(f"  МАРКА {MARKS[mn]:8} ({mn}): класс={rec.Class} anchor=({a.XCoordinate},{a.YCoordinate})")
            cls = rec.Class
            print(f"  Базовые якоря для класса {cls}:")
            for bn in sorted(hit_bases):
                bi = bases.index(bn)
                ba = sub.BaseArray.BaseRecord[bi].BaseAnchor[cls]
                if ba:
                    print(f"    {bn:14} -> ({ba.XCoordinate}, {ba.YCoordinate})")
                else:
                    print(f"    {bn:14} -> ЯКОРЯ НЕТ")
            print()
