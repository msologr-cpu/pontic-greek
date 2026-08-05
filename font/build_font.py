#!/usr/bin/env python3
"""
Создаёт шрифт Pontic Sans на основе Noto Sans (OFL).

ПРОБЛЕМА, которую решает этот скрипт
------------------------------------
Дмитрий Иванович сообщил: «гачек хорошо сидит только над Ζ и Χ, а над Σ, Ξ, Ψ,
ξ, ζ — очень низко и его почти не видно».

Разбор показал точную причину. В Noto Sans таблица GPOS содержит якоря
(mark-attachment anchors) для комбинируемого гачека U+030C только у части
греческих букв: Α Χ Κ Ο Ζ α χ κ ο. Именно поэтому над Ζ и Χ знак стоит
правильно — у них якорь есть.

У остальных понтийских букв якоря НЕТ. Когда якоря нет, система ставит знак
в позицию по умолчанию, и он налезает на букву. Особенно заметно на высоких
строчных ξ ζ ψ (их верх 760) и на заглавных Σ Ξ Ψ (верх 714).

РЕШЕНИЕ
-------
Добавляем недостающие якоря в GPOS: для каждой буквы ставим точку крепления
по центру буквы на высоте её верхней границы. Знак начинает «плавать» над
буквой, как и должен.
"""
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib.tables.otTables import Anchor, BaseRecord

SRC = 'font/work/NotoSans.ttf'
DST = 'font/work/PonticSans-Regular.ttf'

FAMILY = 'Pontic Sans'
VERSION = '4.0'

# Буквы, которым нужен якорь для знаков СВЕРХУ (гачек U+030C, бреве U+0306).
# Значение — высота якоря. Для строчных обычной высоты берём x-height 536,
# для высоких строчных (ξ ζ ψ) — их реальный верх 760,
# для заглавных — cap-height 714.
TOP_TARGETS = {
    0x3BE: 760,  # ξ  xi          — высокая строчная
    0x3B6: 760,  # ζ  zeta        — высокая строчная
    0x3C8: 760,  # ψ  psi         — высокая строчная
    0x3C3: 536,  # σ  sigma
    0x3C2: 536,  # ς  sigma final
    0x3B3: 536,  # γ  gamma       — для бреве γ̆
    0x3A3: 714,  # Σ  SIGMA
    0x39E: 714,  # Ξ  XI
    0x3A8: 714,  # Ψ  PSI
    0x393: 714,  # Γ  GAMMA       — для бреве Γ̆
}

# Буквы, которым нужен якорь для знака СНИЗУ (две точки U+0324).
# Ставится под базовой линией.
BOTTOM_TARGETS = {
    0x3AC: 0,    # ά  alpha tonos
    0x3CC: 0,    # ό  omicron tonos
    0x386: 0,    # Ά  ALPHA tonos
    0x38C: 0,    # Ό  OMICRON tonos
}

# Эти же буквы с тоносом нуждаются и в верхнем якоре — на случай,
# если пользователь наберёт их с гачеком.
TOP_TARGETS_TONOS = {
    0x3AC: 700,  # ά
    0x3CC: 700,  # ό
    0x386: 900,  # Ά
    0x38C: 900,  # Ό
}


def glyph_center_x(font, glyph_name):
    """Горизонтальный центр видимой части буквы."""
    gs = font.getGlyphSet()
    bp = BoundsPen(gs)
    gs[glyph_name].draw(bp)
    if not bp.bounds:
        return font['hmtx'][glyph_name][0] // 2
    xmin, _, xmax, _ = bp.bounds
    return round((xmin + xmax) / 2)


def iter_markbase_subtables(gpos):
    """Все MarkBasePos-подтаблицы, включая обёрнутые в Extension."""
    for lookup in gpos.table.LookupList.Lookup:
        for sub in lookup.SubTable:
            if lookup.LookupType == 9:  # Extension
                sub = sub.ExtSubTable
            if hasattr(sub, 'BaseCoverage') and hasattr(sub, 'MarkCoverage'):
                yield sub


def add_base_anchors(font, sub, targets, label):
    """Добавляет якоря для указанных букв в подтаблицу MarkBasePos."""
    cmap = font.getBestCmap()
    order = font.getGlyphOrder()
    gid = {g: i for i, g in enumerate(order)}

    # Существующие записи: имя глифа -> BaseRecord
    existing = dict(zip(sub.BaseCoverage.glyphs, sub.BaseArray.BaseRecord))

    added = []
    for cp, y in targets.items():
        gn = cmap.get(cp)
        if not gn:
            continue
        if gn in existing:
            continue  # якорь уже есть — не трогаем

        anchor = Anchor()
        anchor.Format = 1
        anchor.XCoordinate = glyph_center_x(font, gn)
        anchor.YCoordinate = y

        rec = BaseRecord()
        rec.BaseAnchor = [anchor] * sub.ClassCount

        existing[gn] = rec
        added.append((chr(cp), gn, anchor.XCoordinate, y))

    if not added:
        print(f"  [{label}] нечего добавлять — все якоря уже на месте")
        return 0

    # ВАЖНО: coverage и BaseArray должны идти строго в порядке glyph ID,
    # иначе шрифт скомпилируется с перепутанными якорями.
    ordered = sorted(existing.items(), key=lambda kv: gid[kv[0]])
    sub.BaseCoverage.glyphs = [g for g, _ in ordered]
    sub.BaseArray.BaseRecord = [r for _, r in ordered]
    sub.BaseArray.BaseCount = len(ordered)

    print(f"  [{label}] добавлено якорей: {len(added)}")
    for ch, gn, x, y in added:
        print(f"      {ch}  {gn:16} -> ({x}, {y})")
    return len(added)


def rename_font(font):
    """Переименовываем, чтобы шрифт не конфликтовал с системным Noto Sans."""
    name = font['name']
    full = f'{FAMILY} Regular'
    ps = FAMILY.replace(' ', '') + '-Regular'
    values = {
        1: FAMILY,
        2: 'Regular',
        3: f'{FAMILY} {VERSION}',
        4: full,
        5: f'Version {VERSION}',
        6: ps,
    }
    for nid, val in values.items():
        name.setName(val, nid, 3, 1, 0x409)
        name.setName(val, nid, 1, 0, 0)


def main():
    font = TTFont(SRC)
    print(f"Открыт {SRC}")

    gpos = font['GPOS']
    cmap = font.getBestCmap()

    caron = cmap[0x30C]
    breve = cmap[0x306]
    dbelow = cmap[0x324]

    total = 0
    for sub in iter_markbase_subtables(gpos):
        marks = set(sub.MarkCoverage.glyphs)
        if caron in marks or breve in marks:
            print("Подтаблица со знаками СВЕРХУ (гачек/бреве):")
            total += add_base_anchors(font, sub, TOP_TARGETS, 'верх')
            total += add_base_anchors(font, sub, TOP_TARGETS_TONOS, 'верх+тонос')
        if dbelow in marks:
            print("Подтаблица со знаком СНИЗУ (две точки):")
            total += add_base_anchors(font, sub, BOTTOM_TARGETS, 'низ')

    rename_font(font)
    font.save(DST)
    print(f"\nВсего добавлено якорей: {total}")
    print(f"Сохранено: {DST}")


if __name__ == '__main__':
    main()
