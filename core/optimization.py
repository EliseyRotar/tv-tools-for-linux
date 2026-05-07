from typing import Tuple, Optional, Dict, List
from core.adb_manager import ADBManager
from utils.logger import Logger
from utils.colors import Colors


class OptimizationModule:

    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None):
        self.adb = adb_manager
        self.logger = logger
        self.optimization_history = []

    def disable_animations(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ⚡ Disabling Animations                        ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        animations = [
            ('window_animation_scale', 'Window animation'),
            ('transition_animation_scale', 'Transition animation'),
            ('animator_duration_scale', 'Animator duration')
        ]

        success_count = 0
        for setting, name in animations:
            result = self.adb.shell_command(f'settings put global {setting} 0')
            if result.success:
                print(f"{Colors.OKGREEN}✅ Disabled {name}{Colors.ENDC}")
                success_count += 1
            else:
                print(f"{Colors.FAIL}❌ Failed to disable {name}{Colors.ENDC}")

        if success_count == len(animations):
            self.optimization_history.append('disable_animations')
            if self.logger:
                self.logger.log_event('optimization', 'Disabled all animations')
            return True, "All animations disabled successfully"
        else:
            return False, f"Only {success_count}/{len(animations)} animations disabled"

    def enable_animations(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🎬 Enabling Animations                         ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        animations = [
            ('window_animation_scale', 'Window animation', '1'),
            ('transition_animation_scale', 'Transition animation', '1'),
            ('animator_duration_scale', 'Animator duration', '1')
        ]

        success_count = 0
        for setting, name, value in animations:
            result = self.adb.shell_command(f'settings put global {setting} {value}')
            if result.success:
                print(f"{Colors.OKGREEN}✅ Enabled {name}{Colors.ENDC}")
                success_count += 1
            else:
                print(f"{Colors.FAIL}❌ Failed to enable {name}{Colors.ENDC}")

        if success_count == len(animations):
            if self.logger:
                self.logger.log_event('optimization', 'Enabled all animations')
            return True, "All animations enabled successfully"
        else:
            return False, f"Only {success_count}/{len(animations)} animations enabled"

    def clear_app_cache(self, package_name: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🧹 Clearing App Cache                          ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  Package: {package_name}{Colors.ENDC}\n")

        result = self.adb.shell_command(f'pm clear {package_name}')

        if result.success and 'Success' in result.output:
            print(f"{Colors.OKGREEN}✅ Cache cleared for {package_name}{Colors.ENDC}")
            if self.logger:
                self.logger.log_event('optimization', f'Cleared cache for {package_name}')
            return True, f"Cache cleared for {package_name}"
        else:
            print(f"{Colors.FAIL}❌ Failed to clear cache{Colors.ENDC}")
            return False, f"Failed to clear cache: {result.error}"

    def clear_all_app_caches(self) -> Tuple[bool, str, Dict[str, int]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🧹 Clearing All App Caches                     ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.WARNING}⚠️  This will clear cache for all user apps{Colors.ENDC}\n")

        result = self.adb.shell_command('pm list packages -3')
        if not result.success:
            return False, "Failed to list packages", {'success': 0, 'failed': 0}

        packages = [line.replace('package:', '').strip()
                    for line in result.output.split('\n') if line.startswith('package:')]

        success_count = 0
        failed_count = 0

        for i, package in enumerate(packages, 1):
            print(f"{Colors.OKBLUE}[{i}/{len(packages)}] Clearing {package}...{Colors.ENDC}")
            clear_result = self.adb.shell_command(f'pm clear {package}')

            if clear_result.success and 'Success' in clear_result.output:
                success_count += 1
            else:
                failed_count += 1

        print(f"\n{Colors.OKGREEN}✅ Cleared cache for {success_count} apps{Colors.ENDC}")
        if failed_count > 0:
            print(f"{Colors.WARNING}⚠️  Failed for {failed_count} apps{Colors.ENDC}")

        self.optimization_history.append('clear_all_caches')
        if self.logger:
            self.logger.log_event('optimization', f'Cleared cache for {success_count} apps')

        return True, f"Cleared cache for {success_count}/{len(packages)} apps", {
            'success': success_count,
            'failed': failed_count
        }

    def clear_system_cache(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🧹 Clearing System Cache                       ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        commands = [
            ('rm -rf /data/dalvik-cache/*', 'Dalvik cache'),
            ('rm -rf /cache/*', 'System cache')
        ]

        success_count = 0
        for cmd, name in commands:
            result = self.adb.shell_command(cmd)
            if result.success or result.return_code == 0:
                print(f"{Colors.OKGREEN}✅ Cleared {name}{Colors.ENDC}")
                success_count += 1
            else:
                print(f"{Colors.WARNING}⚠️  Could not clear {name} (may require root){Colors.ENDC}")

        if success_count > 0:
            self.optimization_history.append('clear_system_cache')
            if self.logger:
                self.logger.log_event('optimization', 'Cleared system cache')
            return True, f"Cleared {success_count} system cache locations"
        else:
            return False, "Failed to clear system cache (may require root)"

    def force_stop_apps(self, package_names: Optional[List[str]] = None) -> Tuple[bool, str, Dict[str, int]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🛑 Force Stopping Apps                         ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if package_names is None:
            result = self.adb.shell_command('pm list packages -3')
            if not result.success:
                return False, "Failed to list packages", {'success': 0, 'failed': 0}

            package_names = [line.replace('package:', '').strip()
                             for line in result.output.split('\n') if line.startswith('package:')]

        success_count = 0
        failed_count = 0

        for i, package in enumerate(package_names, 1):
            print(f"{Colors.OKBLUE}[{i}/{len(package_names)}] Stopping {package}...{Colors.ENDC}")
            stop_result = self.adb.shell_command(f'am force-stop {package}')

            if stop_result.success or stop_result.return_code == 0:
                success_count += 1
            else:
                failed_count += 1

        print(f"\n{Colors.OKGREEN}✅ Stopped {success_count} apps{Colors.ENDC}")
        if failed_count > 0:
            print(f"{Colors.WARNING}⚠️  Failed to stop {failed_count} apps{Colors.ENDC}")

        self.optimization_history.append('force_stop_apps')
        if self.logger:
            self.logger.log_event('optimization', f'Force stopped {success_count} apps')

        return True, f"Stopped {success_count}/{len(package_names)} apps", {
            'success': success_count,
            'failed': failed_count
        }

    def disable_unused_services(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ⚙️  Disabling Unused Services                  ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        services_to_disable = [
            'com.google.android.gms/.stats.service.DropBoxEntryAddedService',
            'com.google.android.gms/.gcm.nts.TaskExecutionService',
            'com.google.android.gms/.analytics.service.AnalyticsService'
        ]

        success_count = 0
        for service in services_to_disable:
            result = self.adb.shell_command(f'pm disable {service}')
            if result.success or 'disabled' in result.output.lower():
                print(f"{Colors.OKGREEN}✅ Disabled {service.split('/')[-1]}{Colors.ENDC}")
                success_count += 1
            else:
                print(f"{Colors.WARNING}⚠️  Could not disable {service.split('/')[-1]}{Colors.ENDC}")

        if success_count > 0:
            self.optimization_history.append('disable_services')
            if self.logger:
                self.logger.log_event('optimization', f'Disabled {success_count} services')
            return True, f"Disabled {success_count} services"
        else:
            return False, "No services were disabled"

    def get_memory_usage(self) -> Tuple[bool, Dict[str, str]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📊 Memory Usage Information                    ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        result = self.adb.shell_command('dumpsys meminfo')

        if not result.success:
            return False, {}

        memory_info = {}
        lines = result.output.split('\n')

        for line in lines:
            if 'Total RAM:' in line:
                memory_info['total_ram'] = line.split(':')[1].strip()
            elif 'Free RAM:' in line:
                memory_info['free_ram'] = line.split(':')[1].strip()
            elif 'Used RAM:' in line:
                memory_info['used_ram'] = line.split(':')[1].strip()
            elif 'Lost RAM:' in line:
                memory_info['lost_ram'] = line.split(':')[1].strip()

        for key, value in memory_info.items():
            label = key.replace('_', ' ').title()
            print(f"{Colors.OKBLUE}{label}: {Colors.ENDC}{value}")

        return True, memory_info

    def get_optimization_history(self) -> List[str]:
        return self.optimization_history.copy()

    def revert_optimizations(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ↩️  Reverting Optimizations                    ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.optimization_history:
            print(f"{Colors.WARNING}⚠️  No optimizations to revert{Colors.ENDC}")
            return False, "No optimizations to revert"

        reverted = []

        if 'disable_animations' in self.optimization_history:
            success, _ = self.enable_animations()
            if success:
                reverted.append('animations')

        if reverted:
            self.optimization_history.clear()
            if self.logger:
                self.logger.log_event('optimization', f'Reverted optimizations: {", ".join(reverted)}')
            return True, f"Reverted: {', '.join(reverted)}"
        else:
            return False, "No optimizations could be reverted"

    def close(self):
        pass


def create_optimization_module(adb_manager: ADBManager, logger: Optional[Logger] = None) -> OptimizationModule:
    return OptimizationModule(adb_manager, logger)


def get_default_optimization_module(adb_manager: ADBManager) -> OptimizationModule:
    from utils.logger import get_default_logger
    return OptimizationModule(adb_manager, get_default_logger())
