#Requires AutoHotkey v2.0
#SingleInstance Force

; ==============================================================================
; Понтийская Греческая Раскладка (Pontic Greek) — Windows AHK v1.2
; ==============================================================================
; Этот скрипт добавляет единую "понтийскую" мёртвую клавишу поверх
; стандартной греческой раскладки Windows.
;
; Требования:
; 1. В Windows должна быть выбрана стандартная ГРЕЧЕСКАЯ раскладка.
; 2. Установлен AutoHotkey v2.
;
; Версия v1.2 — Единая понтийская клавиша:
; - Все понтийские диакритики на одной клавише / (слэш)
; - Скрипт автоматически определяет нужный диакритик по букве:
;     γ/Γ → бреве (γ̆/Γ̆)
;     ζ/χ/σ/ς/κ/ξ/ψ → гачек (ζ̌/χ̌/σ̌/ς̌/κ̌/ξ̌/ψ̌)
;     α/ο → две точки снизу (α̤/ο̤)
;     ά/ό → ударные + две точки снизу (ά̤/ό̤)
; - Апостроф и Shift+запятая работают стандартно
; - Рекомендуемые шрифты: Cambria, Brill, Noto Sans
; ==============================================================================

TraySetIcon("shell32.dll", 268)

; Функция для отправки текста (Text mode — не конфликтует с dead keys)
SendU(chars) {
    SendText(chars)
}

; Функция для отправки комбинируемых символов (base + combining mark)
; Использует SendText чтобы не оставлять "зависшее" состояние клавиатуры.
SendCombining(base, combining) {
    SendText(Chr(base) Chr(combining))
}

; ---------------------------------------------------------
; ЕДИНАЯ ПОНТИЙСКАЯ КЛАВИША: / (слэш / vkBF)
; ---------------------------------------------------------
; Нажмите / затем нужную букву — скрипт сам определит диакритик:
;
; ГАЧЕК (ˇ):
;   / + ζ = ζ̌   / + χ = χ̌   / + σ = σ̌   / + ς = ς̌
;   / + κ = κ̌   / + ξ = ξ̌   / + ψ = ψ̌
;   С Shift: заглавные (Ζ̌, Χ̌, Σ̌, Κ̌, Ξ̌, Ψ̌)
;
; БРЕВЕ (˘):
;   / + γ = γ̆   / + Γ = Γ̆
;
; ДВЕ ТОЧКИ СНИЗУ (̤):
;   / + α = α̤   / + ο = ο̤
;   / + ά = ά̤   / + ό = ό̤  (ударные варианты)
;   С Shift: заглавные (Α̤, Ο̤, Ά̤, Ό̤)
;
; / + пробел = / (слэш)
; / + таймаут = / (слэш)
; Shift + / + таймаут = ? (вопросительный знак)
; / + другая буква = / + буква (passthrough)

$*vkBF:: {
    isShift := GetKeyState("Shift", "P")

    ih := InputHook("L1 T2")
    ih.Start()
    ih.Wait()

    if (ih.Input == "") {
        if isShift
            SendU("?")
        else
            SendU("/")
        return
    }

    char := ih.Input

    ; --- ГАЧЕК (Caron, U+030C) ---
    if (char == "ζ")
        SendCombining(0x03B6, 0x030C) ; ζ̌
    else if (char == "Ζ")
        SendCombining(0x0396, 0x030C) ; Ζ̌
    else if (char == "χ")
        SendCombining(0x03C7, 0x030C) ; χ̌
    else if (char == "Χ")
        SendCombining(0x03A7, 0x030C) ; Χ̌
    else if (char == "σ")
        SendCombining(0x03C3, 0x030C) ; σ̌
    else if (char == "Σ")
        SendCombining(0x03A3, 0x030C) ; Σ̌
    else if (char == "ς")
        SendCombining(0x03C2, 0x030C) ; ς̌  — конечная сигма с гачеком
    else if (char == "κ")
        SendCombining(0x03BA, 0x030C) ; κ̌
    else if (char == "Κ")
        SendCombining(0x039A, 0x030C) ; Κ̌
    else if (char == "ξ")
        SendCombining(0x03BE, 0x030C) ; ξ̌
    else if (char == "Ξ")
        SendCombining(0x039E, 0x030C) ; Ξ̌
    else if (char == "ψ")
        SendCombining(0x03C8, 0x030C) ; ψ̌
    else if (char == "Ψ")
        SendCombining(0x03A8, 0x030C) ; Ψ̌

    ; --- БРЕВЕ (Breve, U+0306) ---
    else if (char == "γ")
        SendCombining(0x03B3, 0x0306) ; γ̆
    else if (char == "Γ")
        SendCombining(0x0393, 0x0306) ; Γ̆

    ; --- ДВЕ ТОЧКИ СНИЗУ (Diaeresis Below, U+0324) ---
    else if (char == "α")
        SendCombining(0x03B1, 0x0324) ; α̤
    else if (char == "Α")
        SendCombining(0x0391, 0x0324) ; Α̤
    else if (char == "ο")
        SendCombining(0x03BF, 0x0324) ; ο̤
    else if (char == "Ο")
        SendCombining(0x039F, 0x0324) ; Ο̤
    else if (char == "ά")
        SendCombining(0x03AC, 0x0324) ; ά̤  — ударная альфа + точки снизу
    else if (char == "Ά")
        SendCombining(0x0386, 0x0324) ; Ά̤
    else if (char == "ό")
        SendCombining(0x03CC, 0x0324) ; ό̤  — ударный омикрон + точки снизу
    else if (char == "Ό")
        SendCombining(0x038C, 0x0324) ; Ό̤

    ; --- ПРОБЕЛ / ДРУГИЕ ---
    else if (char == " ")
        SendU("/") ; пробел = вывести слэш
    else {
        if isShift
            SendU("?" char)
        else
            SendU("/" char)
    }
}

; ---------------------------------------------------------
; Примечания:
; - Тонос (ударение) работает на клавише ; нативно благодаря
;   встроенной греческой раскладке Windows, поэтому в скрипте не нужен.
; - Для конечной сигмы ς используйте клавишу W (стандартная
;   греческая раскладка Windows: S = σ, W = ς).
; - Для ударных ά̤/ό̤ нажмите: ; → α → / (тонос + буква + понтийская клавиша)
; - Рекомендуемые шрифты: Cambria, Brill, Noto Sans
;   (Calibri не поддерживает ψ̌, Times New Roman не поддерживает
;   combining caron с греческими буквами)
; ---------------------------------------------------------

; v1.2
