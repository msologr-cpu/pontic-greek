# macOS Installation & Typing Guide — Pontic Greek Keyboard

Compatible with **macOS Sonoma, Sequoia, Tahoe** (Apple Silicon and Intel).

## Quick Installation

### Option A: Automated Script (`install_macos.sh`)
```bash
git clone https://github.com/msologr-cpu/pontic-greek.git
cd pontic-greek
bash install_macos.sh
```
The installer copies [`pnt-macos-v3.keylayout`](../pnt-macos-v3.keylayout) into `~/Library/Keyboard Layouts/` and installs the 8 `Pontic Sans` and `Pontic Serif` v6.0 `.ttf` font files into `~/Library/Fonts/`.

### Option B: Manual Installation
1. Download [`pnt-macos-v3.keylayout`](../pnt-macos-v3.keylayout).
2. Copy the file into your user keyboard layouts folder:
   ```bash
   mkdir -p "$HOME/Library/Keyboard Layouts"
   cp pnt-macos-v3.keylayout "$HOME/Library/Keyboard Layouts/"
   ```
   *(If Finder hides `Library`, press `Cmd + Shift + G` and enter `~/Library/Keyboard Layouts`.)*
3. Install all 8 `.ttf` font files from [`font/`](../font/) (`PonticSans-*.ttf`, `PonticSerif-*.ttf`) via **Font Book** or copy them into `~/Library/Fonts/`.

### Activating the Input Source in macOS
1. Open **System Settings -> Keyboard -> Text Input -> Input Sources -> Edit...**.
2. Click **`+`**, scroll to **Others** (bottom of the language list), select **Pontic Greek**, and click **Add**.
3. Switch between layouts with `Cmd + Space` or the Input menu in the menu bar.
   *(If the new layout does not appear right away, close and reopen System Settings or log out and log back in.)*

## How to Type Pontic Letters

The macOS driver mirrors the standard Modern Greek QWERTY layout (`Q` = `ς`, `S` = `σ`) and turns `/` into the unified **Pontic Dead Key** (`/` + letter):

### Caron (`U+030C`), Breve (`U+0306`), and Diaeresis Below (`U+0324`)

| Key Sequence | Output | Unicode (NFC) | Name |
|---|---|---|---|
| `/` then `ζ` (`Z`) | `ζ̌` | `U+03B6 U+030C` | Zeta with caron |
| `/` then `χ` (`X`) | `χ̌` | `U+03C7 U+030C` | Chi with caron |
| `/` then `σ` (`S`) | `σ̌` | `U+03C3 U+030C` | Sigma with caron |
| `/` then `ς` (`Q`) | `ς̌` | `U+03C2 U+030C` | Final sigma with caron |
| `/` then `κ` (`K`) | `κ̌` | `U+03BA U+030C` | Kappa with caron |
| `/` then `ξ` (`J`) | `ξ̌` | `U+03BE U+030C` | Xi with caron |
| `/` then `ψ` (`C`) | `ψ̌` | `U+03C8 U+030C` | Psi with caron |
| `/` then `γ` (`G`) | `γ̆` | `U+03B3 U+0306` | Gamma with breve |
| `/` then `α` (`A`) | `α̤` | `U+03B1 U+0324` | Alpha with diaeresis below |
| `/` then `ο` (`O`) | `ο̤` | `U+03BF U+0324` | Omicron with diaeresis below |
| `/` + `Shift` + letter | `Ζ̌ Χ̌ Σ̌ Κ̌ Ξ̌ Ψ̌ Γ̆ Α̤ Ο̤` | Uppercase | Uppercase Pontic letters |
| `/` + `Space` | `/` | `U+002F` | Literal forward slash |

### Stressed Reduced Vowels (`ά̤`, `ό̤`, `Ά̤`, `Ό̤`) & Standard Greek Accents

- **Tonos (`;` dead key):** `;` then `α / ε / η / ι / ο / υ / ω` → `ά / έ / ή / ί / ό / ύ / ώ` (and uppercase with `Shift`).
- **Tonos + Diaeresis Below (`ά̤`, `ό̤`, `Ά̤`, `Ό̤`):** Press `/` then `;` then `α` (or `ο`, `Α`, `Ο`). Both dead-key orders (`/` + `;` and `;` + `/`) produce canonical NFC output (`U+03AC U+0324` / `U+03CC U+0324`).
- **Dialytika (`Shift + ;`):** `:` then `ι` / `υ` → `ϊ` / `ϋ` (and `Ϊ` / `Ϋ`).
- **Command Shortcuts Preserved:** All macOS `Cmd+C`, `Cmd+V`, `Cmd+X`, `Cmd+Z`, `Cmd+A` shortcuts automatically map through standard ASCII Latin keycodes while Pontic Greek is active.

## Option (`Alt`) Layer

| Key Combination | Output |
|---|---|
| `Option + ε` | `€` |
| `Option + α` | `…` |
| `Option + ι` | `"` |
| `Option + ο` | `„` |
| `Option + ,` | `«` |
| `Option + .` | `»` |
| `Option + Space` | Non-breaking space |

## Recommended Fonts & Troubleshooting

- **Recommended:** **Pontic Sans / Pontic Serif v6.0** (included in [`font/`](../font/)), **Noto Sans / Noto Serif** (post-PR #581), **Cambria**, **Brill**, **Gentium Plus**.
- **Avoid:** **Calibri** (`ψ̌` misaligned) and **Times New Roman** (lacks Greek combining caron anchors).
- **Uninstall:** Remove **Pontic Greek** in System Settings -> Input Sources, then delete `~/Library/Keyboard Layouts/pnt-macos-v3.keylayout`.
