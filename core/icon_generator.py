from typing import List, Tuple, Optional
from core.adb_manager import ADBManager
from utils.logger import Logger
from utils.colors import Colors


class IconGenerator:

    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None):
        self.adb = adb_manager
        self.logger = logger
        self.hidden_apps: List[str] = []

    def detect_hidden_apps(self) -> Tuple[bool, List[str]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🔍 Detecting Hidden Apps                       ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, []

        print(f"{Colors.OKBLUE}📦 Scanning for hidden apps...{Colors.ENDC}")

        result = self.adb.shell_command('pm list packages -3')
        if not result.success or not result.output:
            print(f"{Colors.FAIL}❌ Failed to list packages{Colors.ENDC}")
            return False, []

        all_packages = [line.replace('package:', '').strip()
                        for line in result.output.strip().split('\n')
                        if line.startswith('package:')]

        hidden_apps = []
        total = len(all_packages)

        for idx, package in enumerate(all_packages, 1):
            print(f"{Colors.OKBLUE}   Checking {idx}/{total}: {package}{Colors.ENDC}", end='\r')

            result = self.adb.shell_command(f'pm list packages -3 | grep {package}')
            if not result.success:
                continue

            result = self.adb.shell_command(
                f'cmd package resolve-activity --brief {package} | grep {package}'
            )

            if not result.success or not result.output or package not in result.output:
                hidden_apps.append(package)

        print(f"\n{Colors.OKGREEN}✅ Scan complete{Colors.ENDC}\n")

        if hidden_apps:
            print(f"{Colors.WARNING}🔍 Found {len(hidden_apps)} hidden app(s):{Colors.ENDC}\n")
            for app in hidden_apps:
                print(f"{Colors.WARNING}   • {app}{Colors.ENDC}")
        else:
            print(f"{Colors.OKGREEN}✅ No hidden apps found{Colors.ENDC}")

        self.hidden_apps = hidden_apps

        if self.logger:
            self.logger.log_event('detect_hidden_apps', f'Found {len(hidden_apps)} hidden apps')

        return True, hidden_apps

    def generate_launcher_icon(self, package_name: str, label: Optional[str] = None) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🎨 Generating Launcher Icon                    ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        if not package_name:
            print(f"{Colors.FAIL}❌ Package name is required{Colors.ENDC}")
            return False, "Package name is required"

        print(f"{Colors.OKBLUE}📦 Package: {package_name}{Colors.ENDC}")

        result = self.adb.shell_command(f'pm list packages | grep {package_name}')
        if not result.success or package_name not in result.output:
            print(f"{Colors.FAIL}❌ Package not found on device{Colors.ENDC}")
            return False, f"Package {package_name} not found"

        if not label:
            result = self.adb.shell_command(f'pm dump {package_name} | grep "labelRes="')
            if result.success and result.output:
                label = package_name.split('.')[-1].capitalize()
            else:
                label = package_name.split('.')[-1].capitalize()

        print(f"{Colors.OKBLUE}🏷️  Label: {label}{Colors.ENDC}")

        result = self.adb.shell_command(
            f'cmd package resolve-activity --brief {package_name} | tail -n 1'
        )

        if not result.success or not result.output:
            print(f"{Colors.FAIL}❌ Failed to resolve activity{Colors.ENDC}")
            return False, "Failed to resolve activity"

        activity = result.output.strip()
        if '/' not in activity:
            activity = f"{package_name}/.MainActivity"

        print(f"{Colors.OKBLUE}🎯 Activity: {activity}{Colors.ENDC}")

        intent_command = (
            f'am start -a android.intent.action.MAIN '
            f'-c android.intent.category.LAUNCHER '
            f'-n {activity}'
        )

        shortcut_command = (
            f'am broadcast -a com.android.launcher.action.INSTALL_SHORTCUT '
            f'--es "android.intent.extra.shortcut.NAME" "{label}" '
            f'--es "android.intent.extra.shortcut.INTENT" "{intent_command}"'
        )

        print(f"\n{Colors.OKBLUE}🔧 Creating launcher shortcut...{Colors.ENDC}")

        result = self.adb.shell_command(shortcut_command)

        if result.success:
            print(f"{Colors.OKGREEN}✅ Launcher icon created successfully{Colors.ENDC}")
            print(f"{Colors.OKGREEN}   Icon for '{label}' added to launcher{Colors.ENDC}")

            if self.logger:
                self.logger.log_event('generate_launcher_icon', f'Created icon for {package_name}')

            return True, f"Icon created for {label}"
        else:
            print(f"{Colors.WARNING}⚠️  Shortcut broadcast sent{Colors.ENDC}")
            print(f"{Colors.WARNING}   Note: Some launchers may not support shortcuts{Colors.ENDC}")
            print(f"{Colors.OKBLUE}   Alternative: Manually add app from app drawer{Colors.ENDC}")

            return True, "Shortcut broadcast sent (launcher support may vary)"

    def batch_generate_icons(self, packages: Optional[List[str]] = None) -> Tuple[bool, int, int]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🎨 Batch Icon Generation                       ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, 0, 0

        if packages is None:
            if not self.hidden_apps:
                print(f"{Colors.OKBLUE}🔍 Detecting hidden apps first...{Colors.ENDC}\n")
                success, hidden = self.detect_hidden_apps()
                if not success or not hidden:
                    print(f"{Colors.WARNING}⚠️  No hidden apps to process{Colors.ENDC}")
                    return True, 0, 0
                packages = hidden
            else:
                packages = self.hidden_apps

        if not packages:
            print(f"{Colors.WARNING}⚠️  No packages provided{Colors.ENDC}")
            return True, 0, 0

        print(f"{Colors.OKBLUE}📦 Processing {len(packages)} package(s)...{Colors.ENDC}\n")

        successful = 0
        failed = 0

        for idx, package in enumerate(packages, 1):
            print(f"{Colors.HEADER}[{idx}/{len(packages)}] {package}{Colors.ENDC}")

            success, message = self.generate_launcher_icon(package)

            if success:
                successful += 1
                print(f"{Colors.OKGREEN}✅ Success{Colors.ENDC}\n")
            else:
                failed += 1
                print(f"{Colors.FAIL}❌ Failed: {message}{Colors.ENDC}\n")

        print(f"{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📊 Batch Generation Summary                    ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKGREEN}✅ Successful: {successful}{Colors.ENDC}")
        print(f"{Colors.FAIL}❌ Failed: {failed}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}📊 Total: {len(packages)}{Colors.ENDC}\n")

        if self.logger:
            self.logger.log_event(
                'batch_generate_icons',
                f'Generated {successful} icons, {failed} failed'
            )

        return True, successful, failed

    def get_hidden_apps(self) -> List[str]:
        return self.hidden_apps.copy()

    def close(self):
        self.hidden_apps.clear()


def create_icon_generator(adb_manager: ADBManager, logger: Optional[Logger] = None) -> IconGenerator:
    return IconGenerator(adb_manager, logger)


def get_default_icon_generator(adb_manager: ADBManager) -> IconGenerator:
    from utils.logger import get_default_logger
    return IconGenerator(adb_manager, get_default_logger())
