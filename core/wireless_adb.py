from typing import Tuple, Optional
from core.adb_manager import ADBManager
from utils.logger import Logger
from utils.colors import Colors


class WirelessADB:

    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None):
        self.adb = adb_manager
        self.logger = logger
        self.default_port = 5555

    def enable_wireless_adb(self, port: int = 5555) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📡 Enable Wireless ADB                         ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        if not self._validate_port(port):
            print(f"{Colors.FAIL}❌ Invalid port: {port}{Colors.ENDC}")
            return False, f"Invalid port: {port}"

        print(f"{Colors.OKBLUE}🔧 Enabling wireless ADB on port {port}...{Colors.ENDC}\n")

        result = self.adb.shell_command(f'setprop service.adb.tcp.port {port}')
        if not result.success:
            print(f"{Colors.FAIL}❌ Failed to set ADB port{Colors.ENDC}")
            return False, "Failed to set ADB port"

        result = self.adb.shell_command('stop adbd')
        if not result.success:
            print(f"{Colors.FAIL}❌ Failed to stop ADB daemon{Colors.ENDC}")
            return False, "Failed to stop ADB daemon"

        result = self.adb.shell_command('start adbd')
        if not result.success:
            print(f"{Colors.FAIL}❌ Failed to start ADB daemon{Colors.ENDC}")
            return False, "Failed to start ADB daemon"

        ip_address = self._get_device_ip()

        print(f"{Colors.OKGREEN}✅ Wireless ADB enabled{Colors.ENDC}\n")
        print(f"{Colors.OKBLUE}📱 Device IP: {ip_address}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}🔌 Port: {port}{Colors.ENDC}\n")
        print(f"{Colors.WARNING}💡 To connect wirelessly:{Colors.ENDC}")
        print(f"{Colors.WARNING}   adb connect {ip_address}:{port}{Colors.ENDC}\n")

        if self.logger:
            self.logger.log_event('enable_wireless_adb', f'Enabled on port {port}')

        return True, f"Wireless ADB enabled on {ip_address}:{port}"

    def disable_wireless_adb(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🔌 Disable Wireless ADB                        ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        print(f"{Colors.OKBLUE}🔧 Disabling wireless ADB...{Colors.ENDC}\n")

        result = self.adb.shell_command('setprop service.adb.tcp.port -1')
        if not result.success:
            print(f"{Colors.FAIL}❌ Failed to disable ADB port{Colors.ENDC}")
            return False, "Failed to disable ADB port"

        result = self.adb.shell_command('stop adbd')
        if not result.success:
            print(f"{Colors.FAIL}❌ Failed to stop ADB daemon{Colors.ENDC}")
            return False, "Failed to stop ADB daemon"

        result = self.adb.shell_command('start adbd')
        if not result.success:
            print(f"{Colors.FAIL}❌ Failed to start ADB daemon{Colors.ENDC}")
            return False, "Failed to start ADB daemon"

        print(f"{Colors.OKGREEN}✅ Wireless ADB disabled{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   ADB is now USB-only{Colors.ENDC}\n")

        if self.logger:
            self.logger.log_event('disable_wireless_adb', 'Disabled wireless ADB')

        return True, "Wireless ADB disabled"

    def get_adb_mode(self) -> Tuple[bool, str, Optional[int]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📊 ADB Mode Status                             ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected", None

        result = self.adb.shell_command('getprop service.adb.tcp.port')

        if not result.success:
            print(f"{Colors.FAIL}❌ Failed to get ADB mode{Colors.ENDC}")
            return False, "Failed to get ADB mode", None

        port_str = result.output.strip() if result.output else ''

        if port_str == '-1' or port_str == '':
            mode = 'USB'
            port = None
            print(f"{Colors.OKBLUE}🔌 Mode: {mode}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}   ADB is connected via USB only{Colors.ENDC}\n")
        else:
            try:
                port = int(port_str)
                mode = 'Wireless'
                ip_address = self._get_device_ip()
                print(f"{Colors.OKBLUE}📡 Mode: {mode}{Colors.ENDC}")
                print(f"{Colors.OKBLUE}   Port: {port}{Colors.ENDC}")
                print(f"{Colors.OKBLUE}   IP: {ip_address}{Colors.ENDC}\n")
            except ValueError:
                mode = 'Unknown'
                port = None
                print(f"{Colors.WARNING}⚠️  Mode: {mode}{Colors.ENDC}\n")

        if self.logger:
            self.logger.log_event('get_adb_mode', f'Mode: {mode}, Port: {port}')

        return True, mode, port

    def change_adb_port(self, new_port: int) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🔧 Change ADB Port                             ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        if not self._validate_port(new_port):
            print(f"{Colors.FAIL}❌ Invalid port: {new_port}{Colors.ENDC}")
            return False, f"Invalid port: {new_port}"

        success, current_mode, current_port = self.get_adb_mode()

        if not success:
            return False, "Failed to get current ADB mode"

        if current_mode == 'USB':
            print(f"{Colors.WARNING}⚠️  Wireless ADB is not enabled{Colors.ENDC}")
            print(f"{Colors.OKBLUE}   Enabling wireless ADB on port {new_port}...{Colors.ENDC}\n")
            return self.enable_wireless_adb(new_port)

        print(f"{Colors.OKBLUE}🔄 Changing port from {current_port} to {new_port}...{Colors.ENDC}\n")

        return self.enable_wireless_adb(new_port)

    def _get_device_ip(self) -> str:
        result = self.adb.shell_command('ip addr show wlan0')
        if result.success and result.output and 'inet ' in result.output:
            lines = result.output.strip().split('\n')
            for line in lines:
                if 'inet ' in line:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        ip_with_mask = parts[1]
                        ip = ip_with_mask.split('/')[0]
                        return ip
        return 'Unknown'

    def _validate_port(self, port: int) -> bool:
        return 1024 <= port <= 65535

    def close(self):
        pass


def create_wireless_adb(adb_manager: ADBManager, logger: Optional[Logger] = None) -> WirelessADB:
    return WirelessADB(adb_manager, logger)


def get_default_wireless_adb(adb_manager: ADBManager) -> WirelessADB:
    from utils.logger import get_default_logger
    return WirelessADB(adb_manager, get_default_logger())
