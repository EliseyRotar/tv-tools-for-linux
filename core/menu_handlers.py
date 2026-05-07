from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.menu_system import MenuSystem
    from core.ui_manager import UIManager
    from core.adb_manager import ADBManager

from core.file_transfer import FileTransfer
from core.package_manager import PackageManager
from core.backup_restore import BackupRestore
from core.settings_manager import SettingsManager
from core.optimization import OptimizationModule
from core.voice_commands import VoiceCommands
from core.remote_control import RemoteControl
from core.keyboard_remote import KeyboardRemote
from core.power_management import PowerManagement
from core.adb_shell import ADBShell
from core.ad_blocking import AdBlocking
from core.install_helper import InstallHelper
from core.system_monitor import SystemMonitor


class MenuHandlers:

    def __init__(self, ui: 'UIManager', adb: 'ADBManager'):
        self.ui = ui
        self.adb = adb
        self.file_transfer = FileTransfer(adb)
        self.package_manager = PackageManager(adb)
        self.backup_restore = BackupRestore(adb, PackageManager(adb), FileTransfer(adb))
        self.settings_manager = SettingsManager(adb)
        self.optimization = OptimizationModule(adb)
        self.voice_commands = VoiceCommands(adb)
        self.remote_control = RemoteControl(adb)
        self.keyboard_remote = KeyboardRemote(adb)
        self.power_management = PowerManagement(adb)
        self.adb_shell = ADBShell(adb)
        self.ad_blocking = AdBlocking(adb)
        self.install_helper = InstallHelper(adb)
        self.system_monitor = SystemMonitor(adb)

    def handle_push_file(self):
        self.ui.clear_screen()
        local_path = self.ui.get_input('Enter local file path')
        if not local_path:
            return
        remote_path = self.ui.get_input('Enter remote path (or press Enter for /sdcard/)')
        if not remote_path:
            remote_path = '/sdcard/'
        success, message = self.file_transfer.push_file(local_path, remote_path)
        if success:
            self.ui.print_success(message)
        else:
            self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_pull_file(self):
        self.ui.clear_screen()
        remote_path = self.ui.get_input('Enter remote file path')
        if not remote_path:
            return
        local_path = self.ui.get_input('Enter local destination path')
        if not local_path:
            return
        success, message = self.file_transfer.pull_file(remote_path, local_path)
        if success:
            self.ui.print_success(message)
        else:
            self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_ftp_server(self):
        self.ui.clear_screen()
        self.ui.print_info('FTP Server Management')
        print()
        is_running, status = self.file_transfer.check_ftp_server()
        self.ui.print_info(f'Status: {status}')
        print()
        if is_running:
            if self.ui.confirm('Disable FTP server?'):
                success, message = self.file_transfer.disable_ftp_server()
                if success:
                    self.ui.print_success(message)
                else:
                    self.ui.print_error(message)
        else:
            if self.ui.confirm('Enable FTP server?'):
                success, message = self.file_transfer.enable_ftp_server()
                if success:
                    self.ui.print_success(message)
                else:
                    self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_send_text(self):
        self.ui.clear_screen()
        text = self.ui.get_input('Enter text to send to device clipboard')
        if not text:
            return
        success, message = self.file_transfer.send_text_to_clipboard(text)
        if success:
            self.ui.print_success(message)
        else:
            self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_list_packages(self):
        self.ui.clear_screen()
        self.ui.print_info('Package Filter:')
        print('1. All packages')
        print('2. System packages')
        print('3. User packages')
        print('4. Enabled packages')
        print('5. Disabled packages')
        choice = self.ui.get_input('Enter choice (1-5)', default='3')
        filter_map = {'1': 'all', '2': 'system', '3': 'user', '4': 'enabled', '5': 'disabled'}
        filter_type = filter_map.get(choice, 'user')
        packages = self.package_manager.list_packages(filter_type)
        self.package_manager.display_packages_table(packages, f'{filter_type.title()} Packages')
        self.ui.wait_for_key()

    def handle_install_package(self):
        self.ui.clear_screen()
        apk_path = self.ui.get_input('Enter APK file path')
        if not apk_path:
            return
        success = self.package_manager.install_apk(apk_path)
        if success:
            self.ui.print_success('Package installed successfully')
        else:
            self.ui.print_error('Installation failed')
        self.ui.wait_for_key()

    def handle_uninstall_package(self):
        self.ui.clear_screen()
        package_name = self.ui.get_input('Enter package name')
        if not package_name:
            return
        is_system = self.ui.confirm('Is this a system app?', default=False)
        success = self.package_manager.uninstall_package(package_name, is_system)
        if success:
            self.ui.print_success('Package uninstalled successfully')
        else:
            self.ui.print_error('Uninstallation failed')
        self.ui.wait_for_key()

    def handle_enable_package(self):
        self.ui.clear_screen()
        package_name = self.ui.get_input('Enter package name')
        if not package_name:
            return
        success = self.package_manager.enable_package(package_name)
        if success:
            self.ui.print_success('Package enabled successfully')
        else:
            self.ui.print_error('Enable failed')
        self.ui.wait_for_key()

    def handle_disable_package(self):
        self.ui.clear_screen()
        package_name = self.ui.get_input('Enter package name')
        if not package_name:
            return
        success = self.package_manager.disable_package(package_name)
        if success:
            self.ui.print_success('Package disabled successfully')
        else:
            self.ui.print_error('Disable failed')
        self.ui.wait_for_key()

    def handle_search_packages(self):
        self.ui.clear_screen()
        query = self.ui.get_input('Enter search query')
        if not query:
            return
        packages = self.package_manager.search_packages(query)
        self.package_manager.display_packages_table(packages, f'Search Results for "{query}"')
        self.ui.wait_for_key()

    def handle_backup_single(self):
        self.ui.clear_screen()
        package_name = self.ui.get_input('Enter package name to backup')
        if not package_name:
            return
        success, message = self.backup_restore.backup_package(package_name)
        if success:
            self.ui.print_success(message)
        else:
            self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_backup_batch(self):
        self.ui.clear_screen()
        self.ui.print_info('Batch Backup')
        self.ui.print_info('Enter package names (comma-separated)')
        packages_input = self.ui.get_input('Package names')
        if not packages_input:
            return
        package_names = [p.strip() for p in packages_input.split(',')]
        results = self.backup_restore.batch_backup(package_names)
        for pkg, success in results.items():
            if success:
                self.ui.print_success(f'{pkg}: Backed up')
            else:
                self.ui.print_error(f'{pkg}: Failed')
        self.ui.wait_for_key()

    def handle_restore_single(self):
        self.ui.clear_screen()
        backups = self.backup_restore.list_backups()
        if not backups:
            self.ui.print_warning('No backups found')
            self.ui.wait_for_key()
            return
        self.ui.print_info('Available backups:')
        for i, backup in enumerate(backups, 1):
            print(f'{i}. {backup}')
        choice = self.ui.get_input('Enter backup number')
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(backups):
                success, message = self.backup_restore.restore_package(backups[idx])
                if success:
                    self.ui.print_success(message)
                else:
                    self.ui.print_error(message)
        except ValueError:
            self.ui.print_error('Invalid choice')
        self.ui.wait_for_key()

    def handle_restore_batch(self):
        self.ui.clear_screen()
        backups = self.backup_restore.list_backups()
        if not backups:
            self.ui.print_warning('No backups found')
            self.ui.wait_for_key()
            return
        if self.ui.confirm('Restore all backups?'):
            results = self.backup_restore.batch_restore(backups)
            for backup, success in results.items():
                if success:
                    self.ui.print_success(f'{backup}: Restored')
                else:
                    self.ui.print_error(f'{backup}: Failed')
        self.ui.wait_for_key()

    def handle_list_backups(self):
        self.ui.clear_screen()
        backups = self.backup_restore.list_backups()
        if not backups:
            self.ui.print_warning('No backups found')
        else:
            self.ui.print_info('Available backups:')
            for backup in backups:
                print(f'  • {backup}')
        self.ui.wait_for_key()

    def handle_delete_backup(self):
        self.ui.clear_screen()
        backups = self.backup_restore.list_backups()
        if not backups:
            self.ui.print_warning('No backups found')
            self.ui.wait_for_key()
            return
        self.ui.print_info('Available backups:')
        for i, backup in enumerate(backups, 1):
            print(f'{i}. {backup}')
        choice = self.ui.get_input('Enter backup number to delete')
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(backups):
                if self.ui.confirm(f'Delete {backups[idx]}?'):
                    success, message = self.backup_restore.delete_backup(backups[idx])
                    if success:
                        self.ui.print_success(message)
                    else:
                        self.ui.print_error(message)
        except ValueError:
            self.ui.print_error('Invalid choice')
        self.ui.wait_for_key()

    def handle_settings_gps(self):
        self.ui.clear_screen()
        self.ui.print_info('GPS Location Settings')
        print()
        if self.ui.confirm('Enable GPS location?', default=True):
            success, message = self.settings_manager.enable_gps_location()
        else:
            success, message = self.settings_manager.disable_gps_location()
        if success:
            self.ui.print_success(message)
        else:
            self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_settings_timeout(self):
        self.ui.clear_screen()
        self.ui.print_info('Screen Timeout Settings')
        print('Common values:')
        print('  15000 = 15 seconds')
        print('  30000 = 30 seconds')
        print('  60000 = 1 minute')
        print('  300000 = 5 minutes')
        print('  600000 = 10 minutes')
        print('  1800000 = 30 minutes')
        print('  -1 = Never timeout')
        timeout = self.ui.get_input('Enter timeout in milliseconds', default='60000')
        try:
            timeout_ms = int(timeout)
            success, message = self.settings_manager.set_screen_timeout(timeout_ms // 1000)
            if success:
                self.ui.print_success(message)
            else:
                self.ui.print_error(message)
        except ValueError:
            self.ui.print_error('Invalid timeout value')
        self.ui.wait_for_key()

    def handle_settings_updates(self):
        self.ui.clear_screen()
        self.ui.print_info('Automatic Updates Settings')
        print()
        if self.ui.confirm('Enable automatic updates?', default=False):
            success, message = self.settings_manager.enable_auto_updates()
        else:
            success, message = self.settings_manager.disable_auto_updates()
        if success:
            self.ui.print_success(message)
        else:
            self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_settings_animation(self):
        self.ui.clear_screen()
        self.ui.print_info('Animation Scale Settings')
        print('Scale values:')
        print('  0.0 = Off')
        print('  0.5 = Half speed')
        print('  1.0 = Normal (default)')
        print('  1.5 = 1.5x speed')
        print('  2.0 = 2x speed')
        scale = self.ui.get_input('Enter animation scale', default='1.0')
        try:
            scale_val = float(scale)
            success, message = self.settings_manager.set_animation_scale(scale_val)
            if success:
                self.ui.print_success(message)
            else:
                self.ui.print_error(message)
        except ValueError:
            self.ui.print_error('Invalid scale value')
        self.ui.wait_for_key()

    def handle_settings_usb_debug(self):
        self.ui.clear_screen()
        self.ui.print_info('USB Debugging Settings')
        print()
        if self.ui.confirm('Enable USB debugging?', default=True):
            success, message = self.settings_manager.enable_usb_debugging()
        else:
            success, message = self.settings_manager.disable_usb_debugging()
        if success:
            self.ui.print_success(message)
        else:
            self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_settings_adb_network(self):
        self.ui.clear_screen()
        self.ui.print_info('ADB over Network Settings')
        print()
        if self.ui.confirm('Enable ADB over network?', default=True):
            success, message = self.settings_manager.enable_adb_network()
        else:
            success, message = self.settings_manager.disable_adb_network()
        if success:
            self.ui.print_success(message)
        else:
            self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_settings_stay_awake(self):
        self.ui.clear_screen()
        self.ui.print_info('Stay Awake Settings')
        print()
        if self.ui.confirm('Keep screen awake while charging?', default=True):
            success, message = self.settings_manager.enable_stay_awake()
        else:
            success, message = self.settings_manager.disable_stay_awake()
        if success:
            self.ui.print_success(message)
        else:
            self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_settings_unknown_sources(self):
        self.ui.clear_screen()
        self.ui.print_info('Unknown Sources Settings')
        print()
        if self.ui.confirm('Allow installation from unknown sources?', default=True):
            success, message = self.settings_manager.enable_unknown_sources()
        else:
            success, message = self.settings_manager.disable_unknown_sources()
        if success:
            self.ui.print_success(message)
        else:
            self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_display_density(self):
        self.ui.clear_screen()
        self.ui.print_info('Screen Density Settings')
        success, current_dpi, message = self.settings_manager.get_density()
        if success and current_dpi:
            self.ui.print_info(f'Current DPI: {current_dpi}')
        print()
        print('Common DPI values:')
        print('  160 = Low density (ldpi)')
        print('  240 = Medium density (mdpi)')
        print('  320 = High density (hdpi)')
        print('  480 = Extra high density (xhdpi)')
        print('  640 = Extra extra high density (xxhdpi)')
        dpi = self.ui.get_input('Enter new DPI value')
        if not dpi:
            return
        try:
            dpi_val = int(dpi)
            success, message = self.settings_manager.set_density(dpi_val)
            if success:
                self.ui.print_success(message)
            else:
                self.ui.print_error(message)
        except ValueError:
            self.ui.print_error('Invalid DPI value')
        self.ui.wait_for_key()

    def handle_display_font(self):
        self.ui.clear_screen()
        self.ui.print_info('Font Size Settings')
        success, current_scale, message = self.settings_manager.get_font_size()
        if success and current_scale:
            self.ui.print_info(f'Current scale: {current_scale}')
        print()
        print('Font scale values:')
        print('  0.85 = Small')
        print('  1.0 = Normal (default)')
        print('  1.15 = Large')
        print('  1.3 = Extra large')
        scale = self.ui.get_input('Enter font scale', default='1.0')
        try:
            scale_val = float(scale)
            success, message = self.settings_manager.set_font_size(scale_val)
            if success:
                self.ui.print_success(message)
            else:
                self.ui.print_error(message)
        except ValueError:
            self.ui.print_error('Invalid scale value')
        self.ui.wait_for_key()

    def handle_screenshot(self):
        self.ui.clear_screen()
        self.ui.print_info('Taking screenshot...')
        success, message = self.file_transfer.take_screenshot()
        if success:
            self.ui.print_success(message)
        else:
            self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_recording(self):
        self.ui.clear_screen()
        self.ui.print_info('Screen Recording')
        duration = self.ui.get_input('Enter duration in seconds', default='30')
        try:
            duration_val = int(duration)
            self.ui.print_info(f'Recording for {duration_val} seconds...')
            success, message = self.file_transfer.start_recording(duration=duration_val)
            if success:
                self.ui.print_success(message)
            else:
                self.ui.print_error(message)
        except ValueError:
            self.ui.print_error('Invalid duration')
        self.ui.wait_for_key()

    def handle_install_app(self, app_id: str, app_name: str):
        self.ui.clear_screen()
        self.ui.print_info(f'Installing {app_name}...')
        is_installed, version = self.install_helper.check_installed(app_id)
        if is_installed:
            self.ui.print_warning(f'{app_name} is already installed (version {version})')
            if not self.ui.confirm('Reinstall?', default=False):
                self.ui.wait_for_key()
                return
        success, message = self.install_helper.download_and_install(app_id, use_web_search=True)
        if success:
            self.ui.print_success(message)
        else:
            self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_install_smarttube(self):
        self.handle_install_app('smarttube', 'SmartTube')

    def handle_install_launchers(self):
        self.ui.clear_screen()
        self.ui.print_info('Available Launchers:')
        launchers = self.install_helper.list_available_apps('launcher')
        for i, app in enumerate(launchers, 1):
            print(f"{i}. {app.get('name', 'Unknown')}")
        choice = self.ui.get_input('Enter launcher number')
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(launchers):
                app = launchers[idx]
                self.handle_install_app(app['id'], app['name'])
            else:
                self.ui.print_error('Invalid choice')
                self.ui.wait_for_key()
        except ValueError:
            self.ui.print_error('Invalid choice')
            self.ui.wait_for_key()

    def handle_install_iptv(self):
        self.ui.clear_screen()
        self.ui.print_info('Available IPTV Apps:')
        iptv_apps = self.install_helper.list_available_apps('iptv')
        for i, app in enumerate(iptv_apps, 1):
            print(f"{i}. {app.get('name', 'Unknown')}")
        choice = self.ui.get_input('Enter IPTV app number')
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(iptv_apps):
                app = iptv_apps[idx]
                self.handle_install_app(app['id'], app['name'])
            else:
                self.ui.print_error('Invalid choice')
                self.ui.wait_for_key()
        except ValueError:
            self.ui.print_error('Invalid choice')
            self.ui.wait_for_key()

    def handle_install_stores(self):
        self.ui.clear_screen()
        self.ui.print_info('Available App Stores:')
        stores = self.install_helper.list_available_apps('store')
        for i, app in enumerate(stores, 1):
            print(f"{i}. {app.get('name', 'Unknown')}")
        choice = self.ui.get_input('Enter store number')
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(stores):
                app = stores[idx]
                self.handle_install_app(app['id'], app['name'])
            else:
                self.ui.print_error('Invalid choice')
                self.ui.wait_for_key()
        except ValueError:
            self.ui.print_error('Invalid choice')
            self.ui.wait_for_key()

    def handle_install_shizuku(self):
        self.handle_install_app('shizuku', 'Shizuku')

    def handle_install_stremio(self):
        self.handle_install_app('stremio', 'Stremio')

    def handle_opt_disable_animations(self):
        self.ui.clear_screen()
        self.ui.print_info('Disabling animations...')
        success, message = self.optimization.disable_animations()
        if success:
            self.ui.print_success(message)
        else:
            self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_opt_clear_app_cache(self):
        self.ui.clear_screen()
        self.ui.print_info('Clear App Cache')
        print('1. Clear specific app cache')
        print('2. Clear all app caches')
        choice = self.ui.get_input('Enter choice (1-2)')
        if choice == '1':
            package_name = self.ui.get_input('Enter package name')
            if package_name:
                success, message = self.optimization.clear_app_cache(package_name)
                if success:
                    self.ui.print_success(message)
                else:
                    self.ui.print_error(message)
        elif choice == '2':
            if self.ui.confirm('Clear all app caches?'):
                success, message, stats = self.optimization.clear_all_app_caches()
                if success:
                    self.ui.print_success(message)
                    self.ui.print_info(f"Cleared: {stats.get('cleared', 0)} apps")
                else:
                    self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_opt_clear_system_cache(self):
        self.ui.clear_screen()
        if self.ui.confirm('Clear system cache partition?'):
            self.ui.print_info('Clearing system cache...')
            success, message = self.optimization.clear_system_cache()
            if success:
                self.ui.print_success(message)
            else:
                self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_opt_force_stop(self):
        self.ui.clear_screen()
        self.ui.print_info('Force Stop Apps')
        packages_input = self.ui.get_input('Enter package names (comma-separated, or leave empty for all)')
        if packages_input:
            package_names = [p.strip() for p in packages_input.split(',')]
        else:
            package_names = None
        if self.ui.confirm('Force stop apps?'):
            success, message, stats = self.optimization.force_stop_apps(package_names)
            if success:
                self.ui.print_success(message)
                self.ui.print_info(f"Stopped: {stats.get('stopped', 0)} apps")
            else:
                self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_opt_memory_usage(self):
        self.ui.clear_screen()
        self.ui.print_info('Memory Usage Information')
        print()
        success, memory_info = self.optimization.get_memory_usage()
        if success:
            for key, value in memory_info.items():
                self.ui.print_info(f'{key}: {value}')
        else:
            self.ui.print_error('Failed to get memory usage')
        self.ui.wait_for_key()

    def handle_voice_trigger(self):
        self.ui.clear_screen()
        self.ui.print_info('Triggering voice input...')
        success, message = self.voice_commands.trigger_voice_input()
        if success:
            self.ui.print_success(message)
        else:
            self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_voice_command(self):
        self.ui.clear_screen()
        self.ui.print_info('Available commands:')
        commands = self.voice_commands.list_predefined_commands()
        for i, cmd in enumerate(commands, 1):
            print(f"{i}. {cmd['name']}: {cmd['description']}")
        print()
        command = self.ui.get_input('Enter command name')
        if not command:
            return
        query = self.ui.get_input('Enter query (optional)')
        success, message = self.voice_commands.send_voice_command(command, query if query else None)
        if success:
            self.ui.print_success(message)
        else:
            self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_voice_search(self):
        self.ui.clear_screen()
        query = self.ui.get_input('Enter search query')
        if not query:
            return
        self.ui.print_info('Performing voice search...')
        success, message = self.voice_commands.voice_search(query)
        if success:
            self.ui.print_success(message)
        else:
            self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_remote_scrcpy(self):
        self.ui.clear_screen()
        self.ui.print_info('Launching scrcpy...')
        is_installed, version = self.remote_control.check_scrcpy_installed()
        if not is_installed:
            self.ui.print_warning('scrcpy is not installed')
            instructions = self.remote_control.get_installation_instructions()
            self.ui.print_info('Installation instructions:')
            for distro, cmd in instructions.items():
                print(f'  {distro}: {cmd}')
            self.ui.wait_for_key()
            return
        self.ui.print_info(f'scrcpy version: {version}')
        presets = self.remote_control.list_presets()
        print()
        print('Available presets:')
        for i, preset in enumerate(presets, 1):
            print(f"{i}. {preset['name']}: {preset['description']}")
        print(f"{len(presets) + 1}. Custom options")
        choice = self.ui.get_input('Enter preset number', default='1')
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(presets):
                preset_name = presets[idx]['name']
                success, message = self.remote_control.launch_scrcpy(preset=preset_name)
            else:
                options = self.ui.get_input('Enter custom scrcpy options')
                success, message = self.remote_control.launch_scrcpy(custom_options=options.split() if options else None)
            if success:
                self.ui.print_success(message)
            else:
                self.ui.print_error(message)
        except ValueError:
            self.ui.print_error('Invalid choice')
        self.ui.wait_for_key()

    def handle_remote_keyboard(self):
        self.ui.clear_screen()
        self.ui.print_info('Starting keyboard remote...')
        self.ui.print_info('Use arrow keys, Enter, Esc, etc. Press Ctrl+C to exit.')
        self.keyboard_remote.start()
        self.ui.wait_for_key()

    def handle_remote_power(self):
        self.ui.clear_screen()
        self.ui.print_info('Power Management')
        print()
        print('1. Reboot device')
        print('2. Reboot to recovery')
        print('3. Reboot to bootloader')
        print('4. Screen on')
        print('5. Screen off')
        print('6. Battery info')
        choice = self.ui.get_input('Enter choice (1-6)')
        if choice == '1':
            if self.ui.confirm('Reboot device?'):
                success, message = self.power_management.reboot_device(confirm=False)
                if success:
                    self.ui.print_success(message)
                else:
                    self.ui.print_error(message)
        elif choice == '2':
            if self.ui.confirm('Reboot to recovery?'):
                success, message = self.power_management.reboot_recovery(confirm=False)
                if success:
                    self.ui.print_success(message)
                else:
                    self.ui.print_error(message)
        elif choice == '3':
            if self.ui.confirm('Reboot to bootloader?'):
                success, message = self.power_management.reboot_bootloader(confirm=False)
                if success:
                    self.ui.print_success(message)
                else:
                    self.ui.print_error(message)
        elif choice == '4':
            success, message = self.power_management.wake_device()
            if success:
                self.ui.print_success(message)
            else:
                self.ui.print_error(message)
        elif choice == '5':
            success, message = self.power_management.sleep_device()
            if success:
                self.ui.print_success(message)
            else:
                self.ui.print_error(message)
        elif choice == '6':
            success, battery_info = self.power_management.get_battery_info()
            if success and battery_info:
                self.ui.print_info('Battery Information:')
                for key, value in battery_info.items():
                    print(f'  {key}: {value}')
            else:
                self.ui.print_error('Failed to get battery info')
        self.ui.wait_for_key()

    def handle_remote_shell(self):
        self.ui.clear_screen()
        self.ui.print_info('Starting ADB shell...')
        self.ui.print_info('Type "exit" to return to menu')
        print()
        self.adb_shell.start_interactive_shell()
        self.ui.wait_for_key()

    def handle_adblock_dns(self):
        self.ui.clear_screen()
        self.ui.print_info('Private DNS Configuration')
        print()
        success, current_dns = self.ad_blocking.get_private_dns()
        if success and current_dns:
            self.ui.print_info(f'Current DNS: {current_dns}')
        print()
        print('Available DNS providers:')
        print('1. AdGuard DNS (dns.adguard.com)')
        print('2. AdGuard DNS Family (dns-family.adguard.com)')
        print('3. ControlD DNS (freedns.controld.com)')
        print('4. Custom DNS')
        print('5. Disable Private DNS')
        choice = self.ui.get_input('Enter choice (1-5)')
        if choice == '1':
            success, message = self.ad_blocking.enable_adguard_dns(family_mode=False)
            if success:
                self.ui.print_success(message)
            else:
                self.ui.print_error(message)
        elif choice == '2':
            success, message = self.ad_blocking.enable_adguard_dns(family_mode=True)
            if success:
                self.ui.print_success(message)
            else:
                self.ui.print_error(message)
        elif choice == '3':
            success, message = self.ad_blocking.enable_controld_dns()
            if success:
                self.ui.print_success(message)
            else:
                self.ui.print_error(message)
        elif choice == '4':
            custom_dns = self.ui.get_input('Enter custom DNS hostname')
            if custom_dns:
                success, message = self.ad_blocking.enable_custom_dns(custom_dns)
                if success:
                    self.ui.print_success(message)
                else:
                    self.ui.print_error(message)
        elif choice == '5':
            success, message = self.ad_blocking.disable_private_dns()
            if success:
                self.ui.print_success(message)
            else:
                self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_adblock_adguard(self):
        self.ui.clear_screen()
        self.ui.print_info('AdGuard Installation')
        is_installed, version = self.ad_blocking.check_adguard_installed()
        if is_installed:
            self.ui.print_success(f'AdGuard is already installed (version {version})')
            if self.ui.confirm('Launch AdGuard?'):
                success, message = self.ad_blocking.launch_adguard_app()
                if success:
                    self.ui.print_success(message)
                else:
                    self.ui.print_error(message)
        else:
            if self.ui.confirm('Install AdGuard?'):
                success, message = self.ad_blocking.install_adguard_app()
                if success:
                    self.ui.print_success(message)
                    guide = self.ad_blocking.get_adguard_configuration_guide()
                    self.ui.print_info('Configuration Guide:')
                    print(guide)
                else:
                    self.ui.print_error(message)
        self.ui.wait_for_key()

    def handle_device_info(self):
        from core.device_info import DeviceInfo
        self.ui.clear_screen()
        device_info = DeviceInfo(self.adb)
        info = device_info.get_all_device_info()

        self.ui.print_info('Device Information')
        print()

        if info.get('basic'):
            basic = info['basic']
            self.ui.print_info(f"Manufacturer: {basic.get('manufacturer', 'Unknown')}")
            self.ui.print_info(f"Model: {basic.get('model', 'Unknown')}")
            self.ui.print_info(f"Android Version: {basic.get('android_version', 'Unknown')}")
            self.ui.print_info(f"SDK Level: {basic.get('sdk_level', 'Unknown')}")
            print()

        if info.get('display'):
            display = info['display']
            self.ui.print_info(f"Display: {display.get('resolution', 'Unknown')}")
            self.ui.print_info(f"Density: {display.get('density', 'Unknown')} DPI")
            print()

        if info.get('storage'):
            storage = info['storage']
            self.ui.print_info(f"Storage: {storage.get('total', 'Unknown')} total, {storage.get('available', 'Unknown')} available")
            print()

        if info.get('memory'):
            memory = info['memory']
            self.ui.print_info(f"RAM: {memory.get('total', 'Unknown')} total, {memory.get('available', 'Unknown')} available")
            print()

        if info.get('network'):
            network = info['network']
            self.ui.print_info(f"IP Address: {network.get('ip_address', 'Unknown')}")
            self.ui.print_info(f"MAC Address: {network.get('mac_address', 'Unknown')}")
            print()

        if info.get('battery'):
            battery = info['battery']
            self.ui.print_info(f"Battery: {battery.get('level', 'Unknown')}% ({battery.get('status', 'Unknown')})")
            print()

        self.ui.wait_for_key()

    def handle_icon_generator(self):
        from core.icon_generator import IconGenerator
        self.ui.clear_screen()
        self.ui.print_info('Icon Generator for Hidden Apps')
        print()
        self.ui.print_info('This will generate launcher icons for apps that don\'t appear in the launcher.')
        print()

        if not self.ui.confirm('Continue?', default=True):
            return

        icon_gen = IconGenerator(self.adb)
        success, hidden_apps = icon_gen.detect_hidden_apps()

        if not success or not hidden_apps:
            self.ui.print_warning('No hidden apps found')
            self.ui.wait_for_key()
            return

        self.ui.print_info(f'Found {len(hidden_apps)} hidden app(s):')
        for i, app in enumerate(hidden_apps, 1):
            print(f"  {i}. {app}")
        print()

        if self.ui.confirm('Generate icons for all hidden apps?', default=True):
            for app in hidden_apps:
                success, message = icon_gen.generate_launcher_icon(app)
                if success:
                    self.ui.print_success(f'{app}: {message}')
                else:
                    self.ui.print_error(f'{app}: {message}')

        self.ui.wait_for_key()

    def handle_bloatware_removal(self):
        from core.bloatware_removal import BloatwareRemoval
        self.ui.clear_screen()
        self.ui.print_info('Bloatware Removal')
        print()
        self.ui.print_warning('⚠️  WARNING: Removing system apps can cause instability!')
        self.ui.print_info('Only remove apps you are sure about.')
        print()

        if not self.ui.confirm('Continue?', default=False):
            return

        bloatware = BloatwareRemoval(self.adb)
        recommendations = bloatware.get_removal_recommendations()

        if not recommendations:
            self.ui.print_info('No bloatware recommendations available')
            self.ui.wait_for_key()
            return

        self.ui.print_info('Recommended apps to remove:')
        for category, apps in recommendations.items():
            print(f"\n{category}:")
            for app in apps:
                print(f"  - {app}")

        print()
        if self.ui.confirm('Remove recommended bloatware?', default=False):
            all_apps = []
            for apps in recommendations.values():
                all_apps.extend(apps)

            results = bloatware.batch_remove(all_apps)
            for app, success in results.items():
                if success:
                    self.ui.print_success(f'Removed: {app}')
                else:
                    self.ui.print_error(f'Failed: {app}')

        self.ui.wait_for_key()

    def handle_permissions(self):
        from core.permission_manager import PermissionManager
        self.ui.clear_screen()
        self.ui.print_info('Permission Management')
        print()

        package_name = self.ui.get_input('Enter package name')
        if not package_name:
            return

        perm_manager = PermissionManager(self.adb)
        success, permissions = perm_manager.list_permissions(package_name)

        if not success:
            self.ui.print_error('Failed to get permissions')
            self.ui.wait_for_key()
            return

        self.ui.print_info(f'Permissions for {package_name}:')
        for perm in permissions:
            status = '✅' if perm.get('granted') else '❌'
            print(f"  {status} {perm.get('name')}")

        print()
        action = self.ui.get_input('Grant (g) or Revoke (r) permission? (or Enter to cancel)', default='')

        if action.lower() == 'g':
            perm_name = self.ui.get_input('Enter permission name to grant')
            if perm_name:
                success, message = perm_manager.grant_permission(package_name, perm_name)
                if success:
                    self.ui.print_success(message)
                else:
                    self.ui.print_error(message)
        elif action.lower() == 'r':
            perm_name = self.ui.get_input('Enter permission name to revoke')
            if perm_name:
                success, message = perm_manager.revoke_permission(package_name, perm_name)
                if success:
                    self.ui.print_success(message)
                else:
                    self.ui.print_error(message)

        self.ui.wait_for_key()

    def handle_system_monitor(self):
        self.ui.clear_screen()
        self.system_monitor.start_monitor(self.ui)
        self.ui.wait_for_key()


def register_all_handlers(menu_system: 'MenuSystem', ui: 'UIManager', adb: 'ADBManager'):
    handlers = MenuHandlers(ui, adb)

    menu_system.register_handler('file_transfer', menu_system.show_file_transfer_menu)
    menu_system.register_handler('app_management', menu_system.show_app_management_menu)
    menu_system.register_handler('backup_restore', menu_system.show_backup_restore_menu)
    menu_system.register_handler('custom_settings', menu_system.show_custom_settings_menu)
    menu_system.register_handler('display_settings', menu_system.show_display_settings_menu)
    menu_system.register_handler('screenshot_recording', menu_system.show_screenshot_recording_menu)
    menu_system.register_handler('installation_helper', menu_system.show_installation_helper_menu)
    menu_system.register_handler('optimizations', menu_system.show_optimizations_menu)
    menu_system.register_handler('voice_commands', menu_system.show_voice_commands_menu)
    menu_system.register_handler('remote_control', menu_system.show_remote_control_menu)
    menu_system.register_handler('ad_blocking', menu_system.show_ad_blocking_menu)

    menu_system.register_handler('file_transfer_push', handlers.handle_push_file)
    menu_system.register_handler('file_transfer_pull', handlers.handle_pull_file)
    menu_system.register_handler('file_transfer_ftp', handlers.handle_ftp_server)
    menu_system.register_handler('file_transfer_text', handlers.handle_send_text)

    menu_system.register_handler('app_list', handlers.handle_list_packages)
    menu_system.register_handler('app_install', handlers.handle_install_package)
    menu_system.register_handler('app_uninstall', handlers.handle_uninstall_package)
    menu_system.register_handler('app_enable', handlers.handle_enable_package)
    menu_system.register_handler('app_disable', handlers.handle_disable_package)
    menu_system.register_handler('app_search', handlers.handle_search_packages)
    menu_system.register_handler('app_icon_generator', handlers.handle_icon_generator)
    menu_system.register_handler('app_bloatware', handlers.handle_bloatware_removal)
    menu_system.register_handler('app_permissions', handlers.handle_permissions)

    menu_system.register_handler('backup_single', handlers.handle_backup_single)
    menu_system.register_handler('backup_batch', handlers.handle_backup_batch)
    menu_system.register_handler('restore_single', handlers.handle_restore_single)
    menu_system.register_handler('restore_batch', handlers.handle_restore_batch)
    menu_system.register_handler('backup_list', handlers.handle_list_backups)
    menu_system.register_handler('backup_delete', handlers.handle_delete_backup)

    menu_system.register_handler('settings_gps', handlers.handle_settings_gps)
    menu_system.register_handler('settings_timeout', handlers.handle_settings_timeout)
    menu_system.register_handler('settings_updates', handlers.handle_settings_updates)
    menu_system.register_handler('settings_animation', handlers.handle_settings_animation)
    menu_system.register_handler('settings_usb_debug', handlers.handle_settings_usb_debug)
    menu_system.register_handler('settings_adb_network', handlers.handle_settings_adb_network)
    menu_system.register_handler('settings_stay_awake', handlers.handle_settings_stay_awake)
    menu_system.register_handler('settings_unknown_sources', handlers.handle_settings_unknown_sources)

    menu_system.register_handler('display_density', handlers.handle_display_density)
    menu_system.register_handler('display_font', handlers.handle_display_font)

    menu_system.register_handler('screenshot_take', handlers.handle_screenshot)
    menu_system.register_handler('recording_start', handlers.handle_recording)

    menu_system.register_handler('install_smarttube', handlers.handle_install_smarttube)
    menu_system.register_handler('install_launchers', handlers.handle_install_launchers)
    menu_system.register_handler('install_iptv', handlers.handle_install_iptv)
    menu_system.register_handler('install_stores', handlers.handle_install_stores)
    menu_system.register_handler('install_shizuku', handlers.handle_install_shizuku)
    menu_system.register_handler('install_stremio', handlers.handle_install_stremio)

    menu_system.register_handler('opt_disable_animations', handlers.handle_opt_disable_animations)
    menu_system.register_handler('opt_clear_app_cache', handlers.handle_opt_clear_app_cache)
    menu_system.register_handler('opt_clear_system_cache', handlers.handle_opt_clear_system_cache)
    menu_system.register_handler('opt_force_stop', handlers.handle_opt_force_stop)
    menu_system.register_handler('opt_memory_usage', handlers.handle_opt_memory_usage)

    menu_system.register_handler('voice_trigger', handlers.handle_voice_trigger)
    menu_system.register_handler('voice_command', handlers.handle_voice_command)
    menu_system.register_handler('voice_search', handlers.handle_voice_search)

    menu_system.register_handler('remote_scrcpy', handlers.handle_remote_scrcpy)
    menu_system.register_handler('remote_keyboard', handlers.handle_remote_keyboard)
    menu_system.register_handler('remote_power', handlers.handle_remote_power)
    menu_system.register_handler('remote_shell', handlers.handle_remote_shell)

    menu_system.register_handler('adblock_dns', handlers.handle_adblock_dns)
    menu_system.register_handler('adblock_adguard', handlers.handle_adblock_adguard)

    menu_system.register_handler('device_info', handlers.handle_device_info)
    menu_system.register_handler('system_monitor', handlers.handle_system_monitor)
