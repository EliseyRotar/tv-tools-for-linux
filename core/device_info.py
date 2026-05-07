from typing import Tuple, Optional, Dict
from core.adb_manager import ADBManager
from utils.logger import Logger
from utils.colors import Colors


class DeviceInfo:

    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None):
        self.adb = adb_manager
        self.logger = logger
        self.device_info: Dict[str, str] = {}

    def get_device_info(self) -> Tuple[bool, Dict[str, str]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📱 Device Information                            ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚════════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, {}

        info = {}

        info['model'] = self._get_property('ro.product.model')
        info['manufacturer'] = self._get_property('ro.product.manufacturer')
        info['brand'] = self._get_property('ro.product.brand')
        info['device'] = self._get_property('ro.product.device')
        info['android_version'] = self._get_property('ro.build.version.release')
        info['sdk_version'] = self._get_property('ro.build.version.sdk')
        info['build_id'] = self._get_property('ro.build.id')
        info['serial'] = self._get_property('ro.serialno')

        display_info = self._get_display_info()
        info.update(display_info)

        storage_info = self._get_storage_info()
        info.update(storage_info)

        memory_info = self._get_memory_info()
        info.update(memory_info)

        info['cpu_arch'] = self._get_property('ro.product.cpu.abi')

        battery_info = self._get_battery_info()
        info.update(battery_info)

        network_info = self._get_network_info()
        info.update(network_info)

        self.device_info = info
        self._display_device_info(info)

        if self.logger:
            self.logger.log_event('device_info', f'Retrieved info for {info.get("model", "Unknown")}')

        return True, info

    def _get_property(self, prop: str) -> str:
        result = self.adb.shell_command(f'getprop {prop}')
        return result.output.strip() if result.success and result.output else 'Unknown'

    def _get_display_info(self) -> Dict[str, str]:
        info = {}

        result = self.adb.shell_command('wm size')
        if result.success and result.output:
            size_line = result.output.strip().split('\n')[-1]
            if 'Physical size:' in size_line:
                resolution = size_line.split(':')[-1].strip()
                info['resolution'] = resolution
            else:
                info['resolution'] = 'Unknown'
        else:
            info['resolution'] = 'Unknown'

        result = self.adb.shell_command('wm density')
        if result.success and result.output:
            density_line = result.output.strip().split('\n')[-1]
            if 'Physical density:' in density_line:
                density = density_line.split(':')[-1].strip()
                info['density'] = f"{density} dpi"
            else:
                info['density'] = 'Unknown'
        else:
            info['density'] = 'Unknown'

        return info

    def _get_storage_info(self) -> Dict[str, str]:
        info = {}

        result = self.adb.shell_command('df /data')
        if result.success and result.output:
            lines = result.output.strip().split('\n')
            if len(lines) >= 2:
                parts = lines[-1].split()
                if len(parts) >= 4:
                    total = self._format_size(parts[1])
                    used = self._format_size(parts[2])
                    available = self._format_size(parts[3])

                    info['storage_total'] = total
                    info['storage_used'] = used
                    info['storage_available'] = available
                else:
                    info['storage_total'] = 'Unknown'
                    info['storage_used'] = 'Unknown'
                    info['storage_available'] = 'Unknown'
            else:
                info['storage_total'] = 'Unknown'
                info['storage_used'] = 'Unknown'
                info['storage_available'] = 'Unknown'
        else:
            info['storage_total'] = 'Unknown'
            info['storage_used'] = 'Unknown'
            info['storage_available'] = 'Unknown'

        return info

    def _get_memory_info(self) -> Dict[str, str]:
        info = {}

        result = self.adb.shell_command('cat /proc/meminfo')
        if result.success and result.output:
            lines = result.output.strip().split('\n')

            for line in lines:
                if 'MemTotal:' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        total_kb = parts[1]
                        info['ram_total'] = self._format_size(total_kb)

                elif 'MemAvailable:' in line or 'MemFree:' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        available_kb = parts[1]
                        info['ram_available'] = self._format_size(available_kb)

        if 'ram_total' not in info:
            info['ram_total'] = 'Unknown'
        if 'ram_available' not in info:
            info['ram_available'] = 'Unknown'

        return info

    def _get_battery_info(self) -> Dict[str, str]:
        info = {}

        result = self.adb.shell_command('dumpsys battery')
        if result.success and result.output:
            lines = result.output.strip().split('\n')

            for line in lines:
                line = line.strip()

                if 'level:' in line:
                    level = line.split(':')[-1].strip()
                    info['battery_level'] = f"{level}%"

                elif 'status:' in line:
                    status = line.split(':')[-1].strip()
                    status_map = {
                        '1': 'Unknown',
                        '2': 'Charging',
                        '3': 'Discharging',
                        '4': 'Not charging',
                        '5': 'Full'
                    }
                    info['battery_status'] = status_map.get(status, status)

        if 'battery_level' not in info:
            info['battery_level'] = 'Unknown'
        if 'battery_status' not in info:
            info['battery_status'] = 'Unknown'

        return info

    def _get_network_info(self) -> Dict[str, str]:
        info = {}

        result = self.adb.shell_command('ip addr show wlan0')
        if result.success and result.output and 'inet ' in result.output:
            lines = result.output.strip().split('\n')
            for line in lines:
                if 'inet ' in line:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        ip_with_mask = parts[1]
                        ip = ip_with_mask.split('/')[0]
                        info['wifi_ip'] = ip
                        break

        if 'wifi_ip' not in info:
            info['wifi_ip'] = 'Not connected'

        result = self.adb.shell_command('dumpsys wifi | grep "mWifiInfo"')
        if result.success and result.output:
            output = result.output.strip()
            if 'SSID:' in output:
                try:
                    ssid_start = output.index('SSID:') + 5
                    ssid_end = output.index(',', ssid_start)
                    ssid = output[ssid_start:ssid_end].strip().strip('"')
                    info['wifi_ssid'] = ssid
                except Exception:
                    info['wifi_ssid'] = 'Unknown'
            else:
                info['wifi_ssid'] = 'Unknown'
        else:
            info['wifi_ssid'] = 'Unknown'

        return info

    def _format_size(self, size_str: str) -> str:
        try:
            size_kb = int(size_str)

            if size_kb < 1024:
                return f"{size_kb} KB"
            elif size_kb < 1024 * 1024:
                return f"{size_kb / 1024:.2f} MB"
            else:
                return f"{size_kb / (1024 * 1024):.2f} GB"
        except Exception:
            return size_str

    def _display_device_info(self, info: Dict[str, str]):
        print(f"{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📊 Device Details                              ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}🏷️  Device Information:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Model: {info.get('model', 'Unknown')}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Manufacturer: {info.get('manufacturer', 'Unknown')}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Brand: {info.get('brand', 'Unknown')}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Device: {info.get('device', 'Unknown')}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Serial: {info.get('serial', 'Unknown')}{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}🤖 Android Version:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Version: {info.get('android_version', 'Unknown')}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   SDK: {info.get('sdk_version', 'Unknown')}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Build ID: {info.get('build_id', 'Unknown')}{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}🖥️  Display:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Resolution: {info.get('resolution', 'Unknown')}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Density: {info.get('density', 'Unknown')}{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}💾 Storage:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Total: {info.get('storage_total', 'Unknown')}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Used: {info.get('storage_used', 'Unknown')}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Available: {info.get('storage_available', 'Unknown')}{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}🧠 Memory (RAM):{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Total: {info.get('ram_total', 'Unknown')}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Available: {info.get('ram_available', 'Unknown')}{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}⚙️  CPU:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Architecture: {info.get('cpu_arch', 'Unknown')}{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}🔋 Battery:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Level: {info.get('battery_level', 'Unknown')}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Status: {info.get('battery_status', 'Unknown')}{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}📡 Network:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   WiFi IP: {info.get('wifi_ip', 'Unknown')}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   WiFi SSID: {info.get('wifi_ssid', 'Unknown')}{Colors.ENDC}\n")

    def get_cached_info(self) -> Dict[str, str]:
        return self.device_info.copy()

    def close(self):
        pass


def create_device_info(adb_manager: ADBManager, logger: Optional[Logger] = None) -> DeviceInfo:
    return DeviceInfo(adb_manager, logger)


def get_default_device_info(adb_manager: ADBManager) -> DeviceInfo:
    from utils.logger import get_default_logger
    return DeviceInfo(adb_manager, get_default_logger())
