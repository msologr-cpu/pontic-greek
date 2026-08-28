#!/usr/bin/env python3
"""Оптическая поправка положения гачека.

Замечание Д.И. (v5.0): над буквами ξ ζ χ ψ и Σ Ξ Ζ Χ Ψ гачек нужно сдвинуть
«совсем немного вправо».

Почему это законно с точки зрения типографики
----------------------------------------------
Математический (геометрический) центр буквы и ОПТИЧЕСКИЙ центр — разные точки.
У букв с диагональными штрихами и острыми верхушками (Χ, Ψ, Σ, ξ, ζ) глаз
воспринимает центр смещённым относительно центра габаритного прямоугольника.
Поэтому дизайнеры шрифтов ставят такие якоря вручную, а не формулой.

Наш алгоритм считает центр верно математически — Д.И. как носитель языка
видит оптическую несбалансированность. Правки применяются ТОЛЬКО к буквам,
которые он назвал; σ ς κ γ Κ Γ не трогаем — по ним замечаний не было.
"""
from fontTools.ttLib import TTFont

# Буквы из замечания Д.И. → величина сдвига вправо задаётся при вызове.
#
# ВАЖНО: ψ (U+03C8) и Ψ (U+03A8) в список НЕ входят.
# В первом замечании Д.И. называл их, но, посмотрев варианты на картинке,
# уточнил: «ψ̌ и Ψ̌ и так нормальные». Их положение оставляем как есть.
COMPLAINT_CODEPOINTS = [
    0x3BE,  # ξ
    0x3B6,  # ζ
    0x3C7,  # χ
    0x3A3,  # Σ
    0x39E,  # Ξ
    0x396,  # Ζ
    0x3A7,  # Χ
]

# Согласованная с Д.И. величина оптической поправки (единиц при upem=1000).
OPTICAL_SHIFT = 15

MARK_CARON = 0x30C
MARK_BREVE = 0x306


def iter_markbase_subtables(font):
    """Все MarkBasePos-подтаблицы, включая обёрнутые в Extension."""
    if 'GPOS' not in font:
        return
    gpos = font['GPOS'].table
    if not getattr(gpos, 'LookupList', None):
        return
    for lookup in gpos.LookupList.Lookup:
        for sub in lookup.SubTable:
            if lookup.LookupType == 9:
                sub = sub.ExtSubTable
            if hasattr(sub, 'BaseCoverage') and hasattr(sub, 'MarkCoverage'):
                yield sub


def apply_optical_shift(font, shift, codepoints=None):
    """Сдвигает якорь гачека вправо на `shift` единиц у указанных букв.

    Возвращает список (символ, старый_X, новый_X).
    """
    if codepoints is None:
        codepoints = COMPLAINT_CODEPOINTS
    if not shift:
        return []

    cmap = font.getBestCmap()
    caron = cmap.get(MARK_CARON)
    breve = cmap.get(MARK_BREVE)

    changed = []
    for sub in iter_markbase_subtables(font):
        marks = set(sub.MarkCoverage.glyphs)
        if caron not in marks and breve not in marks:
            continue

        # Класс, к которому относится гачек в этой подтаблице
        mark_class = 0
        for mcp in (MARK_CARON, MARK_BREVE):
            gn = cmap.get(mcp)
            if gn and gn in marks:
                mi = sub.MarkCoverage.glyphs.index(gn)
                mark_class = sub.MarkArray.MarkRecord[mi].Class
                break

        cover = dict(zip(sub.BaseCoverage.glyphs, sub.BaseArray.BaseRecord))
        for cp in codepoints:
            gn = cmap.get(cp)
            if not gn or gn not in cover:
                continue
            rec = cover[gn]
            if mark_class >= len(rec.BaseAnchor):
                continue
            anchor = rec.BaseAnchor[mark_class]
            if anchor is None:
                continue
            old = anchor.XCoordinate
            anchor.XCoordinate = old + shift
            changed.append((chr(cp), old, anchor.XCoordinate))
    return changed


def make_shifted_copy(src_path, dst_path, shift):
    """Читает шрифт, применяет сдвиг, сохраняет копию."""
    font = TTFont(src_path)
    changed = apply_optical_shift(font, shift)
    font.save(dst_path)
    return changed


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 4:
        print("Использование: optical_shift.py <вход.ttf> <выход.ttf> <сдвиг>")
        sys.exit(1)
    ch = make_shifted_copy(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    for c, o, n in ch:
        print(f"  {c}  {o} -> {n}")
