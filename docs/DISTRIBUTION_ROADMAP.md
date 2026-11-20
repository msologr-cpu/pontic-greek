# Distribution & Standards Adoption Roadmap

Status overview across fonts, input platforms, and international standards bodies as of November 2026.

## 1. Google Noto Fonts — Merged & Closed

- **Repository:** `notofonts/latin-greek-cyrillic`
- **Issue:** [#547](https://github.com/notofonts/latin-greek-cyrillic/issues/547) (Closed)
- **Pull Request:** [#581](https://github.com/notofonts/latin-greek-cyrillic/pull/581) (Merged)
- **Outcome:** All missing OpenType GPOS top (`U+030C`, `U+0306`) and bottom (`U+0324`) anchors calibrated across Pontic Sans & Pontic Serif v6.0 were reviewed and merged upstream into Noto sources (`NotoSans` & `NotoSerif`), permanently fixing Greek combining caron, breve, and diaeresis-below rendering for downstream Android, ChromeOS, Linux, and web deployments.

## 2. SIL Keyman — Published (#4180) + v6.1 Update Prepared

- **Live Catalog:** <https://keyman.com/keyboards/pontic_greek> ([`keymanapp/keyboards#4180`](https://github.com/keymanapp/keyboards/pull/4180), merged 2026-10-07)
- **v6.1 Update (Ready for PR):** Adds mobile `PostKeystroke` auto-shift (`shift` -> `default` return after capital letters), double-tap Shift sticky `caps` lock layer, `[SHIFT T_TONOS]` / `[SHIFT T_PONTIC_DK]` dead-key parity, and updated English help pages in [`keyman/`](../keyman/).

## 3. Unicode / CLDR — Submitted on #547 (`unicode-submission`)

- **Branch:** `origin/unicode-submission` (`unicode/` directory)
- **Contents:** Schema-validated CLDR Core Data draft (`pnt.xml`), CLDR Keyboard 3.0 XML (`cldr_keyboard_pnt.xml`, XSD-validated against UTS #35 Part 7), GPOS `anchors.json`, v6.0 TTF fonts, and full linguist verification credits (Prof. D.I. Zimov).
- **Engagement:** Detailed package summary posted on `notofonts/latin-greek-cyrillic#547` tagging `@miloush` (Jan Kučera) for next steps toward formal CLDR Core Data & Keyboard 3.0 onboarding.

## 4. Apple (iOS / iPadOS / macOS System Keyboard) — Prepared (`apple-submission`)

- **Branch:** `apple-submission` (`apple/` directory)
- **Contents:** Clean self-contained English engineering dossier including native macOS `.keylayout`, iOS 3-row touch specification & long-press map (reflecting v6.1 auto-shift + Caps Lock), OFL 1.1 v6.0 font references & GPOS anchor documentation, DTD/XSD-validated CLDR references, and QA test corpus for submission via Apple Feedback Assistant / Localization Engineering.

## 5. Desktop & Third-Party Releases

- **Windows:** Standalone AutoHotkey v2 `.exe` binaries built via GitHub Actions ([`.github/workflows/build-exe.yml`](../.github/workflows/build-exe.yml)).
- **macOS:** Native [`pnt-macos-v3.keylayout`](../pnt-macos-v3.keylayout) + [`install_macos.sh`](../install_macos.sh).
- **Yandex:** Mobile touch layout specification delivered to Yandex Keyboard team.
- **Unicode / Noto Font Workarounds:** Resolved upstream via Noto PR #581 and distributed locally via [`font/`](../font/).
