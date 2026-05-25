import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from core.adb_manager import ADBManager
from core.package_manager import PackageManager
from utils.download_manager import DownloadManager, ConsoleDownloadObserver
from utils.web_search import create_web_search
from utils.logger import Logger
from utils.colors import Colors
from utils.ui_components import Emoji, BoxChars


class InstallHelper:
    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None):
        self.adb = adb_manager
        self.logger = logger or Logger()
        self.package_manager = PackageManager(adb_manager)
        self.download_manager = DownloadManager()
        self.download_manager.add_observer(ConsoleDownloadObserver())
        self.web_search = create_web_search()

        self.app_sources = self._load_app_sources()

    def _load_app_sources(self) -> Dict[str, Any]:
        try:
            sources_file = Path(__file__).parent.parent / 'data' / 'app_sources.json'

            if not sources_file.exists():
                self.logger.error(f'App sources file not found: {sources_file}')
                return {}

            with open(sources_file, 'r', encoding='utf-8') as f:
                sources = json.load(f)

            self.logger.info(f'Loaded {len(sources)} app sources')
            return sources

        except Exception as e:
            self.logger.error(f'Failed to load app sources: {e}', exception=e)
            return {}

    def get_app_info(self, app_id: str) -> Optional[Dict[str, Any]]:
        return self.app_sources.get(app_id)

    def list_available_apps(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        apps = []

        for app_id, app_data in self.app_sources.items():
            if category is None or app_data.get('category') == category:
                apps.append({
                    'id': app_id,
                    'name': app_data.get('name'),
                    'category': app_data.get('category'),
                    'description': app_data.get('description'),
                    'package': app_data.get('package')
                })

        return sorted(apps, key=lambda x: x['name'])

    def check_installed(self, app_id: str) -> Tuple[bool, Optional[str]]:
        app_info = self.get_app_info(app_id)

        if not app_info:
            return False, None

        package_name = app_info.get('package')

        if not package_name:
            return False, None

        try:
            packages = self.package_manager.list_packages(filter_type='all')

            for pkg in packages:
                if pkg.package_name == package_name:
                    version = pkg.version_name or 'unknown'
                    self.logger.info(f'{app_info["name"]} is installed (version: {version})')
                    return True, version

            return False, None

        except Exception as e:
            self.logger.error(f'Failed to check if {app_id} is installed: {e}', exception=e)
            return False, None

    def get_installed_version(self, app_id: str) -> Optional[str]:
        is_installed, version = self.check_installed(app_id)
        return version if is_installed else None

    def download_and_install(self, app_id: str, use_web_search: bool = True,
                             custom_url: Optional[str] = None) -> Tuple[bool, str]:
        app_info = self.get_app_info(app_id)

        if not app_info:
            error_msg = f'Unknown app ID: {app_id}'
            self.logger.error(error_msg)
            return False, error_msg

        app_name = app_info.get('name')
        _ = app_info.get('package')

        print(f'\n{Colors.HEADER}{BoxChars.TOP_LEFT}{BoxChars.HORIZONTAL * 60}{BoxChars.TOP_RIGHT}{Colors.ENDC}')
        print(f'{Colors.HEADER}{BoxChars.VERTICAL}{Colors.ENDC} {Colors.BOLD}{Emoji.DOWNLOAD} Installing {app_name}{Colors.ENDC}' +
              ' ' * (60 - len(f' Installing {app_name}') - 2) + f'{Colors.HEADER}{BoxChars.VERTICAL}{Colors.ENDC}')
        print(f'{Colors.HEADER}{BoxChars.BOTTOM_LEFT}{BoxChars.HORIZONTAL * 60}{BoxChars.BOTTOM_RIGHT}{Colors.ENDC}\n')

        is_installed, current_version = self.check_installed(app_id)

        if is_installed:
            print(f'{Colors.WARNING}{Emoji.INFO} {app_name} is already installed (version: {current_version}){Colors.ENDC}')

            response = input(f'{Colors.BOLD}Do you want to reinstall/update? (y/n): {Colors.ENDC}').strip().lower()

            if response != 'y':
                return False, 'Installation cancelled by user'

        download_url = custom_url

        if not download_url and use_web_search:
            print(f'{Colors.OKBLUE}{Emoji.SEARCH} Searching for latest version...{Colors.ENDC}')

            search_query = app_info.get('search_query')

            if search_query:
                result = self.web_search.find_latest_apk_url(app_name)

                if result and result.get('url'):
                    download_url = result['url']
                    print(f'{Colors.OKGREEN}{Emoji.CHECK} Found: {download_url}{Colors.ENDC}')
                else:
                    print(f'{Colors.WARNING}{Emoji.WARNING} Web search did not find a download URL{Colors.ENDC}')

        if not download_url:
            download_url = app_info.get('download_url')

            if not download_url:
                error_msg = f'No download URL available for {app_name}'
                self.logger.error(error_msg)
                return False, error_msg

            print(f'{Colors.OKBLUE}{Emoji.INFO} Using configured URL: {download_url}{Colors.ENDC}')

        print(f'\n{Colors.OKBLUE}{Emoji.DOWNLOAD} Downloading {app_name}...{Colors.ENDC}')

        success = self.download_manager.download_file(
            download_url,
            verify_integrity=False
        )

        if not success:
            error_msg = f'Failed to download {app_name}'
            self.logger.error(error_msg)
            return False, error_msg

        _ = app_info.get('download_pattern', '.*\\.apk')
        temp_files = self.download_manager.get_temp_files()

        apk_file = None
        for file_info in temp_files:
            if file_info['name'].endswith('.apk'):
                apk_file = file_info['path']
                break

        if not apk_file:
            error_msg = f'Downloaded file not found for {app_name}'
            self.logger.error(error_msg)
            return False, error_msg

        print(f'\n{Colors.OKBLUE}{Emoji.PACKAGE} Installing {app_name}...{Colors.ENDC}')

        install_success, install_message = self.adb.install_apk(apk_file)

        if install_success:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} {app_name} installed successfully!{Colors.ENDC}')

            self.download_manager.cleanup_temp_files()

            notes = app_info.get('notes')
            if notes:
                print(f'\n{Colors.OKCYAN}{Emoji.INFO} Note: {notes}{Colors.ENDC}')

            setup_instructions = app_info.get('setup_instructions')
            if setup_instructions:
                print(f'\n{Colors.BOLD}{Emoji.WRENCH} Setup Instructions:{Colors.ENDC}')
                for i, instruction in enumerate(setup_instructions, 1):
                    print(f'  {i}. {instruction}')

            addon_info = app_info.get('addon_info')
            if addon_info:
                print(f'\n{Colors.BOLD}{Emoji.PUZZLE} Available Addons:{Colors.ENDC}')
                for addon_id, addon_data in addon_info.items():
                    print(f'  {Emoji.STAR} {addon_data.get("name")}: {addon_data.get("description")}')
                    if addon_data.get('config_url'):
                        print(f'    Config: {addon_data.get("config_url")}')

            self.logger.info(f'Successfully installed {app_name}')
            return True, f'{app_name} installed successfully'

        else:
            error_msg = f'Failed to install {app_name}: {install_message}'
            self.logger.error(error_msg)
            return False, error_msg

    def uninstall_app(self, app_id: str) -> Tuple[bool, str]:
        app_info = self.get_app_info(app_id)

        if not app_info:
            error_msg = f'Unknown app ID: {app_id}'
            self.logger.error(error_msg)
            return False, error_msg

        app_name = app_info.get('name')
        package_name = app_info.get('package')

        is_installed, version = self.check_installed(app_id)

        if not is_installed:
            return False, f'{app_name} is not installed'

        print(f'\n{Colors.WARNING}{Emoji.WARNING} Uninstalling {app_name}...{Colors.ENDC}')

        response = input(
            f'{Colors.BOLD}Are you sure you want to uninstall {app_name}? (y/n): {Colors.ENDC}').strip().lower()

        if response != 'y':
            return False, 'Uninstallation cancelled by user'

        success, message = self.package_manager.uninstall_package(package_name)

        if success:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} {app_name} uninstalled successfully{Colors.ENDC}')
            self.logger.info(f'Uninstalled {app_name}')
            return True, f'{app_name} uninstalled successfully'
        else:
            error_msg = f'Failed to uninstall {app_name}: {message}'
            self.logger.error(error_msg)
            return False, error_msg

    def check_for_updates(self, app_id: str) -> Tuple[bool, Optional[str], Optional[str]]:
        app_info = self.get_app_info(app_id)

        if not app_info:
            return False, None, 'Unknown app ID'

        is_installed, current_version = self.check_installed(app_id)

        if not is_installed:
            return False, None, 'App not installed'

        app_name = app_info.get('name')

        result = self.web_search.find_latest_apk_url(app_name)

        if not result or not result.get('url'):
            return False, None, 'Could not find latest version'

        latest_url = result['url']

        return True, latest_url, current_version

    def offer_update(self, app_id: str) -> Tuple[bool, str]:
        app_info = self.get_app_info(app_id)

        if not app_info:
            return False, 'Unknown app ID'

        app_name = app_info.get('name')

        has_update, latest_url, current_version = self.check_for_updates(app_id)

        if not has_update:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} {app_name} is up to date (version: {current_version}){Colors.ENDC}')
            return False, 'No update available'

        print(f'\n{Colors.OKCYAN}{Emoji.INFO} Update available for {app_name}{Colors.ENDC}')
        print(f'Current version: {current_version}')
        print(f'Latest URL: {latest_url}')

        response = input(f'{Colors.BOLD}Do you want to update {app_name}? (y/n): {Colors.ENDC}').strip().lower()

        if response != 'y':
            return False, 'Update cancelled by user'

        return self.download_and_install(app_id, use_web_search=False, custom_url=latest_url)

    def display_app_info(self, app_id: str):
        app_info = self.get_app_info(app_id)

        if not app_info:
            print(f'{Colors.FAIL}{Emoji.CROSS} Unknown app ID: {app_id}{Colors.ENDC}')
            return

        is_installed, version = self.check_installed(app_id)

        print(f'\n{Colors.HEADER}{BoxChars.TOP_LEFT}{BoxChars.HORIZONTAL * 60}{BoxChars.TOP_RIGHT}{Colors.ENDC}')
        print(f'{Colors.HEADER}{BoxChars.VERTICAL}{Colors.ENDC} {Colors.BOLD}{app_info.get("name")}{Colors.ENDC}' +
              ' ' * (60 - len(app_info.get("name")) - 2) + f'{Colors.HEADER}{BoxChars.VERTICAL}{Colors.ENDC}')
        print(f'{Colors.HEADER}{BoxChars.BOTTOM_LEFT}{BoxChars.HORIZONTAL * 60}{BoxChars.BOTTOM_RIGHT}{Colors.ENDC}\n')

        print(f'{Colors.BOLD}Category:{Colors.ENDC} {app_info.get("category")}')
        print(f'{Colors.BOLD}Package:{Colors.ENDC} {app_info.get("package")}')
        print(f'{Colors.BOLD}Description:{Colors.ENDC} {app_info.get("description")}')

        if is_installed:
            print(
                f'{
                    Colors.BOLD}Status:{
                    Colors.ENDC} {
                    Colors.OKGREEN}{
                    Emoji.CHECK} Installed (version: {version}){
                        Colors.ENDC}')
        else:
            print(f'{Colors.BOLD}Status:{Colors.ENDC} {Colors.WARNING}{Emoji.CROSS} Not installed{Colors.ENDC}')

        print(f'\n{Colors.BOLD}Features:{Colors.ENDC}')
        for feature in app_info.get('features', []):
            print(f'  {Emoji.STAR} {feature}')

        if app_info.get('notes'):
            print(f'\n{Colors.BOLD}Notes:{Colors.ENDC} {app_info.get("notes")}')

        print(f'\n{Colors.BOLD}Official URL:{Colors.ENDC} {app_info.get("official_url")}')
        print()

    def close(self):
        self.download_manager.close()


def create_install_helper(adb_manager: ADBManager, logger: Optional[Logger] = None) -> InstallHelper:
    return InstallHelper(adb_manager, logger)


_default_install_helper: Optional[InstallHelper] = None


def get_default_install_helper(adb_manager: ADBManager) -> InstallHelper:
    global _default_install_helper
    if _default_install_helper is None:
        _default_install_helper = create_install_helper(adb_manager)
    return _default_install_helper
