# Proposed Fix for notofonts/latin-greek-cyrillic Issue #547
## Title: Greek with combining caron for Pontic Greek (GPOS Anchor Definitions)

### Context
In Noto Sans and Noto Serif (Latin/Greek/Cyrillic), GPOS attachment anchors (`top` / `bottom`) are missing for several Greek letters used in Pontic Greek with combining marks:
- **Caron (U+030C)**: ζ, χ, σ, ς, κ, ξ, ψ and uppercase Ζ, Χ, Σ, Κ, Ξ, Ψ
- **Breve (U+0306)**: γ and uppercase Γ
- **Diaeresis Below (U+0324)**: α, ο, ά, ό and uppercase Α, Ο, Ά, Ό

Without explicit GPOS anchors, rendering engines (HarfBuzz, CoreText, DirectWrite) fall back to default glyph bounding box positioning, causing carons and breves to collide with or misalign over letters with descenders/asymmetric stems.

---

### Suggested GPOS Anchors

#### 1. Top Anchors (`top` anchor for U+030C and U+0306)
For asymmetric glyphs with long descenders (ψ, ξ, ζ), optical visual centering is calculated across the top half / contour upper zone rather than the entire bounding box width:

| Glyph | Unicode | Base Name | Anchor Y | Alignment Strategy |
| :--- | :--- | :--- | :--- | :--- |
| `ξ` | U+03BE | `uni03BE` | Glyph top bounds | Upper-contour visual center (ignoring bottom tail) |
| `ζ` | U+03B6 | `uni03B6` | Glyph top bounds | Upper-contour visual center |
| `ψ` | U+03C8 | `uni03C8` | Glyph top bounds | Stem center / upper cup center |
| `σ` | U+03C3 | `uni03C3` | Glyph top bounds | Center of glyph contour |
| `ς` | U+03C2 | `uni03C2` | Glyph top bounds | Upper loop center |
| `χ` | U+03C7 | `uni03C7` | Glyph top bounds | Intersection X-center |
| `κ` | U+03BA | `uni03BA` | Glyph top bounds | Center between stem and right arms |
| `γ` | U+03B3 | `uni03B3` | Glyph top bounds | Center between upper horns (for breve U+0306) |
| `Σ` | U+03A3 | `uni03A3` | Cap height | Cap center X |
| `Ξ` | U+039E | `uni039E` | Cap height | Cap center X |
| `Ψ` | U+03A8 | `uni03A8` | Cap height | Central stem X |
| `Χ` | U+03A7 | `uni03A7` | Cap height | Center X |
| `Κ` | U+039A | `uni039A` | Cap height | Center X |
| `Ζ` | U+0396 | `uni0396` | Cap height | Center X |
| `Γ` | U+0393 | `uni0393` | Cap height | Top horizontal bar center |

#### 2. Bottom Anchors (`bottom` anchor for U+0324)
| Glyph | Unicode | Base Name | Anchor Y | Alignment Strategy |
| :--- | :--- | :--- | :--- | :--- |
| `α` | U+03B1 | `uni03B1` | `ymin` (baseline) | Horizontal center of loop |
| `ο` | U+03BF | `uni03BF` | `ymin` (baseline) | Horizontal center of bowl |
| `ά` | U+03AC | `uni03AC` | `ymin` (baseline) | Horizontal center of loop |
| `ό` | U+03CC | `uni03CC` | `ymin` (baseline) | Horizontal center of bowl |
| `Α` | U+0391 | `uni0391` | `ymin` (baseline) | Cap baseline center |
| `Ο` | U+039F | `uni039F` | `ymin` (baseline) | Cap baseline center |
| `Ά` | U+0386 | `uni0386` | `ymin` (baseline) | Cap baseline center |
| `Ό` | U+038C | `uni038C` | `ymin` (baseline) | Cap baseline center |

---

### Verification
Anchors tested across 4 styles (Regular, Italic, Bold, Bold Italic) for both Sans and Serif with HarfBuzz (`hb-shape` / `hb-view`).
Positioning verified for:
`ξ̌ ζ̌ χ̌ ψ̌ σ̌ ς̌ κ̌ γ̆ α̤ ο̤ ά̤ ό̤ Σ̌ Ξ̌ Ζ̌ Χ̌ Ψ̌ Κ̌ Γ̆ Α̤ Ο̤ Ά̤ Ό̤`
