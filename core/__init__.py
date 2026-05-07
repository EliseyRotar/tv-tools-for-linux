"""
Core modules for TV Tools for Linux.

This package contains the main functionality modules including:
- ADB Manager: Device communication and ADB operations
- Config Manager: Configuration and settings management
- UI Manager: User interface and menu system
- Package Manager: Application installation and management
- File Transfer: File operations and clipboard management
- Backup/Restore: Application backup and restore operations
- Settings Manager: Android TV settings configuration
- Install Helper: Application installation assistance
- Optimization: Performance optimization operations
- Remote Control: Device remote control functionality
- Ad Blocking: Advertisement blocking configuration
"""

from core.adb_manager import ADBManager
from core.config_manager import ConfigManager

__all__ = [
    'ADBManager',
    'ConfigManager',
]
