import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from models.config import Configuration


class ConfigManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.config_dir = Path.home() / ".android-tv-tools"
        self.config_file = self.config_dir / "config.json"
        self.device_history_file = self.config_dir / "device_history.txt"
        self.config: Optional[Configuration] = None
        self._initialized = True

        self._ensure_config_directory()
        self.load_config()

    def _ensure_config_directory(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)

        downloads_dir = Path(self.config_dir / "downloads")
        downloads_dir.mkdir(parents=True, exist_ok=True)

        backups_dir = Path(self.config_dir / "backups")
        backups_dir.mkdir(parents=True, exist_ok=True)

    def _create_default_config(self) -> Configuration:
        return Configuration()

    def load_config(self) -> Configuration:
        if not self.config_file.exists():
            self.config = self._create_default_config()
            self.save_config()
            return self.config

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            self.config = Configuration.from_dict(config_data)
        except (json.JSONDecodeError, ValueError, KeyError):
            self.config = self._create_default_config()
            self.save_config()

        return self.config

    def save_config(self) -> bool:
        if self.config is None:
            return False

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config.to_dict(), f, indent=2)
            return True
        except (IOError, OSError):
            return False

    def validate_config(self) -> bool:
        if self.config is None:
            return False

        if self.config.default_timeout < 1 or self.config.default_timeout > 300:
            return False

        if self.config.network_scan_timeout < 1 or self.config.network_scan_timeout > 60:
            return False

        return True

    def reset_to_defaults(self) -> None:
        self.config = self._create_default_config()
        self.save_config()

    def update_last_ip(self, ip_address: str) -> None:
        if self.config is None:
            return

        self.config.last_ip = ip_address
        self.save_config()

    def get_last_ip(self) -> str:
        if self.config is None:
            return ""
        return self.config.last_ip

    def log_device_connection(self, ip_address: str, device_name: str = "") -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        device_info = device_name if device_name else "Unknown Device"
        log_entry = f"{timestamp} - {ip_address} - {device_info}\n"

        try:
            with open(self.device_history_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except (IOError, OSError):
            pass

    def get_device_history(self, limit: int = 10) -> list[str]:
        if not self.device_history_file.exists():
            return []

        try:
            with open(self.device_history_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            return lines[-limit:] if limit > 0 else lines
        except (IOError, OSError):
            return []

    def get_connection_history(self, limit: int = 10) -> list[dict]:
        if not self.device_history_file.exists():
            return []

        try:
            with open(self.device_history_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            history = []
            for line in lines[-limit:] if limit > 0 else lines:
                try:
                    parts = line.strip().split(' - ')
                    if len(parts) >= 3:
                        history.append({
                            'timestamp': parts[0],
                            'ip': parts[1],
                            'device': parts[2]
                        })
                except (IndexError, ValueError):
                    continue
            
            return history
        except (IOError, OSError):
            return []

    def get_last_connected_device(self) -> Optional[tuple[str, str, str]]:
        history = self.get_device_history(limit=1)
        if not history:
            return None

        try:
            parts = history[0].strip().split(' - ')
            if len(parts) >= 3:
                timestamp = parts[0]
                ip_address = parts[1]
                device_name = parts[2]
                return (timestamp, ip_address, device_name)
        except (IndexError, ValueError):
            pass

        return None

    def get_config(self) -> Configuration:
        if self.config is None:
            self.load_config()
        return self.config

    def update_config(self, **kwargs) -> bool:
        if self.config is None:
            return False

        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        return self.save_config()
