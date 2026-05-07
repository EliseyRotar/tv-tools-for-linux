from typing import Tuple, Optional, Dict
import time
from core.adb_manager import ADBManager
from utils.logger import Logger
from utils.colors import Colors


class PowerManagement:

    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None):
        self.adb = adb_manager
        self.logger = logger

    def wake_device(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ☀️  Waking Device                              ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        result = self.adb.shell_command('input keyevent KEYCODE_WAKEUP')

        if result.success or result.return_code == 0:
            print(f"{Colors.OKGREEN}✅ Device wake command sent{Colors.ENDC}")

            time.sleep(0.5)

            screen_state = self._get_screen_state()
            if screen_state == 'ON':
                print(f"{Colors.OKGREEN}✅ Screen is now ON{Colors.ENDC}")

            if self.logger:
                self.logger.log_event('power_management', 'Wake device')

            return True, "Device wake command sent"
        else:
            print(f"{Colors.FAIL}❌ Failed to wake device{Colors.ENDC}")
            return False, f"Failed to wake: {result.error}"

    def sleep_device(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🌙 Putting Device to Sleep                     ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        result = self.adb.shell_command('input keyevent KEYCODE_SLEEP')

        if result.success or result.return_code == 0:
            print(f"{Colors.OKGREEN}✅ Device sleep command sent{Colors.ENDC}")

            time.sleep(0.5)

            screen_state = self._get_screen_state()
            if screen_state == 'OFF':
                print(f"{Colors.OKGREEN}✅ Screen is now OFF{Colors.ENDC}")

            if self.logger:
                self.logger.log_event('power_management', 'Sleep device')

            return True, "Device sleep command sent"
        else:
            print(f"{Colors.FAIL}❌ Failed to sleep device{Colors.ENDC}")
            return False, f"Failed to sleep: {result.error}"

    def _get_screen_state(self) -> Optional[str]:
        result = self.adb.shell_command('dumpsys power | grep "Display Power"')

        if result.success and result.output:
            output = result.output.strip().upper()
            if 'STATE=ON' in output:
                return 'ON'
            elif 'STATE=OFF' in output:
                return 'OFF'

        return None

    def detect_standby(self) -> Tuple[bool, Optional[str]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🔍 Detecting Standby State                     ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, None

        screen_state = self._get_screen_state()

        if screen_state:
            if screen_state == 'ON':
                print(f"{Colors.OKGREEN}✅ Device is AWAKE (screen ON){Colors.ENDC}")
            else:
                print(f"{Colors.OKBLUE}ℹ️  Device is in STANDBY (screen OFF){Colors.ENDC}")

            return True, screen_state
        else:
            print(f"{Colors.WARNING}⚠️  Could not determine standby state{Colors.ENDC}")
            return False, None

    def reboot_device(self, confirm: bool = True) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🔄 Rebooting Device                            ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        if confirm:
            print(f"{Colors.WARNING}⚠️  This will reboot the device{Colors.ENDC}")
            print(f"{Colors.WARNING}⚠️  All running apps will be closed{Colors.ENDC}")
            response = input(f"\n{Colors.OKBLUE}Continue? (yes/no): {Colors.ENDC}").strip().lower()

            if response not in ['yes', 'y']:
                print(f"{Colors.WARNING}⚠️  Reboot cancelled{Colors.ENDC}")
                return False, "Reboot cancelled by user"

        print(f"\n{Colors.OKBLUE}ℹ️  Sending reboot command...{Colors.ENDC}")

        result = self.adb.shell_command('reboot')

        if result.success or result.return_code == 0:
            print(f"{Colors.OKGREEN}✅ Reboot command sent{Colors.ENDC}")
            print(f"{Colors.OKBLUE}ℹ️  Device will reboot in a few seconds{Colors.ENDC}")

            if self.logger:
                self.logger.log_event('power_management', 'Reboot device')

            return True, "Reboot command sent"
        else:
            print(f"{Colors.FAIL}❌ Failed to reboot device{Colors.ENDC}")
            return False, f"Failed to reboot: {result.error}"

    def reboot_recovery(self, confirm: bool = True) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🛠️  Rebooting to Recovery Mode                 ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        if confirm:
            print(f"{Colors.WARNING}⚠️  This will reboot the device to recovery mode{Colors.ENDC}")
            print(f"{Colors.WARNING}⚠️  You may need physical access to navigate recovery{Colors.ENDC}")
            response = input(f"\n{Colors.OKBLUE}Continue? (yes/no): {Colors.ENDC}").strip().lower()

            if response not in ['yes', 'y']:
                print(f"{Colors.WARNING}⚠️  Reboot cancelled{Colors.ENDC}")
                return False, "Reboot cancelled by user"

        print(f"\n{Colors.OKBLUE}ℹ️  Sending reboot recovery command...{Colors.ENDC}")

        result = self.adb.shell_command('reboot recovery')

        if result.success or result.return_code == 0:
            print(f"{Colors.OKGREEN}✅ Reboot recovery command sent{Colors.ENDC}")
            print(f"{Colors.OKBLUE}ℹ️  Device will reboot to recovery mode{Colors.ENDC}")

            if self.logger:
                self.logger.log_event('power_management', 'Reboot to recovery')

            return True, "Reboot recovery command sent"
        else:
            print(f"{Colors.FAIL}❌ Failed to reboot to recovery{Colors.ENDC}")
            return False, f"Failed to reboot recovery: {result.error}"

    def reboot_bootloader(self, confirm: bool = True) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ⚡ Rebooting to Bootloader Mode                ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        if confirm:
            print(f"{Colors.WARNING}⚠️  This will reboot the device to bootloader mode{Colors.ENDC}")
            print(f"{Colors.WARNING}⚠️  You will need fastboot to interact with the device{Colors.ENDC}")
            response = input(f"\n{Colors.OKBLUE}Continue? (yes/no): {Colors.ENDC}").strip().lower()

            if response not in ['yes', 'y']:
                print(f"{Colors.WARNING}⚠️  Reboot cancelled{Colors.ENDC}")
                return False, "Reboot cancelled by user"

        print(f"\n{Colors.OKBLUE}ℹ️  Sending reboot bootloader command...{Colors.ENDC}")

        result = self.adb.shell_command('reboot bootloader')

        if result.success or result.return_code == 0:
            print(f"{Colors.OKGREEN}✅ Reboot bootloader command sent{Colors.ENDC}")
            print(f"{Colors.OKBLUE}ℹ️  Device will reboot to bootloader mode{Colors.ENDC}")

            if self.logger:
                self.logger.log_event('power_management', 'Reboot to bootloader')

            return True, "Reboot bootloader command sent"
        else:
            print(f"{Colors.FAIL}❌ Failed to reboot to bootloader{Colors.ENDC}")
            return False, f"Failed to reboot bootloader: {result.error}"

    def get_battery_info(self) -> Tuple[bool, Optional[Dict[str, str]]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🔋 Battery Information                         ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, None

        result = self.adb.shell_command('dumpsys battery')

        if result.success and result.output:
            battery_info = {}

            for line in result.output.split('\n'):
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    battery_info[key.strip()] = value.strip()

            if 'level' in battery_info:
                level = battery_info.get('level', 'Unknown')
                status = battery_info.get('status', 'Unknown')
                health = battery_info.get('health', 'Unknown')

                print(f"{Colors.OKBLUE}🔋 Battery Level: {level}%{Colors.ENDC}")
                print(f"{Colors.OKBLUE}⚡ Status: {status}{Colors.ENDC}")
                print(f"{Colors.OKBLUE}💚 Health: {health}{Colors.ENDC}")

                return True, battery_info
            else:
                print(f"{Colors.WARNING}⚠️  Could not parse battery information{Colors.ENDC}")
                return False, None
        else:
            print(f"{Colors.FAIL}❌ Failed to get battery information{Colors.ENDC}")
            return False, None

    def close(self):
        pass


def create_power_management(adb_manager: ADBManager, logger: Optional[Logger] = None) -> PowerManagement:
    return PowerManagement(adb_manager, logger)


def get_default_power_management(adb_manager: ADBManager) -> PowerManagement:
    from utils.logger import get_default_logger
    return PowerManagement(adb_manager, get_default_logger())
