#!/bin/bash

INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME="android-tv-tools"
INSTALL_PATH="/opt/android-tv-tools"
DESKTOP_FILE="/usr/share/applications/android-tv-tools.desktop"
CONFIG_DIR="$HOME/.android-tv-tools"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}==========================================${NC}"
echo -e "${CYAN}  TV Tools for Linux - Uninstaller${NC}"
echo -e "${CYAN}==========================================${NC}"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}This uninstaller requires sudo privileges.${NC}"
    echo "Rerunning with sudo..."
    exec sudo bash "$0" "$@"
fi

echo -e "${CYAN}Removing TV Tools for Linux...${NC}"
echo ""

if [ -f "$INSTALL_DIR/$SCRIPT_NAME" ]; then
    rm "$INSTALL_DIR/$SCRIPT_NAME"
    echo -e "  ${GREEN}✓${NC} Removed wrapper script"
else
    echo -e "  ${YELLOW}!${NC} Wrapper script not found"
fi

if [ -d "$INSTALL_PATH" ]; then
    rm -rf "$INSTALL_PATH"
    echo -e "  ${GREEN}✓${NC} Removed installation directory"
else
    echo -e "  ${YELLOW}!${NC} Installation directory not found"
fi

if [ -f "$DESKTOP_FILE" ]; then
    rm "$DESKTOP_FILE"
    echo -e "  ${GREEN}✓${NC} Removed desktop entry"
else
    echo -e "  ${YELLOW}!${NC} Desktop entry not found"
fi

echo ""
echo -e "${YELLOW}Configuration directory:${NC} $CONFIG_DIR"
read -p "Remove configuration directory? This will delete all saved settings and history. [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "$CONFIG_DIR" ]; then
        rm -rf "$CONFIG_DIR"
        echo -e "  ${GREEN}✓${NC} Removed configuration directory"
    else
        echo -e "  ${YELLOW}!${NC} Configuration directory not found"
    fi
else
    echo -e "  ${CYAN}→${NC} Configuration kept at $CONFIG_DIR"
fi

echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}  Uninstallation complete!${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo -e "${CYAN}Thank you for using TV Tools for Linux!${NC}"
echo ""
