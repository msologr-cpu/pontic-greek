# Pontic Sans & Pontic Serif v6.0 Fonts

Open-source font families for Pontic Greek with calibrated OpenType `GPOS` combining mark anchors for caron (`U+030C`), breve (`U+0306`), and diaeresis below (`U+0324`).

| Style | Pontic Sans | Pontic Serif |
|---|---|---|
| Regular | `PonticSans-Regular.ttf` | `PonticSerif-Regular.ttf` |
| Italic | `PonticSans-Italic.ttf` | `PonticSerif-Italic.ttf` |
| Bold | `PonticSans-Bold.ttf` | `PonticSerif-Bold.ttf` |
| Bold Italic | `PonticSans-BoldItalic.ttf` | `PonticSerif-BoldItalic.ttf` |

All styles in each family share proper `name` / `OS/2` family linking, so Microsoft Word, LibreOffice, browsers, and mobile apps switch cleanly between Regular, Italic, Bold, and Bold Italic via `Ctrl/Cmd+B` and `Ctrl/Cmd+I`.

## Problem Addressed

Greek orthography uses tonos (`U+0301`) and dialytika (`U+0308`), while Pontic Greek adds:
- Combining Caron (`U+030C`): `ζ̌ χ̌ σ̌ ς̌ κ̌ ξ̌ ψ̌` and uppercase `Ζ̌ Χ̌ Σ̌ Κ̌ Ξ̌ Ψ̌`
- Combining Breve (`U+0306`): `γ̆ Γ̆`
- Combining Diaeresis Below (`U+0324`): `α̤ ο̤ ά̤ ό̤ Α̤ Ο̤ Ά̤ Ό̤`

In unmodified upstream fonts, many Greek glyphs lacked `GPOS` mark-to-base anchors for `U+030C`, `U+0306`, or `U+0324` (notably lowercase `χ`, `ξ`, `ζ`, `ψ`, `σ`, `ς`, `γ` and Serif `α`/`ο` optical placement). Shaping engines fell back to zero-offset placement, causing marks to collide with the glyph or drift right.

## Solution & Upstream Merge

We added and optically calibrated every required `GPOS` `MarkToBase` anchor in [`anchors.json`](anchors.json) and injected them into both `Pontic Sans` and `Pontic Serif` across all 4 weights/styles:

- **Descender & asymmetric compensation:** Centered `U+030C` optically over `ψ`, `ξ`, `ζ` and `σ`/`ς` despite wide loops and long descenders.
- **Italic slope adjustment:** Adjusted horizontal mark coordinates along each italic slant angle so caron and diaeresis stay centered in Italic and Bold Italic.
- **HarfBuzz verification:** Every glyph combination was rendered through `uharfbuzz` (`<= 1` font-unit alignment error) and reviewed visually with Prof. D. I. Zimov.
- **Upstream Google Noto merge:** Anchor tables and coordinates from this project were submitted to Google Noto and merged in [`notofonts/latin-greek-cyrillic#581`](https://github.com/notofonts/latin-greek-cyrillic/pull/581) (Issue [`#547`](https://github.com/notofonts/latin-greek-cyrillic/issues/547)).

## Font Comparison & Recommendation

For general typography alongside system fonts:
- **Pontic Sans / Pontic Serif** (included here) — full v6.0 calibration across all 8 styles
- **Google Noto Sans / Noto Serif** — includes merged PR #581 anchors in newer releases
- **Cambria, Brill, Gentium Plus** — full native support for Pontic combining marks
- Avoid **Calibri** (`ψ̌` misaligned) and **Times New Roman** (lacks Greek combining caron support)

## Build & Verification

Requires `fonttools`, `uharfbuzz`, and `pillow`:

```bash
python3 font/build_font.py sans    # Build Pontic Sans (all 4 styles)
python3 font/build_font.py serif   # Build Pontic Serif (all 4 styles)
python3 font/build_font.py all     # Build all 8 font files
python3 font/verify.py             # Verify HarfBuzz GPOS shaping
python3 font/sample.py sans        # Render before/after PNG sample for Sans
python3 font/sample.py serif       # Render before/after PNG sample for Serif
```

The static source weights for Serif are instanced from Google Fonts Noto Serif variable fonts via `fontTools.varLib.instancer`.

## License

Derived from **Noto Sans** and **Noto Serif** © The Noto Project Authors under the **SIL Open Font License 1.1** ([`OFL.txt`](OFL.txt)). Per SIL OFL 1.1 reserved font naming requirements, the derived families are renamed **Pontic Sans** and **Pontic Serif**.
