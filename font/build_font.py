#!/usr/bin/env python3
"""
Создаёт семейство шрифтов Pontic Sans и Pontic Serif на основе Noto (OFL).

Версия 5.0 — полная семья начертаний
-------------------------------------
Из variable-шрифтов Noto (с осями wght и wdth) создаются статические
экземпляры четырёх начертаний:
  • Regular   (wght=400)
  • Italic    (wght=400, из italic-переменного)
  • Bold      (wght=700)
  • Bold Italic (wght=700, из italic-переменного)

Для каждого экземпляра добавляются недостающие GPOS-якоря для понтийских
комбинируемых знаков (гачек, бреве, две точки снизу).

v5.0 также исправляет центрирование гачека над ψ, ξ, ζ: теперь якорь ставится
по центру ВЕРХНЕЙ половины глифа, а не по всему bounding box. У этих букв
нижний хвост уходит далеко вбок, и полный центр не совпадает с визуальным
центром буквы.

ПРОБЛЕМА, которую решает этот скрипт (оригинальная)
----------------------------------------------------
В Noto Sans/Serif таблица GPOS содержит якоря для комбинируемого гачека
U+030C только у части греческих букв. У остальных понтийских букв якоря
НЕТ. Когда якоря нет, система ставит знак в позицию по умолчанию, и он
налезает на букву.

РЕШЕНИЕ
-------
Добавляем недостающие якоря в GPOS: для каждой буквы ставим точку крепления
по центру буквы на высоте её верхней границы.
"""
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.basePen import BasePen
from fontTools.ttLib.tables.otTables import Anchor, BaseRecord

import os
import sys

VERSION = '5.0'

# ---------------------------------------------------------------------------
# Конфигурация сборок
# ---------------------------------------------------------------------------
# Для каждого семейства (sans/serif) × начертания (regular/italic/bold/bolditalic)
# указываем: исходный variable-шрифт, вес, имя начертания и выходной файл.
#
# 'src_static' — для обратной совместимости: если variable font не найден,
# пытаемся использовать старый статический файл (только для Regular).

FAMILIES = {
    'serif': {
        'family': 'Pontic Serif',
        'upright_vf': 'font/work/NotoSerif-Variable.ttf',
        'italic_vf': 'font/work/NotoSerif-Italic-Variable.ttf',
        'static_regular': 'font/work/NotoSerif.ttf',
    },
    'sans': {
        'family': 'Pontic Sans',
        'upright_vf': 'font/work/NotoSans-Variable.ttf',
        'italic_vf': 'font/work/NotoSans-Italic-Variable.ttf',
        'static_regular': 'font/work/NotoSans.ttf',
    },
}

STYLES = {
    'Regular':     {'weight': 400, 'italic': False},
    'Italic':      {'weight': 400, 'italic': True},
    'Bold':        {'weight': 700, 'italic': False},
    'BoldItalic':  {'weight': 700, 'italic': True},
}


# ---------------------------------------------------------------------------
# Буквы, которым нужны якоря
# ---------------------------------------------------------------------------

