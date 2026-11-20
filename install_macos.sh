#!/usr/bin/env bash
# =============================================================================
# Installer for Pontic Greek Keyboard Layout & Fonts v6.0 on macOS
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
echo "  Installer: Pontic Greek Keyboard Layout & Fonts for macOS"
echo "  Target OS: macOS Sonoma / Sequoia / Tahoe (Unified / Dead Key)"
echo "============================================================"
echo ""

# 1. Verify and install keyboard layout
if [ ! -f "$SOURCE" ]; then
  echo -e "${RED}Error:${NC} layout file not found: $SOURCE"
  exit 1
fi

mkdir -p "$KEYBOARD_DIR"
cp "$SOURCE" "$KEYBOARD_DIR/$LAYOUT_DST"
echo -e "${GREEN}✓${NC} Keyboard layout copied to: $KEYBOARD_DIR/$LAYOUT_DST"

if plutil -lint "$KEYBOARD_DIR/$LAYOUT_DST" > /dev/null 2>&1; then
  echo -e "${GREEN}✓${NC} Keyboard layout XML validation passed"
fi

# 2. Install Pontic Sans & Serif v6.0 fonts
mkdir -p "$FONT_DIR"
FONT_COUNT=0
for f in "$SCRIPT_DIR"/font/Pontic*.ttf; do
  if [ -f "$f" ]; then
    cp "$f" "$FONT_DIR/"
    FONT_COUNT=$((FONT_COUNT + 1))
  fi
done
echo -e "${GREEN}✓${NC} Installed $FONT_COUNT v6.0 font files into $FONT_DIR"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}HOW TO ENABLE THE KEYBOARD IN macOS:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Open: System Settings"
echo "   -> Keyboard"
echo "   -> Input Sources"
echo "   -> Edit..."
echo "   -> click [ + ] at bottom left"
echo ""
echo "2. Select category: Others (bottom of list) or Greek"
echo "   Find in list: Pontic Greek"
echo "   Click: Add"
echo ""
echo "3. Switch input sources with Cmd + Space or Globe (Fn)"
echo ""
echo -e "${CYAN}Pontic Sans & Pontic Serif v6.0 fonts are now installed!${NC}"
echo "They are immediately available across Pages, Microsoft Word, TextEdit, and browsers."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
