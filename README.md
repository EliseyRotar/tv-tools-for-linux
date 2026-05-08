# 🚀 TV Tools for Linux v1.0

![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/platform-linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

A comprehensive tool for managing Android TV devices on Linux — available as both a **CLI** and a **Web UI**. Connect, control, and manage your Android TV from the terminal or your browser.

**Author**: [@eli6](https://github.com/EliseyRotar)

---

## ✨ Features

### 📱 Device Management

- Connect/disconnect via ADB (IP or USB)
- Device information display
- Network scanner for device discovery
- Wireless ADB management
- Multi-device support

### 📦 App Management

- Install/uninstall applications
- Enable/disable packages
- Batch operations
- Package search and listing
- Bloatware removal (30+ packages)

### 💾 Backup & Restore

- Full app backup (APK + data)
- Batch backup/restore
- Backup management with metadata tracking

### 📁 File Operations

- Push/pull files
- FTP server integration
- Clipboard text transfer
- Screenshot capture & gallery
- Screen recording

### ⚙️ Settings Control

- GPS location, screen timeout, animation scale
- USB debugging, ADB over network, stay awake
- Unknown sources, display settings (density, font size)
- Automatic updates toggle

### ⬇️ Installation Helper

Auto-download and install popular apps:

- SmartTube (ad-free YouTube)
- Launchers (Projectivy, FLauncher, Google TV)
- IPTV apps (TiviMate, Kodi, TDTChannels)
- App stores (Aurora, Aptoide TV)
- Shizuku, Stremio

### 🎮 Advanced Features

- Remote control via scrcpy
- Keyboard remote emulator
- Power management (wake, sleep, reboot)
- ADB shell access
- Voice commands
- Direct app launching

### 🛡️ Ad Blocking

- Private DNS configuration (AdGuard, ControlD, Cloudflare)
- AdGuard app installation

### 🔧 System Tools

- System diagnostics (logcat, processes, CPU/memory)
- Storage management
- Permission management
- Input method (IME) management
- Accessibility features
- Icon generation for hidden apps
- Auto-update checker

---

## 🌐 Web UI

TV Tools for Linux includes a full-featured **browser-based Web UI** — manage your Android TV from any device on your network without touching the terminal.

### Starting the Web UI

```bash
python android-tv-tools.py --web --port 8080
```

Then open `http://localhost:8080` in your browser. Default credentials: `admin` / `admin`.

### Web UI Pages

#### 📊 Dashboard

- Real-time CPU, memory, and storage monitoring
- Historical performance charts (Chart.js)
- Top processes list
- Device connection panel with network scanner
- Quick action buttons

#### 📦 App Management (`/apps`)

- Browse all installed apps (user + system)
- Search and filter by type
- Uninstall, enable, or disable apps
- Install APK files via drag & drop
- Batch operations

#### 📁 File Transfer (`/files`)

- Upload files to device
- Download files from device
- Browse device filesystem
- Screenshot gallery with download

#### ⚙️ Settings (`/settings`)

- Toggle developer options, USB debugging, stay awake
- Adjust display density and font size
- Configure animation scales
- Private DNS / ad blocking setup
- ADB over network toggle

#### 🔧 Tools (`/tools`)

- Bloatware removal with preset lists
- App launcher
- Power management (reboot, sleep, wake)
- Network scanner
- Storage manager
- System diagnostics
- Wireless ADB setup
- IME (keyboard) manager
- Permission manager
- Optimization tools

#### 📱 Devices (`/devices`)

- Manage multiple connected devices
- Switch active device
- Per-device metrics history
- Device info cards

#### 🔬 Advanced (`/advanced`)

- ADB shell terminal
- Accessibility settings
- Ad blocking / DNS configuration
- Icon generator for hidden apps
- App installer with source search
- Update checker

### Web UI Requirements

```bash
pip install flask werkzeug requests colorama
# Optional
pip install flask-cors
```

---

## 📋 System Requirements

- Any Linux distribution (see full list below)
- Python 3.8+
- ADB (Android Debug Bridge) — auto-installed on supported distros

---

## 🐧 Supported Linux Distributions

ADB and scrcpy are auto-installed by the tool. All major distro families are supported:

| Distro Family       | Distros                                                                                              | Package Manager |
| ------------------- | ---------------------------------------------------------------------------------------------------- | --------------- |
| Arch-based          | Arch, Manjaro, EndeavourOS, Garuda, CachyOS, Artix, Parabola                                         | pacman          |
| Debian/Ubuntu-based | Ubuntu, Debian, Mint, Pop!\_OS, Kali, Parrot, Zorin, Raspbian, Elementary, MX, Deepin, Tails, Devuan | apt             |
| Fedora/RHEL-based   | Fedora, RHEL, CentOS, AlmaLinux, Rocky, Oracle Linux, Nobara, Ultramarine                            | dnf             |
| openSUSE-based      | openSUSE Leap, openSUSE Tumbleweed, SLES                                                             | zypper          |
| Alpine Linux        | Alpine                                                                                               | apk             |
| Void Linux          | Void                                                                                                 | xbps-install    |
| Gentoo-based        | Gentoo, Funtoo, Calculate                                                                            | emerge          |
| NixOS               | NixOS                                                                                                | nix-env         |
| Solus               | Solus                                                                                                | eopkg           |
| Clear Linux         | Clear Linux OS                                                                                       | swupd           |
| Slackware           | Slackware                                                                                            | slackpkg        |
| Mageia              | Mageia                                                                                               | urpmi           |

Any distro not in this list will still work — the tool auto-detects the package manager via `ID_LIKE` in `/etc/os-release` or by scanning for known package manager binaries. If auto-install fails, manual install instructions are shown for every distro.

---

## 🚀 Quick Start

### 1. Install ADB

```bash
# Arch Linux
sudo pacman -S android-tools

# Ubuntu/Debian
sudo apt install adb

# Fedora
sudo dnf install android-tools

# Alpine Linux
sudo apk add android-tools

# Void Linux
sudo xbps-install -Sy android-tools

# Gentoo
sudo emerge dev-util/android-tools

# NixOS
nix-env -iA nixpkgs.android-tools

# Solus
sudo eopkg install android-tools

# openSUSE
sudo zypper install android-tools
```

### 2. Clone Repository

```bash
git clone https://github.com/EliseyRotar/tv-tools-for-linux.git
cd tv-tools-for-linux
```

### 3. Run

```bash
# CLI mode
python android-tv-tools.py

# Web UI mode
python android-tv-tools.py --web --port 8080
```

Or install system-wide:

```bash
chmod +x install.sh
./install.sh
android-tv-tools
```

---

## 📖 Connecting Your Device

1. **Enable ADB on your Android TV**:
   - Settings → Device Preferences → About → click "Build" 7 times
   - Settings → Device Preferences → Developer Options → enable "Network debugging"

2. **Find your device IP**:
   - Settings → Network & Internet → Your network → Advanced → IP address

3. **Connect**:
   ```bash
   python android-tv-tools.py
   # Enter device IP when prompted, or use the Web UI dashboard
   ```

---

## 🔧 Configuration

Config stored at `~/.android-tv-tools/config.json`

Defaults: ADB timeout 30s, port 5555, auto-save device history, color output enabled.

---

## 🐛 Troubleshooting

**Cannot connect**: Verify IP, ensure network debugging is enabled, check port 5555 is open, try `adb kill-server`.

**Permission denied**: Add user to `adbusers` group — `sudo usermod -aG adbusers $USER`, then reconnect.

**APK install fails**: Enable "Unknown sources", check storage space, verify APK architecture compatibility.

**Web UI 500 errors**: Ensure device is connected before using device-specific endpoints.

---

## 🤝 Contributing

PRs welcome. Clone, make changes, open a pull request.

---

## 📝 License

MIT License — see LICENSE file for details.

---

**Made with ❤️ by [@eli6](https://github.com/EliseyRotar)**
