import os
import json
import re
from typing import List, Dict, Optional
from pathlib import Path

from models.package import PackageInfo
from core.adb_manager import ADBManager
from utils.ui_components import create_table, create_progress_bar
from utils.colors import Colors
from utils.logger import Logger


class PackageManager:
    def __init__(self, adb_manager: ADBManager):
        self.adb = adb_manager
        self.logger = Logger()
        self.friendly_names = self._load_friendly_names()

    def _load_friendly_names(self) -> Dict[str, str]:
        try:
            data_dir = Path(__file__).parent.parent / 'data'
            package_names_file = data_dir / 'package_names.json'

            if package_names_file.exists():
                with open(package_names_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"Package names database not found: {package_names_file}")
                return {}
        except Exception as e:
            self.logger.error(f"Failed to load package names database: {e}")
            return {}

    def list_packages(self, filter_type: str = 'all') -> List[PackageInfo]:
        try:
            if filter_type == 'all':
                cmd = 'pm list packages'
            elif filter_type == 'system':
                cmd = 'pm list packages -s'
            elif filter_type == 'user':
                cmd = 'pm list packages -3'
            elif filter_type == 'enabled':
                cmd = 'pm list packages -e'
            elif filter_type == 'disabled':
                cmd = 'pm list packages -d'
            elif filter_type == 'uninstalled':
                cmd = 'pm list packages -u'
            else:
                self.logger.error(f"Invalid filter type: {filter_type}")
                return []

            result = self.adb.shell_command(cmd)

            if not result or not result.success:
                self.logger.warning("No packages found")
                return []

            # Get system packages list for fast is_system check
            sys_result = self.adb.shell_command('pm list packages -s')
            system_packages = set()
            if sys_result and sys_result.success:
                for line in sys_result.output.strip().split('\n'):
                    if line.startswith('package:'):
                        system_packages.add(line.replace('package:', '').strip())

            # Get disabled packages list for fast is_enabled check
            dis_result = self.adb.shell_command('pm list packages -d')
            disabled_packages = set()
            if dis_result and dis_result.success:
                for line in dis_result.output.strip().split('\n'):
                    if line.startswith('package:'):
                        disabled_packages.add(line.replace('package:', '').strip())

            packages = []
            for line in result.output.strip().split('\n'):
                if line.startswith('package:'):
                    package_name = line.replace('package:', '').strip()
                    if not package_name:
                        continue
                    label = self.friendly_names.get(package_name, package_name)
                    packages.append(PackageInfo(
                        package_name=package_name,
                        label=label,
                        version_code=0,
                        version_name='',
                        is_system=package_name in system_packages,
                        is_enabled=package_name not in disabled_packages,
                        install_location='',
                        apk_path=''
                    ))

            packages.sort(key=lambda p: p.label.lower() if p.label else p.package_name.lower())
            return packages

        except Exception as e:
            self.logger.error(f"Failed to list packages: {e}")
            return []

    def get_package_info(self, package_name: str) -> Optional[PackageInfo]:
        try:
            dump_result = self.adb.shell_command(f'dumpsys package {package_name}')

            if not dump_result or not dump_result.success or 'Unable to find package' in dump_result.output:
                return None

            dump_output = dump_result.output

            version_code = 0
            version_name = ""
            is_system = False
            is_enabled = True
            install_location = ""
            apk_path = ""

            version_code_match = re.search(r'versionCode=(\d+)', dump_output)
            if version_code_match:
                version_code = int(version_code_match.group(1))

            version_name_match = re.search(r'versionName=([^\s]+)', dump_output)
            if version_name_match:
                version_name = version_name_match.group(1)

            if 'system/app' in dump_output or 'system/priv-app' in dump_output:
                is_system = True

            if 'enabled=' in dump_output:
                enabled_match = re.search(r'enabled=(\d+)', dump_output)
                if enabled_match:
                    is_enabled = enabled_match.group(1) != '2'

            apk_path_match = re.search(r'codePath=([^\s]+)', dump_output)
            if apk_path_match:
                apk_path = apk_path_match.group(1)

            install_location_match = re.search(r'installLocation=([^\s]+)', dump_output)
            if install_location_match:
                install_location = install_location_match.group(1)

            label = self.get_package_label(package_name)

            return PackageInfo(
                package_name=package_name,
                label=label,
                version_code=version_code,
                version_name=version_name,
                is_system=is_system,
                is_enabled=is_enabled,
                install_location=install_location,
                apk_path=apk_path
            )

        except Exception as e:
            self.logger.error(f"Failed to get package info for {package_name}: {e}")
            return None

    def get_package_label(self, package_name: str) -> str:
        if package_name in self.friendly_names:
            return self.friendly_names[package_name]

        try:
            result = self.adb.shell_command(f'pm dump {package_name} | grep -A1 "applicationInfo"')

            if result and result.success and result.output:
                label_match = re.search(r'labelRes=0x[0-9a-f]+', result.output)
                if label_match:
                    result2 = self.adb.shell_command(f'dumpsys package {package_name} | grep "label="')
                    if result2 and result2.success:
                        label_match2 = re.search(r'label="([^"]+)"', result2.output)
                        if label_match2:
                            return label_match2.group(1)

            return package_name

        except Exception as e:
            self.logger.debug(f"Failed to get label for {package_name}: {e}")
            return package_name

    def search_packages(self, query: str) -> List[PackageInfo]:
        try:
            all_packages = self.list_packages('all')

            query_lower = query.lower()
            matching_packages = []

            for package in all_packages:
                if (query_lower in package.package_name.lower() or
                        query_lower in package.label.lower()):
                    matching_packages.append(package)

            return matching_packages

        except Exception as e:
            self.logger.error(f"Failed to search packages: {e}")
            return []

    def display_packages_table(self, packages: List[PackageInfo], title: str = "Packages"):
        if not packages:
            print(f"{Colors.WARNING}No packages found{Colors.ENDC}")
            return

        headers = ["#", "Type", "Status", "Name", "Package", "Version"]
        rows = []

        for idx, package in enumerate(packages, 1):
            type_icon = "⚙️" if package.is_system else "📦"
            status_icon = "✓" if package.is_enabled else "✗"
            name = package.label if package.label else package.package_name
            version = package.version_name if package.version_name else "N/A"

            rows.append([
                str(idx),
                type_icon,
                status_icon,
                name[:40],
                package.package_name[:40],
                version
            ])

        table = create_table(headers, rows, title)
        print(table)
        print(f"\n{Colors.OKCYAN}Total: {len(packages)} packages{Colors.ENDC}")

    def install_apk(self, apk_path: str, show_progress: bool = True) -> bool:
        try:
            if not os.path.exists(apk_path):
                self.logger.error(f"APK file not found: {apk_path}")
                print(f"{Colors.FAIL}✗ APK file not found: {apk_path}{Colors.ENDC}")
                return False

            if not apk_path.lower().endswith('.apk'):
                self.logger.error(f"Invalid file extension: {apk_path}")
                print(f"{Colors.FAIL}✗ File must have .apk extension{Colors.ENDC}")
                return False

            file_size = os.path.getsize(apk_path)
            file_size_mb = file_size / (1024 * 1024)

            apk_name = os.path.basename(apk_path)
            print(f"{Colors.OKBLUE}📦 Installing {apk_name} ({file_size_mb:.2f} MB)...{Colors.ENDC}")

            if show_progress:
                print(create_progress_bar(0, 100, prefix="Progress"))

            result = self.adb.install_apk(apk_path)

            if show_progress:
                print(create_progress_bar(100, 100, prefix="Progress"))

            if result:
                print(f"{Colors.OKGREEN}✓ Successfully installed {apk_name}{Colors.ENDC}")
                self.logger.info(f"Installed APK: {apk_path}")
                return True
            else:
                print(f"{Colors.FAIL}✗ Failed to install {apk_name}{Colors.ENDC}")
                self.logger.error(f"Failed to install APK: {apk_path}")
                return False

        except Exception as e:
            self.logger.error(f"Error installing APK {apk_path}: {e}")
            print(f"{Colors.FAIL}✗ Error: {e}{Colors.ENDC}")
            return False

    def batch_install(self, apk_paths: List[str]) -> Dict[str, bool]:
        results = {}
        total = len(apk_paths)

        print(f"{Colors.HEADER}╔══════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📦 Batch Installation ({total} APKs)                ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        for idx, apk_path in enumerate(apk_paths, 1):
            apk_name = os.path.basename(apk_path)
            print(f"\n{Colors.OKCYAN}[{idx}/{total}] Processing: {apk_name}{Colors.ENDC}")

            overall_progress = int((idx - 1) / total * 100)
            print(create_progress_bar(overall_progress, 100, prefix="Overall"))

            success = self.install_apk(apk_path, show_progress=False)
            results[apk_path] = success

        print(create_progress_bar(100, 100, prefix="Overall"))

        success_count = sum(1 for v in results.values() if v)
        fail_count = total - success_count

        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║                    Installation Summary                      ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╠══════════════════════════════════════════════════════════════╣{Colors.ENDC}")
        print(
            f"{
                Colors.HEADER}║{
                Colors.ENDC} {
                Colors.OKGREEN}✓ Successful: {
                    success_count:2d}{
                        Colors.ENDC}                                          {
                            Colors.HEADER}║{
                                Colors.ENDC}")
        print(
            f"{
                Colors.HEADER}║{
                Colors.ENDC} {
                Colors.FAIL}✗ Failed:     {
                    fail_count:2d}{
                        Colors.ENDC}                                          {
                            Colors.HEADER}║{
                                Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}")

        return results

    def uninstall_package(self, package_name: str, system_app: bool = False) -> bool:
        try:
            package_info = self.get_package_info(package_name)

            if not package_info:
                print(f"{Colors.FAIL}✗ Package not found: {package_name}{Colors.ENDC}")
                return False

            display_name = package_info.label if package_info.label else package_name

            if package_info.is_system and not system_app:
                print(f"{Colors.WARNING}⚠ {display_name} is a system app{Colors.ENDC}")
                print(f"{Colors.WARNING}Use system app uninstall option to remove it{Colors.ENDC}")
                return False

            print(f"{Colors.OKBLUE}🗑️  Uninstalling {display_name}...{Colors.ENDC}")

            if system_app:
                result = self.adb.shell_command(f'pm uninstall --user 0 {package_name}')
                success = result and result.success and 'Success' in result.output
            else:
                success = self.adb.uninstall_package(package_name)

            if success:
                print(f"{Colors.OKGREEN}✓ Successfully uninstalled {display_name}{Colors.ENDC}")
                self.logger.info(f"Uninstalled package: {package_name}")
                return True
            else:
                print(f"{Colors.FAIL}✗ Failed to uninstall {display_name}{Colors.ENDC}")
                self.logger.error(f"Failed to uninstall package: {package_name}")
                return False

        except Exception as e:
            self.logger.error(f"Error uninstalling package {package_name}: {e}")
            print(f"{Colors.FAIL}✗ Error: {e}{Colors.ENDC}")
            return False

    def batch_uninstall(self, package_names: List[str], system_apps: bool = False) -> Dict[str, bool]:
        results = {}
        total = len(package_names)

        print(f"{Colors.HEADER}╔══════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║         🗑️  Batch Uninstallation ({total} packages)           ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        for idx, package_name in enumerate(package_names, 1):
            print(f"\n{Colors.OKCYAN}[{idx}/{total}] Processing: {package_name}{Colors.ENDC}")

            overall_progress = int((idx - 1) / total * 100)
            print(create_progress_bar(overall_progress, 100, prefix="Overall"))

            success = self.uninstall_package(package_name, system_app=system_apps)
            results[package_name] = success

        print(create_progress_bar(100, 100, prefix="Overall"))

        success_count = sum(1 for v in results.values() if v)
        fail_count = total - success_count

        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║                  Uninstallation Summary                      ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╠══════════════════════════════════════════════════════════════╣{Colors.ENDC}")
        print(
            f"{
                Colors.HEADER}║{
                Colors.ENDC} {
                Colors.OKGREEN}✓ Successful: {
                    success_count:2d}{
                        Colors.ENDC}                                          {
                            Colors.HEADER}║{
                                Colors.ENDC}")
        print(
            f"{
                Colors.HEADER}║{
                Colors.ENDC} {
                Colors.FAIL}✗ Failed:     {
                    fail_count:2d}{
                        Colors.ENDC}                                          {
                            Colors.HEADER}║{
                                Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}")

        return results

    def enable_package(self, package_name: str) -> bool:
        try:
            package_info = self.get_package_info(package_name)

            if not package_info:
                print(f"{Colors.FAIL}✗ Package not found: {package_name}{Colors.ENDC}")
                return False

            display_name = package_info.label if package_info.label else package_name

            if package_info.is_enabled:
                print(f"{Colors.WARNING}⚠ {display_name} is already enabled{Colors.ENDC}")
                return True

            print(f"{Colors.OKBLUE}✓ Enabling {display_name}...{Colors.ENDC}")

            result = self.adb.shell_command(f'pm enable {package_name}')

            if result and result.success and ('enabled' in result.output.lower() or 'success' in result.output.lower()):
                print(f"{Colors.OKGREEN}✓ Successfully enabled {display_name}{Colors.ENDC}")
                self.logger.info(f"Enabled package: {package_name}")
                return True
            else:
                print(f"{Colors.FAIL}✗ Failed to enable {display_name}{Colors.ENDC}")
                self.logger.error(f"Failed to enable package: {package_name}")
                return False

        except Exception as e:
            self.logger.error(f"Error enabling package {package_name}: {e}")
            print(f"{Colors.FAIL}✗ Error: {e}{Colors.ENDC}")
            return False

    def disable_package(self, package_name: str) -> bool:
        try:
            package_info = self.get_package_info(package_name)

            if not package_info:
                print(f"{Colors.FAIL}✗ Package not found: {package_name}{Colors.ENDC}")
                return False

            display_name = package_info.label if package_info.label else package_name

            if not package_info.is_enabled:
                print(f"{Colors.WARNING}⚠ {display_name} is already disabled{Colors.ENDC}")
                return True

            print(f"{Colors.OKBLUE}✗ Disabling {display_name}...{Colors.ENDC}")

            result = self.adb.shell_command(f'pm disable-user {package_name}')

            if result and result.success and ('disabled' in result.output.lower() or 'success' in result.output.lower()):
                print(f"{Colors.OKGREEN}✓ Successfully disabled {display_name}{Colors.ENDC}")
                self.logger.info(f"Disabled package: {package_name}")
                return True
            else:
                print(f"{Colors.FAIL}✗ Failed to disable {display_name}{Colors.ENDC}")
                self.logger.error(f"Failed to disable package: {package_name}")
                return False

        except Exception as e:
            self.logger.error(f"Error disabling package {package_name}: {e}")
            print(f"{Colors.FAIL}✗ Error: {e}{Colors.ENDC}")
            return False

    def batch_enable(self, package_names: List[str]) -> Dict[str, bool]:
        results = {}
        total = len(package_names)

        print(f"{Colors.HEADER}╔══════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║            ✓ Batch Enable ({total} packages)                  ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        for idx, package_name in enumerate(package_names, 1):
            print(f"\n{Colors.OKCYAN}[{idx}/{total}] Processing: {package_name}{Colors.ENDC}")

            overall_progress = int((idx - 1) / total * 100)
            print(create_progress_bar(overall_progress, 100, prefix="Overall"))

            success = self.enable_package(package_name)
            results[package_name] = success

        print(create_progress_bar(100, 100, prefix="Overall"))

        success_count = sum(1 for v in results.values() if v)
        fail_count = total - success_count

        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║                      Enable Summary                          ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╠══════════════════════════════════════════════════════════════╣{Colors.ENDC}")
        print(
            f"{
                Colors.HEADER}║{
                Colors.ENDC} {
                Colors.OKGREEN}✓ Successful: {
                    success_count:2d}{
                        Colors.ENDC}                                          {
                            Colors.HEADER}║{
                                Colors.ENDC}")
        print(
            f"{
                Colors.HEADER}║{
                Colors.ENDC} {
                Colors.FAIL}✗ Failed:     {
                    fail_count:2d}{
                        Colors.ENDC}                                          {
                            Colors.HEADER}║{
                                Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}")

        return results

    def batch_disable(self, package_names: List[str]) -> Dict[str, bool]:
        results = {}
        total = len(package_names)

        print(f"{Colors.HEADER}╔══════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║            ✗ Batch Disable ({total} packages)                 ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        for idx, package_name in enumerate(package_names, 1):
            print(f"\n{Colors.OKCYAN}[{idx}/{total}] Processing: {package_name}{Colors.ENDC}")

            overall_progress = int((idx - 1) / total * 100)
            print(create_progress_bar(overall_progress, 100, prefix="Overall"))

            success = self.disable_package(package_name)
            results[package_name] = success

        print(create_progress_bar(100, 100, prefix="Overall"))

        success_count = sum(1 for v in results.values() if v)
        fail_count = total - success_count

        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║                     Disable Summary                          ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╠══════════════════════════════════════════════════════════════╣{Colors.ENDC}")
        print(
            f"{
                Colors.HEADER}║{
                Colors.ENDC} {
                Colors.OKGREEN}✓ Successful: {
                    success_count:2d}{
                        Colors.ENDC}                                          {
                            Colors.HEADER}║{
                                Colors.ENDC}")
        print(
            f"{
                Colors.HEADER}║{
                Colors.ENDC} {
                Colors.FAIL}✗ Failed:     {
                    fail_count:2d}{
                        Colors.ENDC}                                          {
                            Colors.HEADER}║{
                                Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}")

        return results
