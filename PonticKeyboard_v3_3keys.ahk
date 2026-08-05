#Requires AutoHotkey v2.0
#SingleInstance Off

; ==============================================================================
; Понтийская Греческая Раскладка (Pontic Greek) — Windows AHK v4.0 (3 клавиши)
; ==============================================================================
; АЛЬТЕРНАТИВНАЯ ВЕРСИЯ (по предложению носителя языка)
;
; Три раздельных мёртвых клавиши рядом в нижнем ряду:
;   ,  → гачек (ˇ)          — ζ̌ χ̌ σ̌ ς̌ κ̌ ξ̌ ψ̌
;   .  → две точки снизу (̤) — α̤ ο̤ ά̤ ό̤
;   /  → бреве (˘)          — γ̆
;
; Изменения v4.0 (ГЛАВНОЕ ОБНОВЛЕНИЕ):
; - НАСТОЯЩЕЕ решение проблем MS Word: скрипт теперь САМ ОТКЛЮЧАЕТ в MS Word
;   автозамену (AutoCorrect), из-за которой ломались σ̌ и τ'. Раньше мы пытались
;   «обмануть» Word — это не срабатывало. Теперь причина устраняется в корне.
; - Уведомление при запуске с НОМЕРОМ ВЕРСИИ.
; - Меню в трее и окно ДИАГНОСТИКИ (Ctrl+Alt+P).
; - Надёжное определение греческой раскладки и вставка через буфер обмена.
; ==============================================================================

global APP_VERSION := "4.0"
global APP_TITLE := "Понтийская клавиатура v" APP_VERSION
global APP_VARIANT := "Вариант 2: три клавиши , . /"

TraySetIcon("shell32.dll", 268)
A_IconTip := APP_TITLE "`n" APP_VARIANT

; Разрешаем отправку сообщений от процессов с меньшими правами (UIPI Bypass)
try {
    DllCall("User32\ChangeWindowMessageFilter", "UInt", 0x0010, "UInt", 1) ; WM_CLOSE
    DllCall("User32\ChangeWindowMessageFilter", "UInt", 0x0111, "UInt", 1) ; WM_COMMAND
}

; ==============================================================================
; Управление единственным экземпляром
; ==============================================================================
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
                    APP_TITLE, "YesNo Icon?"
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

; ==============================================================================
; ОПРЕДЕЛЕНИЕ РАСКЛАДКИ
; ==============================================================================
GetActiveHKL() {
    try {
        hwnd := WinGetID("A")
        tid := DllCall("GetWindowThreadProcessId", "Ptr", hwnd, "Ptr", 0)
        h := DllCall("GetKeyboardLayout", "UInt", tid, "Ptr")
        if (h != 0)
            return h
    }
    return DllCall("GetKeyboardLayout", "UInt", 0, "Ptr")
}

IsGreekLayout() {
    return (GetActiveHKL() & 0xFFFF) == 0x0408
}

; ==============================================================================
; ИСПРАВЛЕНИЕ MS WORD — отключение автозамены, ломающей понтийские символы
; ==============================================================================
global g_WordFixed := false
global g_WordLastPID := 0

FixWordAutoCorrect(silent := true) {
    global g_WordFixed
    try {
        w := ComObjActive("Word.Application")
    } catch {
        if !silent {
            MsgBox(
                "MS Word сейчас не запущен.`n`n"
              . "Откройте Word и снова выберите этот пункт меню,`n"
              . "либо просто начните печатать — исправление применится само.",
                APP_TITLE, "Icon!"
            )
        }
        return false
    }

    try w.AutoCorrect.ReplaceText := false
    try w.AutoCorrect.ReplaceTextFromSpellingChecker := false
    try w.AutoCorrect.CorrectSentenceCaps := false
    try w.AutoCorrect.CorrectInitialCaps := false
    try w.AutoCorrect.CorrectCapsLock := false
    try w.AutoCorrect.CorrectDays := false
    try w.AutoCorrect.CorrectHangulAndAlphabet := false
    try w.Options.AutoFormatAsYouTypeReplaceQuotes := false
    try w.Options.AutoFormatAsYouTypeReplaceSymbols := false
    try w.Options.AutoFormatAsYouTypeReplaceOrdinals := false

    g_WordFixed := true

    if !silent {
        MsgBox(
            "Готово! Автозамена MS Word отключена.`n`n"
          . "Теперь σ̌ между гласными и τ' должны вводиться правильно.",
            APP_TITLE, "Iconi"
        )
    }
    return true
}

