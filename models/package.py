from dataclasses import dataclass


@dataclass
class PackageInfo:
    package_name: str
    label: str = ""
    version_code: int = 0
    version_name: str = ""
    is_system: bool = False
    is_enabled: bool = True
    install_location: str = ""
    apk_path: str = ""

    def __str__(self) -> str:
        display_name = self.label if self.label else self.package_name
        status = "✓" if self.is_enabled else "✗"
        type_indicator = "📦" if not self.is_system else "⚙️"
        return f"{type_indicator} {status} {display_name} ({self.package_name}) v{self.version_name}"

    def to_dict(self) -> dict:
        return {
            'package_name': self.package_name,
            'label': self.label,
            'version_code': self.version_code,
            'version_name': self.version_name,
            'is_system': self.is_system,
            'is_enabled': self.is_enabled,
            'install_location': self.install_location,
            'apk_path': self.apk_path
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PackageInfo':
        return cls(
            package_name=data.get('package_name', ''),
            label=data.get('label', ''),
            version_code=data.get('version_code', 0),
            version_name=data.get('version_name', ''),
            is_system=data.get('is_system', False),
            is_enabled=data.get('is_enabled', True),
            install_location=data.get('install_location', ''),
            apk_path=data.get('apk_path', '')
        )
