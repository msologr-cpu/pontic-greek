#Requires AutoHotkey v2.0
#SingleInstance Off

; ==============================================================================
; Понтийская Греческая Раскладка (Pontic Greek) — Windows AHK v3.1 (3 клавиши)
; ==============================================================================
; АЛЬТЕРНАТИВНАЯ ВЕРСИЯ (по предложению Дмитрия Ивановича)
;
; Три раздельных мёртвых клавиши рядом в нижнем ряду:
;   ,  → гачек (ˇ)        — ζ̌ χ̌ σ̌ ς̌ κ̌ ξ̌ ψ̌
;   .  → две точки снизу (̤) — α̤ ο̤ ά̤ ό̤
;   /  → бреве (˘)         — γ̆
;
; Изменения v3.1:
; - Исправлено: ς̌ (конечная сигма с гачеком) выводится при нажатии , + W (ς).
; - Исправлено: устранена ошибка "Could not close the previous instance".
;   Скрипт корректно закрывает старые экземпляры (включая запущенные от админа).
;
; Требования:
; 1. В Windows должна быть выбрана стандартная ГРЕЧЕСКАЯ раскладка.
; 2. Установлен AutoHotkey v2 (или запуск готового .exe).
; ==============================================================================

TraySetIcon("shell32.dll", 268)

; Разрешаем отправку сообщений от процессов с меньшими правами (UIPI Bypass)
try {
    DllCall("User32\ChangeWindowMessageFilter", "UInt", 0x0010, "UInt", 1) ; WM_CLOSE
    DllCall("User32\ChangeWindowMessageFilter", "UInt", 0x0111, "UInt", 1) ; WM_COMMAND
}

; Собственное корректное управление единственным экземпляром
ClosePreviousInstances() {
    DetectHiddenWindows(true)
    ourPID := ProcessExist()
    scriptTitle := A_ScriptName " ahk_class AutoHotkey"

    for hwnd in WinGetList(scriptTitle) {
        winPID := WinGetPID(hwnd)
        if (winPID != ourPID) {
            PostMessage(0x0010, 0, 0, hwnd) ; WM_CLOSE
            if !WinWaitClose(hwnd, 1.5) {
                result := MsgBox(
                    "Обнаружена ранее запущенная копия клавиатуры.`n`n"
                  . "Закрыть старую копию и запустить новую?",
                    "Pontic Keyboard v3.1 (3 клавиши)", "YesNo Icon?"
                )
                if (result == "Yes") {
                    try {
                        RunWait('powershell -Command "Stop-Process -Id ' winPID ' -Force"', , "Hide")
                    } catch {
                        RunWait('*RunAs taskkill /F /PID ' winPID, , "Hide")
                    }
                } else {
                    ExitApp()
                }
            }
        }
    }
}
ClosePreviousInstances()

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

SendU(chars) {
    SendText(chars)
}

SendCombining(base, combining) {
    SendText(Chr(base) Chr(combining))
}

; ---------------------------------------------------------
; 1. ГАЧЕК (Caron): Клавиша , (запятая / vkBC)
; ---------------------------------------------------------
; , + ζ = ζ̌   , + χ = χ̌   , + σ = σ̌   , + ς = ς̌
; , + κ = κ̌   , + ξ = ξ̌   , + ψ = ψ̌
; , + пробел = , (запятая)
; , + таймаут = , (запятая)
; Shift + , + таймаут = < (угловая скобка)

$*vkBC:: {
    if !IsGreekLayout() {
        Send("{Blind}{vkBC}")
        return
    }

    isShift := GetKeyState("Shift", "P")

    ih := InputHook("L1 T2")
    ih.Start()
    ih.Wait()

    if (ih.Input == "") {
        if isShift
            SendU("<")
        else
            SendU(",")
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
        SendCombining(0x03C3, 0x030C) ; σ̌ (медиальная сигма)
    else if (char == "Σ")
        SendCombining(0x03A3, 0x030C) ; Σ̌ (заглавная сигма)
    else if (char == "ς")
        SendCombining(0x03C2, 0x030C) ; ς̌ (конечная сигма с гачеком)
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
        SendU(",")
    else {
        if isShift
            SendU("<" char)
        else
            SendU("," char)
    }
}

; ---------------------------------------------------------
; 2. ДВЕ ТОЧКИ СНИЗУ (Diaeresis Below): Клавиша . (точка / vkBE)
; ---------------------------------------------------------
; . + α = α̤   . + ο = ο̤
; . + ά = ά̤   . + ό = ό̤  (ударные варианты)
; . + пробел = . (точка)
; . + таймаут = . (точка)
; Shift + . + таймаут = > (угловая скобка)

$*vkBE:: {
    if !IsGreekLayout() {
        Send("{Blind}{vkBE}")
        return
    }

    isShift := GetKeyState("Shift", "P")

    ih := InputHook("L1 T2")
    ih.Start()
    ih.Wait()

    if (ih.Input == "") {
        if isShift
            SendU(">")
        else
            SendU(".")
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
        SendCombining(0x03AC, 0x0324) ; ά̤
    else if (char == "Ά")
        SendCombining(0x0386, 0x0324) ; Ά̤
    else if (char == "ό")
        SendCombining(0x03CC, 0x0324) ; ό̤
    else if (char == "Ό")
        SendCombining(0x038C, 0x0324) ; Ό̤
    else if (char == " ")
        SendU(".")
    else {
        if isShift
            SendU(">" char)
        else
            SendU("." char)
    }
}

; ---------------------------------------------------------
; 3. БРЕВЕ (Breve): Клавиша / (слэш / vkBF)
; ---------------------------------------------------------
; / + γ = γ̆   / + Γ = Γ̆
; / + пробел = / (слэш)
; / + таймаут = / (слэш)
; Shift + / + таймаут = ? (вопросительный знак)

$*vkBF:: {
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

    if (char == "γ")
        SendCombining(0x03B3, 0x0306) ; γ̆
    else if (char == "Γ")
        SendCombining(0x0393, 0x0306) ; Γ̆
    else if (char == " ")
        SendU("/")
    else {
        if isShift
            SendU("?" char)
        else
            SendU("/" char)
    }
}
