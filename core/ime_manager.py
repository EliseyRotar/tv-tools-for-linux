from typing import Tuple, List, Optional
from core.adb_manager import ADBManager
from utils.logger import Logger
from utils.colors import Colors


class IMEManager:

    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None):
        self.adb = adb_manager
        self.logger = logger

    def list_input_methods(self) -> Tuple[bool, List[str]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ⌨️  Input Methods                              ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, []

        result = self.adb.shell_command('ime list -s')

        if not result.success or not result.output:
            print(f"{Colors.FAIL}❌ Failed to list input methods{Colors.ENDC}")
            return False, []

        imes = [line.strip() for line in result.output.strip().split('\n') if line.strip()]

        print(f"{Colors.OKGREEN}✅ Found {len(imes)} input method(s){Colors.ENDC}\n")

        for idx, ime in enumerate(imes, 1):
            print(f"{Colors.OKBLUE}   {idx}. {ime}{Colors.ENDC}")

        print()

        if self.logger:
            self.logger.log_event('list_input_methods', f'Listed {len(imes)} IMEs')

        return True, imes

    def get_current_ime(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ⌨️  Current Input Method                       ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        result = self.adb.shell_command('settings get secure default_input_method')

        if not result.success or not result.output:
            print(f"{Colors.FAIL}❌ Failed to get current IME{Colors.ENDC}")
            return False, "Failed to get current IME"

        current_ime = result.output.strip()

        print(f"{Colors.OKBLUE}⌨️  Current IME: {current_ime}{Colors.ENDC}\n")

        if self.logger:
            self.logger.log_event('get_current_ime', f'Current: {current_ime}')

        return True, current_ime

    def enable_ime(self, ime_id: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ✅ Enable Input Method                         ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        if not ime_id:
            print(f"{Colors.FAIL}❌ IME ID is required{Colors.ENDC}")
            return False, "IME ID is required"

        print(f"{Colors.OKBLUE}⌨️  Enabling: {ime_id}{Colors.ENDC}\n")

        result = self.adb.shell_command(f'ime enable {ime_id}')

        if result.success:
            print(f"{Colors.OKGREEN}✅ IME enabled{Colors.ENDC}\n")

            if self.logger:
                self.logger.log_event('enable_ime', f'Enabled {ime_id}')

            return True, f"IME {ime_id} enabled"
        else:
            print(f"{Colors.FAIL}❌ Failed to enable IME{Colors.ENDC}")
            return False, "Failed to enable IME"

    def disable_ime(self, ime_id: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ❌ Disable Input Method                        ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        if not ime_id:
            print(f"{Colors.FAIL}❌ IME ID is required{Colors.ENDC}")
            return False, "IME ID is required"

        print(f"{Colors.OKBLUE}⌨️  Disabling: {ime_id}{Colors.ENDC}\n")

        result = self.adb.shell_command(f'ime disable {ime_id}')

        if result.success:
            print(f"{Colors.OKGREEN}✅ IME disabled{Colors.ENDC}\n")

            if self.logger:
                self.logger.log_event('disable_ime', f'Disabled {ime_id}')

            return True, f"IME {ime_id} disabled"
        else:
            print(f"{Colors.FAIL}❌ Failed to disable IME{Colors.ENDC}")
            return False, "Failed to disable IME"

    def set_default_ime(self, ime_id: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🔧 Set Default Input Method                    ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        if not ime_id:
            print(f"{Colors.FAIL}❌ IME ID is required{Colors.ENDC}")
            return False, "IME ID is required"

        print(f"{Colors.OKBLUE}⌨️  Setting default: {ime_id}{Colors.ENDC}\n")

        result = self.adb.shell_command(f'ime set {ime_id}')

        if result.success:
            print(f"{Colors.OKGREEN}✅ Default IME set{Colors.ENDC}\n")

            if self.logger:
                self.logger.log_event('set_default_ime', f'Set default to {ime_id}')

            return True, f"Default IME set to {ime_id}"
        else:
            print(f"{Colors.FAIL}❌ Failed to set default IME{Colors.ENDC}")
            return False, "Failed to set default IME"

    def close(self):
        pass


def create_ime_manager(adb_manager: ADBManager, logger: Optional[Logger] = None) -> IMEManager:
    return IMEManager(adb_manager, logger)


def get_default_ime_manager(adb_manager: ADBManager) -> IMEManager:
    from utils.logger import get_default_logger
    return IMEManager(adb_manager, get_default_logger())
