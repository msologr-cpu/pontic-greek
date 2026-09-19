#!/usr/bin/env python3
"""
Извлечение данных о GPOS-якорях для редактора Pontoskey.
Формирует anchors.json по спецификации раздела 2.1 мастер-промпта.
"""

import os
import sys
import json
from datetime import datetime, timezone
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.basePen import BasePen

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from optical_shift import iter_markbase_subtables

VERSION = "5.1"

FONT_FILES = [
    "PonticSans-Regular.ttf",
    "PonticSans-Italic.ttf",
    "PonticSans-Bold.ttf",
    "PonticSans-BoldItalic.ttf",
    "PonticSerif-Regular.ttf",
    "PonticSerif-Italic.ttf",
    "PonticSerif-Bold.ttf",
    "PonticSerif-BoldItalic.ttf",
]

MARK_CONFIG = [
    (0x030C, "caron", "гачек / caron"),
    (0x0306, "breve", "бреве / breve"),
    (0x0324, "dbelow", "две точки снизу / diaeresis below"),
    (0x0331, "mbelow", "черта снизу / macron below"),
    (0x0307, "dotabove", "точка сверху / dot above"),
    (0x0301, "acute", "тонос / acute"),
    (0x0308, "diaeresis", "диалитика / diaeresis"),
]

# Все целевые буквы из разделов 5.1 и 5.2
TOP_TARGETS = [
    0x03C3,  # σ
    0x03C2,  # ς
    0x03B6,  # ζ
    0x03BE,  # ξ
    0x03C8,  # ψ
    0x03C7,  # χ
    0x03BA,  # κ
    0x03B3,  # γ
    0x03A3,  # Σ
    0x0396,  # Ζ
    0x039E,  # Ξ
    0x03A8,  # Ψ
    0x03A7,  # Χ
    0x039A,  # Κ
    0x0393,  # Γ
]

BOTTOM_TARGETS = [
    0x03B1,  # α
    0x03B5,  # ε
    0x03BF,  # ο
    0x03C5,  # υ
    0x03B7,  # η
    0x03C9,  # ω
    0x03AC,  # ά
    0x03CC,  # ό
    0x0391,  # Α
    0x039F,  # Ο
    0x0386,  # Ά
    0x038C,  # Ό
    0x03B9,  # ι
]


class PointCollector(BasePen):
    """Сборщик всех точек контура глифа."""
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


def get_glyph_bounds(font, glyph_name):
    gs = font.getGlyphSet()
    bp = BoundsPen(gs)
    gs[glyph_name].draw(bp)
    return bp.bounds


def get_visual_center_x(font, glyph_name, side='top'):
    b = get_glyph_bounds(font, glyph_name)
    if not b:
        return font['hmtx'][glyph_name][0] // 2
    gs = font.getGlyphSet()
    pc = PointCollector(gs)
    gs[glyph_name].draw(pc)
    h = b[3] - b[1]
    if side == 'top':
        thresh = b[1] + h * 0.80
        pts = [p for p in pc.points if p[1] >= thresh]
    else:
        thresh = b[1] + h * 0.25
        pts = [p for p in pc.points if p[1] <= thresh]
    if pts:
        return round((min(p[0] for p in pts) + max(p[0] for p in pts)) / 2)
    return round((b[0] + b[2]) / 2)


