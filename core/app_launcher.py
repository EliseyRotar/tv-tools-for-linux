from typing import Tuple, Optional, Dict, List
from core.adb_manager import ADBManager
from utils.logger import Logger
from utils.colors import Colors


class AppLauncher:

    COMMON_APPS = {
        'netflix': {
            'package': 'com.netflix.ninja',
            'activity': '.MainActivity',
            'name': 'Netflix'
        },
        'youtube': {
            'package': 'com.google.android.youtube.tv',
            'activity': '.activity.ShellActivity',
            'name': 'YouTube'
        },
        'prime_video': {
            'package': 'com.amazon.avod.thirdpartyclient',
            'activity': '.LauncherActivity',
            'name': 'Prime Video'
        },
        'disney_plus': {
            'package': 'com.disney.disneyplus',
            'activity': '.MainActivity',
            'name': 'Disney+'
        },
        'plex': {
            'package': 'com.plexapp.android',
            'activity': '.activities.MainActivity',
            'name': 'Plex'
        },
        'kodi': {
            'package': 'org.xbmc.kodi',
            'activity': '.Splash',
            'name': 'Kodi'
        },
        'smarttube': {
            'package': 'com.liskovsoft.smarttubetv.beta',
            'activity': '.MainActivity',
            'name': 'SmartTube'
        },
        'spotify': {
            'package': 'com.spotify.tv.android',
            'activity': '.SpotifyTVActivity',
            'name': 'Spotify'
        }
    }

    SETTINGS_SHORTCUTS = {
        'wifi': {
            'action': 'android.settings.WIFI_SETTINGS',
            'description': 'WiFi settings'
        },
        'display': {
            'action': 'android.settings.DISPLAY_SETTINGS',
            'description': 'Display settings'
        },
        'apps': {
            'action': 'android.settings.APPLICATION_SETTINGS',
            'description': 'Apps settings'
        },
        'storage': {
            'action': 'android.settings.INTERNAL_STORAGE_SETTINGS',
            'description': 'Storage settings'
        },
        'sound': {
            'action': 'android.settings.SOUND_SETTINGS',
            'description': 'Sound settings'
        },
        'network': {
            'action': 'android.settings.NETWORK_SETTINGS',
            'description': 'Network settings'
        },
        'bluetooth': {
            'action': 'android.settings.BLUETOOTH_SETTINGS',
            'description': 'Bluetooth settings'
        },
        'location': {
            'action': 'android.settings.LOCATION_SOURCE_SETTINGS',
            'description': 'Location settings'
        },
        'security': {
            'action': 'android.settings.SECURITY_SETTINGS',
            'description': 'Security settings'
        },
        'date_time': {
            'action': 'android.settings.DATE_SETTINGS',
            'description': 'Date & time settings'
        },
        'accessibility': {
            'action': 'android.settings.ACCESSIBILITY_SETTINGS',
            'description': 'Accessibility settings'
        },
        'developer': {
            'action': 'android.settings.APPLICATION_DEVELOPMENT_SETTINGS',
            'description': 'Developer options'
        }
    }

    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None):
        self.adb = adb_manager
        self.logger = logger

    def launch_app_by_package(self, package_name: str, activity: Optional[str] = None) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🚀 Launching App by Package                    ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  Package: {package_name}{Colors.ENDC}")
        if activity:
            print(f"{Colors.OKBLUE}ℹ️  Activity: {activity}{Colors.ENDC}")
        print()

        if activity:
            full_component = f"{package_name}/{activity}"
            cmd = f"am start -n {full_component}"
        else:
            cmd = f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1"

        result = self.adb.shell_command(cmd)

        if result.success or result.return_code == 0:
            print(f"{Colors.OKGREEN}✅ App launched successfully{Colors.ENDC}")
            if self.logger:
                self.logger.log_event('app_launcher', f'Launched {package_name}')
            return True, f"Launched {package_name}"
        else:
            print(f"{Colors.FAIL}❌ Failed to launch app{Colors.ENDC}")
            return False, f"Failed to launch: {result.error}"

    def launch_app_by_activity(self, package_name: str, activity: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🎯 Launching App by Activity                   ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  Package: {package_name}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Activity: {activity}{Colors.ENDC}\n")

        full_component = f"{package_name}/{activity}"
        result = self.adb.shell_command(f"am start -n {full_component}")

        if result.success or result.return_code == 0:
            print(f"{Colors.OKGREEN}✅ Activity launched successfully{Colors.ENDC}")
            if self.logger:
                self.logger.log_event('app_launcher', f'Launched {full_component}')
            return True, f"Launched {full_component}"
        else:
            print(f"{Colors.FAIL}❌ Failed to launch activity{Colors.ENDC}")
            return False, f"Failed to launch: {result.error}"

    def launch_common_app(self, app_key: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📱 Launching Common App                        ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if app_key not in self.COMMON_APPS:
            print(f"{Colors.FAIL}❌ Unknown app: {app_key}{Colors.ENDC}")
            return False, f"Unknown app: {app_key}"

        app_info = self.COMMON_APPS[app_key]
        print(f"{Colors.OKBLUE}ℹ️  App: {app_info['name']}{Colors.ENDC}\n")

        return self.launch_app_by_activity(app_info['package'], app_info['activity'])

    def open_settings_page(self, settings_key: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ⚙️  Opening Settings Page                      ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if settings_key not in self.SETTINGS_SHORTCUTS:
            print(f"{Colors.FAIL}❌ Unknown settings page: {settings_key}{Colors.ENDC}")
            return False, f"Unknown settings page: {settings_key}"

        settings_info = self.SETTINGS_SHORTCUTS[settings_key]
        print(f"{Colors.OKBLUE}ℹ️  Opening: {settings_info['description']}{Colors.ENDC}\n")

        result = self.adb.shell_command(f"am start -a {settings_info['action']}")

        if result.success or result.return_code == 0:
            print(f"{Colors.OKGREEN}✅ Settings page opened{Colors.ENDC}")
            if self.logger:
                self.logger.log_event('app_launcher', f'Opened settings: {settings_key}')
            return True, f"Opened {settings_info['description']}"
        else:
            print(f"{Colors.FAIL}❌ Failed to open settings page{Colors.ENDC}")
            return False, f"Failed to open settings: {result.error}"

    def list_common_apps(self) -> List[Dict[str, str]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📋 Common Apps                                 ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        apps = []
        for key, info in self.COMMON_APPS.items():
            print(f"{Colors.OKBLUE}• {key:15} - {info['name']}{Colors.ENDC}")
            apps.append({
                'key': key,
                'name': info['name'],
                'package': info['package']
            })

        return apps

    def list_settings_shortcuts(self) -> List[Dict[str, str]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ⚙️  Settings Shortcuts                         ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        shortcuts = []
        for key, info in self.SETTINGS_SHORTCUTS.items():
            print(f"{Colors.OKBLUE}• {key:15} - {info['description']}{Colors.ENDC}")
            shortcuts.append({
                'key': key,
                'description': info['description'],
                'action': info['action']
            })

        return shortcuts

    def get_current_app(self) -> Tuple[bool, Optional[str]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🔍 Getting Current App                         ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        result = self.adb.shell_command('dumpsys window | grep mCurrentFocus')

        if result.success and result.output:
            output = result.output.strip()
            if '/' in output:
                parts = output.split('/')
                if len(parts) >= 2:
                    package = parts[0].split()[-1]
                    activity = parts[1].split('}')[0]
                    current = f"{package}/{activity}"
                    print(f"{Colors.OKGREEN}✅ Current app: {current}{Colors.ENDC}")
                    return True, current

        print(f"{Colors.WARNING}⚠️  Could not determine current app{Colors.ENDC}")
        return False, None

    def launch_url(self, url: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🌐 Opening URL                                 ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  URL: {url}{Colors.ENDC}\n")

        result = self.adb.shell_command(f'am start -a android.intent.action.VIEW -d "{url}"')

        if result.success or result.return_code == 0:
            print(f"{Colors.OKGREEN}✅ URL opened{Colors.ENDC}")
            if self.logger:
                self.logger.log_event('app_launcher', f'Opened URL: {url}')
            return True, f"Opened URL: {url}"
        else:
            print(f"{Colors.FAIL}❌ Failed to open URL{Colors.ENDC}")
            return False, f"Failed to open URL: {result.error}"

    def stop_app(self, package_name: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🛑 Stopping App                                ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  Package: {package_name}{Colors.ENDC}\n")

        result = self.adb.shell_command(f'am force-stop {package_name}')

        if result.success or result.return_code == 0:
            print(f"{Colors.OKGREEN}✅ App stopped{Colors.ENDC}")
            if self.logger:
                self.logger.log_event('app_launcher', f'Stopped {package_name}')
            return True, f"Stopped {package_name}"
        else:
            print(f"{Colors.FAIL}❌ Failed to stop app{Colors.ENDC}")
            return False, f"Failed to stop: {result.error}"

    def close(self):
        pass


def create_app_launcher(adb_manager: ADBManager, logger: Optional[Logger] = None) -> AppLauncher:
    return AppLauncher(adb_manager, logger)


def get_default_app_launcher(adb_manager: ADBManager) -> AppLauncher:
    from utils.logger import get_default_logger
    return AppLauncher(adb_manager, get_default_logger())
