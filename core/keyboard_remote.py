from typing import Tuple, Optional, Dict
import sys
import tty
import termios
from core.adb_manager import ADBManager
from utils.logger import Logger
from utils.colors import Colors


class KeyboardRemote:

    KEY_MAPPINGS = {
        'w': {'keycode': 'KEYCODE_DPAD_UP', 'description': 'D-pad Up'},
        'a': {'keycode': 'KEYCODE_DPAD_LEFT', 'description': 'D-pad Left'},
        's': {'keycode': 'KEYCODE_DPAD_DOWN', 'description': 'D-pad Down'},
        'd': {'keycode': 'KEYCODE_DPAD_RIGHT', 'description': 'D-pad Right'},
        '\r': {'keycode': 'KEYCODE_DPAD_CENTER', 'description': 'Select/Enter'},
        '\x7f': {'keycode': 'KEYCODE_BACK', 'description': 'Back'},
        'h': {'keycode': 'KEYCODE_HOME', 'description': 'Home'},
        'm': {'keycode': 'KEYCODE_MENU', 'description': 'Menu'},
        '+': {'keycode': 'KEYCODE_VOLUME_UP', 'description': 'Volume Up'},
        '=': {'keycode': 'KEYCODE_VOLUME_UP', 'description': 'Volume Up'},
        '-': {'keycode': 'KEYCODE_VOLUME_DOWN', 'description': 'Volume Down'},
        '_': {'keycode': 'KEYCODE_VOLUME_DOWN', 'description': 'Volume Down'},
        '0': {'keycode': 'KEYCODE_VOLUME_MUTE', 'description': 'Mute'},
        'i': {'keycode': 'KEYCODE_SETTINGS', 'description': 'Settings'},
        'p': {'keycode': 'KEYCODE_MEDIA_PLAY_PAUSE', 'description': 'Play/Pause'},
        'n': {'keycode': 'KEYCODE_MEDIA_NEXT', 'description': 'Next'},
        'b': {'keycode': 'KEYCODE_MEDIA_PREVIOUS', 'description': 'Previous'},
        'f': {'keycode': 'KEYCODE_MEDIA_FAST_FORWARD', 'description': 'Fast Forward'},
        'r': {'keycode': 'KEYCODE_MEDIA_REWIND', 'description': 'Rewind'},
        ' ': {'keycode': 'KEYCODE_MEDIA_PLAY_PAUSE', 'description': 'Play/Pause'},
        'q': {'keycode': 'EXIT', 'description': 'Exit Remote'},
        '\x1b': {'keycode': 'EXIT', 'description': 'Exit Remote'}
    }

    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None):
        self.adb = adb_manager
        self.logger = logger
        self.running = False

    def send_keycode(self, keycode: str) -> Tuple[bool, str]:
        if keycode == 'EXIT':
            return True, "Exit command"

        result = self.adb.shell_command(f'input keyevent {keycode}')

        if result.success or result.return_code == 0:
            return True, f"Sent {keycode}"
        else:
            return False, f"Failed to send {keycode}"

    def display_key_mappings(self):
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ⌨️  Keyboard Remote Control Mappings           ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}📍 Navigation:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  W / A / S / D    - D-pad Up / Left / Down / Right{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  Enter            - Select/OK{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  Backspace        - Back{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}🏠 System:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  H                - Home{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  M                - Menu{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  I                - Settings{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}🔊 Volume:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  + / =            - Volume Up{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  -                - Volume Down{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  0                - Mute{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}🎵 Media:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  P / Space        - Play/Pause{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  N                - Next{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  B                - Previous{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  F                - Fast Forward{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  R                - Rewind{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}🚪 Exit:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  Q / ESC          - Exit Remote Control{Colors.ENDC}\n")

    def get_key_mappings(self) -> Dict[str, Dict[str, str]]:
        return self.KEY_MAPPINGS.copy()

    def start_remote_emulator(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ⌨️  Keyboard Remote Emulator                   ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        print(f"{Colors.OKGREEN}✅ Device connected{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Starting keyboard remote emulator...{Colors.ENDC}\n")

        self.display_key_mappings()

        print(f"{Colors.OKGREEN}🎮 Remote control active! Press keys to control your device.{Colors.ENDC}\n")

        if self.logger:
            self.logger.log_event('keyboard_remote', 'Started keyboard remote emulator')

        self.running = True

        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)

            try:
                tty.setraw(fd)

                while self.running:
                    char = sys.stdin.read(1)

                    char_lower = char.lower()

                    if char_lower in self.KEY_MAPPINGS:
                        mapping = self.KEY_MAPPINGS[char_lower]
                        keycode = mapping['keycode']
                        description = mapping['description']

                        if keycode == 'EXIT':
                            print(f"\r\n{Colors.OKGREEN}👋 Exiting keyboard remote emulator...{Colors.ENDC}\n")
                            self.running = False
                            break

                        success, message = self.send_keycode(keycode)

                        if success:
                            print(f"\r{Colors.OKGREEN}✓{Colors.ENDC} {description:20} ", end='', flush=True)
                        else:
                            print(f"\r{Colors.FAIL}✗{Colors.ENDC} {description:20} ", end='', flush=True)
                    else:
                        print(f"\r{Colors.WARNING}⚠{Colors.ENDC} Unknown key: {repr(char):20} ", end='', flush=True)

            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                print()

        except KeyboardInterrupt:
            print(f"\n\n{Colors.OKGREEN}👋 Keyboard remote emulator stopped{Colors.ENDC}\n")
            self.running = False

        except Exception as e:
            print(f"\n\n{Colors.FAIL}❌ Error: {e}{Colors.ENDC}\n")
            self.running = False
            return False, str(e)

        if self.logger:
            self.logger.log_event('keyboard_remote', 'Stopped keyboard remote emulator')

        return True, "Remote emulator stopped"

    def stop_remote_emulator(self):
        self.running = False

    def is_running(self) -> bool:
        return self.running

    def test_key_mapping(self, key: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🧪 Testing Key Mapping                         ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        key_lower = key.lower()

        if key_lower not in self.KEY_MAPPINGS:
            print(f"{Colors.FAIL}❌ Unknown key: {key}{Colors.ENDC}")
            return False, f"Unknown key: {key}"

        mapping = self.KEY_MAPPINGS[key_lower]
        keycode = mapping['keycode']
        description = mapping['description']

        print(f"{Colors.OKBLUE}ℹ️  Key: {key}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Keycode: {keycode}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Description: {description}{Colors.ENDC}\n")

        if keycode == 'EXIT':
            print(f"{Colors.WARNING}⚠️  This is an exit command, not sending to device{Colors.ENDC}")
            return True, "Exit command (not sent)"

        success, message = self.send_keycode(keycode)

        if success:
            print(f"{Colors.OKGREEN}✅ Key sent successfully{Colors.ENDC}")
            if self.logger:
                self.logger.log_event('keyboard_remote', f'Tested key: {key} -> {keycode}')
            return True, f"Sent {keycode}"
        else:
            print(f"{Colors.FAIL}❌ Failed to send key{Colors.ENDC}")
            return False, message

    def close(self):
        self.running = False


def create_keyboard_remote(adb_manager: ADBManager, logger: Optional[Logger] = None) -> KeyboardRemote:
    return KeyboardRemote(adb_manager, logger)


def get_default_keyboard_remote(adb_manager: ADBManager) -> KeyboardRemote:
    from utils.logger import get_default_logger
    return KeyboardRemote(adb_manager, get_default_logger())