WordWatch() {
    global g_WordFixed, g_WordLastPID
    pid := ProcessExist("WINWORD.EXE")
    if (pid == 0) {
        g_WordFixed := false
        g_WordLastPID := 0
        return
    }
    if (pid != g_WordLastPID) {
        g_WordLastPID := pid
        g_WordFixed := false
    }
    if !g_WordFixed
        FixWordAutoCorrect(true)
}
SetTimer(WordWatch, 4000)
SetTimer(() => WordWatch(), -1500)

; ==============================================================================
; ОТПРАВКА СИМВОЛОВ
; ==============================================================================
SendU(chars) {
    SendText(chars)
}

PasteText(str) {
    clipSaved := ClipboardAll()
    A_Clipboard := ""
    A_Clipboard := str
    if !ClipWait(1, 1) {
        SendText(str)
        try A_Clipboard := clipSaved
        return
    }
    SendInput("^v")
    Sleep(150)
    try A_Clipboard := clipSaved
}

SendCombining(base, combining) {
    ; Медиальная сигма σ (U+03C3) — вставляем атомарно через буфер обмена
    if (base == 0x03C3) {
        PasteText(Chr(base) Chr(combining))
    } else {
        SendText(Chr(base) Chr(combining))
    }
}

global g_LastVK := 0
HandleKeyDown(ih, vk, sc) {
    global g_LastVK
    g_LastVK := vk
}

