# Quick Start Guide 🚀

## CLI Mode

Start the interactive menu:

```bash
./android-tv-tools.py
```

## Web UI Mode

### Start Web Server

```bash
./android-tv-tools.py --web
```

Access at: **http://127.0.0.1:5000**

### Custom Port

```bash
./android-tv-tools.py --web --port 8080
```

### Network Access

```bash
./android-tv-tools.py --web --host 0.0.0.0 --port 8080
```

Access from any device: **http://YOUR_IP:8080**

## Installation

### Minimal (CLI only)

Already installed! Just run `./android-tv-tools.py`

### Web UI Dependencies

**Option 1: Arch Linux (recommended)**

```bash
sudo pacman -S python-flask
```

**Option 2: pip**

```bash
pip install Flask
```

**Optional: CORS Support**

```bash
# Arch Linux
sudo pacman -S python-flask-cors

# pip
pip install Flask-CORS
```

## Default Credentials (Web UI)

- **Username:** `admin`
- **Password:** `admin`

Note: Localhost (127.0.0.1) bypasses authentication automatically.

## Features

### CLI Mode (68 Features)

- File Transfer
- App Management
- Backup & Restore
- Custom Settings
- Display Settings
- Screenshot & Recording
- Installation Helper
- Optimizations
- Voice Commands
- Remote Control
- Ad Blocking
- Device Info
- System Monitor (btop-like)

### Web UI (MVP Phase 1, 2 & 3 - Complete)

**Phase 1:**

- Device Connection
- Real-Time Monitoring (CPU, Memory, Storage, Battery)
- Top Processes
- Dark/Light Theme
- Auto-Refresh
- Responsive Design

**Phase 2:**

- App Management (install/uninstall, enable/disable, search)
- File Transfer (upload/download, screenshots, gallery)
- Settings Management (display, system, remote control)
- Remote Control (scrcpy integration with presets)

**Phase 3:**

- Historical Charts (CPU, Memory, Storage, Battery trends)
- Multi-Device Support (manage multiple devices)
- Enhanced Screenshot Gallery (thumbnails, preview, download)
- Advanced Features (backup/restore, batch operations)

## Documentation

- `README.md` - Full documentation
- `WEB_UI_GUIDE.md` - Web UI usage guide
- `INSTALL_ARCH.md` - Arch Linux installation
- `CHANGELOG.md` - Version history

## Troubleshooting

### Web UI won't start

Check if Flask is installed:

```bash
python3 -c "import flask; print('Flask OK')"
```

If not installed:

```bash
sudo pacman -S python-flask
```

### Port already in use

Use a different port:

```bash
./android-tv-tools.py --web --port 8080
```

### Can't connect to device

1. Enable ADB debugging on your Android TV
2. Connect to same network
3. Use device IP address (find in Settings > Network)

## Support

- GitHub: https://github.com/EliseyRotar
- Author: @eli6
