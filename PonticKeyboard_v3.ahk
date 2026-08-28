#Requires AutoHotkey v2.0
#SingleInstance Off

; ==============================================================================
; Понтийская Греческая Раскладка (Pontic Greek) — Windows AHK v5.1
; ==============================================================================
; Единая понтийская мёртвая клавиша / (слэш) поверх стандартной греческой
; раскладки Windows.
;
; Изменения v5.1 — ИСПРАВЛЕНИЕ ПРОБЛЕМЫ С АПОСТРОФОМ:
; - НАЙДЕНА И УСТРАНЕНА ПРИЧИНА жалобы Д.И.: «клавиша Э печатает прямой штрих
;   вместо ‘ ’, и даже при выключенной понтийской раскладке».
;   Виноваты были МЫ: версии 4.0–5.0 выключали в Word «умные кавычки»
;   (AutoFormatAsYouTypeReplaceQuotes := false). Это глобальная настройка,
;   она сохраняется в реестре и действует во всех документах постоянно.
;   Программа ломала её и никогда не возвращала обратно.
; - Теперь: «умные кавычки» НЕ выключаются. Если они уже выключены прошлой
;   версией — программа включает их обратно (лечит след старой ошибки).
; - Добавлено ВОССТАНОВЛЕНИЕ настроек при выходе (OnExit) и пункт меню
;   «Восстановить апостроф ‘κ’ в Word».
; - Из автозамены удаляются только конкретные вредные записи (τ' → τα'),
;   а не вся автозамена целиком. При выходе они возвращаются на место.
; - Хотстринги апострофа теперь работают только ВНЕ Word, чтобы не спорить
;   со штатными «умными кавычками».
;
; Изменения v5.0:
; - Единая версия всего релиза (шрифты, клавиатура, эта программа) — 5.0.
;   Логика ввода не менялась относительно 4.1; обновлён номер версии, чтобы
;   у пользователя всё сходилось. Главное в 5.0 — полное семейство шрифтов
;   (Regular/Italic/Bold/Bold Italic) для Pontic Sans и Pontic Serif.
;
; Изменения v4.1:
; - ИСПРАВЛЕНА КОНЕЧНАЯ СИГМА ς̌ (по отзыву Д.И.: «не пропечатывается вообще,
;   и W, и S дают медиальную»). Причина: выбор σ̌/ς̌ шёл по физической клавише
;   через переменную g_LastVK, заполняемую колбэком InputHook.OnKeyDown.
;   Колбэк не гарантированно срабатывал до проверки — g_LastVK оставался 0,
;   и код всегда уходил в ветку «медиальная σ̌». До вставки ς̌ дело не доходило.
;   Решение: определяем сигму ПО СИМВОЛУ, который вернул перехватчик
;   (греческая раскладка сама даёт W → ς, S → σ). Клавиша — лишь запасной путь.
; - Конечная ς̌ теперь тоже вставляется атомарно через буфер обмена (раньше
;   атомарно шла только медиальная σ̌) — защита от подмены σ ↔ ς в Word.
;
; Изменения v4.0:
; - НАСТОЯЩЕЕ решение проблем MS Word: скрипт теперь САМ ОТКЛЮЧАЕТ в MS Word
;   автозамену (AutoCorrect), из-за которой ломались σ̌ и τ'. Раньше мы пытались
;   «обмануть» Word — это не срабатывало. Теперь причина устраняется в корне.
; - Уведомление при запуске с НОМЕРОМ ВЕРСИИ — теперь всегда видно, какая
;   именно версия работает.
; - Меню в трее: «О программе», «Диагностика», «Починить MS Word», «Выход».
; - Окно ДИАГНОСТИКИ (Ctrl+Alt+P): показывает версию, активную раскладку,
;   программу и состояние MS Word. Скриншот этого окна помогает найти проблему.
; - Надёжное определение греческой раскладки (с запасным способом).
; - Надёжная вставка через буфер обмена (ClipWait + корректные задержки).
;
; Требования:
; 1. В Windows должна быть выбрана стандартная ГРЕЧЕСКАЯ раскладка.
; 2. Установлен AutoHotkey v2 (или запуск готового .exe).
; ==============================================================================

