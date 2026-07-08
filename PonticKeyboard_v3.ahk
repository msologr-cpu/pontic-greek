#Requires AutoHotkey v2.0
#SingleInstance Force

; ==============================================================================
; Понтийская Греческая Раскладка (Pontic Greek) — Windows AHK v3.0
; ==============================================================================
; Единая понтийская мёртвая клавиша / (слэш) поверх стандартной греческой
; раскладки Windows.
;
; Требования:
; 1. В Windows должна быть выбрана стандартная ГРЕЧЕСКАЯ раскладка.
; 2. Установлен AutoHotkey v2.
;
; Изменения v3.0 (относительно v1.2):
; - Исправлено: σ̌ в межгласном/постконсонантном положении (ас̌а) —
;   Windows auto-converts σ→ς из-за паузы InputHook, теперь ς всегда → σ̌
; - Исправлено: хук больше не перехватывает клавиши в русской/другой раскладке
;   (добавлена проверка IsGreekLayout)
; - Добавлено: предупреждение при запуске от имени администратора
;   (причина ошибки "Could not close the previous instance")
;
; Рекомендуемые шрифты: Cambria, Brill, Noto Sans
; ==============================================================================

TraySetIcon("shell32.dll", 268)

; Предупреждение если запущено от имени администратора
if A_IsAdmin {
    MsgBox("Скрипт запущен от имени администратора.`n`n"
         . "Это может вызвать ошибку 'Could not close the previous instance' "
         . "при повторном запуске.`n`n"
         . "Рекомендуется запускать БЕЗ прав администратора.",
         "Pontic Keyboard v3", "Icon!")
}

; Проверка: активна ли греческая раскладка (0x0408 = Greek)
IsGreekLayout() {
    try {
        threadId := DllCall("GetWindowThreadProcessId", "Ptr", WinGetID("A"), "Ptr", 0)
        hkl := DllCall("GetKeyboardLayout", "UInt", threadId, "Ptr")
        return (hkl & 0xFFFF) == 0x0408
    } catch {
        return false
    }
}

; Функция для отправки текста (Text mode — не конфликтует с dead keys)
SendU(chars) {
    SendText(chars)
}

; Функция для отправки комбинируемых символов (base + combining mark)
SendCombining(base, combining) {
    SendText(Chr(base) Chr(combining))
}

; ---------------------------------------------------------
; ЕДИНАЯ ПОНТИЙСКАЯ КЛАВИША: / (слэш / vkBF)
; ---------------------------------------------------------
; Нажмите / затем нужную букву — скрипт сам определит диакритик:
;
; ГАЧЕК (ˇ):
;   / + ζ = ζ̌   / + χ = χ̌   / + σ = σ̌   / + ς = σ̌
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
;
; Для ударных ά̤/ό̤:  / → ; → α  (понтийская → тонос → буква)
;   или:              ; → / → α  (тонос → понтийская → буква)

$*vkBF:: {
    ; Не перехватываем клавишу если активна НЕ греческая раскладка
    if !IsGreekLayout() {
        Send("{Blind}{vkBF}")
        return
    }

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
        SendCombining(0x03C3, 0x030C) ; σ̌ — ВСЕГДА медиальная сигма
                                       ; Windows auto-converts σ→ς из-за паузы dead key,
                                       ; поэтому пользователь на самом деле нажал S (= σ)
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
; - Для ударных ά̤/ό̤ нажмите: / → ; → α (или ; → / → α)
;   Порядок dead keys не важен, буква нажимается последней.
; - Рекомендуемые шрифты: Cambria, Brill, Noto Sans
;   (Calibri не поддерживает ψ̌, Times New Roman не поддерживает
;   combining caron с греческими буквами)
; ---------------------------------------------------------
