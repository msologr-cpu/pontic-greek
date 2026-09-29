# Заявка на добавление Core Locale Data для Pontic Greek (pnt) в Unicode CLDR

> **СТАТУС ДОКУМЕНТА:** Черновик для согласования.  
> **ВАЖНО:** Не отправлять в Unicode Jira и репозитории без явного согласия Макса.

---

## 1. Идентификация языка

- **Код языка (BCP 47 / IANA Subtag):** `pnt`
  - Проверено по реестру IANA Language Subtag Registry:
    ```
    Type: language
    Subtag: pnt
    Description: Pontic
    Added: 2009-07-29
    ```
  - Двухбуквенного кода ISO 639-1 не существует. По правилам CLDR («Picking the Right Language Identifier») используется 3-буквенный субтег `pnt`.
- **Название языка:**
  - Английское: **Pontic** / **Pontic Greek**
  - Самоназвание: **Ποντιακά** (Pontiká)
- **Письменность:** Греческая (`Grek`, 200). Направление письма: слева-направо (`left-to-right`), сверху-вниз (`top-to-bottom`).
- **Связь с существующими данными CLDR:**
  В репозитории `unicode-org/cldr` язык `pnt` **уже присутствует в дополнительных метаданных**:
  - `common/supplemental/likelySubtags.xml`: `<likelySubtag from="pnt" to="pnt_Grek_GR"/>`
  - `common/supplemental/supplementalData.xml`: `<language type="pnt" scripts="Grek"/>`
  - `common/validity/language.xml`: входит в регулярный валидный диапазон `png~z`.
  Однако в `common/main/` файл `pnt.xml` **отсутствует**, то есть язык ещё не доведён до уровня Core Data.

---

## 2. Регион по умолчанию и демография

*(Нужно подтвердить Максу — выбрать предпочтительный вариант для тикета)*

### Вариант 1 (Рекомендуемый): Греция (GR)
- **Территория по умолчанию:** `GR` (Greece).
- **Обоснование:**
  1. В самом CLDR в правиле `likelySubtags.xml` язык `pnt` по умолчанию раскрывается именно в `pnt_Grek_GR`.
  2. Греция — основная территория современного компактного проживания и официального функционирования понтийского греческого языка.
- **Оценка численности говорящих:**
  - По данным действующего `supplementalData.xml` в CLDR: **3.7% населения Греции** (~387 000 человек при населении 10 461 100).
  - По данным Ethnologue (ISO 639-3 `pnt`): около 400 000 говорящих в Греции (оценка на базе переселенцев и их потомков).
  - Источник: Ethnologue (27th ed., 2024), Всегреческая федерация понтийских обществ (ΠΟΕ).

### Вариант 2: Международная диаспора (Global / Multi-territory)
- Помимо Греции, CLDR уже содержит демографические записи для:
  - Россия (`RU`): 0.04% (~56 300 человек, перепись РФ / Ethnologue, ref R1335).
  - Турция (`TR`): 0.0061% (~5 130 человек, трапезундские говоры / ромейка, ref R1336).
- Общая оценка носителей и понимающих в мире: 500 000 – 750 000 человек (включая общины в Грузии, Армении, Германии, Казахстане, Украине).

---

## 3. Наборы букв (Exemplar Characters)

Наборы выведены из раскладки клавиатуры и проверены по шрифтам Pontic v6.0 (с калибровкой Зимова Д.И.):