global APP_VERSION := "5.1"
global APP_TITLE := "Понтийская клавиатура v" APP_VERSION
global APP_VARIANT := "Вариант 1: одна клавиша /"

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
    ; Запасной способ: раскладка текущего потока
    return DllCall("GetKeyboardLayout", "UInt", 0, "Ptr")
}

IsGreekLayout() {
    return (GetActiveHKL() & 0xFFFF) == 0x0408
}

; ==============================================================================
; MS WORD — аккуратное вмешательство (v5.1)
; ==============================================================================
; ИСТОРИЯ ОШИБКИ — чтобы никогда не повторить:
;
;   В версиях 4.0–5.0 скрипт выключал в Word «умные кавычки»:
;       w.Options.AutoFormatAsYouTypeReplaceQuotes := false
;
;   Это ГЛОБАЛЬНАЯ настройка Word: она пишется в реестр
;   (HKCU\Software\Microsoft\Office\...\Word) и остаётся там НАВСЕГДА —
;   даже после выхода из нашей программы. Мы ломали и не чинили.
;
;   Последствия у Дмитрия Ивановича: апостроф на клавише «Э» перестал
;   давать типографские ‘ ’ и стал давать прямой штрих ' — во всех
;   документах, в том числе при ВЫКЛЮЧЕННОЙ понтийской раскладке.
;   Вернуть удалось только удалением ветки реестра.
;
;   Причина в том, что правильное понтийское ‘κ’ делают именно «умные
;   кавычки» Word: слева U+2018 (перевёрнутая запятая), справа U+2019.
;   ЭТУ НАСТРОЙКУ ТРОГАТЬ НЕЛЬЗЯ. Наоборот: если она выключена — включаем.
;
; ЧТО ДЕЛАЕМ ТЕПЕРЬ:
;   1. ВОССТАНАВЛИВАЕМ «умные кавычки», если они выключены — лечим след,
;      оставленный прошлыми версиями на машине пользователя.
;   2. Удаляем ТОЛЬКО одну вредную запись автозамены (τ' → τα' и подобные
;      из греческого списка Office), запомнив её содержимое.
;   3. При выходе из программы возвращаем всё в исходное состояние.
;
;   Проблема σ̌/ς̌ решается атомарной вставкой (PasteText) начиная с v4.1,
;   поэтому глобальные переключатели автозамены больше НЕ трогаем.
; ==============================================================================
global g_WordFixed := false
global g_WordLastPID := 0
global g_RemovedEntries := []   ; [{name, value}] — удалённые записи автозамены
global g_QuotesHealed := false  ; включали ли мы «умные кавычки» обратно

; Записи автозамены, ломающие понтийский набор: греческая буква + апостроф,
; после которых Office подставляет лишнюю букву (τ' → τα').
IsHarmfulEntry(name, value) {
    ; Интересуют только короткие записи вида «буква + апостроф»
    if (StrLen(name) > 3)
        return false
    if !(InStr(name, "'") || InStr(name, "’"))
        return false
    ; Вредная запись добавляет символы к тому, что набрал пользователь
    return (StrLen(value) > StrLen(name))
}

