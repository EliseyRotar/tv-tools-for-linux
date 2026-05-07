"""
Utility modules for TV Tools for Linux.

This package contains utility functions and helper classes including:
- Download Manager: File download operations with progress tracking
- Network Scanner: Network device discovery
- Distro Detector: Linux distribution detection and package manager identification
- Logger: Logging and event tracking
- Colors: ANSI color code definitions
- Validators: Input validation utilities
- Error Handler: Error handling with actionable solutions
- Web Search: Web search integration for APK sources and error solutions
- UI Components: Progress bars, tables, and other UI elements
"""

from utils.download_manager import DownloadManager
from utils.logger import Logger
from utils.web_search import WebSearch

__all__ = [
    'DownloadManager',
    'Logger',
    'WebSearch',
]
