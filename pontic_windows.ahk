#Requires AutoHotkey v2.0
#SingleInstance Force

; ==============================================================================
; Понтийская Греческая Раскладка (Pontic Greek) — Windows AHK
; ==============================================================================
; Этот скрипт добавляет "мертвые клавиши" для понтийского языка поверх 
; стандартной греческой раскладки Windows.
; 
; Требования:
; 1. В Windows должна быть выбрана стандартная ГРЕЧЕСКАЯ раскладка.
; 2. Установлен AutoHotkey v2.
; ==============================================================================

TraySetIcon("shell32.dll", 268) ; Устанавливаем иконку клавиатуры в трее

; Функция для отправки Unicode-символов
SendU(chars) {
    Send("{Text}" chars)
}

; ---------------------------------------------------------
; 1. ГАЧЕК (Caron): Клавиша ' (апостроф / vkDE)
; ---------------------------------------------------------
$*vkDE:: {
    isShift := GetKeyState("Shift", "P")
    
    ih := InputHook("L1 T2") ; Ждем 1 символ, таймаут 2 секунды
    ih.Start()
    ih.Wait()
    
    if (ih.Input == "") {
        ; Если ничего не нажали за 2 секунды, выводим сам апостроф/кавычку
        if isShift
            SendU('"')
        else
            SendU("'")
        return
    }
    
    char := ih.Input
    
    if (char == "ζ")
        Send("{U+03B6}{U+030C}") ; ζ̌
    else if (char == "Ζ")
        Send("{U+0396}{U+030C}") ; Ζ̌
    else if (char == "χ")
        Send("{U+03C7}{U+030C}")
    else if (char == "Χ")
        Send("{U+03A7}{U+030C}")
    else if (char == "σ")
        Send("{U+03C3}{U+030C}")
    else if (char == "Σ")
        Send("{U+03A3}{U+030C}")
    else if (char == "κ")
        Send("{U+03BA}{U+030C}")
    else if (char == "Κ")
        Send("{U+039A}{U+030C}")
    else if (char == "ξ")
        Send("{U+03BE}{U+030C}")
    else if (char == "Ξ")
        Send("{U+039E}{U+030C}")
    else if (char == "ψ")
        Send("{U+03C8}{U+030C}")
    else if (char == "Ψ")
        Send("{U+03A8}{U+030C}")
    else if (char == " ")
        Send("{U+02C7}") ; Гачек отдельным символом
    else {
        ; Если нажата другая клавиша, выводим апостроф + нажатый символ
        if isShift
            SendU('"' char)
        else
            SendU("'" char)
    }
}

; ---------------------------------------------------------
; 2. ДВЕ ТОЧКИ СНИЗУ (Dot Below): Клавиша / (слэш / vkBF)
; ---------------------------------------------------------
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
        Send("{U+03B1}{U+0324}") ; α̤
    else if (char == "Α")
        Send("{U+0391}{U+0324}")
    else if (char == "ο")
        Send("{U+03BF}{U+0324}")
    else if (char == "Ο")
        Send("{U+039F}{U+0324}")
    else if (char == " ")
        Send("{U+0324}") ; Метка отдельным символом
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
$+vkBC:: {
    ih := InputHook("L1 T2")
    ih.Start()
    ih.Wait()
    
    if (ih.Input == "") {
        SendU("<") ; Shift+, на стандартной клавиатуре выводит <
        return
    }
    
    char := ih.Input
    
    if (char == "γ")
        Send("{U+03B3}{U+0306}") ; γ̆
    else if (char == "Γ")
        Send("{U+0393}{U+0306}")
    else if (char == " ")
        Send("{U+02D8}")
    else {
        SendU("<" char)
    }
}

; Тонос (ударение) работает на клавише [ ; ] нативно благодаря 
; встроенной греческой раскладке Windows, поэтому в скрипте не нужен.
