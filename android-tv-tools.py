#!/usr/bin/env python3

import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.ui_manager import UIManager
from core.config_manager import ConfigManager
from core.adb_manager import ADBManager
from core.menu_system import MenuSystem
from core.menu_handlers import register_all_handlers
from utils.distro_detector import DistroDetector
from utils.logger import Logger
from utils.colors import Colors


VERSION = "1.0"
APP_NAME = "TV Tools for Linux"
AUTHOR = "@eli6"
GITHUB = "https://github.com/EliseyRotar"


class AndroidTVTools:
    def __init__(self):
        self.ui = UIManager()
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()
        self.adb = ADBManager(default_timeout=self.config.default_timeout)
        self.distro = DistroDetector()
        self.logger = Logger()
        self.connected_device_info = None
        self.menu_system = None

    def display_header(self):
        title = f'TV Tools for Linux v{VERSION}'
        device_info = None

        if self.connected_device_info:
            device_info = self.connected_device_info

        self.ui.print_header(
            title=title,
            author=AUTHOR,
            github=GITHUB,
            device_info=device_info
        )

    def check_internet_connectivity(self) -> bool:
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '3', 'google.com'],
                capture_output=True,
                timeout=3
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, OSError):
            return False

    def check_and_install_adb(self) -> bool:
        if self.adb.check_adb_installed():
            version = self.adb.get_adb_version()
            if version:
                self.ui.print_success(f'ADB found: version {version}')
                self.logger.info(f'ADB version {version} detected')
            else:
                self.ui.print_success('ADB is installed')
            return True

        self.ui.print_warning('ADB is not installed')
        self.logger.warning('ADB not found on system')

        if self.ui.confirm('Do you want to install ADB?', default=True):
            self.ui.print_info('Installing ADB...')
            success, message = self.distro.install_dependency('adb')

            if success:
                self.ui.print_success(message)
                self.logger.info('ADB installed successfully')
                self.adb.adb_path = self.adb._find_adb_path()
                return True
            else:
                self.ui.print_error(message)
                self.logger.error(f'ADB installation failed: {message}')
                self.ui.print_info(self.distro.get_manual_install_instructions('adb'))
                return False
        else:
            self.ui.print_error('ADB is required to use TV Tools for Linux')
            self.logger.warning('User declined ADB installation')
            return False

    def _detect_already_connected_device(self):
        """Check if ADB already has a connected device and populate device info."""
        if not self.adb.check_adb_installed():
            return

        try:
            result = subprocess.run(
                [self.adb.adb_path, 'devices', '-l'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                return

            lines = result.stdout.strip().splitlines()
            for line in lines[1:]:  # skip "List of devices attached" header
                if not line.strip() or 'offline' in line or 'unauthorized' in line:
                    continue
                parts = line.split()
                if len(parts) >= 2 and parts[1] == 'device':
                    address = parts[0]
                    self.adb.connected_device = address

                    manufacturer = self.adb.get_device_property('ro.product.manufacturer') or 'Unknown'
                    model = self.adb.get_device_property('ro.product.model') or 'Unknown'
                    android_version = self.adb.get_device_property('ro.build.version.release') or 'Unknown'

                    self.connected_device_info = f'{address} ({manufacturer} {model})'
                    self.logger.info(f'Already connected device detected: {self.connected_device_info}')

                    self.ui.print_success(f'Already connected: {manufacturer} {model}')
                    self.ui.print_info(f'  Address : {address}')
                    self.ui.print_info(f'  Android : {android_version}')

                    self.menu_system = MenuSystem(self.ui, self.adb)
                    register_all_handlers(self.menu_system, self.ui, self.adb)
                    return
        except Exception as e:
            self.logger.error(f'Device detection error: {e}')

    def startup_checks(self) -> bool:
        self.ui.clear_screen()
        self.display_header()

        self.ui.print_info('Performing startup checks...')
        print()

        internet_available = self.check_internet_connectivity()
        if internet_available:
            self.ui.print_success('Internet connectivity: Available')
            self.logger.info('Internet connectivity check passed')
        else:
            self.ui.print_warning('Internet connectivity: Not available')
            self.ui.print_info('Some features may not work properly')
            self.logger.warning('No internet connectivity detected')

        print()

        if not self.check_and_install_adb():
            return False

        print()

        distro_info = self.distro.get_system_info()
        self.ui.print_info(f"Distribution: {distro_info['distro_name']}")
        self.ui.print_info(f"Package Manager: {distro_info['package_manager']}")
        self.logger.info(f"System info: {distro_info}")

        print()

        # Check for already-connected devices before asking user to connect
        self._detect_already_connected_device()

        print()
        self.ui.wait_for_key()

        return True

    def connect_to_device(self):
        self.ui.clear_screen()
        self.display_header()

        last_device = self.config_manager.get_last_connected_device()
        if last_device:
            timestamp, ip, device_name = last_device
            self.ui.print_info(f'Last connected: {ip} ({device_name}) at {timestamp}')

            if self.ui.confirm(f'Reconnect to {ip}?', default=True):
                ip_address = ip
            else:
                self.ui.print_info('Enter device IP address')
                self.ui.print_info('  - Type FIND to scan network')
                self.ui.print_info('  - Type LOG to view connection history')
                self.ui.print_info('  - Press Enter to cancel')
                ip_address = self.ui.get_input('IP Address', default='')
        else:
            self.ui.print_info('Enter device IP address')
            self.ui.print_info('  - Type FIND to scan network')
            self.ui.print_info('  - Type LOG to view connection history')
            self.ui.print_info('  - Press Enter to cancel')
            ip_address = self.ui.get_input('IP Address', default='')

        if not ip_address:
            return

        if ip_address.upper() == 'FIND':
            self._scan_and_connect()
            return

        if ip_address.upper() == 'LOG':
            self._show_connection_history()
            return

        self._connect_to_ip(ip_address)

    def _connect_to_ip(self, ip_address: str):
        self.ui.print_info(f'Connecting to {ip_address}:5555...')

        success, message = self.adb.connect(ip_address)

        if success:
            self.ui.print_success(f'Connected to {ip_address}')

            manufacturer = self.adb.get_device_property('ro.product.manufacturer') or 'Unknown'
            model = self.adb.get_device_property('ro.product.model') or 'Unknown'
            android_version = self.adb.get_device_property('ro.build.version.release') or 'Unknown'

            self.connected_device_info = f'{ip_address} ({manufacturer} {model})'

            device_info = {
                'manufacturer': manufacturer,
                'model': model,
                'android_version': android_version
            }

            self.ui.print_info(f'Device: {manufacturer} {model}')
            self.ui.print_info(f'Android: {android_version}')

            self._check_standby_mode()

            self.config_manager.update_last_ip(ip_address)
            self.config_manager.log_device_connection(ip_address, f'{manufacturer} {model}')
            self.logger.log_device_connection(ip_address, device_info)

            self.menu_system = MenuSystem(self.ui, self.adb)
            register_all_handlers(self.menu_system, self.ui, self.adb)
        else:
            self.ui.print_error(f'Connection failed: {message}')
            self.logger.error(f'Connection to {ip_address} failed: {message}')

            solutions = [
                'Verify the IP address is correct',
                'Enable USB debugging on the device (Settings > Developer Options)',
                'Enable Network debugging on the device',
                'Check that the device and PC are on the same network',
                'Try connecting via USB first, then enable wireless debugging'
            ]
            self.ui.print_error_with_solutions('Connection failed', solutions)

    def _show_connection_history(self):
        self.ui.clear_screen()
        self.ui.print_info('Connection History')
        print()

        history = self.config_manager.get_connection_history()
        if not history:
            self.ui.print_warning('No connection history found')
        else:
            for i, entry in enumerate(history[-10:], 1):
                timestamp = entry.get('timestamp', 'Unknown')
                ip = entry.get('ip', 'Unknown')
                device = entry.get('device', 'Unknown')
                print(f"  {i}. {timestamp} - {ip} ({device})")

        print()
        self.ui.wait_for_key()

    def _check_standby_mode(self):
        try:
            result = self.adb.execute_command('dumpsys input_method | grep mInteractive')
            if result.success and 'mInteractive=false' in result.output:
                print()
                self.ui.print_warning('Device is in Stand-By mode')
                if self.ui.confirm('Wake up the device?', default=True):
                    wake_result = self.adb.execute_command('input keyevent KEYCODE_WAKEUP')
                    if wake_result.success:
                        self.ui.print_success('Device woken up')
                    else:
                        self.ui.print_error('Failed to wake device')
        except Exception as e:
            self.logger.error(f'Failed to check standby mode: {e}')

    def _scan_and_connect(self):
        from core.network_scanner import NetworkScanner

        self.ui.clear_screen()
        self.ui.print_info('Scanning network for Android TV devices...')
        print()

        scanner = NetworkScanner(self.adb, self.logger)
        success, devices = scanner.scan_network()

        if not success or not devices:
            self.ui.print_warning('No devices found on the network')
            self.ui.print_info('Make sure your Android TV is:')
            print('  - Connected to the same Wi-Fi network')
            print('  - Has USB debugging enabled')
            print('  - Has Network debugging enabled')
            self.ui.wait_for_key()
            return

        if len(devices) == 1:
            device = devices[0]
            if self.ui.confirm(f"Connect to {device['ip']}?", default=True):
                self._connect_to_ip(device['ip'])
        else:
            print()
            self.ui.print_info('Select a device to connect:')
            for i, device in enumerate(devices, 1):
                print(f"  {i}. {device['ip']} ({device['hostname']})")
            print(f"  0. Cancel")
            print()

            choice = self.ui.get_input('Enter device number', default='0')
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(devices):
                    device = devices[idx]
                    self._connect_to_ip(device['ip'])
                else:
                    self.ui.print_info('Cancelled')
            except ValueError:
                self.ui.print_error('Invalid choice')

        self.ui.wait_for_key()

    def main_menu(self):
        while True:
            if not self.menu_system:
                self.menu_system = MenuSystem(self.ui, self.adb)
                register_all_handlers(self.menu_system, self.ui, self.adb)

            self.menu_system.running = True
            self.menu_system.disconnected = False

            while self.menu_system.running:
                self.ui.clear_screen()
                self.display_header()
                self.menu_system.show_main_menu()

            # If disconnect was triggered, go back to connect screen
            if self.menu_system.disconnected:
                self.connected_device_info = None
                self.menu_system = None
                self.connect_to_device()
                if not self.adb.is_connected():
                    break  # user cancelled connect, exit
                # rebuild menu for new device
                self.menu_system = MenuSystem(self.ui, self.adb)
                register_all_handlers(self.menu_system, self.ui, self.adb)
            else:
                break  # normal exit

    def shutdown(self):
        self.ui.clear_screen()
        self.ui.print_success('Thank you for using TV Tools for Linux!')
        self.ui.print_info(f'Author: {AUTHOR}')
        self.ui.print_info(f'GitHub: {GITHUB}')
        self.logger.info('Application shutdown')
        print()

    def run(self):
        try:
            if not self.startup_checks():
                self.ui.print_error('Startup checks failed. Exiting.')
                self.logger.error('Startup checks failed')
                sys.exit(1)

            if not self.adb.is_connected():
                self.connect_to_device()
                self.ui.wait_for_key()

            if not self.adb.is_connected():
                self.ui.print_error('No device connected. Exiting.')
                self.logger.error('User did not connect to a device')
                sys.exit(0)

            self.main_menu()
            print()
            self.ui.print_warning('Interrupted by user')
            self.shutdown()
            self.logger.info('Application interrupted by user')
            sys.exit(0)
        except Exception as e:
            self.ui.print_error(f'Unexpected error: {str(e)}')
            self.logger.error('Unexpected error', exception=e)
            sys.exit(1)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='TV Tools for Linux')
    parser.add_argument('--web', action='store_true', help='Start web server mode')
    parser.add_argument('--host', default='127.0.0.1', help='Web server host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000, help='Web server port (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    if args.web:
        from web_server import WebServer
        server = WebServer()
        server.run(host=args.host, port=args.port, debug=args.debug)
    else:
        app = AndroidTVTools()
        app.run()


if __name__ == '__main__':
    main()
