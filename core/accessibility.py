from typing import Tuple, List, Optional
from core.adb_manager import ADBManager
from utils.logger import Logger
from utils.colors import Colors


class Accessibility:

    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None):
        self.adb = adb_manager
        self.logger = logger

    def enable_talkback(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🔊 Enable TalkBack                             ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        print(f"{Colors.OKBLUE}🔊 Enabling TalkBack...{Colors.ENDC}\n")

        result = self.adb.shell_command(
            'settings put secure enabled_accessibility_services com.google.android.marvin.talkback/.TalkBackService')

        if not result.success:
            print(f"{Colors.FAIL}❌ Failed to enable TalkBack{Colors.ENDC}")
            return False, "Failed to enable TalkBack"

        result = self.adb.shell_command('settings put secure accessibility_enabled 1')

        if result.success:
            print(f"{Colors.OKGREEN}✅ TalkBack enabled{Colors.ENDC}\n")

            if self.logger:
                self.logger.log_event('enable_talkback', 'TalkBack enabled')

            return True, "TalkBack enabled"
        else:
            print(f"{Colors.FAIL}❌ Failed to enable accessibility{Colors.ENDC}")
            return False, "Failed to enable accessibility"

    def disable_talkback(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🔇 Disable TalkBack                            ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        print(f"{Colors.OKBLUE}🔇 Disabling TalkBack...{Colors.ENDC}\n")

        result = self.adb.shell_command('settings put secure enabled_accessibility_services ""')

        if not result.success:
            print(f"{Colors.FAIL}❌ Failed to disable TalkBack{Colors.ENDC}")
            return False, "Failed to disable TalkBack"

        result = self.adb.shell_command('settings put secure accessibility_enabled 0')

        if result.success:
            print(f"{Colors.OKGREEN}✅ TalkBack disabled{Colors.ENDC}\n")

            if self.logger:
                self.logger.log_event('disable_talkback', 'TalkBack disabled')

            return True, "TalkBack disabled"
        else:
            print(f"{Colors.FAIL}❌ Failed to disable accessibility{Colors.ENDC}")
            return False, "Failed to disable accessibility"

    def configure_captions(self, enabled: bool, font_scale: float = 1.0) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📝 Configure Captions                          ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        enabled_val = '1' if enabled else '0'

        print(f"{Colors.OKBLUE}📝 {'Enabling' if enabled else 'Disabling'} captions...{Colors.ENDC}")

        result = self.adb.shell_command(f'settings put secure accessibility_captioning_enabled {enabled_val}')

        if not result.success:
            print(f"{Colors.FAIL}❌ Failed to configure captions{Colors.ENDC}")
            return False, "Failed to configure captions"

        if enabled and font_scale != 1.0:
            print(f"{Colors.OKBLUE}   Setting font scale to {font_scale}...{Colors.ENDC}")
            result = self.adb.shell_command(f'settings put secure accessibility_captioning_font_scale {font_scale}')

        print(f"{Colors.OKGREEN}✅ Captions configured{Colors.ENDC}\n")

        if self.logger:
            self.logger.log_event('configure_captions', f'Enabled: {enabled}, Scale: {font_scale}')

        return True, f"Captions {'enabled' if enabled else 'disabled'}"

    def enable_high_contrast(self, enabled: bool) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🎨 High Contrast Mode                          ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        enabled_val = '1' if enabled else '0'

        print(f"{Colors.OKBLUE}🎨 {'Enabling' if enabled else 'Disabling'} high contrast...{Colors.ENDC}\n")

        result = self.adb.shell_command(f'settings put secure high_text_contrast_enabled {enabled_val}')

        if result.success:
            print(f"{Colors.OKGREEN}✅ High contrast {'enabled' if enabled else 'disabled'}{Colors.ENDC}\n")

            if self.logger:
                self.logger.log_event('enable_high_contrast', f'Enabled: {enabled}')

            return True, f"High contrast {'enabled' if enabled else 'disabled'}"
        else:
            print(f"{Colors.FAIL}❌ Failed to configure high contrast{Colors.ENDC}")
            return False, "Failed to configure high contrast"

    def configure_color_correction(self, mode: int) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🌈 Color Correction                            ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        modes = {
            0: 'Disabled',
            11: 'Deuteranomaly (red-green)',
            12: 'Protanomaly (red-green)',
            13: 'Tritanomaly (blue-yellow)'
        }

        if mode not in modes:
            print(f"{Colors.FAIL}❌ Invalid mode: {mode}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}   Valid modes: 0 (Disabled), 11 (Deuteranomaly), 12 (Protanomaly), 13 (Tritanomaly){Colors.ENDC}\n")
            return False, f"Invalid mode: {mode}"

        print(f"{Colors.OKBLUE}🌈 Setting color correction to: {modes[mode]}{Colors.ENDC}\n")

        result = self.adb.shell_command(f'settings put secure accessibility_display_daltonizer {mode}')

        if not result.success:
            print(f"{Colors.FAIL}❌ Failed to set color correction{Colors.ENDC}")
            return False, "Failed to set color correction"

        enabled_val = '1' if mode != 0 else '0'
        result = self.adb.shell_command(f'settings put secure accessibility_display_daltonizer_enabled {enabled_val}')

        if result.success:
            print(f"{Colors.OKGREEN}✅ Color correction set to: {modes[mode]}{Colors.ENDC}\n")

            if self.logger:
                self.logger.log_event('configure_color_correction', f'Mode: {modes[mode]}')

            return True, f"Color correction: {modes[mode]}"
        else:
            print(f"{Colors.FAIL}❌ Failed to enable color correction{Colors.ENDC}")
            return False, "Failed to enable color correction"

    def enable_magnification(self, enabled: bool) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🔍 Magnification                               ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        enabled_val = '1' if enabled else '0'

        print(f"{Colors.OKBLUE}🔍 {'Enabling' if enabled else 'Disabling'} magnification...{Colors.ENDC}\n")

        result = self.adb.shell_command(
            f'settings put secure accessibility_display_magnification_enabled {enabled_val}')

        if result.success:
            print(f"{Colors.OKGREEN}✅ Magnification {'enabled' if enabled else 'disabled'}{Colors.ENDC}\n")

            if self.logger:
                self.logger.log_event('enable_magnification', f'Enabled: {enabled}')

            return True, f"Magnification {'enabled' if enabled else 'disabled'}"
        else:
            print(f"{Colors.FAIL}❌ Failed to configure magnification{Colors.ENDC}")
            return False, "Failed to configure magnification"

    def list_accessibility_services(self) -> Tuple[bool, List[str]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ♿ Accessibility Services                      ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, []

        result = self.adb.shell_command('settings get secure enabled_accessibility_services')

        if not result.success:
            print(f"{Colors.FAIL}❌ Failed to list services{Colors.ENDC}")
            return False, []

        services_str = result.output.strip()

        if not services_str or services_str == 'null':
            print(f"{Colors.WARNING}⚠️  No accessibility services enabled{Colors.ENDC}\n")
            return True, []

        services = [s.strip() for s in services_str.split(':') if s.strip()]

        print(f"{Colors.OKGREEN}✅ Found {len(services)} enabled service(s){Colors.ENDC}\n")

        for idx, service in enumerate(services, 1):
            print(f"{Colors.OKBLUE}   {idx}. {service}{Colors.ENDC}")

        print()

        if self.logger:
            self.logger.log_event('list_accessibility_services', f'Found {len(services)} services')

        return True, services

    def close(self):
        pass


def create_accessibility(adb_manager: ADBManager, logger: Optional[Logger] = None) -> Accessibility:
    return Accessibility(adb_manager, logger)


def get_default_accessibility(adb_manager: ADBManager) -> Accessibility:
    from utils.logger import get_default_logger
    return Accessibility(adb_manager, get_default_logger())
