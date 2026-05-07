#!/bin/bash

set -e

INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME="android-tv-tools"
CONFIG_DIR="$HOME/.android-tv-tools"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}==========================================${NC}"
echo -e "${CYAN}  TV Tools for Linux - Installer${NC}"
echo -e "${CYAN}  Author: @eli6${NC}"
echo -e "${CYAN}  GitHub: https://github.com/EliseyRotar${NC}"
echo -e "${CYAN}==========================================${NC}"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}This installer requires sudo privileges.${NC}"
    echo "Rerunning with sudo..."
    exec sudo bash "$0" "$@"
fi

echo -e "${CYAN}[1/5] Detecting Linux distribution...${NC}"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    echo -e "  ${GREEN}✓${NC} Detected: $PRETTY_NAME"
else
    DISTRO="unknown"
    echo -e "  ${YELLOW}!${NC} Could not detect distribution"
fi

echo ""
echo -e "${CYAN}[2/5] Checking Python version...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "  ${RED}✗${NC} Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "  ${RED}✗${NC} Python 3.8+ is required (found Python $PYTHON_VERSION)"
    exit 1
fi

echo -e "  ${GREEN}✓${NC} Python $PYTHON_VERSION found"

echo ""
echo -e "${CYAN}[3/5] Checking system dependencies...${NC}"

if ! command -v adb &> /dev/null; then
    echo -e "  ${YELLOW}!${NC} ADB not found. Installing..."
    
    case "$DISTRO" in
        arch|manjaro|endeavouros|garuda)
            pacman -S --noconfirm android-tools
            ;;
        ubuntu|debian|mint|pop|elementary|kali)
            apt update && apt install -y adb
            ;;
        fedora|rhel|centos|almalinux|rocky)
            dnf install -y android-tools
            ;;
        opensuse|suse)
            zypper install -y android-tools
            ;;
        *)
            echo -e "  ${RED}✗${NC} Please install 'adb' manually for your distribution"
            exit 1
            ;;
    esac
    echo -e "  ${GREEN}✓${NC} ADB installed"
else
    echo -e "  ${GREEN}✓${NC} ADB found"
fi

echo ""
echo -e "${CYAN}[4/5] Installing Python dependencies...${NC}"

if [ -f "requirements.txt" ]; then
    if command -v pip3 &> /dev/null; then
        pip3 install -r requirements.txt --quiet
        echo -e "  ${GREEN}✓${NC} Python dependencies installed"
    else
        echo -e "  ${YELLOW}!${NC} pip3 not found, skipping Python dependencies"
        echo -e "  ${YELLOW}!${NC} You may need to install: pytest, pytest-cov, requests"
    fi
else
    echo -e "  ${YELLOW}!${NC} requirements.txt not found, skipping"
fi

echo ""
echo -e "${CYAN}[5/5] Installing TV Tools for Linux...${NC}"

TEMP_DIR=$(mktemp -d)
cp -r android-tv-tools.py core/ utils/ models/ data/ "$TEMP_DIR/"

cat > "$INSTALL_DIR/$SCRIPT_NAME" << 'WRAPPER'
#!/bin/bash
INSTALL_PATH="/opt/android-tv-tools"
export PYTHONPATH="$INSTALL_PATH:$PYTHONPATH"
exec python3 "$INSTALL_PATH/android-tv-tools.py" "$@"
WRAPPER

chmod +x "$INSTALL_DIR/$SCRIPT_NAME"

mkdir -p /opt/android-tv-tools
cp -r "$TEMP_DIR"/* /opt/android-tv-tools/
rm -rf "$TEMP_DIR"

echo -e "  ${GREEN}✓${NC} Installed to /opt/android-tv-tools"
echo -e "  ${GREEN}✓${NC} Wrapper script created at $INSTALL_DIR/$SCRIPT_NAME"

echo ""
echo -e "${CYAN}Creating config directory...${NC}"
sudo -u $SUDO_USER mkdir -p "$CONFIG_DIR"
sudo -u $SUDO_USER touch "$CONFIG_DIR/.keep"
echo -e "  ${GREEN}✓${NC} Config directory created at $CONFIG_DIR"

echo ""
echo -e "${CYAN}Creating desktop entry...${NC}"

DESKTOP_FILE="/usr/share/applications/android-tv-tools.desktop"
cat > "$DESKTOP_FILE" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=TV Tools for Linux
Comment=Manage Android TV devices from Linux
Exec=x-terminal-emulator -e android-tv-tools
Icon=phone
Terminal=true
Categories=Development;Utility;
Keywords=android;adb;tv;tools;
EOF

echo -e "  ${GREEN}✓${NC} Desktop entry created"

echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}  Installation complete!${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo -e "${CYAN}Usage:${NC}"
echo -e "  • Run ${GREEN}android-tv-tools${NC} from anywhere to start"
echo -e "  • Or find it in your application menu"
echo -e "  • Config stored in: ${YELLOW}$CONFIG_DIR${NC}"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo -e "  1. Connect your Android TV device to the same network"
echo -e "  2. Enable USB debugging on your TV"
echo -e "  3. Run ${GREEN}android-tv-tools${NC} and enter your TV's IP address"
echo ""