; ==============================================================================
; 1. ГАЧЕК (Caron): Клавиша , (запятая / vkBC)
; ==============================================================================
$*vkBC:: {
    global g_LastVK

    if !IsGreekLayout() {
        Send("{Blind}{vkBC}")
        return
    }

    isShift := GetKeyState("Shift", "P")
    g_LastVK := 0

    ih := InputHook("L1 T2")
    ih.KeyOpt("{All}", "N")
    ih.OnKeyDown := HandleKeyDown
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
    else if (char == "σ" || char == "ς") {
        if (g_LastVK == 0x57)
            SendCombining(0x03C2, 0x030C) ; ς̌
        else
            SendCombining(0x03C3, 0x030C) ; σ̌
    }
    else if (char == "Σ")
        SendCombining(0x03A3, 0x030C) ; Σ̌
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

; ==============================================================================
; 2. ДВЕ ТОЧКИ СНИЗУ (Diaeresis Below): Клавиша . (точка / vkBE)
; ==============================================================================
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

; ==============================================================================
; 3. БРЕВЕ (Breve): Клавиша / (слэш / vkBF)
; ==============================================================================
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

; ==============================================================================
; Страховка: типографский апостроф после τ / Τ
; ==============================================================================
#HotIf IsGreekLayout()
:?*:τ'::τ’
:?*:Τ'::Τ’
#HotIf

; ==============================================================================
; ДИАГНОСТИКА (Ctrl+Alt+P)
; ==============================================================================
ShowDiagnostics(*) {
    global APP_VERSION, APP_TITLE, APP_VARIANT

    hklText := "не определена"
    layoutText := "?"
    winTitle := "?"
    winProc := "?"

    try {
        hwnd := WinGetID("A")
        tid := DllCall("GetWindowThreadProcessId", "Ptr", hwnd, "Ptr", 0)
        hkl := DllCall("GetKeyboardLayout", "UInt", tid, "Ptr")
        langId := hkl & 0xFFFF
        hklText := Format("0x{:04X}", langId)
        layoutText := (langId == 0x0408) ? "ГРЕЧЕСКАЯ — верно"
                    : (langId == 0x0419) ? "Русская — переключитесь на греческую!"
                    : (langId == 0x0409) ? "Английская — переключитесь на греческую!"
                    : "Другая — переключитесь на греческую!"
        winTitle := WinGetTitle(hwnd)
        winProc := WinGetProcessName(hwnd)
    }

    wordState := "MS Word не запущен"
    if ProcessExist("WINWORD.EXE") {
        try {
            w := ComObjActive("Word.Application")
            rt := w.AutoCorrect.ReplaceText
            wordState := rt ? "Word запущен, автозамена ВКЛЮЧЕНА (это плохо)"
                            : "Word запущен, автозамена ОТКЛЮЧЕНА — всё верно"
        } catch {
            wordState := "Word запущен, но связаться с ним не удалось"
        }
    }

    MsgBox(
        "ДИАГНОСТИКА ПОНТИЙСКОЙ КЛАВИАТУРЫ`n"
      . "————————————————————————`n`n"
      . "Версия скрипта: " APP_VERSION "`n"
      . "Файл: " A_ScriptName "`n"
      . "Раскладка: " APP_VARIANT "`n`n"
      . "Активная программа: " winProc "`n"
      . "Окно: " winTitle "`n`n"
      . "Раскладка клавиатуры: " hklText "`n"
      . "  → " layoutText "`n`n"
      . "MS Word: " wordState "`n`n"
      . "————————————————————————`n"
      . "Если что-то не работает — сделайте`n"
      . "снимок этого окна и пришлите его.",
        APP_TITLE " — Диагностика", "Iconi"
    )
}
^!p::ShowDiagnostics()

; ==============================================================================
; МЕНЮ В ТРЕЕ
; ==============================================================================
ShowAbout(*) {
    MsgBox(
        APP_TITLE "`n"
      . APP_VARIANT "`n`n"
      . "Как печатать:`n"
      . "  ,  + ζ χ σ ς κ ξ ψ  →  ζ̌ χ̌ σ̌ ς̌ κ̌ ξ̌ ψ̌  (гачек)`n"
      . "  .  + α ο ά ό         →  α̤ ο̤ ά̤ ό̤        (две точки снизу)`n"
      . "  /  + γ               →  γ̆              (бреве)`n`n"
      . "Обычные , . / печатаются как всегда,`n"
      . "если следом идёт не понтийская буква.`n`n"
      . "Важно: раскладка Windows должна быть ГРЕЧЕСКОЙ.`n"
      . "Переключение: Alt+Shift или Win+Пробел.`n`n"
      . "Диагностика: Ctrl+Alt+P",
        APP_TITLE, "Iconi"
    )
}

A_TrayMenu.Delete()
A_TrayMenu.Add(APP_TITLE, ShowAbout)
A_TrayMenu.SetIcon(APP_TITLE, "shell32.dll", 268)
A_TrayMenu.Default := APP_TITLE
A_TrayMenu.Add()
A_TrayMenu.Add("О программе / Как печатать", ShowAbout)
A_TrayMenu.Add("Диагностика (Ctrl+Alt+P)", ShowDiagnostics)
A_TrayMenu.Add("Починить MS Word (отключить автозамену)", (*) => FixWordAutoCorrect(false))
A_TrayMenu.Add()
A_TrayMenu.Add("Выход", (*) => ExitApp())

; ==============================================================================
; УВЕДОМЛЕНИЕ О ЗАПУСКЕ
; ==============================================================================
TrayTip(
    "Версия " APP_VERSION " запущена.`n"
  . APP_VARIANT "`n"
  . "Не забудьте включить греческую раскладку.",
    APP_TITLE, 0x1
)
SetTimer(() => TrayTip(), -6000)
