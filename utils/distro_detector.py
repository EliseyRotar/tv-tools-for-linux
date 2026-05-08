import os
import subprocess
import shutil
from typing import Optional, Dict, List, Tuple


class DistroDetector:
    # Maps distro ID (from /etc/os-release) to package manager
    DISTRO_PACKAGE_MANAGERS = {
        # Arch-based
        'arch': 'pacman',
        'manjaro': 'pacman',
        'endeavouros': 'pacman',
        'garuda': 'pacman',
        'artix': 'pacman',
        'cachyos': 'pacman',
        'blackarch': 'pacman',
        'parabola': 'pacman',
        'hyperbola': 'pacman',
        # Debian/Ubuntu-based
        'ubuntu': 'apt',
        'debian': 'apt',
        'linuxmint': 'apt',
        'pop': 'apt',
        'elementary': 'apt',
        'kali': 'apt',
        'parrot': 'apt',
        'mx': 'apt',
        'mxlinux': 'apt',
        'zorin': 'apt',
        'raspbian': 'apt',
        'deepin': 'apt',
        'pureos': 'apt',
        'tails': 'apt',
        'devuan': 'apt',
        'lmde': 'apt',
        'bunsenlabs': 'apt',
        'antix': 'apt',
        'sparky': 'apt',
        # Fedora/RHEL-based
        'fedora': 'dnf',
        'rhel': 'dnf',
        'centos': 'dnf',
        'almalinux': 'dnf',
        'rocky': 'dnf',
        'ol': 'dnf',           # Oracle Linux
        'scientific': 'dnf',
        'nobara': 'dnf',
        'ultramarine': 'dnf',
        'qubes': 'dnf',
        # openSUSE-based
        'opensuse': 'zypper',
        'opensuse-leap': 'zypper',
        'opensuse-tumbleweed': 'zypper',
        'suse': 'zypper',
        'sles': 'zypper',
        # Alpine
        'alpine': 'apk',
        # Void Linux
        'void': 'xbps',
        # Gentoo-based
        'gentoo': 'emerge',
        'funtoo': 'emerge',
        'calculate': 'emerge',
        # NixOS
        'nixos': 'nix',
        # Solus
        'solus': 'eopkg',
        # Clear Linux
        'clear-linux-os': 'swupd',
        # Slackware-based
        'slackware': 'slackpkg',
        # Mageia/OpenMandriva
        'mageia': 'urpmi',
        'openmandriva': 'dnf',
        # PCLinuxOS
        'pclinuxos': 'apt-rpm',
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
            'install': ['sudo', 'zypper', '--non-interactive', 'install'],
            'check': ['rpm', '-q'],
        },
        'apk': {
            'install': ['sudo', 'apk', 'add'],
            'check': ['apk', 'info', '-e'],
        },
        'xbps': {
            'install': ['sudo', 'xbps-install', '-Sy'],
            'check': ['xbps-query', '-S'],
        },
        'emerge': {
            'install': ['sudo', 'emerge', '--ask=n'],
            'check': ['equery', 'list'],
        },
        'nix': {
            'install': ['nix-env', '-iA', 'nixpkgs'],
            'check': ['nix-env', '-q'],
        },
        'eopkg': {
            'install': ['sudo', 'eopkg', 'install', '-y'],
            'check': ['eopkg', 'info'],
        },
        'swupd': {
            'install': ['sudo', 'swupd', 'bundle-add'],
            'check': ['swupd', 'bundle-list'],
        },
        'slackpkg': {
            'install': ['sudo', 'slackpkg', 'install'],
            'check': ['ls', '/var/log/packages/'],
        },
        'urpmi': {
            'install': ['sudo', 'urpmi', '--auto'],
            'check': ['rpm', '-q'],
        },
    }

    # Package names per package manager
    PACKAGE_NAMES = {
        'adb': {
            'pacman': 'android-tools',
            'apt': 'adb',
            'dnf': 'android-tools',
            'yum': 'android-tools',
            'zypper': 'android-tools',
            'apk': 'android-tools',
            'xbps': 'android-tools',
            'emerge': 'dev-util/android-tools',
            'nix': 'nixpkgs.android-tools',
            'eopkg': 'android-tools',
            'swupd': 'android-platform-tools',
            'slackpkg': 'android-tools',
            'urpmi': 'android-tools',
        },
        'scrcpy': {
            'pacman': 'scrcpy',
            'apt': 'scrcpy',
            'dnf': 'scrcpy',          # requires: dnf copr enable zeno/scrcpy first
            'yum': 'scrcpy',
            'zypper': 'scrcpy',
            'apk': 'scrcpy',
            'xbps': 'scrcpy',
            'emerge': 'app-mobilephone/scrcpy',
            'nix': 'nixpkgs.scrcpy',
            'eopkg': 'scrcpy',
            'swupd': 'scrcpy',
            'slackpkg': 'scrcpy',
            'urpmi': 'scrcpy',
        },
        'nmap': {
            'pacman': 'nmap',
            'apt': 'nmap',
            'dnf': 'nmap',
            'yum': 'nmap',
            'zypper': 'nmap',
            'apk': 'nmap',
            'xbps': 'nmap',
            'emerge': 'net-analyzer/nmap',
            'nix': 'nixpkgs.nmap',
            'eopkg': 'nmap',
            'swupd': 'nmap',
            'slackpkg': 'nmap',
            'urpmi': 'nmap',
        },
    }

    # Special pre-install steps needed for some distros/packages
    PRE_INSTALL_STEPS = {
        ('dnf', 'scrcpy'): ['sudo', 'dnf', 'copr', 'enable', '-y', 'zeno/scrcpy'],
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

        # Direct match
        if distro_id in self.DISTRO_PACKAGE_MANAGERS:
            return self.DISTRO_PACKAGE_MANAGERS[distro_id]

        # ID_LIKE fallback (e.g. "ubuntu debian" → apt)
        id_like = self.distro_info['id_like']
        if id_like:
            for distro in id_like.split():
                if distro in self.DISTRO_PACKAGE_MANAGERS:
                    return self.DISTRO_PACKAGE_MANAGERS[distro]

        # Binary detection fallback — works for any distro using a known PM
        for pm in ['pacman', 'apt-get', 'dnf', 'yum', 'zypper', 'apk', 'xbps-install',
                   'emerge', 'nix-env', 'eopkg', 'swupd', 'slackpkg', 'urpmi']:
            if shutil.which(pm):
                # Normalize to our internal key
                return {
                    'apt-get': 'apt',
                    'xbps-install': 'xbps',
                    'nix-env': 'nix',
                }.get(pm, pm)

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

        # nix uses attribute path syntax: nix-env -iA nixpkgs.android-tools
        if self.package_manager == 'nix':
            return ['nix-env', '-iA', package_name]

        install_cmd = self.PACKAGE_MANAGER_COMMANDS[self.package_manager]['install'].copy()
        install_cmd.append(package_name)
        return install_cmd

    def install_dependency(self, dependency: str) -> Tuple[bool, str]:
        if not self.package_manager:
            return False, (
                f"Cannot install {dependency}: no package manager detected.\n"
                f"Please install {dependency} manually for your distribution."
            )

        install_cmd = self.get_install_command(dependency)
        if not install_cmd:
            return False, (
                f"Cannot install {dependency}: unknown package manager '{self.package_manager}'.\n"
                f"Please install {dependency} manually."
            )

        # Run any required pre-install steps (e.g. enabling COPR for scrcpy on Fedora)
        pre_step = self.PRE_INSTALL_STEPS.get((self.package_manager, dependency))
        if pre_step:
            try:
                subprocess.run(pre_step, capture_output=True, text=True, timeout=60)
            except Exception:
                pass  # best-effort, continue with install

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
                return False, (
                    f"Failed to install {dependency}.\n"
                    f"Error: {result.stderr}\n"
                    f"Try manually: {' '.join(install_cmd)}"
                )
        except subprocess.TimeoutExpired:
            return False, f"Installation of {dependency} timed out. Try manually: {' '.join(install_cmd)}"
        except Exception as e:
            return False, f"Failed to install {dependency}: {str(e)}\nTry manually: {' '.join(install_cmd)}"

    def get_manual_install_instructions(self, dependency: str) -> str:
        lines = [f"\nManual installation instructions for {dependency}:\n"]

        if dependency in self.PACKAGE_NAMES:
            pm_labels = {
                'pacman': 'Arch/Manjaro/EndeavourOS',
                'apt':    'Debian/Ubuntu/Mint/Kali/Raspbian',
                'dnf':    'Fedora/RHEL/AlmaLinux/Rocky',
                'yum':    'CentOS (legacy)',
                'zypper': 'openSUSE/SLES',
                'apk':    'Alpine Linux',
                'xbps':   'Void Linux',
                'emerge': 'Gentoo/Funtoo',
                'nix':    'NixOS',
                'eopkg':  'Solus',
                'swupd':  'Clear Linux',
                'slackpkg': 'Slackware',
                'urpmi':  'Mageia',
            }
            for pm, pkg_name in self.PACKAGE_NAMES[dependency].items():
                label = pm_labels.get(pm, pm)
                if pm == 'nix':
                    lines.append(f"  {label:35}: nix-env -iA {pkg_name}")
                elif pm == 'emerge':
                    lines.append(f"  {label:35}: sudo emerge {pkg_name}")
                elif pm == 'apk':
                    lines.append(f"  {label:35}: sudo apk add {pkg_name}")
                elif pm == 'xbps':
                    lines.append(f"  {label:35}: sudo xbps-install -Sy {pkg_name}")
                elif pm == 'eopkg':
                    lines.append(f"  {label:35}: sudo eopkg install {pkg_name}")
                elif pm == 'swupd':
                    lines.append(f"  {label:35}: sudo swupd bundle-add {pkg_name}")
                else:
                    cmd = self.PACKAGE_MANAGER_COMMANDS.get(pm, {}).get('install', [pm, 'install'])
                    lines.append(f"  {label:35}: {' '.join(cmd)} {pkg_name}")

            # Special notes
            if dependency == 'scrcpy':
                lines.append("\n  Note (Fedora): enable COPR first:")
                lines.append("    sudo dnf copr enable zeno/scrcpy")
                lines.append("  Note (all distros): snap install scrcpy  (universal fallback)")
        else:
            lines.append(f"Please consult your distribution's documentation for {dependency}.")

        return '\n'.join(lines)

    def get_system_info(self) -> Dict[str, str]:
        return {
            'distro_id': self.distro_info['id'],
            'distro_name': self.distro_info['name'],
            'distro_version': self.distro_info['version'],
            'package_manager': self.package_manager or 'unknown',
        }