### Основной набор (Main Exemplar Characters):
Буквы стандартного греческого алфавита с монотонической диакритикой + специфические понтийские графемы:
```
[α ά {α̤} {ά̤} β γ {γ̆} {γ̇} δ ε έ {ε̤} ζ {ζ̌} η ή {η̤} θ ι ί ϊ ΐ {ι̱} κ {κ̌} λ μ ν ξ {ξ̌} ο ό {ο̤} {ό̤} π ρ σ ς {σ̌} {ς̌} τ υ ύ ϋ ΰ {υ̤} φ χ {χ̌} ψ {ψ̌} ω ώ {ω̤}]
```
*Примечание:* Комбинируемые знаки по стандарту CLDR оформлены составными графемами в фигурных скобках `{...}`:
- Гачек (U+030C): `{σ̌} {ς̌} {ζ̌} {ξ̌} {ψ̌} {χ̌} {κ̌}`
- Бреве (U+0306): `{γ̆}`
- Точка сверху (U+0307): `{γ̇}`
- Две точки снизу (U+0324): `{α̤} {ά̤} {ε̤} {η̤} {ο̤} {ό̤} {υ̤} {ω̤}`
- Черта снизу (U+0331): `{ι̱}`

### Дополнительный набор (Auxiliary Exemplar Characters):
Политонические знаки, встречающиеся в классических понтийских текстах и исторических словарях (Пападопулос и др.):
```
[ἀ ἄ ἂ ἆ ἁ ἅ ἃ ἇ ὰ ᾶ ἐ ἔ ἒ ἑ ἕ ἓ ὲ ἠ ἤ ἢ ἦ ἡ ἥ ἣ ἧ ὴ ῆ ἰ ἴ ἲ ἶ ἱ ἵ ἳ ἷ ὶ ῖ ῒ ῗ ὄ ὂ ὃ ὸ ὐ ὔ ὒ ὖ ὑ ὕ ὓ ὗ ὺ ῦ ῢ ῧ ὤ ὢ ὦ ὥ ὣ ὧ ὼ ῶ]
```

### Набор индекса (Index Exemplar Characters):
Заглавные буквы для алфавитных указателей:
```
[Α {Α̤} Β Γ {Γ̆} {Γ̇} Δ Ε {Ε̤} Ζ {Ζ̌} Η {Η̤} Θ Ι {Ι̱} Κ {Κ̌} Λ Μ Ν Ξ {Ξ̌} Ο {Ο̤} Π Ρ Σ {Σ̌} Τ Υ {Υ̤} Φ Χ {Χ̌} Ψ {Ψ̌} Ω {Ω̤}]
```

### Цифры и пунктуация:
- Цифры: `[\- ‐ ‑ , . % ‰ + 0 1 2 3 4 5 6 7 8 9]`
- Пунктуация: `[\- ‐ ‑ – — , ; \: ! ? . … ' ’ " « » ( ) \[ \] § @ * / \&]`

---

## 4. Календарно-временные форматы

- **Формат времени:** 24-часовой предпочтительный (`H:mm`), 12-часовой допустимый (`h:mm a`).
- **Первый день недели:** Понедельник (код `mon`, стандарт региона `GR`).

---

## 5. Проект текста для тикета в Unicode Jira (CLDR)

```
Project: CLDR
Issue Type: New Locale
Summary: Add core data for Pontic Greek [pnt]

Description:
We would like to submit core data for Pontic Greek (ISO 639-3: pnt, BCP 47: pnt).
Pontic is already recognized in CLDR supplementalData.xml (languageData for 'pnt' with Grek script, and territoryInfo for GR, RU, TR) and likelySubtags.xml (pnt -> pnt_Grek_GR).

However, core locale data in common/main/ is currently missing, which prevents the keyboard repository from accepting keyboards for pnt.

Proposed Core Data Details:
- Language: pnt (Pontic / Ποντιακά)
- Default Territory: GR (Greece)
- Default Content: pnt_GR
- Script: Grek (Greek)
- Orientation: left-to-right
- Time cycle: 24-hour preferred (H), 12-hour allowed
- Exemplar characters: Greek monotonic alphabet + Pontic combining marks (caron, breve, dot above, diaeresis below, macron below)
- External references: ISO 639-3 (SIL), UNESCO Atlas of Endangered Languages, Ethnologue.

Attached files:
- common/main/pnt.xml
- common/main/pnt_GR.xml
- patch for supplementalMetadata.xml (defaultContent: pnt_GR)
- patch for attributeValueValidity.xml (pnt added to $languageNonTcLtBasic)
```