FixWordAutoCorrect(silent := true) {
    global g_WordFixed, g_RemovedEntries, g_QuotesHealed
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

    ; --- 1. ЛЕЧЕНИЕ: возвращаем «умные кавычки», если их кто-то выключил ---
    ; Именно они дают правильные понтийские ‘κ’ с обеих сторон.
    healed := false
    try {
        if (w.Options.AutoFormatAsYouTypeReplaceQuotes = false) {
            w.Options.AutoFormatAsYouTypeReplaceQuotes := true
            healed := true
            g_QuotesHealed := true
        }
    }

    ; --- 2. Убираем только конкретные вредные записи автозамены ---
    removed := 0
    if (g_RemovedEntries.Length = 0) {
        try {
            entries := w.AutoCorrect.Entries
            doomed := []
            for e in entries {
                try {
                    if IsHarmfulEntry(e.Name, e.Value)
                        doomed.Push({name: e.Name, value: e.Value})
                }
            }
            for item in doomed {
                try {
                    entries.Item(item.name).Delete()
                    g_RemovedEntries.Push(item)
                    removed++
                }
            }
        }
    }

    g_WordFixed := true

    if !silent {
        msg := "Настройки MS Word проверены.`n`n"
        if healed
            msg .= "• «Умные кавычки» были выключены — включил обратно.`n"
                .  "  Апостроф снова печатается правильно: ‘κ’`n"
        else
            msg .= "• «Умные кавычки» включены — апостроф ‘κ’ работает.`n"
        if (g_RemovedEntries.Length > 0)
            msg .= "• Убрано вредных правил автозамены: "
                .  g_RemovedEntries.Length "`n"
        msg .= "`nПри выходе из программы всё вернётся как было."
        MsgBox(msg, APP_TITLE, "Iconi")
    }
    return true
}

; ==============================================================================
; ВОССТАНОВЛЕНИЕ настроек Word — вызывается при выходе и из меню
; ==============================================================================
RestoreWordSettings(silent := true) {
    global g_RemovedEntries
    try {
        w := ComObjActive("Word.Application")
    } catch {
        if !silent {
            MsgBox(
                "MS Word сейчас не запущен.`n`n"
              . "Откройте Word и выберите этот пункт снова.",
                APP_TITLE, "Icon!"
            )
        }
        return false
    }

    ; Всегда включаем «умные кавычки» — это нормальное состояние Word
    ; и то, что нужно для правильного апострофа ‘κ’.
    try w.Options.AutoFormatAsYouTypeReplaceQuotes := true

    ; Возвращаем удалённые записи автозамены
    restored := 0
    try {
        for item in g_RemovedEntries {
            try {
                w.AutoCorrect.Entries.Add(item.name, item.value)
                restored++
            }
        }
    }
    g_RemovedEntries := []

    if !silent {
        MsgBox(
            "Настройки MS Word восстановлены.`n`n"
          . "• «Умные кавычки» включены — апостроф ‘κ’ печатается верно.`n"
          . "• Возвращено правил автозамены: " restored "`n`n"
          . "Перезапускать Word не нужно.",
            APP_TITLE, "Iconi"
        )
    }
    return true
}

; При закрытии программы обязательно приводим Word в исходное состояние
OnExit((*) => RestoreWordSettings(true))

; Следим за запуском Word и применяем исправление автоматически
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

; Надёжная вставка через буфер обмена (страховка от посимвольной автозамены)
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

; Отправка комбинируемых символов (база + комбинируемый знак)
SendCombining(base, combining) {
    ; ОБЕ сигмы — медиальная σ (U+03C3) и конечная ς (U+03C2) — вставляем
    ; атомарно через буфер обмена. Если отправлять их посимвольно, Word и
    ; некоторые редакторы успевают вмешаться между буквой и гачеком и
    ; подменяют σ ↔ ς (гачек для них не буква, значит «конец слова»).
    if (base == 0x03C3 || base == 0x03C2) {
        PasteText(Chr(base) Chr(combining))
    } else {
        SendText(Chr(base) Chr(combining))
    }
}

; ==============================================================================
; ЕДИНАЯ ПОНТИЙСКАЯ КЛАВИША: / (слэш / vkBF)
; ==============================================================================
global g_LastVK := 0
HandleKeyDown(ih, vk, sc) {
    global g_LastVK
    g_LastVK := vk
}

