# Pontic Greek Alphabet & Unicode Input Specification

This document describes the orthographic, phonological, and Unicode normalization model behind the Pontic Greek keyboard suite and companion OpenType fonts across iOS, Android, macOS, Windows, Linux, and Web.

## 1. Alphabet Structure

```
[Pontic Alphabet] = [Standard Greek Alphabet (24 letters)] + [Pontic Diacritic Letters]
```

The Pontic alphabet shares all 24 standard Modern Greek letters (`Α–Ω`, `α–ω`, plus final `ς` and monotonic tonos/dialytika) and extends specific letters using standard Unicode combining marks (`U+030C`, `U+0306`, `U+0324`, `U+0301`) with **zero Private Use Area (PUA) characters**.

![Pontic letters](pontic_letters.jpg)

## 2. Unicode Normalization & Combining Sequences

### Letters with Diaeresis Below (`U+0324`)

| Base | Description | Base Codepoint | Combining Sequence (NFC) | Combining Sequence (NFD) | Result |
|---|---|---|---|---|---|
| `Α` | Capital Alpha with diaeresis below | `U+0391` | `U+0391 U+0324` | `U+0391 U+0324` | `Α̤` |
| `α` | Small Alpha with diaeresis below | `U+03B1` | `U+03B1 U+0324` | `U+03B1 U+0324` | `α̤` |
| `Ά` | Capital Alpha with tonos + diaeresis below | `U+0386` | `U+0386 U+0324` | `U+0391 U+0324 U+0301` | `Ά̤` |
| `ά` | Small Alpha with tonos + diaeresis below | `U+03AC` | `U+03AC U+0324` | `U+03B1 U+0324 U+0301` | `ά̤` |
| `Ο` | Capital Omicron with diaeresis below | `U+039F` | `U+039F U+0324` | `U+039F U+0324` | `Ο̤` |
| `ο` | Small Omicron with diaeresis below | `U+03BF` | `U+03BF U+0324` | `U+03BF U+0324` | `ο̤` |
| `Ό` | Capital Omicron with tonos + diaeresis below | `U+038C` | `U+038C U+0324` | `U+039F U+0324 U+0301` | `Ό̤` |
| `ό` | Small Omicron with tonos + diaeresis below | `U+03CC` | `U+03CC U+0324` | `U+03BF U+0324 U+0301` | `ό̤` |

*Canonical Ordering Note:* Because `U+0324` (combining class `220`) has lower canonical combining class than `U+0301` (combining class `230`), canonical NFD places `U+0324` before `U+0301`, and Unicode NFC composes the base vowel + acute into precomposed `ά`/`ό`/`Ά`/`Ό` followed by `U+0324`.

### Letters with Caron (`U+030C`)

| Base | Sound (Approx.) | Base Codepoint | Combining Sequence (NFC) | Result |
|---|---|---|---|---|
| `Ζ` | *Zh* `[ʒ]` | `U+0396` | `U+0396 U+030C` | `Ζ̌` |
| `ζ` | *zh* `[ʒ]` | `U+03B6` | `U+03B6 U+030C` | `ζ̌` |
| `Ξ` | *Ksh* `[kʃ]` | `U+039E` | `U+039E U+030C` | `Ξ̌` |
| `ξ` | *ksh* `[kʃ]` | `U+03BE` | `U+03BE U+030C` | `ξ̌` |
| `Σ` | *Sh* `[ʃ]` | `U+03A3` | `U+03A3 U+030C` | `Σ̌` |
| `σ` | *sh* `[ʃ]` | `U+03C3` | `U+03C3 U+030C` | `σ̌` |
| `ς` | *sh* `[ʃ]` (word-final) | `U+03C2` | `U+03C2 U+030C` | `ς̌` |
| `Χ` | *Ch* `[tʃ]` | `U+03A7` | `U+03A7 U+030C` | `Χ̌` |
| `χ` | *ch* `[tʃ]` | `U+03C7` | `U+03C7 U+030C` | `χ̌` |
| `Ψ` | *Psh* `[pʃ]` | `U+03A8` | `U+03A8 U+030C` | `Ψ̌` |
| `ψ` | *psh* `[pʃ]` | `U+03C8` | `U+03C8 U+030C` | `ψ̌` |
| `Κ` | Palatal `[c]` / `[tɕ]` | `U+039A` | `U+039A U+030C` | `Κ̌` |
| `κ` | Palatal `[c]` / `[tɕ]` | `U+03BA` | `U+03BA U+030C` | `κ̌` |

### Letters with Breve (`U+0306`)

| Base | Sound (Approx.) | Base Codepoint | Combining Sequence (NFC) | Result |
|---|---|---|---|---|
| `Γ` | Palatal approximant `[j]` | `U+0393` | `U+0393 U+0306` | `Γ̆` |
| `γ` | Palatal approximant `[j]` | `U+03B3` | `U+03B3 U+0306` | `γ̆` |

![Combined Breve Examples](pontic_various_breve.jpg)

## 3. Dead-Key Composition Reference

Hardware desktop layouts (`.keylayout`, Keyman desktop, Windows AutoHotkey) implement non-invasive overlay composition directly on top of the Modern Greek QWERTY layout:

- **Tonos (`;` dead key):** `;` + `α/ε/η/ι/ο/υ/ω` → `ά/έ/ή/ί/ό/ύ/ώ` (and uppercase `Ά–Ώ`).
- **Dialytika (`:` / `Shift+;` dead key):** `:` + `ι/υ` → `ϊ/ϋ` (and uppercase `Ϊ/Ϋ`).
- **Dialytika + Tonos (`W` uppercase / `Q` or `;` + `:`):** `ΐ`, `ΰ`, `Ϊ́`, `Ϋ́`.
- **Pontic Dead Key (`/`):** `/` + `{ζ, ξ, σ, ς, χ, ψ, κ}` → caron (`ζ̌–ψ̌`); `/` + `{γ, Γ}` → breve (`γ̆, Γ̆`); `/` + `{α, ο, Α, Ο}` → diaeresis below (`α̤, ο̤, Α̤, Ο̤`); `/` + Space → literal `/`.
- **Stressed Reduced Vowels:** `;` + `/` (or `/` + `;`) + `{α, ο, Α, Ο}` → `ά̤`, `ό̤`, `Ά̤`, `Ό̤`.

## 4. Font Requirements (`GPOS` Anchors)

Standard Greek fonts (such as Times New Roman or pre-patch Noto Sans) historically lacked OpenType `GPOS` `mark` anchors bridging Latin/Cyrillic combining caron (`U+030C`), breve (`U+0306`), and diaeresis below (`U+0324`) onto Greek base glyphs. Through Google Noto PR [`notofonts/latin-greek-cyrillic#581`](https://github.com/notofonts/latin-greek-cyrillic/pull/581) and the companion [`font/`](font/) release (Pontic Sans & Pontic Serif v6.0), all anchors are now calibrated and verified with HarfBuzz across Regular, Italic, Bold, and Bold Italic weights.
