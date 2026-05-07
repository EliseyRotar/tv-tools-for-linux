"""
Data models for TV Tools for Linux.

This package contains data model classes including:
- Device: Device connection state and information
- Package: Package information and metadata
- Backup: Backup metadata and archive information
- Config: Configuration settings and preferences
"""

from models.config import Configuration

__all__ = [
    'Configuration',
]