$*vkBF:: {
    global g_LastVK

    if !IsGreekLayout() {
        Send("{Blind}{vkBF}")
        return
    }

    isShift := GetKeyState("Shift", "P")
    g_LastVK := 0

    ih := InputHook("L1 T2")
    ih.KeyOpt("{All}", "N")     ; Уведомления обо всех клавишах → OnKeyDown
    ih.OnKeyDown := HandleKeyDown
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
    else if (char == "σ" || char == "ς") {
        ; ИСПРАВЛЕНО в v4.1 (по отзыву Д.И.: «конечная сигма не пропечатывается»).
        ; Раньше выбор делался по физической клавише через g_LastVK, который
        ; заполняется колбэком OnKeyDown. Колбэк не всегда успевал сработать,
        ; g_LastVK оставался 0 — и ВСЕГДА получалась медиальная σ̌.
        ; Теперь доверяем символу: греческая раскладка Windows сама даёт
        ; W → ς и S → σ. Физическая клавиша — только запасной вариант.
        if (char == "ς")
            SendCombining(0x03C2, 0x030C) ; ς̌ — конечная
        else if (g_LastVK == 0x57)        ; запасной путь: клавиша W
            SendCombining(0x03C2, 0x030C) ; ς̌ — конечная
        else
            SendCombining(0x03C3, 0x030C) ; σ̌ — медиальная
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
        SendCombining(0x03AC, 0x0324) ; ά̤
    else if (char == "Ά")
        SendCombining(0x0386, 0x0324) ; Ά̤
    else if (char == "ό")
        SendCombining(0x03CC, 0x0324) ; ό̤
    else if (char == "Ό")
        SendCombining(0x038C, 0x0324) ; Ό̤

    ; --- ПРОБЕЛ / ДРУГИЕ ---
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
; Типографский апостроф после согласных — ТОЛЬКО ВНЕ MS WORD (v5.1)
; ==============================================================================
; В Word эту работу делают штатные «умные кавычки»: они дают ‘ слева (U+2018)
; и ’ справа (U+2019). Мы их больше не выключаем, поэтому в Word наши правила
; НЕ НУЖНЫ — и, что важнее, могут конфликтовать с работой Word.
;
; А вот в Блокноте, браузере и других программах умных кавычек нет — там
; прямой штрих ' так и останется прямым. Для них правила ниже полезны.
; Поэтому условие: греческая раскладка И активное окно — не Word.
; ==============================================================================
IsNotWord() {
    try {
        return !WinActive("ahk_exe WINWORD.EXE")
    }
    return true
}

#HotIf IsGreekLayout() && IsNotWord()
:?*:τ'::τ’
:?*:Τ'::Τ’
:?*:σ'::σ’
:?*:Σ'::Σ’
:?*:κ'::κ’
:?*:Κ'::Κ’
:?*:μ'::μ’
:?*:Μ'::Μ’
#HotIf

; ==============================================================================
; ДИАГНОСТИКА (Ctrl+Alt+P)
; ==============================================================================
ShowDiagnostics(*) {
    global APP_VERSION, APP_TITLE, APP_VARIANT, g_WordFixed

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
      . "  /  + ζ χ σ ς κ ξ ψ  →  ζ̌ χ̌ σ̌ ς̌ κ̌ ξ̌ ψ̌  (гачек)`n"
      . "  /  + γ               →  γ̆              (бреве)`n"
      . "  /  + α ο ά ό         →  α̤ ο̤ ά̤ ό̤        (две точки снизу)`n`n"
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
A_TrayMenu.Add("Проверить настройки MS Word", (*) => FixWordAutoCorrect(false))
A_TrayMenu.Add("Восстановить апостроф ‘κ’ в Word", (*) => RestoreWordSettings(false))
A_TrayMenu.Add()
A_TrayMenu.Add("Выход", (*) => ExitApp())

; ==============================================================================
; УВЕДОМЛЕНИЕ О ЗАПУСКЕ — чтобы всегда было видно номер работающей версии
; ==============================================================================
TrayTip(
    "Версия " APP_VERSION " запущена.`n"
  . APP_VARIANT "`n"
  . "Не забудьте включить греческую раскладку.",
    APP_TITLE, 0x1
)
SetTimer(() => TrayTip(), -6000)
