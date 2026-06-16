#Requires AutoHotkey v2.0
#SingleInstance Force

; ==============================================================================
; Понтийская Греческая Раскладка (Pontic Greek) — Windows AHK v1.1
; ==============================================================================
; Этот скрипт добавляет "мертвые клавиши" для понтийского языка поверх 
; стандартной греческой раскладки Windows.
; 
; Требования:
; 1. В Windows должна быть выбрана стандартная ГРЕЧЕСКАЯ раскладка.
; 2. Установлен AutoHotkey v2.
;
; Исправления v1.1:
; - Исправлено: после набора α̤/ο̤ не нужно нажимать пробел для продолжения
; - Добавлен гачек для ς (конечная сигма): ' + ς = ς̌
; - Добавлена поддержка ударных вариантов: ; + α + / = ά̤, ; + ο + / = ό̤
; - Напоминание: для ς на конце слов используйте клавишу W
; ==============================================================================

TraySetIcon("shell32.dll", 268)

; Функция для отправки текста (Text mode — не конфликтует с dead keys)
SendU(chars) {
    SendText(chars)
}

; Функция для отправки комбинируемых символов (base + combining mark)
; Использует SendText чтобы не оставлять "зависшее" состояние клавиатуры.
; Именно это исправляет проблему с необходимостью нажимать пробел после α̤/ο̤.
SendCombining(base, combining) {
    SendText(Chr(base) Chr(combining))
}

; ---------------------------------------------------------
; 1. ГАЧЕК (Caron): Клавиша ' (апостроф / vkDE)
; ---------------------------------------------------------
; Нажмите ' затем нужную букву:
;   ' + ζ = ζ̌   ' + χ = χ̌   ' + σ = σ̌   ' + ς = ς̌
;   ' + κ = κ̌   ' + ξ = ξ̌   ' + ψ = ψ̌
; С Shift: заглавные (Ζ̌, Χ̌, Σ̌, Κ̌, Ξ̌, Ψ̌)
; ' + пробел = ˇ (гачек отдельно)
; ' + другая буква = апостроф + буква
; Shift + ' + таймаут = " (кавычка)

$*vkDE:: {
    isShift := GetKeyState("Shift", "P")
    
    ih := InputHook("L1 T2")
    ih.Start()
    ih.Wait()
    
    if (ih.Input == "") {
        if isShift
            SendU('"')
        else
            SendU("'")
        return
    }
    
    char := ih.Input
    
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
    else if (char == " ")
        SendText(Chr(0x02C7)) ; ˇ гачек отдельным символом
    else {
        if isShift
            SendU('"' char)
        else
            SendU("'" char)
    }
}

; ---------------------------------------------------------
; 2. ДВЕ ТОЧКИ СНИЗУ (Dot Below): Клавиша / (слэш / vkBF)
; ---------------------------------------------------------
; Нажмите / затем нужную букву:
;   / + α = α̤   / + ο = ο̤
;   / + ά = ά̤   / + ό = ό̤  (ударные варианты)
; С Shift: заглавные (Α̤, Ο̤, Ά̤, Ό̤)
; / + пробел = ̤ (метка отдельно)
; / + другая буква = слэш + буква
; Shift + / + таймаут = ? (вопросительный знак)

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
    
    if (char == "α")
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
    else if (char == " ")
        SendText(Chr(0x0324)) ; ̤ метка отдельным символом
    else {
        if isShift
            SendU("?" char)
        else
            SendU("/" char)
    }
}

; ---------------------------------------------------------
; 3. БРЕВЕ (Breve): Клавиша Shift + , (запятая / vkBC)
; ---------------------------------------------------------
; Нажмите Shift+, затем нужную букву:
;   Shift+, + γ = γ̆   Shift+, + Γ = Γ̆
; Shift+, + пробел = ˘ (бреве отдельно)
; Shift+, + другая буква = < + буква

$+vkBC:: {
    ih := InputHook("L1 T2")
    ih.Start()
    ih.Wait()
    
    if (ih.Input == "") {
        SendU("<")
        return
    }
    
    char := ih.Input
    
    if (char == "γ")
        SendCombining(0x03B3, 0x0306) ; γ̆
    else if (char == "Γ")
        SendCombining(0x0393, 0x0306) ; Γ̆
    else if (char == " ")
        SendText(Chr(0x02D8)) ; ˘
    else {
        SendU("<" char)
    }
}

; ---------------------------------------------------------
; Примечания:
; - Тонос (ударение) работает на клавише ; нативно благодаря 
;   встроенной греческой раскладке Windows, поэтому в скрипте не нужен.
; - Для конечной сигмы ς используйте клавишу W (стандартная 
;   греческая раскладка Windows: S = σ, W = ς).
; - Для ударных α̤/ο̤ нажмите: ; → α → / (тонос + буква + точки снизу)
; ---------------------------------------------------------
