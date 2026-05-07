from dataclasses import dataclass
from datetime import datetime


@dataclass
class BackupMetadata:
    package_name: str
    label: str
    version_code: int
    version_name: str
    backup_timestamp: datetime
    has_data: bool
    apk_size: int
    data_size: int
    backup_path: str

    def __str__(self) -> str:
        timestamp_str = self.backup_timestamp.strftime('%Y-%m-%d %H:%M:%S')
        total_size_mb = (self.apk_size + self.data_size) / (1024 * 1024)
        data_status = "✓" if self.has_data else "✗"
        return f"📦 {self.label} v{self.version_name} | {timestamp_str} | {total_size_mb:.2f} MB | Data: {data_status}"

    def to_dict(self) -> dict:
        return {
            'package_name': self.package_name,
            'label': self.label,
            'version_code': self.version_code,
            'version_name': self.version_name,
            'backup_timestamp': self.backup_timestamp.isoformat(),
            'has_data': self.has_data,
            'apk_size': self.apk_size,
            'data_size': self.data_size,
            'backup_path': self.backup_path
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'BackupMetadata':
        return cls(
            package_name=data.get('package_name', ''),
            label=data.get('label', ''),
            version_code=data.get('version_code', 0),
            version_name=data.get('version_name', ''),
            backup_timestamp=datetime.fromisoformat(data.get('backup_timestamp', datetime.now().isoformat())),
            has_data=data.get('has_data', False),
            apk_size=data.get('apk_size', 0),
            data_size=data.get('data_size', 0),
            backup_path=data.get('backup_path', '')
        )

    def get_total_size_mb(self) -> float:
        return (self.apk_size + self.data_size) / (1024 * 1024)

    def get_apk_size_mb(self) -> float:
        return self.apk_size / (1024 * 1024)

    def get_data_size_mb(self) -> float:
        return self.data_size / (1024 * 1024)
