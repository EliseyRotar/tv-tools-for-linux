from typing import Tuple, Optional, List, Dict
import subprocess
import shutil
from core.adb_manager import ADBManager
from utils.logger import Logger
from utils.colors import Colors


class RemoteControl:

    SCRCPY_PRESETS = {
        'default': {
            'name': 'Default (Compatible)',
            'args': ['--video-codec=h264'],
            'description': 'H264 codec, works with all Android versions'
        },
        'high_quality': {
            'name': 'High Quality',
            'args': ['--video-codec=h264', '-b', '8M', '-m', '1920'],
            'description': 'High bitrate, 1080p max resolution'
        },
        'low_latency': {
            'name': 'Low Latency',
            'args': ['--video-codec=h264', '-b', '2M', '-m', '1280', '--max-fps', '30'],
            'description': 'Lower quality for reduced latency'
        },
        'high_fps': {
            'name': 'High FPS',
            'args': ['--video-codec=h264', '-b', '8M', '--max-fps', '60'],
            'description': 'Smooth 60 FPS experience'
        },
        'power_saving': {
            'name': 'Power Saving',
            'args': ['--video-codec=h264', '-b', '1M', '-m', '960', '--max-fps', '15', '--power-off-on-close'],
            'description': 'Minimal resource usage'
        },
        'fullscreen': {
            'name': 'Fullscreen',
            'args': ['--video-codec=h264', '-f'],
            'description': 'Launch in fullscreen mode'
        },
        'no_control': {
            'name': 'View Only',
            'args': ['--video-codec=h264', '--no-control'],
            'description': 'Display only, no input control'
        },
        'stay_awake': {
            'name': 'Stay Awake',
            'args': ['--video-codec=h264', '--stay-awake'],
            'description': 'Keep device awake while connected'
        }
    }

    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None):
        self.adb = adb_manager
        self.logger = logger

    def check_scrcpy_installed(self) -> Tuple[bool, Optional[str]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🔍 Checking scrcpy Installation                ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        scrcpy_path = shutil.which('scrcpy')

        if scrcpy_path:
            try:
                result = subprocess.run(
                    ['scrcpy', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    print(f"{Colors.OKGREEN}✅ scrcpy is installed{Colors.ENDC}")
                    print(f"{Colors.OKBLUE}ℹ️  Version: {version}{Colors.ENDC}")
                    print(f"{Colors.OKBLUE}ℹ️  Path: {scrcpy_path}{Colors.ENDC}")
                    return True, version
            except (subprocess.TimeoutExpired, Exception) as e:
                print(f"{Colors.WARNING}⚠️  scrcpy found but version check failed: {e}{Colors.ENDC}")
                return True, None

        print(f"{Colors.FAIL}❌ scrcpy is not installed{Colors.ENDC}")
        return False, None

    def get_installation_instructions(self) -> Dict[str, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📦 scrcpy Installation Instructions            ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        instructions = {
            'arch': 'sudo pacman -S scrcpy',
            'ubuntu': 'sudo apt install scrcpy',
            'debian': 'sudo apt install scrcpy',
            'fedora': 'sudo dnf install scrcpy',
            'opensuse': 'sudo zypper install scrcpy',
            'snap': 'sudo snap install scrcpy',
            'flatpak': 'flatpak install flathub com.github.Genymobile.scrcpy',
            'source': 'https://github.com/Genymobile/scrcpy'
        }

        print(f"{Colors.OKBLUE}📋 Installation commands by distribution:{Colors.ENDC}\n")
        for distro, cmd in instructions.items():
            if distro != 'source':
                print(f"{Colors.OKBLUE}  • {distro.capitalize():12} : {cmd}{Colors.ENDC}")

        print(f"\n{Colors.OKBLUE}🔗 Source: {instructions['source']}{Colors.ENDC}")

        return instructions

    def launch_scrcpy(
        self,
        preset: Optional[str] = None,
        custom_args: Optional[List[str]] = None,
        bitrate: Optional[str] = None,
        max_size: Optional[int] = None,
        max_fps: Optional[int] = None,
        fullscreen: bool = False,
        always_on_top: bool = False,
        no_control: bool = False,
        stay_awake: bool = False,
        turn_screen_off: bool = False,
        show_touches: bool = False,
        record_file: Optional[str] = None
    ) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🖥️  Launching scrcpy Remote Control            ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        is_installed, version = self.check_scrcpy_installed()
        if not is_installed:
            print(f"\n{Colors.FAIL}❌ scrcpy is not installed{Colors.ENDC}")
            self.get_installation_instructions()
            return False, "scrcpy is not installed"

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        cmd = ['scrcpy']

        if preset and preset in self.SCRCPY_PRESETS:
            preset_info = self.SCRCPY_PRESETS[preset]
            print(f"{Colors.OKBLUE}ℹ️  Using preset: {preset_info['name']}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}ℹ️  {preset_info['description']}{Colors.ENDC}\n")
            cmd.extend(preset_info['args'])

        if bitrate:
            cmd.extend(['-b', bitrate])
            print(f"{Colors.OKBLUE}ℹ️  Bitrate: {bitrate}{Colors.ENDC}")

        if max_size:
            cmd.extend(['-m', str(max_size)])
            print(f"{Colors.OKBLUE}ℹ️  Max size: {max_size}p{Colors.ENDC}")

        if max_fps:
            cmd.extend(['--max-fps', str(max_fps)])
            print(f"{Colors.OKBLUE}ℹ️  Max FPS: {max_fps}{Colors.ENDC}")

        if fullscreen:
            cmd.append('-f')
            print(f"{Colors.OKBLUE}ℹ️  Fullscreen mode enabled{Colors.ENDC}")

        if always_on_top:
            cmd.append('--always-on-top')
            print(f"{Colors.OKBLUE}ℹ️  Always on top enabled{Colors.ENDC}")

        if no_control:
            cmd.append('--no-control')
            print(f"{Colors.OKBLUE}ℹ️  View-only mode (no control){Colors.ENDC}")

        if stay_awake:
            cmd.append('--stay-awake')
            print(f"{Colors.OKBLUE}ℹ️  Stay awake enabled{Colors.ENDC}")

        if turn_screen_off:
            cmd.append('--turn-screen-off')
            print(f"{Colors.OKBLUE}ℹ️  Turn screen off enabled{Colors.ENDC}")

        if show_touches:
            cmd.append('--show-touches')
            print(f"{Colors.OKBLUE}ℹ️  Show touches enabled{Colors.ENDC}")

        if record_file:
            cmd.extend(['--record', record_file])
            print(f"{Colors.OKBLUE}ℹ️  Recording to: {record_file}{Colors.ENDC}")

        if custom_args:
            cmd.extend(custom_args)
            print(f"{Colors.OKBLUE}ℹ️  Custom args: {' '.join(custom_args)}{Colors.ENDC}")

        print(f"\n{Colors.OKGREEN}🚀 Launching scrcpy...{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Command: {' '.join(cmd)}{Colors.ENDC}\n")

        try:
            subprocess.Popen(cmd)

            print(f"{Colors.OKGREEN}✅ scrcpy launched successfully{Colors.ENDC}")
            print(f"\n{Colors.OKBLUE}💡 Tips:{Colors.ENDC}")
            print(f"{Colors.OKBLUE}  • Ctrl+F: Toggle fullscreen{Colors.ENDC}")
            print(f"{Colors.OKBLUE}  • Ctrl+O: Turn device screen off{Colors.ENDC}")
            print(f"{Colors.OKBLUE}  • Ctrl+S: Take screenshot{Colors.ENDC}")
            print(f"{Colors.OKBLUE}  • Ctrl+V: Paste clipboard{Colors.ENDC}")
            print(f"{Colors.OKBLUE}  • Ctrl+Shift+V: Inject text{Colors.ENDC}")
            print(f"{Colors.OKBLUE}  • Right-click: Back button{Colors.ENDC}")
            print(f"{Colors.OKBLUE}  • Middle-click: Home button{Colors.ENDC}")

            if self.logger:
                self.logger.log_event('remote_control', f'Launched scrcpy with preset: {preset}')

            return True, "scrcpy launched"

        except FileNotFoundError:
            print(f"{Colors.FAIL}❌ scrcpy executable not found{Colors.ENDC}")
            return False, "scrcpy not found"
        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to launch scrcpy: {e}{Colors.ENDC}")
            return False, f"Launch failed: {e}"

    def list_presets(self) -> List[Dict[str, str]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📋 scrcpy Presets                              ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        presets = []
        for key, info in self.SCRCPY_PRESETS.items():
            print(f"{Colors.OKBLUE}• {key:15} - {info['name']}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}  {info['description']}{Colors.ENDC}\n")
            presets.append({
                'key': key,
                'name': info['name'],
                'description': info['description'],
                'args': ' '.join(info['args'])
            })

        return presets

    def get_scrcpy_help(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ❓ scrcpy Help                                  ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        is_installed, _ = self.check_scrcpy_installed()
        if not is_installed:
            return False, "scrcpy is not installed"

        try:
            result = subprocess.run(
                ['scrcpy', '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                print(result.stdout)
                return True, result.stdout
            else:
                print(f"{Colors.FAIL}❌ Failed to get help{Colors.ENDC}")
                return False, "Failed to get help"

        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
            return False, str(e)

    def close(self):
        pass


def create_remote_control(adb_manager: ADBManager, logger: Optional[Logger] = None) -> RemoteControl:
    return RemoteControl(adb_manager, logger)


def get_default_remote_control(adb_manager: ADBManager) -> RemoteControl:
    from utils.logger import get_default_logger
    return RemoteControl(adb_manager, get_default_logger())
