import os
import subprocess
import shutil
from typing import Optional, Dict, List, Tuple


class DistroDetector:
    DISTRO_PACKAGE_MANAGERS = {
        'arch': 'pacman',
        'manjaro': 'pacman',
        'endeavouros': 'pacman',
        'garuda': 'pacman',
        'ubuntu': 'apt',
        'debian': 'apt',
        'linuxmint': 'apt',
        'pop': 'apt',
        'elementary': 'apt',
        'kali': 'apt',
        'fedora': 'dnf',
        'rhel': 'dnf',
        'centos': 'dnf',
        'almalinux': 'dnf',
        'rocky': 'dnf',
        'opensuse': 'zypper',
        'suse': 'zypper',
    }

    PACKAGE_MANAGER_COMMANDS = {
        'pacman': {
            'install': ['sudo', 'pacman', '-S', '--noconfirm'],
            'check': ['pacman', '-Q'],
        },
        'apt': {
            'install': ['sudo', 'apt-get', 'install', '-y'],
            'check': ['dpkg', '-l'],
        },
        'dnf': {
            'install': ['sudo', 'dnf', 'install', '-y'],
            'check': ['rpm', '-q'],
        },
        'yum': {
            'install': ['sudo', 'yum', 'install', '-y'],
            'check': ['rpm', '-q'],
        },
        'zypper': {
            'install': ['sudo', 'zypper', 'install', '-y'],
            'check': ['rpm', '-q'],
        },
    }

    PACKAGE_NAMES = {
        'adb': {
            'pacman': 'android-tools',
            'apt': 'adb',
            'dnf': 'android-tools',
            'yum': 'android-tools',
            'zypper': 'android-tools',
        },
        'scrcpy': {
            'pacman': 'scrcpy',
            'apt': 'scrcpy',
            'dnf': 'scrcpy',
            'yum': 'scrcpy',
            'zypper': 'scrcpy',
        },
        'nmap': {
            'pacman': 'nmap',
            'apt': 'nmap',
            'dnf': 'nmap',
            'yum': 'nmap',
            'zypper': 'nmap',
        },
    }

    def __init__(self):
        self.distro_info = self._detect_distro()
        self.package_manager = self._get_package_manager()

    def _detect_distro(self) -> Dict[str, str]:
        distro_info = {
            'id': 'unknown',
            'name': 'Unknown',
            'version': 'unknown',
            'id_like': '',
        }

        os_release_path = '/etc/os-release'
        if not os.path.exists(os_release_path):
            return distro_info

        try:
            with open(os_release_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        value = value.strip('"').strip("'")

                        if key == 'ID':
                            distro_info['id'] = value.lower()
                        elif key == 'NAME':
                            distro_info['name'] = value
                        elif key == 'VERSION_ID':
                            distro_info['version'] = value
                        elif key == 'ID_LIKE':
                            distro_info['id_like'] = value.lower()
        except Exception:
            pass

        return distro_info

    def _get_package_manager(self) -> Optional[str]:
        distro_id = self.distro_info['id']

        if distro_id in self.DISTRO_PACKAGE_MANAGERS:
            return self.DISTRO_PACKAGE_MANAGERS[distro_id]

        id_like = self.distro_info['id_like']
        if id_like:
            for distro in id_like.split():
                if distro in self.DISTRO_PACKAGE_MANAGERS:
                    return self.DISTRO_PACKAGE_MANAGERS[distro]

        for pm in ['pacman', 'apt', 'dnf', 'yum', 'zypper']:
            if shutil.which(pm):
                return pm

        return None

    def detect_distro(self) -> str:
        return self.distro_info['id']

    def get_distro_name(self) -> str:
        return self.distro_info['name']

    def get_distro_version(self) -> str:
        return self.distro_info['version']

    def get_package_manager(self) -> Optional[str]:
        return self.package_manager

    def is_command_available(self, command: str) -> bool:
        return shutil.which(command) is not None

    def get_install_command(self, package: str) -> Optional[List[str]]:
        if not self.package_manager:
            return None

        if self.package_manager not in self.PACKAGE_MANAGER_COMMANDS:
            return None

        package_name = package
        if package in self.PACKAGE_NAMES:
            if self.package_manager in self.PACKAGE_NAMES[package]:
                package_name = self.PACKAGE_NAMES[package][self.package_manager]

        install_cmd = self.PACKAGE_MANAGER_COMMANDS[self.package_manager]['install'].copy()
        install_cmd.append(package_name)

        return install_cmd

    def install_dependency(self, dependency: str) -> Tuple[bool, str]:
        if not self.package_manager:
            error_msg = (
                f"Cannot install {dependency}: No package manager detected.\n"
                f"Please install {dependency} manually for your distribution."
            )
            return False, error_msg

        install_cmd = self.get_install_command(dependency)
        if not install_cmd:
            error_msg = (
                f"Cannot install {dependency}: Unknown package manager.\n"
                f"Please install {dependency} manually."
            )
            return False, error_msg

        try:
            result = subprocess.run(
                install_cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                return True, f"Successfully installed {dependency}"
            else:
                error_msg = (
                    f"Failed to install {dependency}.\n"
                    f"Error: {result.stderr}\n"
                    f"Please try installing manually: {' '.join(install_cmd)}"
                )
                return False, error_msg
        except subprocess.TimeoutExpired:
            error_msg = (
                f"Installation of {dependency} timed out.\n"
                f"Please try installing manually: {' '.join(install_cmd)}"
            )
            return False, error_msg
        except Exception as e:
            error_msg = (
                f"Failed to install {dependency}: {str(e)}\n"
                f"Please try installing manually: {' '.join(install_cmd)}"
            )
            return False, error_msg

    def get_manual_install_instructions(self, dependency: str) -> str:
        instructions = [
            f"\nManual installation instructions for {dependency}:\n"
        ]

        if dependency in self.PACKAGE_NAMES:
            instructions.append("Package names by distribution:")
            for pm, pkg_name in self.PACKAGE_NAMES[dependency].items():
                if pm == 'pacman':
                    instructions.append(f"  Arch/Manjaro: sudo pacman -S {pkg_name}")
                elif pm == 'apt':
                    instructions.append(f"  Debian/Ubuntu: sudo apt-get install {pkg_name}")
                elif pm == 'dnf':
                    instructions.append(f"  Fedora/RHEL: sudo dnf install {pkg_name}")
                elif pm == 'yum':
                    instructions.append(f"  CentOS (old): sudo yum install {pkg_name}")
                elif pm == 'zypper':
                    instructions.append(f"  openSUSE: sudo zypper install {pkg_name}")
        else:
            instructions.append(f"Please consult your distribution's documentation for installing {dependency}.")

        return '\n'.join(instructions)

    def get_system_info(self) -> Dict[str, str]:
        return {
            'distro_id': self.distro_info['id'],
            'distro_name': self.distro_info['name'],
            'distro_version': self.distro_info['version'],
            'package_manager': self.package_manager or 'unknown',
        }
