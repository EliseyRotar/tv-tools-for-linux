from typing import Optional, Tuple
from core.adb_manager import ADBManager
from utils.logger import Logger
from utils.colors import Colors
from utils.ui_components import Emoji, BoxChars
from utils.error_handler import ErrorHandler


class SettingsManager:
    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None,
                 error_handler: Optional[ErrorHandler] = None):
        self.adb = adb_manager
        self.logger = logger
        self.error_handler = error_handler

        self.settings_map = {
            'gps_location': {
                'namespace': 'secure',
                'key': 'location_providers_allowed',
                'enable_value': 'gps,network',
                'disable_value': '',
                'display_name': 'GPS Location Services'
            },
            'screen_timeout': {
                'namespace': 'system',
                'key': 'screen_off_timeout',
                'display_name': 'Screen Timeout'
            },
            'auto_updates': {
                'namespace': 'global',
                'key': 'ota_disable_automatic_update',
                'enable_value': '0',
                'disable_value': '1',
                'display_name': 'Automatic System Updates'
            },
            'animation_scale_window': {
                'namespace': 'global',
                'key': 'window_animation_scale',
                'display_name': 'Window Animation Scale'
            },
            'animation_scale_transition': {
                'namespace': 'global',
                'key': 'transition_animation_scale',
                'display_name': 'Transition Animation Scale'
            },
            'animation_scale_animator': {
                'namespace': 'global',
                'key': 'animator_duration_scale',
                'display_name': 'Animator Duration Scale'
            },
            'usb_debugging': {
                'namespace': 'global',
                'key': 'adb_enabled',
                'enable_value': '1',
                'disable_value': '0',
                'display_name': 'USB Debugging'
            },
            'adb_network': {
                'namespace': 'global',
                'key': 'adb_wifi_enabled',
                'enable_value': '1',
                'disable_value': '0',
                'display_name': 'ADB over Network'
            },
            'stay_awake': {
                'namespace': 'global',
                'key': 'stay_on_while_plugged_in',
                'enable_value': '7',
                'disable_value': '0',
                'display_name': 'Stay Awake While Charging'
            },
            'unknown_sources': {
                'namespace': 'secure',
                'key': 'install_non_market_apps',
                'enable_value': '1',
                'disable_value': '0',
                'display_name': 'Unknown Sources Installation'
            },
            'autofill_service': {
                'namespace': 'secure',
                'key': 'autofill_service',
                'display_name': 'Auto-fill Service'
            },
            'usage_access': {
                'namespace': 'secure',
                'key': 'enabled_accessibility_services',
                'display_name': 'Usage Access'
            }
        }

    def get_setting(self, setting_name: str) -> Tuple[bool, Optional[str], str]:
        if setting_name not in self.settings_map:
            error_msg = f'Unknown setting: {setting_name}'
            if self.logger:
                self.logger.error(error_msg)
            return False, None, error_msg

        setting_info = self.settings_map[setting_name]
        namespace = setting_info['namespace']
        key = setting_info['key']

        result = self.adb.shell_command(f'settings get {namespace} {key}')

        if result.success:
            value = result.output.strip()
            if value == 'null' or value == '':
                value = None

            if self.logger:
                self.logger.debug(f'Retrieved setting {setting_name}: {value}')

            return True, value, ''
        else:
            error_msg = result.error if result.error else 'Failed to retrieve setting'
            if self.logger:
                self.logger.error(f'Failed to get setting {setting_name}', {'error': error_msg})
            return False, None, error_msg

    def set_setting(self, setting_name: str, value: str) -> Tuple[bool, str]:
        if setting_name not in self.settings_map:
            error_msg = f'Unknown setting: {setting_name}'
            if self.logger:
                self.logger.error(error_msg)
            return False, error_msg

        setting_info = self.settings_map[setting_name]
        namespace = setting_info['namespace']
        key = setting_info['key']

        if not self._validate_setting_value(setting_name, value):
            error_msg = f'Invalid value for {setting_name}: {value}'
            if self.logger:
                self.logger.error(error_msg)
            return False, error_msg

        result = self.adb.shell_command(f'settings put {namespace} {key} {value}')

        if result.success or result.return_code == 0:
            if self.logger:
                self.logger.info(f'Set setting {setting_name} to {value}')
            return True, f'Successfully set {setting_info["display_name"]} to {value}'
        else:
            error_msg = result.error if result.error else 'Failed to set setting'
            if self.logger:
                self.logger.error(f'Failed to set setting {setting_name}', {'error': error_msg})
            return False, error_msg

    def _validate_setting_value(self, setting_name: str, value: str) -> bool:
        if setting_name == 'screen_timeout':
            try:
                timeout_ms = int(value)
                return 0 <= timeout_ms <= 2147483647
            except ValueError:
                return False

        if setting_name.startswith('animation_scale'):
            try:
                scale = float(value)
                return 0.0 <= scale <= 10.0
            except ValueError:
                return False

        return True

    def enable_gps_location(self) -> Tuple[bool, str]:
        success, current_value, error = self.get_setting('gps_location')

        if not success:
            return False, f'Failed to check current GPS status: {error}'

        print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current GPS Location: {current_value or "Disabled"}{Colors.ENDC}')

        enable_value = self.settings_map['gps_location']['enable_value']
        success, message = self.set_setting('gps_location', enable_value)

        if success:
            success_new, new_value, _ = self.get_setting('gps_location')
            if success_new:
                print(f'{Colors.OKGREEN}{Emoji.CHECK} New GPS Location: {new_value}{Colors.ENDC}\n')
            return True, 'GPS Location Services enabled'
        else:
            return False, message

    def disable_gps_location(self) -> Tuple[bool, str]:
        success, current_value, error = self.get_setting('gps_location')

        if not success:
            return False, f'Failed to check current GPS status: {error}'

        print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current GPS Location: {current_value or "Disabled"}{Colors.ENDC}')

        disable_value = self.settings_map['gps_location']['disable_value']
        success, message = self.set_setting('gps_location', disable_value)

        if success:
            success_new, new_value, _ = self.get_setting('gps_location')
            if success_new:
                print(f'{Colors.OKGREEN}{Emoji.CHECK} New GPS Location: {new_value or "Disabled"}{Colors.ENDC}\n')
            return True, 'GPS Location Services disabled'
        else:
            return False, message

    def set_screen_timeout(self, timeout_seconds: int) -> Tuple[bool, str]:
        timeout_ms = timeout_seconds * 1000

        success, current_value, error = self.get_setting('screen_timeout')

        if success and current_value:
            try:
                current_seconds = int(current_value) // 1000
                print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current Screen Timeout: {current_seconds} seconds{Colors.ENDC}')
            except ValueError:
                print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current Screen Timeout: {current_value}{Colors.ENDC}')

        success, message = self.set_setting('screen_timeout', str(timeout_ms))

        if success:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} New Screen Timeout: {timeout_seconds} seconds{Colors.ENDC}\n')
            return True, f'Screen timeout set to {timeout_seconds} seconds'
        else:
            return False, message

    def enable_auto_updates(self) -> Tuple[bool, str]:
        success, current_value, error = self.get_setting('auto_updates')

        if success:
            is_enabled = current_value == '0' or current_value is None
            status = 'Enabled' if is_enabled else 'Disabled'
            print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current Auto Updates: {status}{Colors.ENDC}')

        enable_value = self.settings_map['auto_updates']['enable_value']
        success, message = self.set_setting('auto_updates', enable_value)

        if success:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} New Auto Updates: Enabled{Colors.ENDC}\n')
            return True, 'Automatic system updates enabled'
        else:
            return False, message

    def disable_auto_updates(self) -> Tuple[bool, str]:
        success, current_value, error = self.get_setting('auto_updates')

        if success:
            is_enabled = current_value == '0' or current_value is None
            status = 'Enabled' if is_enabled else 'Disabled'
            print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current Auto Updates: {status}{Colors.ENDC}')

        disable_value = self.settings_map['auto_updates']['disable_value']
        success, message = self.set_setting('auto_updates', disable_value)

        if success:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} New Auto Updates: Disabled{Colors.ENDC}\n')
            return True, 'Automatic system updates disabled'
        else:
            return False, message

    def set_animation_scale(self, scale: float, animation_type: str = 'all') -> Tuple[bool, str]:
        if animation_type not in ['all', 'window', 'transition', 'animator']:
            return False, f'Invalid animation type: {animation_type}'

        if not (0.0 <= scale <= 10.0):
            return False, 'Animation scale must be between 0.0 and 10.0'

        scale_str = str(scale)
        results = []

        if animation_type == 'all' or animation_type == 'window':
            success, current, _ = self.get_setting('animation_scale_window')
            if success:
                print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current Window Animation Scale: {current or "1.0"}{Colors.ENDC}')

            success, message = self.set_setting('animation_scale_window', scale_str)
            results.append(('Window', success, message))

            if success:
                print(f'{Colors.OKGREEN}{Emoji.CHECK} New Window Animation Scale: {scale}{Colors.ENDC}')

        if animation_type == 'all' or animation_type == 'transition':
            success, current, _ = self.get_setting('animation_scale_transition')
            if success and animation_type != 'all':
                print(
                    f'\n{
                        Colors.OKCYAN}{
                        Emoji.INFO} Current Transition Animation Scale: {
                        current or "1.0"}{
                        Colors.ENDC}')

            success, message = self.set_setting('animation_scale_transition', scale_str)
            results.append(('Transition', success, message))

            if success:
                print(f'{Colors.OKGREEN}{Emoji.CHECK} New Transition Animation Scale: {scale}{Colors.ENDC}')

        if animation_type == 'all' or animation_type == 'animator':
            success, current, _ = self.get_setting('animation_scale_animator')
            if success and animation_type != 'all':
                print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current Animator Duration Scale: {current or "1.0"}{Colors.ENDC}')

            success, message = self.set_setting('animation_scale_animator', scale_str)
            results.append(('Animator', success, message))

            if success:
                print(f'{Colors.OKGREEN}{Emoji.CHECK} New Animator Duration Scale: {scale}{Colors.ENDC}\n')

        all_success = all(r[1] for r in results)

        if all_success:
            return True, f'Animation scale set to {scale}'
        else:
            failed = [r[0] for r in results if not r[1]]
            return False, f'Failed to set animation scale for: {", ".join(failed)}'

    def enable_usb_debugging(self) -> Tuple[bool, str]:
        success, current_value, error = self.get_setting('usb_debugging')

        if success:
            is_enabled = current_value == '1'
            status = 'Enabled' if is_enabled else 'Disabled'
            print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current USB Debugging: {status}{Colors.ENDC}')

        enable_value = self.settings_map['usb_debugging']['enable_value']
        success, message = self.set_setting('usb_debugging', enable_value)

        if success:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} New USB Debugging: Enabled{Colors.ENDC}\n')
            return True, 'USB Debugging enabled'
        else:
            return False, message

    def disable_usb_debugging(self) -> Tuple[bool, str]:
        success, current_value, error = self.get_setting('usb_debugging')

        if success:
            is_enabled = current_value == '1'
            status = 'Enabled' if is_enabled else 'Disabled'
            print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current USB Debugging: {status}{Colors.ENDC}')

        disable_value = self.settings_map['usb_debugging']['disable_value']
        success, message = self.set_setting('usb_debugging', disable_value)

        if success:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} New USB Debugging: Disabled{Colors.ENDC}\n')
            return True, 'USB Debugging disabled'
        else:
            return False, message

    def enable_adb_network(self) -> Tuple[bool, str]:
        success, current_value, error = self.get_setting('adb_network')

        if success:
            is_enabled = current_value == '1'
            status = 'Enabled' if is_enabled else 'Disabled'
            print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current ADB over Network: {status}{Colors.ENDC}')

        enable_value = self.settings_map['adb_network']['enable_value']
        success, message = self.set_setting('adb_network', enable_value)

        if success:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} New ADB over Network: Enabled{Colors.ENDC}\n')
            return True, 'ADB over Network enabled'
        else:
            return False, message

    def disable_adb_network(self) -> Tuple[bool, str]:
        success, current_value, error = self.get_setting('adb_network')

        if success:
            is_enabled = current_value == '1'
            status = 'Enabled' if is_enabled else 'Disabled'
            print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current ADB over Network: {status}{Colors.ENDC}')

        disable_value = self.settings_map['adb_network']['disable_value']
        success, message = self.set_setting('adb_network', disable_value)

        if success:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} New ADB over Network: Disabled{Colors.ENDC}\n')
            return True, 'ADB over Network disabled'
        else:
            return False, message

    def enable_stay_awake(self) -> Tuple[bool, str]:
        success, current_value, error = self.get_setting('stay_awake')

        if success:
            is_enabled = current_value == '7' or current_value == '3'
            status = 'Enabled' if is_enabled else 'Disabled'
            print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current Stay Awake While Charging: {status}{Colors.ENDC}')

        enable_value = self.settings_map['stay_awake']['enable_value']
        success, message = self.set_setting('stay_awake', enable_value)

        if success:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} New Stay Awake While Charging: Enabled{Colors.ENDC}\n')
            return True, 'Stay Awake While Charging enabled'
        else:
            return False, message

    def disable_stay_awake(self) -> Tuple[bool, str]:
        success, current_value, error = self.get_setting('stay_awake')

        if success:
            is_enabled = current_value == '7' or current_value == '3'
            status = 'Enabled' if is_enabled else 'Disabled'
            print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current Stay Awake While Charging: {status}{Colors.ENDC}')

        disable_value = self.settings_map['stay_awake']['disable_value']
        success, message = self.set_setting('stay_awake', disable_value)

        if success:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} New Stay Awake While Charging: Disabled{Colors.ENDC}\n')
            return True, 'Stay Awake While Charging disabled'
        else:
            return False, message

    def enable_unknown_sources(self) -> Tuple[bool, str]:
        success, current_value, error = self.get_setting('unknown_sources')

        if success:
            is_enabled = current_value == '1'
            status = 'Enabled' if is_enabled else 'Disabled'
            print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current Unknown Sources: {status}{Colors.ENDC}')

        enable_value = self.settings_map['unknown_sources']['enable_value']
        success, message = self.set_setting('unknown_sources', enable_value)

        if success:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} New Unknown Sources: Enabled{Colors.ENDC}\n')
            return True, 'Unknown Sources Installation enabled'
        else:
            return False, message

    def disable_unknown_sources(self) -> Tuple[bool, str]:
        success, current_value, error = self.get_setting('unknown_sources')

        if success:
            is_enabled = current_value == '1'
            status = 'Enabled' if is_enabled else 'Disabled'
            print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current Unknown Sources: {status}{Colors.ENDC}')

        disable_value = self.settings_map['unknown_sources']['disable_value']
        success, message = self.set_setting('unknown_sources', disable_value)

        if success:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} New Unknown Sources: Disabled{Colors.ENDC}\n')
            return True, 'Unknown Sources Installation disabled'
        else:
            return False, message

    def get_autofill_service(self) -> Tuple[bool, Optional[str], str]:
        success, value, error = self.get_setting('autofill_service')

        if success:
            service_name = value if value else 'None'
            print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current Auto-fill Service: {service_name}{Colors.ENDC}\n')
            return True, value, ''
        else:
            return False, None, error

    def set_autofill_service(self, service_component: str) -> Tuple[bool, str]:
        success, current_value, error = self.get_setting('autofill_service')

        if success:
            service_name = current_value if current_value else 'None'
            print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current Auto-fill Service: {service_name}{Colors.ENDC}')

        success, message = self.set_setting('autofill_service', service_component)

        if success:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} New Auto-fill Service: {service_component}{Colors.ENDC}\n')
            return True, f'Auto-fill service set to {service_component}'
        else:
            return False, message

    def disable_autofill_service(self) -> Tuple[bool, str]:
        success, current_value, error = self.get_setting('autofill_service')

        if success:
            service_name = current_value if current_value else 'None'
            print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current Auto-fill Service: {service_name}{Colors.ENDC}')

        success, message = self.set_setting('autofill_service', 'null')

        if success:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} Auto-fill Service Disabled{Colors.ENDC}\n')
            return True, 'Auto-fill service disabled'
        else:
            return False, message

    def list_packages_with_usage_access(self) -> Tuple[bool, list, str]:
        result = self.adb.shell_command('appops query-op USAGE_STATS allow')

        if result.success:
            packages = []
            lines = result.output.strip().split('\n')
            for line in lines:
                if line.strip():
                    packages.append(line.strip())

            if packages:
                print(f'\n{Colors.OKCYAN}{Emoji.INFO} Packages with Usage Access:{Colors.ENDC}')
                for pkg in packages:
                    print(f'  {Colors.OKBLUE}• {pkg}{Colors.ENDC}')
                print()
            else:
                print(f'\n{Colors.WARNING}{Emoji.WARNING} No packages have usage access{Colors.ENDC}\n')

            return True, packages, ''
        else:
            error_msg = result.error if result.error else 'Failed to list packages with usage access'
            return False, [], error_msg

    def grant_usage_access(self, package_name: str) -> Tuple[bool, str]:
        result = self.adb.shell_command(f'appops set {package_name} USAGE_STATS allow')

        if result.success or result.return_code == 0:
            if self.logger:
                self.logger.info(f'Granted usage access to {package_name}')

            print(f'{Colors.OKGREEN}{Emoji.CHECK} Usage access granted to {package_name}{Colors.ENDC}\n')
            return True, f'Usage access granted to {package_name}'
        else:
            error_msg = result.error if result.error else 'Failed to grant usage access'
            if self.logger:
                self.logger.error(f'Failed to grant usage access to {package_name}', {'error': error_msg})
            return False, error_msg

    def revoke_usage_access(self, package_name: str) -> Tuple[bool, str]:
        result = self.adb.shell_command(f'appops set {package_name} USAGE_STATS deny')

        if result.success or result.return_code == 0:
            if self.logger:
                self.logger.info(f'Revoked usage access from {package_name}')

            print(f'{Colors.OKGREEN}{Emoji.CHECK} Usage access revoked from {package_name}{Colors.ENDC}\n')
            return True, f'Usage access revoked from {package_name}'
        else:
            error_msg = result.error if result.error else 'Failed to revoke usage access'
            if self.logger:
                self.logger.error(f'Failed to revoke usage access from {package_name}', {'error': error_msg})
            return False, error_msg

    def get_density(self) -> Tuple[bool, Optional[int], str]:
        result = self.adb.shell_command('wm density')

        if result.success:
            output = result.output.strip()

            import re
            match = re.search(r'Physical density: (\d+)', output)
            if match:
                density = int(match.group(1))
                if self.logger:
                    self.logger.debug(f'Retrieved screen density: {density}')
                return True, density, ''

            match = re.search(r'Override density: (\d+)', output)
            if match:
                density = int(match.group(1))
                if self.logger:
                    self.logger.debug(f'Retrieved override screen density: {density}')
                return True, density, ''

            try:
                density = int(output)
                return True, density, ''
            except ValueError:
                pass

            return False, None, 'Could not parse density value'
        else:
            error_msg = result.error if result.error else 'Failed to retrieve density'
            if self.logger:
                self.logger.error('Failed to get screen density', {'error': error_msg})
            return False, None, error_msg

    def set_density(self, dpi: int) -> Tuple[bool, str]:
        if not self._validate_density(dpi):
            error_msg = f'Invalid DPI value: {dpi}. Must be between 120 and 640.'
            if self.logger:
                self.logger.error(error_msg)
            return False, error_msg

        success, current_density, error = self.get_density()

        if success and current_density:
            print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current Screen Density: {current_density} DPI{Colors.ENDC}')

        result = self.adb.shell_command(f'wm density {dpi}')

        if result.success or result.return_code == 0:
            if self.logger:
                self.logger.info(f'Set screen density to {dpi} DPI')

            print(f'{Colors.OKGREEN}{Emoji.CHECK} New Screen Density: {dpi} DPI{Colors.ENDC}\n')
            print(f'{Colors.WARNING}{Emoji.WARNING} Note: You may need to restart the device for changes to take full effect{Colors.ENDC}\n')

            return True, f'Screen density set to {dpi} DPI'
        else:
            error_msg = result.error if result.error else 'Failed to set density'
            if self.logger:
                self.logger.error('Failed to set screen density', {'error': error_msg})
            return False, error_msg

    def reset_density(self) -> Tuple[bool, str]:
        success, current_density, error = self.get_density()

        if success and current_density:
            print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current Screen Density: {current_density} DPI{Colors.ENDC}')

        result = self.adb.shell_command('wm density reset')

        if result.success or result.return_code == 0:
            if self.logger:
                self.logger.info('Reset screen density to default')

            success_new, new_density, _ = self.get_density()
            if success_new and new_density:
                print(f'{Colors.OKGREEN}{Emoji.CHECK} Screen Density Reset to Default: {new_density} DPI{Colors.ENDC}\n')
            else:
                print(f'{Colors.OKGREEN}{Emoji.CHECK} Screen Density Reset to Default{Colors.ENDC}\n')

            return True, 'Screen density reset to default'
        else:
            error_msg = result.error if result.error else 'Failed to reset density'
            if self.logger:
                self.logger.error('Failed to reset screen density', {'error': error_msg})
            return False, error_msg

    def _validate_density(self, dpi: int) -> bool:
        return 120 <= dpi <= 640

    def get_font_size(self) -> Tuple[bool, Optional[float], str]:
        result = self.adb.shell_command('settings get system font_scale')

        if result.success:
            value = result.output.strip()

            if value == 'null' or value == '':
                if self.logger:
                    self.logger.debug('Font size is default (1.0)')
                return True, 1.0, ''

            try:
                font_scale = float(value)
                if self.logger:
                    self.logger.debug(f'Retrieved font size: {font_scale}')
                return True, font_scale, ''
            except ValueError:
                return False, None, f'Could not parse font size value: {value}'
        else:
            error_msg = result.error if result.error else 'Failed to retrieve font size'
            if self.logger:
                self.logger.error('Failed to get font size', {'error': error_msg})
            return False, None, error_msg

    def set_font_size(self, scale: float) -> Tuple[bool, str]:
        if not self._validate_font_size(scale):
            error_msg = f'Invalid font size scale: {scale}. Must be between 0.5 and 2.0.'
            if self.logger:
                self.logger.error(error_msg)
            return False, error_msg

        success, current_scale, error = self.get_font_size()

        if success and current_scale:
            size_name = self._get_font_size_name(current_scale)
            print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current Font Size: {current_scale} ({size_name}){Colors.ENDC}')

        result = self.adb.shell_command(f'settings put system font_scale {scale}')

        if result.success or result.return_code == 0:
            if self.logger:
                self.logger.info(f'Set font size to {scale}')

            size_name = self._get_font_size_name(scale)
            print(f'{Colors.OKGREEN}{Emoji.CHECK} New Font Size: {scale} ({size_name}){Colors.ENDC}\n')

            return True, f'Font size set to {scale} ({size_name})'
        else:
            error_msg = result.error if result.error else 'Failed to set font size'
            if self.logger:
                self.logger.error('Failed to set font size', {'error': error_msg})
            return False, error_msg

    def reset_font_size(self) -> Tuple[bool, str]:
        success, current_scale, error = self.get_font_size()

        if success and current_scale:
            size_name = self._get_font_size_name(current_scale)
            print(f'\n{Colors.OKCYAN}{Emoji.INFO} Current Font Size: {current_scale} ({size_name}){Colors.ENDC}')

        result = self.adb.shell_command('settings delete system font_scale')

        if result.success or result.return_code == 0:
            if self.logger:
                self.logger.info('Reset font size to default')

            print(f'{Colors.OKGREEN}{Emoji.CHECK} Font Size Reset to Default (1.0 - Normal){Colors.ENDC}\n')

            return True, 'Font size reset to default'
        else:
            error_msg = result.error if result.error else 'Failed to reset font size'
            if self.logger:
                self.logger.error('Failed to reset font size', {'error': error_msg})
            return False, error_msg

    def _validate_font_size(self, scale: float) -> bool:
        return 0.5 <= scale <= 2.0

    def _get_font_size_name(self, scale: float) -> str:
        if scale <= 0.85:
            return 'Small'
        elif scale <= 1.15:
            return 'Normal'
        elif scale <= 1.45:
            return 'Large'
        else:
            return 'Huge'

    def display_all_settings(self):
        print(f'\n{Colors.HEADER}{BoxChars.TOP_LEFT}{BoxChars.HORIZONTAL * 78}{BoxChars.TOP_RIGHT}{Colors.ENDC}')
        print(
            f'{
                Colors.HEADER}{
                BoxChars.VERTICAL}{
                Colors.ENDC} {
                    Colors.BOLD}{
                        Emoji.GEAR} Available Custom Settings{
                            Colors.ENDC}' + ' ' * 48 + f'{
                                Colors.HEADER}{
                                    BoxChars.VERTICAL}{
                                        Colors.ENDC}')
        print(f'{Colors.HEADER}{BoxChars.BOTTOM_LEFT}{BoxChars.HORIZONTAL * 78}{BoxChars.BOTTOM_RIGHT}{Colors.ENDC}\n')

        settings_list = [
            ('1', 'GPS Location Services', 'Enable/Disable'),
            ('2', 'Screen Timeout', 'Configure duration'),
            ('3', 'Automatic System Updates', 'Enable/Disable'),
            ('4', 'Animation Scale', 'Configure scale (0.0-10.0)'),
            ('5', 'USB Debugging', 'Enable/Disable'),
            ('6', 'ADB over Network', 'Enable/Disable'),
            ('7', 'Stay Awake While Charging', 'Enable/Disable'),
            ('8', 'Unknown Sources Installation', 'Enable/Disable'),
            ('9', 'Auto-fill Services', 'Configure/Disable'),
            ('10', 'Usage Access', 'Grant/Revoke for packages'),
            ('11', 'Screen Density', 'Configure DPI (120-640)'),
            ('12', 'Font Size', 'Configure scale (0.5-2.0)')
        ]

        for num, name, description in settings_list:
            print(f'{Colors.OKCYAN}{num:>2}. {Colors.ENDC}{Colors.BOLD}{name}{Colors.ENDC}')
            print(f'    {Colors.OKBLUE}{description}{Colors.ENDC}\n')