def extract_font_data(font_path):
    font = TTFont(font_path)
    upem = font['head'].unitsPerEm
    os2 = font['OS/2']
    hhea = font['hhea']
    cmap = font.getBestCmap()

    metrics = {
        "xHeight": int(os2.sxHeight),
        "capHeight": int(os2.sCapHeight),
        "ascender": int(hhea.ascent),
        "descender": int(hhea.descent),
        "baseline": 0
    }

    marks = {}
    # Mark information and anchor lookups
    # Note: caron, breve, dotabove are top marks; dbelow, mbelow are bottom marks
    mark_records = {}
    for sub in iter_markbase_subtables(font):
        for mi, m_glyph in enumerate(sub.MarkCoverage.glyphs):
            if m_glyph not in mark_records:
                mrec = sub.MarkArray.MarkRecord[mi]
                mark_records[m_glyph] = (sub, mrec)

    for cp, key_name, note in MARK_CONFIG:
        gn = cmap.get(cp)
        hex_key = f"{cp:04X}"
        if not gn:
            continue
        if gn in mark_records:
            sub, mrec = mark_records[gn]
            ma = mrec.MarkAnchor
            marks[hex_key] = {
                "anchor": {"x": int(ma.XCoordinate), "y": int(ma.YCoordinate)},
                "note": note
            }
        else:
            marks[hex_key] = {
                "anchor": {"x": 0, "y": 0},
                "note": f"{note} (нет якоря марки в GPOS)"
            }

    # Поиск базовых якорей:
    # Для TOP: ищем в подтаблицах, где есть caron (0x30C) или breve (0x306)
    # Для BOTTOM: ищем в подтаблицах, где есть dbelow (0x324)
    gn_caron = cmap.get(0x30C)
    gn_breve = cmap.get(0x306)
    gn_dbelow = cmap.get(0x324)

    all_target_cps = sorted(list(set(TOP_TARGETS + BOTTOM_TARGETS)))
    bases = {}

    for cp in all_target_cps:
        gn = cmap.get(cp)
        if not gn:
            continue
        hex_key = f"{cp:04X}"
        char = chr(cp)

        top_anchor = None
        bottom_anchor = None
        top_vc = get_visual_center_x(font, gn, 'top')
        bot_vc = get_visual_center_x(font, gn, 'bottom')

        # Top anchor search
        for sub in iter_markbase_subtables(font):
            m_glyphs = sub.MarkCoverage.glyphs
            top_mark_glyph = None
            if gn_caron and gn_caron in m_glyphs:
                top_mark_glyph = gn_caron
            elif gn_breve and gn_breve in m_glyphs:
                top_mark_glyph = gn_breve

            if top_mark_glyph and gn in sub.BaseCoverage.glyphs:
                mi = m_glyphs.index(top_mark_glyph)
                cls = sub.MarkArray.MarkRecord[mi].Class
                bi = sub.BaseCoverage.glyphs.index(gn)
                brec = sub.BaseArray.BaseRecord[bi]
                if cls < len(brec.BaseAnchor) and brec.BaseAnchor[cls] is not None:
                    ba = brec.BaseAnchor[cls]
                    top_anchor = {
                        "x": int(ba.XCoordinate),
                        "y": int(ba.YCoordinate),
                        "origin": "computed",
                        "visualCenterX": top_vc
                    }
                    break

        # Bottom anchor search
        if gn_dbelow:
            for sub in iter_markbase_subtables(font):
                m_glyphs = sub.MarkCoverage.glyphs
                if gn_dbelow in m_glyphs and gn in sub.BaseCoverage.glyphs:
                    mi = m_glyphs.index(gn_dbelow)
                    cls = sub.MarkArray.MarkRecord[mi].Class
                    bi = sub.BaseCoverage.glyphs.index(gn)
                    brec = sub.BaseArray.BaseRecord[bi]
                    if cls < len(brec.BaseAnchor) and brec.BaseAnchor[cls] is not None:
                        ba = brec.BaseAnchor[cls]
                        bottom_anchor = {
                            "x": int(ba.XCoordinate),
                            "y": int(ba.YCoordinate),
                            "origin": "computed",
                            "visualCenterX": bot_vc
                        }
                        break

        bases[hex_key] = {
            "char": char,
            "top": top_anchor,
            "bottom": bottom_anchor
        }

    return {
        "upem": upem,
        "metrics": metrics,
        "marks": marks,
        "bases": bases
    }


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    font_dir = script_dir
    data_dir = "/Users/solomon/Projects/pontos-world/pontoskey/data"
    os.makedirs(data_dir, exist_ok=True)

    result = {
        "schemaVersion": "1.0",
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sourceFontsVersion": VERSION,
        "fonts": {}
    }

    for ff in FONT_FILES:
        font_path = os.path.join(font_dir, ff)
        if not os.path.exists(font_path):
            print(f"ОШИБКА: Файл шрифта не найден: {font_path}", file=sys.stderr)
            sys.exit(1)
        font_key = os.path.splitext(ff)[0]
        fdata = extract_font_data(font_path)
        fdata["file"] = ff
        result["fonts"][font_key] = fdata

    out_path = os.path.join(data_dir, "anchors.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    local_copy = os.path.join(script_dir, "anchors.json")
    with open(local_copy, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"anchors.json успешно сгенерирован: {out_path}")
    print(f"Копия сохранена: {local_copy}")

    for fk, fd in result["fonts"].items():
        top_count = sum(1 for b in fd["bases"].values() if b["top"] is not None)
        bot_count = sum(1 for b in fd["bases"].values() if b["bottom"] is not None)
        missing_top = [f"{b['char']}({k})" for k, b in fd["bases"].items() if b["top"] is None and int(k, 16) in TOP_TARGETS]
        missing_bot = [f"{b['char']}({k})" for k, b in fd["bases"].items() if b["bottom"] is None and int(k, 16) in BOTTOM_TARGETS]
        print(f"\n--- {fk} ---")
        print(f"  TOP якорей: {top_count} (отсутствуют из TOP_TARGETS: {missing_top or 'нет'})")
        print(f"  BOTTOM якорей: {bot_count} (отсутствуют из BOTTOM_TARGETS: {missing_bot or 'нет'})")


if __name__ == "__main__":
    main()
