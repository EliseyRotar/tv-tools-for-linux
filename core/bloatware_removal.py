from typing import Tuple, Optional, List, Dict
import json
import os
from core.adb_manager import ADBManager
from utils.logger import Logger
from utils.colors import Colors


class BloatwareRemoval:

    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None):
        self.adb = adb_manager
        self.logger = logger
        self.bloatware_lists = self._load_bloatware_lists()
        self.removed_packages: List[str] = []

    def _load_bloatware_lists(self) -> Dict:
        bloatware_file = os.path.join('data', 'bloatware_lists.json')

        try:
            with open(bloatware_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'safe': {'description': '', 'risk_level': 'low', 'packages': []},
                'caution': {'description': '', 'risk_level': 'medium', 'packages': []},
                'advanced': {'description': '', 'risk_level': 'high', 'packages': []}
            }

    def list_bloatware(self, category: str = 'all') -> Tuple[bool, List[Dict]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📋 Bloatware List                              ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, []

        all_packages = []

        if category == 'all' or category == 'safe':
            self._display_category('safe')
            all_packages.extend(self.bloatware_lists['safe']['packages'])

        if category == 'all' or category == 'caution':
            self._display_category('caution')
            all_packages.extend(self.bloatware_lists['caution']['packages'])

        if category == 'all' or category == 'advanced':
            self._display_category('advanced')
            all_packages.extend(self.bloatware_lists['advanced']['packages'])

        return True, all_packages

    def _display_category(self, category: str):
        if category not in self.bloatware_lists:
            return

        cat_data = self.bloatware_lists[category]

        risk_color = Colors.OKGREEN if cat_data['risk_level'] == 'low' else \
            Colors.WARNING if cat_data['risk_level'] == 'medium' else Colors.FAIL

        risk_icon = '🟢' if cat_data['risk_level'] == 'low' else \
                    '🟡' if cat_data['risk_level'] == 'medium' else '🔴'

        print(f"{risk_color}{risk_icon} {category.upper()} - {cat_data['description']}{Colors.ENDC}")
        print(f"{risk_color}Risk Level: {cat_data['risk_level'].upper()}{Colors.ENDC}\n")

        for pkg in cat_data['packages']:
            installed = self._check_package_installed(pkg['package'])
            status = f"{
                Colors.OKGREEN}[INSTALLED]{
                Colors.ENDC}" if installed else f"{
                Colors.OKBLUE}[NOT INSTALLED]{
                Colors.ENDC}"

            print(f"{Colors.OKBLUE}• {pkg['name']:30} {status}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}  Package: {pkg['package']}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}  Description: {pkg['description']}{Colors.ENDC}\n")

    def _check_package_installed(self, package: str) -> bool:
        result = self.adb.shell_command(f'pm list packages {package}')
        return result.success and package in result.output

    def remove_bloatware(self, category: str, confirm: bool = True) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🗑️  Removing Bloatware                         ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        if category not in self.bloatware_lists:
            print(f"{Colors.FAIL}❌ Unknown category: {category}{Colors.ENDC}")
            return False, f"Unknown category: {category}"

        cat_data = self.bloatware_lists[category]
        packages = cat_data['packages']

        print(f"{Colors.OKBLUE}ℹ️  Category: {category.upper()}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Risk Level: {cat_data['risk_level'].upper()}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Packages: {len(packages)}{Colors.ENDC}\n")

        if cat_data['risk_level'] == 'high':
            print(f"{Colors.FAIL}⚠️  WARNING: HIGH RISK CATEGORY{Colors.ENDC}")
            print(f"{Colors.FAIL}⚠️  Removing these packages may cause system instability{Colors.ENDC}")
            print(f"{Colors.FAIL}⚠️  Some apps and features may stop working{Colors.ENDC}\n")
        elif cat_data['risk_level'] == 'medium':
            print(f"{Colors.WARNING}⚠️  CAUTION: MEDIUM RISK CATEGORY{Colors.ENDC}")
            print(f"{Colors.WARNING}⚠️  Some features may be affected{Colors.ENDC}\n")

        if confirm:
            response = input(f"{Colors.OKBLUE}Continue with removal? (yes/no): {Colors.ENDC}").strip().lower()
            if response not in ['yes', 'y']:
                print(f"{Colors.WARNING}⚠️  Removal cancelled{Colors.ENDC}")
                return False, "Removal cancelled by user"

        print(f"\n{Colors.OKBLUE}🗑️  Starting removal...{Colors.ENDC}\n")

        removed = 0
        not_found = 0
        failed = 0

        for pkg in packages:
            package_name = pkg['package']
            app_name = pkg['name']

            if not self._check_package_installed(package_name):
                print(f"{Colors.OKBLUE}⊘ {app_name:30} - Not installed{Colors.ENDC}")
                not_found += 1
                continue

            print(f"{Colors.OKBLUE}🗑️  Removing: {app_name}{Colors.ENDC}")

            result = self.adb.shell_command(f'pm uninstall --user 0 {package_name}')

            if result.success or 'Success' in result.output:
                print(f"{Colors.OKGREEN}✅ Removed: {app_name}{Colors.ENDC}\n")
                removed += 1
                self.removed_packages.append(package_name)
            else:
                print(f"{Colors.FAIL}❌ Failed: {app_name}{Colors.ENDC}\n")
                failed += 1

        print(f"{Colors.OKGREEN}✅ Removal complete{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Removed: {removed}/{len(packages)}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Not found: {not_found}/{len(packages)}{Colors.ENDC}")

        if failed > 0:
            print(f"{Colors.WARNING}⚠️  Failed: {failed}/{len(packages)}{Colors.ENDC}")

        if self.logger:
            self.logger.log_event('bloatware_removal', f'Removed {removed} packages from {category}')

        return removed > 0, f"Removed {removed} packages"

    def remove_package(self, package_name: str, confirm: bool = True) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🗑️  Removing Package                           ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        print(f"{Colors.OKBLUE}ℹ️  Package: {package_name}{Colors.ENDC}\n")

        if not self._check_package_installed(package_name):
            print(f"{Colors.WARNING}⚠️  Package not installed{Colors.ENDC}")
            return False, "Package not installed"

        risk_level = self._get_package_risk_level(package_name)
        if risk_level:
            risk_color = Colors.OKGREEN if risk_level == 'low' else \
                Colors.WARNING if risk_level == 'medium' else Colors.FAIL
            print(f"{risk_color}⚠️  Risk Level: {risk_level.upper()}{Colors.ENDC}\n")

        if confirm:
            response = input(f"{Colors.OKBLUE}Remove this package? (yes/no): {Colors.ENDC}").strip().lower()
            if response not in ['yes', 'y']:
                print(f"{Colors.WARNING}⚠️  Removal cancelled{Colors.ENDC}")
                return False, "Removal cancelled by user"

        print(f"\n{Colors.OKBLUE}🗑️  Removing package...{Colors.ENDC}\n")

        result = self.adb.shell_command(f'pm uninstall --user 0 {package_name}')

        if result.success or 'Success' in result.output:
            print(f"{Colors.OKGREEN}✅ Package removed{Colors.ENDC}")
            self.removed_packages.append(package_name)

            if self.logger:
                self.logger.log_event('bloatware_removal', f'Removed package: {package_name}')

            return True, f"Removed {package_name}"
        else:
            print(f"{Colors.FAIL}❌ Failed to remove package{Colors.ENDC}")
            return False, f"Failed to remove: {result.error}"

    def _get_package_risk_level(self, package_name: str) -> Optional[str]:
        for category in ['safe', 'caution', 'advanced']:
            if category in self.bloatware_lists:
                for pkg in self.bloatware_lists[category]['packages']:
                    if pkg['package'] == package_name:
                        return self.bloatware_lists[category]['risk_level']
        return None

    def create_backup_list(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           💾 Creating Backup List                        ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.removed_packages:
            print(f"{Colors.WARNING}⚠️  No packages have been removed yet{Colors.ENDC}")
            return False, "No packages removed"

        backup_file = 'removed_packages_backup.txt'

        try:
            with open(backup_file, 'w') as f:
                f.write("# Removed Packages Backup\n")
                f.write("# Use these commands to reinstall if needed\n\n")
                for package in self.removed_packages:
                    f.write(f"# {package}\n")
                    f.write(f"adb shell pm install-existing {package}\n\n")

            print(f"{Colors.OKGREEN}✅ Backup list created{Colors.ENDC}")
            print(f"{Colors.OKBLUE}ℹ️  File: {backup_file}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}ℹ️  Packages: {len(self.removed_packages)}{Colors.ENDC}")

            return True, f"Backup list created: {backup_file}"

        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to create backup list: {e}{Colors.ENDC}")
            return False, f"Failed to create backup: {e}"

    def get_removed_packages(self) -> List[str]:
        return self.removed_packages.copy()

    def close(self):
        pass


def create_bloatware_removal(adb_manager: ADBManager, logger: Optional[Logger] = None) -> BloatwareRemoval:
    return BloatwareRemoval(adb_manager, logger)


def get_default_bloatware_removal(adb_manager: ADBManager) -> BloatwareRemoval:
    from utils.logger import get_default_logger
    return BloatwareRemoval(adb_manager, get_default_logger())
