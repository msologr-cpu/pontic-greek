#!/usr/bin/env python3
"""
Создаёт шрифт Pontic Sans на основе Noto Sans (OFL).

ПРОБЛЕМА, которую решает этот скрипт
------------------------------------
носитель языка сообщил: «гачек хорошо сидит только над Ζ и Χ, а над Σ, Ξ, Ψ,
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

VERSION = '4.1'

# Готовые сборки: имя → (исходник, результат, семейство).
# Noto Sans и Noto Serif распространяются по OFL, поэтому производные шрифты
# можно свободно раздавать — при условии переименования (Reserved Font Name).
BUILDS = {
    'sans': {
        'src': 'font/work/NotoSans.ttf',
        'dst': 'font/work/PonticSans-Regular.ttf',
        'family': 'Pontic Sans',
    },
    'serif': {
        'src': 'font/work/NotoSerif.ttf',
        'dst': 'font/work/PonticSerif-Regular.ttf',
        'family': 'Pontic Serif',
    },
}

# Буквы, которым нужен якорь для знаков СВЕРХУ (гачек U+030C, бреве U+0306).
# Высоту НЕ задаём числом: она вычисляется из самого глифа (его верхняя
# граница). Так один и тот же скрипт правильно работает и для Sans, и для
# Serif, у которых разные x-height и cap-height.
TOP_TARGETS = [
    0x3BE,  # ξ  xi
    0x3B6,  # ζ  zeta
    0x3C8,  # ψ  psi
    0x3C3,  # σ  sigma
    0x3C2,  # ς  sigma final
    0x3C7,  # χ  chi    — БЫЛА ПРОПУЩЕНА в v4.0: якоря не было ни в Noto Sans,
            #             ни в нашем шрифте, поэтому гачек уезжал ВПРАВО
            #             (ставился по ширине буквы). Отзыв носитель языка: «сбой
            #             произошёл со строчной χ — гачек сдвинулся вправо».
    0x3BA,  # κ  kappa
    0x3B3,  # γ  gamma  — для бреве γ̆
    0x3A3,  # Σ  SIGMA
    0x39E,  # Ξ  XI
    0x3A8,  # Ψ  PSI
    0x3A7,  # Χ  CHI
    0x39A,  # Κ  KAPPA
    0x396,  # Ζ  ZETA
    0x393,  # Γ  GAMMA  — для бреве Γ̆
]

# Буквы, которым нужен якорь для знака СНИЗУ (две точки U+0324).
# Ставится под базовой линией.
BOTTOM_TARGETS = [
    0x3B1,  # α
    0x3BF,  # ο
    0x391,  # Α
    0x39F,  # Ο
    0x3AC,  # ά  alpha tonos
    0x3CC,  # ό  omicron tonos
    0x386,  # Ά  ALPHA tonos
    0x38C,  # Ό  OMICRON tonos
]


def glyph_bounds(font, glyph_name):
    """Габариты видимой части буквы: (xmin, ymin, xmax, ymax)."""
    gs = font.getGlyphSet()
    bp = BoundsPen(gs)
    gs[glyph_name].draw(bp)
    return bp.bounds


def glyph_center_x(font, glyph_name):
    """Горизонтальный центр видимой части буквы."""
    b = glyph_bounds(font, glyph_name)
    if not b:
        return font['hmtx'][glyph_name][0] // 2
    xmin, _, xmax, _ = b
    return round((xmin + xmax) / 2)


def glyph_top_y(font, glyph_name):
    """Верхняя граница буквы — сюда крепится знак сверху (гачек, бреве)."""
    b = glyph_bounds(font, glyph_name)
    if not b:
        return round(font['head'].unitsPerEm * 0.7)
    return round(b[3])


def iter_markbase_subtables(gpos):
    """Все MarkBasePos-подтаблицы, включая обёрнутые в Extension."""
    for lookup in gpos.table.LookupList.Lookup:
        for sub in lookup.SubTable:
            if lookup.LookupType == 9:  # Extension
                sub = sub.ExtSubTable
            if hasattr(sub, 'BaseCoverage') and hasattr(sub, 'MarkCoverage'):
                yield sub


def add_base_anchors(font, sub, targets, label, side):
    """Добавляет якоря для указанных букв в подтаблицу MarkBasePos.

    targets — список кодпойнтов.
    side    — 'top' (знак сверху: Y = верх буквы) или 'bottom' (Y = базовая
              линия, т.е. 0). Высота больше не задаётся вручную числом:
              она берётся из реальных габаритов глифа, поэтому скрипт
              одинаково верно работает и для Sans, и для Serif.
    """
    cmap = font.getBestCmap()
    order = font.getGlyphOrder()
    gid = {g: i for i, g in enumerate(order)}

    # Существующие записи: имя глифа -> BaseRecord
    existing = dict(zip(sub.BaseCoverage.glyphs, sub.BaseArray.BaseRecord))

    added = []
    for cp in targets:
        gn = cmap.get(cp)
        if not gn:
            continue
        if gn in existing:
            continue  # якорь уже есть — не трогаем

        y = glyph_top_y(font, gn) if side == 'top' else 0

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


def rename_font(font, family):
    """Переименовываем, чтобы шрифт не конфликтовал с системным Noto."""
    name = font['name']
    full = f'{family} Regular'
    ps = family.replace(' ', '') + '-Regular'
    values = {
        1: family,
        2: 'Regular',
        3: f'{family} {VERSION}',
        4: full,
        5: f'Version {VERSION}',
        6: ps,
    }
    for nid, val in values.items():
        name.setName(val, nid, 3, 1, 0x409)
        name.setName(val, nid, 1, 0, 0)


def build_one(src, dst, family):
    font = TTFont(src)
    print(f"\n=== Сборка {family} ===")
    print(f"Открыт {src}")

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
            total += add_base_anchors(font, sub, TOP_TARGETS, 'верх', 'top')
        if dbelow in marks:
            print("Подтаблица со знаком СНИЗУ (две точки):")
            total += add_base_anchors(font, sub, BOTTOM_TARGETS, 'низ', 'bottom')

    rename_font(font, family)
    font.save(dst)
    print(f"Всего добавлено якорей: {total}")
    print(f"Сохранено: {dst}")
    return total


def main():
    import sys
    which = sys.argv[1] if len(sys.argv) > 1 else 'sans'
    names = list(BUILDS) if which == 'all' else [which]
    for n in names:
        b = BUILDS[n]
        try:
            build_one(b['src'], b['dst'], b['family'])
        except FileNotFoundError:
            print(f"\n[пропуск {b['family']}] нет исходника {b['src']}")


if __name__ == '__main__':
    main()
