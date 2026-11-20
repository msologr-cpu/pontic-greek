# Windows Installation & Usage Guide — Pontic Greek Keyboard

Compatible with **Windows 10 and Windows 11**. No administrator privileges or separate AutoHotkey installation required — the `.exe` builds run portably in any user session.

## Prerequisites

1. In Windows Settings, add the standard **Greek (Ελληνικά)** keyboard layout so you can switch to Greek with `Alt + Shift` or `Win + Space`.
2. Download the desired Windows executable from [`releases/latest`](https://github.com/msologr-cpu/pontic-greek/releases/latest):
   - **`PonticKeyboard_v3.exe`** *(recommended)* — Unified Pontic dead key `/`.
   - **`PonticKeyboard_v3_3keys.exe`** — Optional 3-key variant using `,` (caron), `.` (diaeresis below), and `/` (breve).
   - **`PonticWordRestore.exe`** — Utility to restore MS Word's smart-quote AutoCorrect setting if it was disabled by earlier v4.0–5.0 releases.
3. Install the 8 `Pontic Sans` & `Pontic Serif` v6.0 `.ttf` fonts from [`font/`](../font/) (select all `.ttf` files -> Right-click -> **Install**) for crystal-clear diacritic rendering in Word and LibreOffice.

## Running the Keyboard

Double-click `PonticKeyboard_v3.exe`. An icon appears in the Windows system tray, and the script intercepts keys **only when the active Windows keyboard layout is Greek**. When you switch to English, Russian, or German, it stays completely passive.

- Press `Ctrl + Alt + P` at any time (or click **Diagnostics** in the tray menu) to verify script version, active Windows keyboard layout status, and MS Word AutoCorrect status.

## How to Type (Unified `/` Variant — Recommended)

| Sequence | Output | Unicode (NFC) | Notes |
|---|---|---|---|
| `/` + `ζ` / `χ` / `σ` / `ς` / `κ` / `ξ` / `ψ` | `ζ̌ χ̌ σ̌ ς̌ κ̌ ξ̌ ψ̌` | Base + `U+030C` | Note: on Windows Greek, `W` = `ς`, `S` = `σ` |
| `/` + `γ` | `γ̆` | `U+03B3 U+0306` | Gamma with breve |
| `/` + `α` / `ο` | `α̤` / `ο̤` | Base + `U+0324` | Diaeresis below |
| `;` + `α` / `ο` then `/` (or `/ ά`) | `ά̤` / `ό̤` | `U+03AC/CC U+0324` | Stressed vowels with diaeresis below |
| `/` + `Shift` + letter | `Ζ̌ Χ̌ Σ̌ Κ̌ Ξ̌ Ψ̌ Γ̆ Α̤ Ο̤ Ά̤ Ό̤` | Uppercase | Works with uppercase Shift |
| `/` + `Space` | `/` | `U+002F` | Emits literal forward slash |

## Microsoft Word Smart-Quotes Protection

Earlier v4.0–5.0 versions turned off MS Word's smart quotes globally to protect elision apostrophes. Starting with v5.1+, your global Word preferences are never overwritten; if an older build previously disabled curly quotes (`‘ ’`), run **`PonticWordRestore.exe`** once to restore clean Word behavior.
