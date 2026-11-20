# Unicode CLDR Core Locale Data Proposal — Pontic Greek (`pnt`)

> **Status:** Schema-verified and submitted on branch [`unicode-submission`](../../unicode) (referenced in `notofonts/latin-greek-cyrillic#547`). Submitter: Maxim Solomonidi (`msologr@gmail.com`). Linguistic advisor: Prof. D. I. Zimov.

## 1. CLDR Core Data Submission Requirements

Source specification: <https://cldr.unicode.org/index/cldr-spec/core-data-for-new-locales>

1. Language code: **`pnt`** (ISO 639-3 / BCP 47).
2. Four exemplar character sets: `main`, `auxiliary`, `numbers`, `punctuation` (see Section 6 and [`pnt.xml`](../../cldr/pnt.xml)).
3. Verified speaker population figures by territory (covering roughly 75% of total language users where attested).
4. Default script (`Grek`) and default region (`GR`).
5. Preferred time cycle in default region (`h` preferred, `H` allowed — aligned with CLDR `timeData` for `GR`).
6. Survey Tool commitment to advance the locale to **Basic** coverage in the next open cycle.

## 2. Language Identification & Existing CLDR Coverage

- **Code:** `pnt` (ISO 639-3, IANA, BCP 47; no ISO 639-1 2-letter code exists).
- **Name / Autonym:** Pontic / Pontic Greek; endonym **Ποντιακά** (also **Ρωμαίικα**).
- **Default Script:** Greek (`Grek`, LTR).
- **Existing upstream CLDR entries (`main`):**
  - `likelySubtags.xml`: `pnt` -> `pnt_Grek_GR`, `pnt_RU` -> `pnt_Cyrl_RU`, `pnt_TR` -> `pnt_Latn_TR`.
  - `supplementalData.xml`: `pnt` primary script `Grek` (GR 3.7%), secondary `Cyrl` (RU 0.04%), `Latn` (TR 0.0061%).

## 3. Speaker Population Reference Data

CLDR tracks active language users (L1 + L2) rather than ethnic heritage totals alone. Both metrics are documented clearly below:

| Territory | Speaker Estimate | Source | Notes |
|---|---|---|---|
| **Worldwide** | **778,000** | *Ethnologue*, 21st ed. (2018 snapshot) | Total users across all countries |
| **Greece (`GR`)** | **400,000** | *Ethnologue* (citing Z. Diakonikolaou, 2009) | ~3.7–3.8% of population; matches CLDR `supplementalData.xml` |
| **Russia (`RU`)** | **~56,000** | Existing CLDR (`0.04%`, R1335) | Marked as declining usage (`pnt_Cyrl`) |
| **Türkiye (`TR`)** | **~5,100** | Existing CLDR (`0.0061%`, R1336) | Romeyka variety, Trabzon (`pnt_Latn`) |

Context: UNESCO classifies Pontic as *Definitely Endangered* (2010 Atlas); worldwide Pontic Greek heritage population is estimated at 2.0–2.5 million across Greece, USA, Germany, Russia, Ukraine, Georgia, Kazakhstan, and Australia.

## 4. Basic-Level Survey Tool Corpus (Validated by Prof. D. I. Zimov)

1. **Language name:** full `Το ποντεϊκόν η γλώσσα`; short/synonyms `τα ποντεϊκά`, `το ρωμαίικον η γλώσσα`, `τα ρωμαίικα`.
2. **Script name:** `Το ελενικόν η γραφή`.
3. **Territory names:** Greece `Η Ελλάδα`, Russia `Η Ρουσία`, Türkiye `Η Τουρκία`, Germany `Η Γερμανία`, USA `Η Αμερική`, UK `Η Αγγλία`.
4. **Months (1–12):** `ο Καλαντάτρς`, `ο Κούντουρον`, `ο Μάρτς`, `ο Απρίλτς`, `ο Καλομηνάς`, `ο Κερασινόν`, `ο Χορτοθέρτς`, `ο Αλωνάρτς` (`ο Αύγουστον`), `ο Σταυρίτες`, `ο Τρυγομηνάς`, `ο Αεργίτες` (`ο Αγιωργίτες`), `ο Χριστιαννάρτς` (`ο Χριστιεννάρτς`).
5. **Weekdays (Sun–Sat):** `η Κερεκή`, `η Δευτέρα`, `η Τρίτ’`, `η Τετράδ`, `η Πέφτ’`, `η Παρασ̌κευή`, `η Σάββα`.
6. **AM / PM:** `πριν το μεσημέρ` / `μετά το μεσημέρ`.
7. **Date & time formats:** `11 τι (τη) Τρυγομηνά 2026`, `16:57`.
8. **Date intervals:** `ας … ους` (e.g., `ας 11 ους 15 Τρυγομηνά`).
9. **Time zones & numbers:** Aligned with Modern Greek (`Ώρα ({0})`, `GMT+3`, decimal `,`, grouping `.`).
10. **Delimiters:** `« »`.
11. **Measurement system:** `Μετρικόν σύστεμαν μέτρων` (metric).
12. **Locale display pattern:** `Ποντεϊκά (Ελλάδα)` / `Ρωμαίικα (Ελλάδα)`.

## 5. Character Sets (Final Canonical NFC Repertoire)

- **`main`:** `[α ά {α̤} {ά̤} β γ {γ̆} δ ε έ ζ {ζ̌} η ή θ ι ί ϊ ΐ κ {κ̌} λ μ ν ξ {ξ̌} ο ό {ο̤} {ό̤} π ρ σ ς {σ̌} {ς̌} τ υ ύ ϋ ΰ φ χ {χ̌} ψ {ψ̌} ω ώ]`
- **`auxiliary`:** `[ἀἄἂἆἁἅἃἇὰᾶ ἐἔἒἑἕἓὲ ἠἤἢἦἡἥἣἧὴῆ ἰἴἲἶἱἵἳἷὶῖῒῗ ὄὂὃὸ ὐὔὒὖὑὕὓὗὺῦῢῧ ὤὢὦὥὣὧὼῶ]`
- **`index`:** `[Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω]` *(uses Greek `U+039A` Kappa, avoiding any Cyrillic homoglyph)*.
- **`numbers`:** `[\- ‐‑ , . % ‰ + 0 1 2 3 4 5 6 7 8 9]`
- **`punctuation`:** `[\- ‐‑ – — , ; \: ! . … ' ’ " « » ( ) \[ \] § @ * / \\ \&]` *(uses Greek question mark `;` plus elision apostrophes `'`, `’`)*.

## 6. Supporting References

- SIL Keyman Keyboard: <https://keyman.com/keyboards/pontic_greek> ([PR #4180](https://github.com/keymanapp/keyboards/pull/4180))
- Google Noto GPOS Fix: [`notofonts/latin-greek-cyrillic#581`](https://github.com/notofonts/latin-greek-cyrillic/pull/581) (Issue [#547](https://github.com/notofonts/latin-greek-cyrillic/issues/547))
- Source Repository: <https://github.com/msologr-cpu/pontic-greek>