# Буквы, которым нужен якорь для знаков СВЕРХУ (гачек U+030C, бреве U+0306).
TOP_TARGETS = [
    0x3BE,  # ξ  xi
    0x3B6,  # ζ  zeta
    0x3C8,  # ψ  psi
    0x3C3,  # σ  sigma
    0x3C2,  # ς  sigma final
    0x3C7,  # χ  chi
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

# Буквы с длинным нижним выносным элементом. У них центр bounding box
# не совпадает с визуальным центром верхней части буквы. Для них
# вычисляем центр по точкам выше середины глифа.
ASYMMETRIC_DESCENDERS = {0x3C8, 0x3BE, 0x3B6}  # ψ ξ ζ

# Буквы, которым нужен якорь для знака СНИЗУ (две точки U+0324).
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


# ---------------------------------------------------------------------------
# Утилиты для работы с глифами
# ---------------------------------------------------------------------------

class PointCollector(BasePen):
    """Собирает все on-curve и off-curve точки контуров глифа."""
    def __init__(self, glyphSet):
        super().__init__(glyphSet)
        self.points = []

    def _moveTo(self, pt):
        self.points.append(pt)

    def _lineTo(self, pt):
        self.points.append(pt)

    def _curveToOne(self, pt1, pt2, pt3):
        self.points.extend([pt1, pt2, pt3])

    def _qCurveToOne(self, pt1, pt2):
        self.points.extend([pt1, pt2])

    def _closePath(self):
        pass

    def _endPath(self):
        pass


def glyph_bounds(font, glyph_name):
    """Габариты видимой части буквы: (xmin, ymin, xmax, ymax)."""
    gs = font.getGlyphSet()
    bp = BoundsPen(gs)
    gs[glyph_name].draw(bp)
    return bp.bounds


def glyph_center_x(font, glyph_name, codepoint=None):
    """Горизонтальный центр видимой части буквы.

    Для букв с длинным нижним выносным элементом (ψ, ξ, ζ) вычисляет
    центр по верхней половине глифа, чтобы гачек стоял ровно над
    визуальным центром буквы, а не сдвигался из-за асимметричного хвоста.
    """
    b = glyph_bounds(font, glyph_name)
    if not b:
        return font['hmtx'][glyph_name][0] // 2

    xmin, ymin, xmax, ymax = b

    # Для асимметричных букв (ψ ξ ζ) центр всего bounding box не годится:
    # у них длинный нижний хвост, уводящий центр вбок. Берём центр ВЕРХНИХ
    # 15% высоты глифа — это захватывает только верхушку стержня, над которой
    # стоит гачек.
    #
    # Почему не «верхняя половина»: у ψ bounding box от -240 до 760,
    # середина = 260. Практически все точки выше 260, так что «верхняя
    # половина» ≈ весь глиф, и центр не сдвигается. Top-15% = точки
    # выше y=610, и для Serif ψ это даёт центр ~383 (между двумя
    # верхними точками стержня 358 и 408), что точно совпадает с
    # визуальным центром.
    if codepoint and codepoint in ASYMMETRIC_DESCENDERS:
        gs = font.getGlyphSet()
        pc = PointCollector(gs)
        gs[glyph_name].draw(pc)
        height = ymax - ymin
        cutoff_y = ymin + height * 0.85  # верхние 15%
        upper_points = [p for p in pc.points if p[1] > cutoff_y]
        if upper_points:
            ux_min = min(p[0] for p in upper_points)
            ux_max = max(p[0] for p in upper_points)
            return round((ux_min + ux_max) / 2)

    return round((xmin + xmax) / 2)


def glyph_top_y(font, glyph_name):
    """Верхняя граница буквы — сюда крепится знак сверху (гачек, бреве)."""
    b = glyph_bounds(font, glyph_name)
    if not b:
        return round(font['head'].unitsPerEm * 0.7)
    return round(b[3])


# ---------------------------------------------------------------------------
# GPOS: поиск и модификация MarkBasePos-подтаблиц
# ---------------------------------------------------------------------------

def iter_markbase_subtables(gpos):
    """Все MarkBasePos-подтаблицы, включая обёрнутые в Extension."""
    for lookup in gpos.table.LookupList.Lookup:
        for sub in lookup.SubTable:
            if lookup.LookupType == 9:  # Extension
                sub = sub.ExtSubTable
            if hasattr(sub, 'BaseCoverage') and hasattr(sub, 'MarkCoverage'):
                yield sub


def _find_mark_class(sub, mark_codepoints, cmap):
    """Определяет номер класса, к которому относятся указанные марки."""
    for cp in mark_codepoints:
        gn = cmap.get(cp)
        if gn and gn in sub.MarkCoverage.glyphs:
            mi = sub.MarkCoverage.glyphs.index(gn)
            return sub.MarkArray.MarkRecord[mi].Class
    return 0  # fallback


def _glyph_center_x_raw(font, glyph_name):
    """Геометрический центр глифа целиком (для знака-марки)."""
    b = glyph_bounds(font, glyph_name)
    if not b:
        return 0
    return (b[0] + b[2]) / 2


def top_mark_slant_offset(font, sub, cmap):
    """Смещение гачека из-за наклона начертания (курсив).

    В mark-to-base знак ставится так, что его точка привязки (markAnchor)
    совмещается с base-anchor. Но у КУРСИВНОГО гачека геометрический центр
    не совпадает с точкой привязки — знак нарисован наклонным. Поэтому,
    если ставить base-anchor просто в центр буквы, гачек уезжает вбок
    (у Noto Serif Italic — на ~105 единиц вправо; отзыв носитель языка про ψ).

    Возвращаем (caron_center − markAnchor_x). На эту величину нужно
    СДВИНУТЬ base-anchor в обратную сторону, чтобы центр знака попал точно
    над центром буквы. Для прямых начертаний смещение ≈ 0.
    """
    caron = cmap.get(0x30C)
    if not caron or caron not in sub.MarkCoverage.glyphs:
        return 0
    mi = sub.MarkCoverage.glyphs.index(caron)
    a = sub.MarkArray.MarkRecord[mi].MarkAnchor
    if a is None:
        return 0
    return _glyph_center_x_raw(font, caron) - a.XCoordinate


def add_base_anchors(font, sub, targets, label, side):
    """Добавляет якоря для указанных букв в подтаблицу MarkBasePos.

    targets — список кодпойнтов.
    side    — 'top' (знак сверху: Y = верх буквы) или 'bottom' (Y = 0).

    Обрабатывает два случая:
    1) Глифа нет в BaseCoverage — добавляем полную запись.
    2) Глиф есть, но его якорь для нужного класса = None — заполняем
       якорь, сохраняя остальные классы нетронутыми. Это бывает в
       Noto Serif Italic, где coverage широкий, но якоря заданы не
       для всех классов.
    """
    cmap = font.getBestCmap()
    order = font.getGlyphOrder()
    gid = {g: i for i, g in enumerate(order)}

    # Определяем номер класса для нашего типа марки
    if side == 'top':
        mark_class = _find_mark_class(sub, [0x30C, 0x306], cmap)  # caron, breve
        # Поправка на наклон знака сверху (важна для курсива)
        slant = top_mark_slant_offset(font, sub, cmap)
    else:
        mark_class = _find_mark_class(sub, [0x324], cmap)  # dbelow
        slant = 0

    # Существующие записи: имя глифа -> BaseRecord
    existing = dict(zip(sub.BaseCoverage.glyphs, sub.BaseArray.BaseRecord))

    added = []
    for cp in targets:
        gn = cmap.get(cp)
        if not gn:
            continue

        # Проверяем, есть ли уже РЕАЛЬНЫЙ якорь для нужного класса
        if gn in existing:
            rec = existing[gn]
            if mark_class < len(rec.BaseAnchor) and rec.BaseAnchor[mark_class] is not None:
                # Родной якорь есть. В ПРЯМЫХ начертаниях он идеален — не трогаем.
                # В КУРСИВЕ (slant заметный) родные якоря дают неровный вид:
                # у разных букв гачек «плывёт» вправо по-разному. Чтобы курсив
                # был единообразным, перезаписываем верхние якоря наших целевых
                # букв на строго центрированные (с наклонной поправкой).
                if not (side == 'top' and abs(slant) > 8):
                    continue  # прямое начертание или нижний знак — не трогаем

        y = glyph_top_y(font, gn) if side == 'top' else 0

        anchor = Anchor()
        anchor.Format = 1
        # Центр буквы минус наклонное смещение знака. Поправку применяем ко
        # ВСЕМ буквам, чтобы гачек стоял строго по центру каждой — и в прямых,
        # и в курсивных начертаниях. Так все буквы выглядят единообразно
        # (в отличие от родного Noto, где в курсиве знак «плывёт» вправо
        # по-разному у разных букв). Для прямых начертаний slant ≈ 0.
        cx = glyph_center_x(font, gn, codepoint=cp) - slant
        anchor.XCoordinate = round(cx)
        anchor.YCoordinate = y

        if gn in existing:
            # Глиф уже в coverage — заполняем только нужный класс
            rec = existing[gn]
            new_anchors = list(rec.BaseAnchor)
            # Расширяем список, если классов стало больше
            while len(new_anchors) <= mark_class:
                new_anchors.append(None)
            new_anchors[mark_class] = anchor
            rec.BaseAnchor = new_anchors
        else:
            # Глифа нет в coverage — создаём полную запись
            rec = BaseRecord()
            rec.BaseAnchor = [None] * sub.ClassCount
            rec.BaseAnchor[mark_class] = anchor
            existing[gn] = rec

        added.append((chr(cp), gn, anchor.XCoordinate, y))

    if not added:
        print(f"  [{label}] нечего добавлять — все якоря уже на месте")
        return 0

    # ВАЖНО: coverage и BaseArray должны идти строго в порядке glyph ID
    ordered = sorted(existing.items(), key=lambda kv: gid[kv[0]])
    sub.BaseCoverage.glyphs = [g for g, _ in ordered]
    sub.BaseArray.BaseRecord = [r for _, r in ordered]
    sub.BaseArray.BaseCount = len(ordered)

    print(f"  [{label}] добавлено якорей: {len(added)}")
    for ch, gn, x, y in added:
        print(f"      {ch}  {gn:16} -> ({x}, {y})")
    return len(added)


# ---------------------------------------------------------------------------
# Создание статического экземпляра из variable font
# ---------------------------------------------------------------------------

def instantiate_static(vf_path, weight, out_path):
    """Создаёт статический .ttf из variable font, фиксируя вес и ширину."""
    from fontTools.varLib.instancer import instantiateVariableFont

    print(f"  Instantiate: {vf_path} @ wght={weight} -> {out_path}")
    vf = TTFont(vf_path)
    static = instantiateVariableFont(vf, {'wght': weight, 'wdth': 100}, inplace=True)
    static.save(out_path)
    return out_path


# ---------------------------------------------------------------------------
# Переименование и установка метаданных начертания
# ---------------------------------------------------------------------------

def rename_font(font, family, style_name):
    """Переименовываем и выставляем правильные флаги начертания.

    OTF-спецификация требует:
    - nameID 1: имя семейства (одинаковое для всех начертаний)
    - nameID 2: начертание (Regular, Italic, Bold, Bold Italic)
    - nameID 4: полное имя
    - nameID 6: PostScript name (без пробелов)
    - OS/2.fsSelection: биты ITALIC(0), BOLD(5), REGULAR(6)
    - head.macStyle: биты BOLD(0), ITALIC(1)
    - OS/2.usWeightClass: 400 или 700
    """
    is_bold = 'Bold' in style_name
    is_italic = 'Italic' in style_name

    name = font['name']
    os2 = font['OS/2']
    head = font['head']

    # nameID 2 subfamilyName: должен быть один из 4 стандартных
    if style_name == 'BoldItalic':
        subfamily = 'Bold Italic'
    else:
        subfamily = style_name

    full_name = f'{family} {subfamily}'
    ps_name = family.replace(' ', '') + '-' + style_name

    values = {
        1: family,
        2: subfamily,
        3: f'{family} {VERSION}',
        4: full_name,
        5: f'Version {VERSION}',
        6: ps_name,
    }
    for nid, val in values.items():
        name.setName(val, nid, 3, 1, 0x409)
        name.setName(val, nid, 1, 0, 0)

    # OS/2.fsSelection
    # Bit 0: ITALIC, Bit 5: BOLD, Bit 6: REGULAR
    fs = 0
    if is_italic:
        fs |= (1 << 0)
    if is_bold:
        fs |= (1 << 5)
    if not is_bold and not is_italic:
        fs |= (1 << 6)
    # Preserve USE_TYPO_METRICS (bit 7) if set
    if os2.fsSelection & (1 << 7):
        fs |= (1 << 7)
    os2.fsSelection = fs

    # head.macStyle
    # Bit 0: BOLD, Bit 1: ITALIC
    ms = 0
    if is_bold:
        ms |= (1 << 0)
    if is_italic:
        ms |= (1 << 1)
    head.macStyle = ms

    # usWeightClass
    os2.usWeightClass = 700 if is_bold else 400

    print(f"  Renamed: {full_name} (PS: {ps_name}, fsSelection={fs:#06x}, macStyle={ms})")


# ---------------------------------------------------------------------------
# Сборка одного шрифта
# ---------------------------------------------------------------------------

def build_one(font_or_path, dst, family, style_name):
    """Добавляет якоря и переименовывает один шрифт."""
    if isinstance(font_or_path, str):
        font = TTFont(font_or_path)
    else:
        font = font_or_path

    subfamily = 'Bold Italic' if style_name == 'BoldItalic' else style_name
    print(f"\n=== Сборка {family} {subfamily} ===")

    gpos = font['GPOS']
    cmap = font.getBestCmap()

    caron = cmap.get(0x30C)
    breve = cmap.get(0x306)
    dbelow = cmap.get(0x324)

    total = 0
    for sub in iter_markbase_subtables(gpos):
        marks = set(sub.MarkCoverage.glyphs)
        if (caron and caron in marks) or (breve and breve in marks):
            print("Подтаблица со знаками СВЕРХУ (гачек/бреве):")
            total += add_base_anchors(font, sub, TOP_TARGETS, 'верх', 'top')
        if dbelow and dbelow in marks:
            print("Подтаблица со знаком СНИЗУ (две точки):")
            total += add_base_anchors(font, sub, BOTTOM_TARGETS, 'низ', 'bottom')

    rename_font(font, family, style_name)
    font.save(dst)
    print(f"Всего добавлено якорей: {total}")
    print(f"Сохранено: {dst}")
    return total


# ---------------------------------------------------------------------------
# Главная функция
# ---------------------------------------------------------------------------

def build_family(family_key):
    """Собирает все начертания одного семейства."""
    fam = FAMILIES[family_key]
    family_name = fam['family']
    has_vf = os.path.exists(fam['upright_vf']) and os.path.exists(fam['italic_vf'])

    if not has_vf:
        # Фоллбэк: собираем только Regular из старого статического файла
        src = fam.get('static_regular')
        if not src or not os.path.exists(src):
            print(f"\n[пропуск {family_name}] нет исходников")
            return
        tag = family_key.title()
        dst = f'font/work/Pontic{tag}-Regular.ttf'
        build_one(src, dst, family_name, 'Regular')
        return

    for style_name, style_cfg in STYLES.items():
        weight = style_cfg['weight']
        is_italic = style_cfg['italic']

        vf_path = fam['italic_vf'] if is_italic else fam['upright_vf']
        tag = family_key.title()
        dst = f'font/work/Pontic{tag}-{style_name}.ttf'

        # Instantiate static font from variable
        tmp = dst + '.tmp'
        instantiate_static(vf_path, weight, tmp)

        # Add anchors and rename
        font = TTFont(tmp)
        build_one(font, dst, family_name, style_name)

        # Clean up temp
        os.remove(tmp)


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else 'serif'

    if which == 'all':
        for key in FAMILIES:
            try:
                build_family(key)
            except Exception as e:
                print(f"\n[ошибка {FAMILIES[key]['family']}] {e}")
                import traceback
                traceback.print_exc()
    elif which in FAMILIES:
        build_family(which)
    else:
        # Backward compat: try as style name
        print(f"Использование: python3 build_font.py [serif|sans|all]")
        sys.exit(1)


if __name__ == '__main__':
    main()
