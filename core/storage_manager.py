from typing import Tuple, Dict, Optional
from core.adb_manager import ADBManager
from utils.logger import Logger
from utils.colors import Colors


class StorageManager:

    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None):
        self.adb = adb_manager
        self.logger = logger

    def get_storage_info(self) -> Tuple[bool, Dict[str, str]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           💾 Storage Information                         ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, {}

        info = {}

        result = self.adb.shell_command('df /data')
        if result.success and result.output:
            lines = result.output.strip().split('\n')
            if len(lines) >= 2:
                parts = lines[-1].split()
                if len(parts) >= 4:
                    info['total'] = self._format_size(parts[1])
                    info['used'] = self._format_size(parts[2])
                    info['available'] = self._format_size(parts[3])

                    try:
                        total_kb = int(parts[1])
                        used_kb = int(parts[2])
                        percentage = (used_kb / total_kb * 100) if total_kb > 0 else 0
                        info['percentage'] = f"{percentage:.1f}%"
                    except Exception:
                        info['percentage'] = 'Unknown'

        if not info:
            print(f"{Colors.FAIL}❌ Failed to get storage info{Colors.ENDC}")
            return False, {}

        print(f"{Colors.OKBLUE}📊 Storage Details:{Colors.ENDC}\n")
        print(f"{Colors.OKBLUE}   Total:     {info.get('total', 'Unknown')}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Used:      {info.get('used', 'Unknown')} ({info.get('percentage', 'Unknown')}){Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Available: {info.get('available', 'Unknown')}{Colors.ENDC}\n")

        if self.logger:
            self.logger.log_event('get_storage_info', f"Total: {info.get('total')}, Available: {info.get('available')}")

        return True, info

    def clear_all_cache(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🧹 Clear All Cache                             ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        print(f"{Colors.WARNING}⚠️  This will clear cache for all apps{Colors.ENDC}")
        print(f"{Colors.WARNING}   This is safe and will not delete app data{Colors.ENDC}\n")

        success, before_info = self.get_storage_info()
        if not success:
            return False, "Failed to get storage info"

        print(f"{Colors.OKBLUE}🧹 Clearing cache...{Colors.ENDC}\n")

        result = self.adb.shell_command('pm list packages')
        if not result.success or not result.output:
            print(f"{Colors.FAIL}❌ Failed to list packages{Colors.ENDC}")
            return False, "Failed to list packages"

        packages = [line.replace('package:', '').strip()
                    for line in result.output.strip().split('\n')
                    if line.startswith('package:')]

        cleared = 0
        failed = 0

        for idx, package in enumerate(packages, 1):
            print(f"{Colors.OKBLUE}   [{idx}/{len(packages)}] {package}{Colors.ENDC}", end='\r')

            result = self.adb.shell_command(f'pm clear --cache-only {package}')
            if result.success:
                cleared += 1
            else:
                failed += 1

        print(f"\n\n{Colors.OKGREEN}✅ Cache clearing complete{Colors.ENDC}\n")
        print(f"{Colors.OKGREEN}   Cleared: {cleared} packages{Colors.ENDC}")
        if failed > 0:
            print(f"{Colors.WARNING}   Failed: {failed} packages{Colors.ENDC}")

        success, after_info = self.get_storage_info()

        if success and before_info and after_info:
            try:
                before_avail = self._parse_size(before_info.get('available', '0'))
                after_avail = self._parse_size(after_info.get('available', '0'))
                freed = after_avail - before_avail
                if freed > 0:
                    print(f"\n{Colors.OKGREEN}💾 Space freed: {self._format_size(str(int(freed)))}{Colors.ENDC}\n")
            except Exception:
                pass

        if self.logger:
            self.logger.log_event('clear_all_cache', f'Cleared {cleared} packages, {failed} failed')

        return True, f"Cleared cache for {cleared} packages"

    def clear_app_data(self, package_name: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🗑️  Clear App Data                             ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        if not package_name:
            print(f"{Colors.FAIL}❌ Package name is required{Colors.ENDC}")
            return False, "Package name is required"

        print(f"{Colors.OKBLUE}📦 Package: {package_name}{Colors.ENDC}\n")

        result = self.adb.shell_command(f'pm list packages | grep {package_name}')
        if not result.success or package_name not in result.output:
            print(f"{Colors.FAIL}❌ Package not found{Colors.ENDC}")
            return False, f"Package {package_name} not found"

        print(f"{Colors.FAIL}⚠️  WARNING: This will delete ALL app data!{Colors.ENDC}")
        print(f"{Colors.WARNING}   - All settings will be lost{Colors.ENDC}")
        print(f"{Colors.WARNING}   - All user data will be deleted{Colors.ENDC}")
        print(f"{Colors.WARNING}   - The app will be reset to initial state{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}🗑️  Clearing app data...{Colors.ENDC}")

        result = self.adb.shell_command(f'pm clear {package_name}')

        if result.success and 'Success' in result.output:
            print(f"{Colors.OKGREEN}✅ App data cleared successfully{Colors.ENDC}")

            if self.logger:
                self.logger.log_event('clear_app_data', f'Cleared data for {package_name}')

            return True, f"Data cleared for {package_name}"
        else:
            print(f"{Colors.FAIL}❌ Failed to clear app data{Colors.ENDC}")
            return False, "Failed to clear app data"

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

    def _parse_size(self, size_str: str) -> float:
        try:
            parts = size_str.split()
            if len(parts) == 2:
                value = float(parts[0])
                unit = parts[1].upper()

                if unit == 'KB':
                    return value
                elif unit == 'MB':
                    return value * 1024
                elif unit == 'GB':
                    return value * 1024 * 1024
            return 0.0
        except Exception:
            return 0.0

    def close(self):
        pass


def create_storage_manager(adb_manager: ADBManager, logger: Optional[Logger] = None) -> StorageManager:
    return StorageManager(adb_manager, logger)


def get_default_storage_manager(adb_manager: ADBManager) -> StorageManager:
    from utils.logger import get_default_logger
    return StorageManager(adb_manager, get_default_logger())
