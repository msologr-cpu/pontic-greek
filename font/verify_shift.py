#!/usr/bin/env python3
"""Сверяет два шрифта и печатает РЕАЛЬНУЮ разницу якорей гачека по буквам.

Нужен, чтобы доказать: сдвиг применён ровно к тем буквам, о которых просил
Д.И., ровно на согласованную величину, и ни к каким другим.
"""
import sys
from fontTools.ttLib import TTFont

ASKED = 'ξζχΣΞΖΧ'      # семь букв из замечания (после уточнения)
EXCLUDED = 'ψΨ'         # Д.И.: «и так нормальные»
WATCH = 'ξζχψΣΞΖΧΨσςκγΚΓ'


def anchors(path):
    """{символ: X якоря гачека} по первой подтаблице, где есть гачек."""
    font = TTFont(path)
    cmap = font.getBestCmap()
    caron = cmap.get(0x30C)
    gpos = font['GPOS'].table

    for lu in gpos.LookupList.Lookup:
        for sub in lu.SubTable:
            if lu.LookupType == 9:
                sub = sub.ExtSubTable
            if not (hasattr(sub, 'BaseCoverage') and hasattr(sub, 'MarkCoverage')):
                continue
            if caron not in sub.MarkCoverage.glyphs:
                continue
            mi = sub.MarkCoverage.glyphs.index(caron)
            mclass = sub.MarkArray.MarkRecord[mi].Class
            cover = dict(zip(sub.BaseCoverage.glyphs, sub.BaseArray.BaseRecord))
            out = {}
            for ch in WATCH:
                gn = cmap.get(ord(ch))
                if not gn or gn not in cover:
                    continue
                rec = cover[gn]
                if mclass >= len(rec.BaseAnchor):
                    continue
                a = rec.BaseAnchor[mclass]
                if a is not None:
                    out[ch] = a.XCoordinate
            return out
    return {}


def main(before, after, expected=15):
    a = anchors(before)
    b = anchors(after)
    print(f"\n=== {after} ===")
    ok = True
    for ch in WATCH:
        if ch not in a or ch not in b:
            continue
        d = b[ch] - a[ch]
        if ch in ASKED:
            good = (d == expected)
            note = f"просил Д.И. → ожидаем +{expected}"
        else:
            good = (d == 0)
            note = "не трогаем → ожидаем 0"
            if ch in EXCLUDED:
                note = "«и так нормальные» → ожидаем 0"
        ok &= good
        print(f"  {ch}  {a[ch]:>5} -> {b[ch]:>5}  ({d:+3})  "
              f"{'OK ' if good else 'ОШИБКА'}  {note}")
    print("ИТОГ:", "всё верно" if ok else "ЕСТЬ РАСХОЖДЕНИЯ")
    return ok


if __name__ == '__main__':
    sys.exit(0 if main(sys.argv[1], sys.argv[2]) else 1)
