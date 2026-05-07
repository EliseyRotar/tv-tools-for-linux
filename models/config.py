from dataclasses import dataclass, asdict
import json


@dataclass
class Configuration:
    last_ip: str = ""
    auto_update_check: bool = True
    default_timeout: int = 30
    download_directory: str = "~/.android-tv-tools/downloads"
    backup_directory: str = "~/.android-tv-tools/backups"
    color_output: bool = True
    confirm_destructive: bool = True
    network_scan_range: str = "192.168.1.0/24"
    network_scan_timeout: int = 5

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Configuration':
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'Configuration':
        data = json.loads(json_str)
        return cls.from_dict(data)
