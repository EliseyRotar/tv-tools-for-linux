from typing import Tuple, Optional, List
from core.adb_manager import ADBManager
from utils.logger import Logger
from utils.colors import Colors


class ADBShell:

    COMMON_COMMANDS = {
        'pm': {
            'description': 'Package Manager',
            'examples': [
                'pm list packages',
                'pm list packages -3',
                'pm uninstall --user 0 <package>',
                'pm enable <package>',
                'pm disable <package>'
            ]
        },
        'am': {
            'description': 'Activity Manager',
            'examples': [
                'am start -n <package>/<activity>',
                'am force-stop <package>',
                'am broadcast -a <action>'
            ]
        },
        'input': {
            'description': 'Input Events',
            'examples': [
                'input keyevent <keycode>',
                'input text "hello"',
                'input tap <x> <y>',
                'input swipe <x1> <y1> <x2> <y2>'
            ]
        },
        'dumpsys': {
            'description': 'System Services Dump',
            'examples': [
                'dumpsys battery',
                'dumpsys window',
                'dumpsys package <package>',
                'dumpsys meminfo'
            ]
        },
        'settings': {
            'description': 'Settings Management',
            'examples': [
                'settings get global <key>',
                'settings put global <key> <value>',
                'settings list global',
                'settings list system'
            ]
        },
        'getprop': {
            'description': 'Get System Properties',
            'examples': [
                'getprop',
                'getprop ro.build.version.release',
                'getprop ro.product.model'
            ]
        },
        'screencap': {
            'description': 'Take Screenshot',
            'examples': [
                'screencap /sdcard/screen.png'
            ]
        },
        'screenrecord': {
            'description': 'Record Screen',
            'examples': [
                'screenrecord /sdcard/video.mp4',
                'screenrecord --time-limit 30 /sdcard/video.mp4'
            ]
        }
    }

    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None):
        self.adb = adb_manager
        self.logger = logger
        self.command_history: List[str] = []
        self.running = False

    def execute_shell_command(self, command: str) -> Tuple[bool, str]:
        if not command.strip():
            return True, ""

        result = self.adb.shell_command(command)

        if result.success or result.return_code == 0:
            return True, result.output
        else:
            return False, result.error if result.error else result.output

    def display_common_commands(self):
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📚 Common ADB Shell Commands                   ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        for cmd, info in self.COMMON_COMMANDS.items():
            print(f"{Colors.OKBLUE}▸ {cmd:15} - {info['description']}{Colors.ENDC}")
            for example in info['examples']:
                print(f"{Colors.OKBLUE}  └─ {example}{Colors.ENDC}")
            print()

    def get_common_commands(self) -> dict:
        return self.COMMON_COMMANDS.copy()

    def get_command_history(self) -> List[str]:
        return self.command_history.copy()

    def clear_command_history(self):
        self.command_history.clear()

    def start_interactive_shell(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🐚 Interactive ADB Shell                       ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        print(f"{Colors.OKGREEN}✅ Device connected{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Starting interactive shell...{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}💡 Tips:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  • Type 'help' to see common commands{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  • Type 'history' to see command history{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  • Type 'clear' to clear screen{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  • Type 'exit' or 'quit' to exit shell{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  • Press Ctrl+C to exit{Colors.ENDC}\n")

        if self.logger:
            self.logger.log_event('adb_shell', 'Started interactive shell')

        self.running = True

        try:
            while self.running:
                try:
                    command = input(f"{Colors.OKGREEN}shell@android:{Colors.ENDC} ").strip()

                    if not command:
                        continue

                    if command.lower() in ['exit', 'quit']:
                        print(f"\n{Colors.OKGREEN}👋 Exiting ADB shell...{Colors.ENDC}\n")
                        self.running = False
                        break

                    if command.lower() == 'help':
                        self.display_common_commands()
                        continue

                    if command.lower() == 'history':
                        self._display_history()
                        continue

                    if command.lower() == 'clear':
                        self._clear_screen()
                        continue

                    self.command_history.append(command)

                    success, output = self.execute_shell_command(command)

                    if output:
                        print(output)

                    if not success and not output:
                        print(f"{Colors.FAIL}❌ Command failed{Colors.ENDC}")

                except EOFError:
                    print(f"\n\n{Colors.OKGREEN}👋 ADB shell closed{Colors.ENDC}\n")
                    self.running = False
                    break

        except KeyboardInterrupt:
            print(f"\n\n{Colors.OKGREEN}👋 ADB shell interrupted{Colors.ENDC}\n")
            self.running = False

        except Exception as e:
            print(f"\n\n{Colors.FAIL}❌ Error: {e}{Colors.ENDC}\n")
            self.running = False
            return False, str(e)

        if self.logger:
            self.logger.log_event('adb_shell', 'Stopped interactive shell')

        return True, "Interactive shell stopped"

    def _display_history(self):
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📜 Command History                             ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.command_history:
            print(f"{Colors.WARNING}⚠️  No commands in history{Colors.ENDC}\n")
            return

        for i, cmd in enumerate(self.command_history, 1):
            print(f"{Colors.OKBLUE}{i:3}. {cmd}{Colors.ENDC}")

        print()

    def _clear_screen(self):
        import os
        os.system('clear' if os.name != 'nt' else 'cls')

    def stop_interactive_shell(self):
        self.running = False

    def is_running(self) -> bool:
        return self.running

    def run_shell_script(self, script_path: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📜 Running Shell Script                        ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        try:
            with open(script_path, 'r') as f:
                commands = f.readlines()

            print(f"{Colors.OKBLUE}ℹ️  Script: {script_path}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}ℹ️  Commands: {len(commands)}{Colors.ENDC}\n")

            results = []
            failed = 0

            for i, command in enumerate(commands, 1):
                command = command.strip()

                if not command or command.startswith('#'):
                    continue

                print(f"{Colors.OKBLUE}[{i}/{len(commands)}] {command}{Colors.ENDC}")

                success, output = self.execute_shell_command(command)

                if success:
                    print(f"{Colors.OKGREEN}✓{Colors.ENDC}")
                    if output:
                        print(output)
                else:
                    print(f"{Colors.FAIL}✗ Failed{Colors.ENDC}")
                    if output:
                        print(output)
                    failed += 1

                results.append((command, success, output))
                print()

            print(f"{Colors.OKGREEN}✅ Script execution complete{Colors.ENDC}")
            print(f"{Colors.OKBLUE}ℹ️  Success: {len(results) - failed}/{len(results)}{Colors.ENDC}")

            if failed > 0:
                print(f"{Colors.WARNING}⚠️  Failed: {failed}/{len(results)}{Colors.ENDC}")

            if self.logger:
                self.logger.log_event('adb_shell', f'Ran script: {script_path}')

            return failed == 0, f"Script executed: {len(results) - failed}/{len(results)} successful"

        except FileNotFoundError:
            print(f"{Colors.FAIL}❌ Script file not found: {script_path}{Colors.ENDC}")
            return False, f"File not found: {script_path}"

        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
            return False, str(e)

    def close(self):
        self.running = False


def create_adb_shell(adb_manager: ADBManager, logger: Optional[Logger] = None) -> ADBShell:
    return ADBShell(adb_manager, logger)


def get_default_adb_shell(adb_manager: ADBManager) -> ADBShell:
    from utils.logger import get_default_logger
    return ADBShell(adb_manager, get_default_logger())
