#!/usr/bin/env bash
# =============================================================================
# Установщик Понтийской Греческой раскладки и шрифтов v6.0 для macOS
# Pontic Greek Keyboard Layout & Fonts v6.0 — macOS Installer
# =============================================================================
set -euo pipefail

LAYOUT_SRC="pnt-macos-v3.keylayout"
LAYOUT_DST="Pontic Greek.keylayout"
KEYBOARD_DIR="$HOME/Library/Keyboard Layouts"
FONT_DIR="$HOME/Library/Fonts"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$SCRIPT_DIR/$LAYOUT_SRC"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo "============================================================"
echo "  Установка: Понтийская раскладка и шрифты v6.0 для macOS"
echo "  Pontic Greek Keyboard Layout & Fonts v6.0"
echo "============================================================"
echo ""

# 1. Проверяем раскладку
if [ ! -f "$SOURCE" ]; then
  echo -e "${RED}Ошибка:${NC} файл не найден: $SOURCE"
  exit 1
fi

mkdir -p "$KEYBOARD_DIR"
cp "$SOURCE" "$KEYBOARD_DIR/$LAYOUT_DST"
echo -e "${GREEN}✓${NC} Раскладка скопирована в: $KEYBOARD_DIR/$LAYOUT_DST"

if plutil -lint "$KEYBOARD_DIR/$LAYOUT_DST" > /dev/null 2>&1; then
  echo -e "${GREEN}✓${NC} XML раскладки прошёл валидацию"
fi

# 2. Устанавливаем шрифты v6.0
mkdir -p "$FONT_DIR"
FONT_COUNT=0
for f in "$SCRIPT_DIR"/font/Pontic*.ttf; do
  if [ -f "$f" ]; then
    cp "$f" "$FONT_DIR/"
    FONT_COUNT=$((FONT_COUNT + 1))
  fi
done
echo -e "${GREEN}✓${NC} Установлено шрифтов v6.0: $FONT_COUNT файлов в $FONT_DIR"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}КАК ВКЛЮЧИТЬ РАСКЛАДКУ В macOS:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Откройте: Системные настройки (System Settings)"
echo "   → Клавиатура (Keyboard)"
echo "   → Источники ввода (Input Sources)"
echo "   → Редактировать... (Edit...)"
echo "   → нажмите [ + ] внизу слева"
echo ""
echo "2. Выберите язык: Другой (Other) или Греческий"
echo "   В списке найдите: Pontic Greek"
echo "   Нажмите: Добавить (Add)"
echo ""
echo "3. Переключение языка: Cmd + Space или глобус (Fn)"
echo ""
echo -e "${CYAN}Шрифты Pontic Sans & Serif v6.0 уже установлены в систему!${NC}"
echo "Они сразу доступны во всех приложениях (Pages, Word, TextEdit, браузер)."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
