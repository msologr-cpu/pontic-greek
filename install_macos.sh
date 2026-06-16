#!/usr/bin/env bash
# =============================================================================
# Установщик Понтийской Греческой раскладки клавиатуры для macOS
# Pontic Greek Keyboard Layout — macOS Installer
# =============================================================================
set -euo pipefail

LAYOUT_FILE="pnt-macos.keylayout"
INSTALL_DIR="$HOME/Library/Keyboard Layouts"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$SCRIPT_DIR/$LAYOUT_FILE"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo "================================================"
echo "  Установка: Понтийская Греческая раскладка"
echo "  Pontic Greek Keyboard Layout for macOS"
echo "================================================"
echo ""

# Проверяем наличие файла
if [ ! -f "$SOURCE" ]; then
  echo -e "${RED}Ошибка:${NC} файл не найден: $SOURCE"
  echo "Запустите скрипт из папки с файлом pnt-macos.keylayout"
  echo ""
  echo "Пример:"
  echo "  cd /путь/к/папке/pontic"
  echo "  bash install_macos.sh"
  exit 1
fi

# Создаём папку если нужно
mkdir -p "$INSTALL_DIR"

# Проверяем, не установлена ли уже раскладка
if [ -f "$INSTALL_DIR/$LAYOUT_FILE" ]; then
  echo -e "${YELLOW}⚠${NC}  Раскладка уже установлена. Обновляем..."
  echo ""
fi

# Копируем файл
cp "$SOURCE" "$INSTALL_DIR/$LAYOUT_FILE"

echo -e "${GREEN}✓${NC} Файл скопирован:"
echo "  $INSTALL_DIR/$LAYOUT_FILE"
echo ""

# Проверяем формат XML
if plutil -lint "$INSTALL_DIR/$LAYOUT_FILE" > /dev/null 2>&1; then
  echo -e "${GREEN}✓${NC} XML-файл прошёл проверку формата"
else
  echo -e "${YELLOW}⚠${NC}  Не удалось проверить XML (это не критично)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}СЛЕДУЮЩИЕ ШАГИ (нужно сделать вручную):${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Откройте Системные настройки (System Settings)"
echo "   → Клавиатура (Keyboard)"
echo "   → Источники ввода (Input Sources)"
echo "   → Редактировать... (Edit...)"
echo "   → нажмите [  +  ] внизу слева"
echo ""
echo "2. В левой колонке выберите: Другой (Other)"
echo "   В списке найдите: Pontic Greek"
echo "   Нажмите: Добавить (Add)"
echo ""
echo "3. Переключение между раскладками:"
echo "   • Fn (глобус) или Cmd+Space — переключить язык"
echo "   • Клик на флаге в меню-баре — выбор вручную"
echo ""
echo -e "${CYAN}ВАЖНО:${NC} Если раскладка не появляется — выйдите из Системных"
echo "настроек и откройте заново, или перезагрузите Mac."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "Подробная инструкция: ${YELLOW}ИНСТРУКЦИЯ.md${NC}"
echo ""

# Открываем папку в Finder для удобства
open "$INSTALL_DIR" 2>/dev/null || true

echo -e "${GREEN}Готово!${NC}"
echo ""
