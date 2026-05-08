from typing import Callable, Dict, List
from core.ui_manager import UIManager
from core.adb_manager import ADBManager


class MenuSystem:

    def __init__(self, ui_manager: UIManager, adb_manager: ADBManager):
        self.ui = ui_manager
        self.adb = adb_manager
        self.breadcrumb: List[str] = []
        self.running = True
        self.disconnected = False
        self.handlers: Dict[str, Callable] = {}

    def register_handler(self, menu_id: str, handler: Callable):
        self.handlers[menu_id] = handler

    def show_main_menu(self):
        self.breadcrumb = ['Main Menu']

        options = [
            '📁 File Transfer',
            '📦 App Management',
            '💾 Backup & Restore',
            '⚙️  Custom Settings',
            '🖥️  Display Settings',
            '📸 Screenshot & Recording',
            '⬇️  Installation Helper',
            '⚡ Optimizations',
            '🎤 Voice Commands',
            '🎮 Remote Control',
            '🛡️  Ad Blocking',
            '📊 Device Info',
            '📈 System Monitor (btop)',
            '🔌 Disconnect Device',
            '🚪 Exit'
        ]

        self.ui.display_menu_with_breadcrumb(' > '.join(self.breadcrumb), options)

        choice = self.ui.get_input('Enter your choice (1-15, 0 to exit)', default='')

        if not choice:
            return

        menu_map = {
            '1': 'file_transfer',
            '2': 'app_management',
            '3': 'backup_restore',
            '4': 'custom_settings',
            '5': 'display_settings',
            '6': 'screenshot_recording',
            '7': 'installation_helper',
            '8': 'optimizations',
            '9': 'voice_commands',
            '10': 'remote_control',
            '11': 'ad_blocking',
            '12': 'device_info',
            '13': 'system_monitor',
            '14': 'disconnect_device',
            '15': 'exit',
            '0': 'exit'
        }

        menu_id = menu_map.get(choice)
        if menu_id and menu_id in self.handlers:
            self.handlers[menu_id]()
        elif menu_id == 'exit':
            self.running = False
        else:
            self.ui.print_error('Invalid choice')
            self.ui.wait_for_key()

    def show_file_transfer_menu(self):
        while self.running:
            self.breadcrumb = ['Main Menu', 'File Transfer']

            options = [
                '📤 Push file to device',
                '📥 Pull file from device',
                '📂 FTP Server Management',
                '📋 Send text to device',
                '🔙 Back to Main Menu'
            ]

            self.ui.display_menu_with_breadcrumb(' > '.join(self.breadcrumb), options, 'File Transfer Options')

            choice = self.ui.get_input('Enter your choice (1-4, 0)', default='0')

            if choice == '1':
                if 'file_transfer_push' in self.handlers:
                    self.handlers['file_transfer_push']()
            elif choice == '2':
                if 'file_transfer_pull' in self.handlers:
                    self.handlers['file_transfer_pull']()
            elif choice == '3':
                if 'file_transfer_ftp' in self.handlers:
                    self.handlers['file_transfer_ftp']()
            elif choice == '4':
                if 'file_transfer_text' in self.handlers:
                    self.handlers['file_transfer_text']()
            elif choice == '0' or choice == '':
                return
            else:
                self.ui.print_error('Invalid choice')
                self.ui.wait_for_key()

    def show_app_management_menu(self):
        while self.running:
            self.breadcrumb = ['Main Menu', 'App Management']

            options = [
                '📋 List packages',
                '📦 Install APK',
                '🗑️  Uninstall package',
                '✅ Enable package',
                '❌ Disable package',
                '🔍 Search packages',
                '🎨 Generate icons for hidden apps',
                '🧹 Remove bloatware',
                '🔐 Manage permissions',
                '🔙 Back to Main Menu'
            ]

            self.ui.display_menu_with_breadcrumb(' > '.join(self.breadcrumb), options, 'App Management Options')

            choice = self.ui.get_input('Enter your choice (1-9, 0)', default='0')

            if choice == '1':
                if 'app_list' in self.handlers:
                    self.handlers['app_list']()
            elif choice == '2':
                if 'app_install' in self.handlers:
                    self.handlers['app_install']()
            elif choice == '3':
                if 'app_uninstall' in self.handlers:
                    self.handlers['app_uninstall']()
            elif choice == '4':
                if 'app_enable' in self.handlers:
                    self.handlers['app_enable']()
            elif choice == '5':
                if 'app_disable' in self.handlers:
                    self.handlers['app_disable']()
            elif choice == '6':
                if 'app_search' in self.handlers:
                    self.handlers['app_search']()
            elif choice == '7':
                if 'app_icon_generator' in self.handlers:
                    self.handlers['app_icon_generator']()
            elif choice == '8':
                if 'app_bloatware' in self.handlers:
                    self.handlers['app_bloatware']()
            elif choice == '9':
                if 'app_permissions' in self.handlers:
                    self.handlers['app_permissions']()
            elif choice == '0' or choice == '':
                return
            else:
                self.ui.print_error('Invalid choice')
                self.ui.wait_for_key()

    def show_backup_restore_menu(self):
        while self.running:
            self.breadcrumb = ['Main Menu', 'Backup & Restore']

            options = [
                '💾 Backup single package',
                '📦 Batch backup',
                '♻️  Restore single package',
                '📥 Batch restore',
                '📋 List backups',
                '🗑️  Delete backup',
                '🔙 Back to Main Menu'
            ]

            self.ui.display_menu_with_breadcrumb(' > '.join(self.breadcrumb), options, 'Backup & Restore Options')

            choice = self.ui.get_input('Enter your choice (1-6, 0)', default='0')

            if choice == '1':
                if 'backup_single' in self.handlers:
                    self.handlers['backup_single']()
            elif choice == '2':
                if 'backup_batch' in self.handlers:
                    self.handlers['backup_batch']()
            elif choice == '3':
                if 'restore_single' in self.handlers:
                    self.handlers['restore_single']()
            elif choice == '4':
                if 'restore_batch' in self.handlers:
                    self.handlers['restore_batch']()
            elif choice == '5':
                if 'backup_list' in self.handlers:
                    self.handlers['backup_list']()
            elif choice == '6':
                if 'backup_delete' in self.handlers:
                    self.handlers['backup_delete']()
            elif choice == '0' or choice == '':
                return
            else:
                self.ui.print_error('Invalid choice')
                self.ui.wait_for_key()

    def show_custom_settings_menu(self):
        while self.running:
            self.breadcrumb = ['Main Menu', 'Custom Settings']

            # Fetch current states for display
            def _get(namespace, key, enabled_val='1'):
                try:
                    r = self.adb.shell_command(f'settings get {namespace} {key}')
                    if r.success:
                        v = r.output.strip()
                        if v == enabled_val:
                            return ' [✅]'
                        elif v in ('null', ''):
                            return ' [❓]'
                        else:
                            return ' [❌]'
                except Exception:
                    pass
                return ''

            gps    = _get('secure', 'location_providers_allowed', 'gps,network')
            upd    = _get('global', 'ota_disable_automatic_update', '0')
            usb    = _get('global', 'adb_enabled', '1')
            adbnet = _get('global', 'adb_wifi_enabled', '1')
            # adb_wifi_enabled is read-only on Fire OS / many Android TV builds — show note
            if adbnet == ' [❌]':
                adbnet = ' [use tcpip]'
            awake  = _get('global', 'stay_on_while_plugged_in', '7')
            unk    = _get('secure', 'install_non_market_apps', '1')

            # screen timeout current value
            try:
                r = self.adb.shell_command('settings get system screen_off_timeout')
                ms = int(r.output.strip()) if r.success and r.output.strip().lstrip('-').isdigit() else None
                if ms == -1:
                    tout = ' [Never]'
                elif ms and ms < 60000:
                    tout = f' [{ms // 1000}s]'
                elif ms:
                    tout = f' [{ms // 60000}m]'
                else:
                    tout = ''
            except Exception:
                tout = ''

            # animation scale
            try:
                r = self.adb.shell_command('settings get global window_animation_scale')
                anim = f' [{r.output.strip()}x]' if r.success and r.output.strip() not in ('null', '') else ''
            except Exception:
                anim = ''

            options = [
                f'📍 GPS Location{gps}',
                f'⏰ Screen Timeout{tout}',
                f'🔄 Automatic Updates{upd}',
                f'🎬 Animation Scale{anim}',
                f'🔌 USB Debugging{usb}',
                f'📡 ADB over Network{adbnet}',
                f'⚡ Stay Awake{awake}',
                f'🔓 Unknown Sources{unk}',
                '🔙 Back to Main Menu'
            ]

            self.ui.display_menu_with_breadcrumb(' > '.join(self.breadcrumb), options, 'Custom Settings Options')

            choice = self.ui.get_input('Enter your choice (1-8, 0)', default='0')

            if choice == '1':
                if 'settings_gps' in self.handlers:
                    self.handlers['settings_gps']()
            elif choice == '2':
                if 'settings_timeout' in self.handlers:
                    self.handlers['settings_timeout']()
            elif choice == '3':
                if 'settings_updates' in self.handlers:
                    self.handlers['settings_updates']()
            elif choice == '4':
                if 'settings_animation' in self.handlers:
                    self.handlers['settings_animation']()
            elif choice == '5':
                if 'settings_usb_debug' in self.handlers:
                    self.handlers['settings_usb_debug']()
            elif choice == '6':
                if 'settings_adb_network' in self.handlers:
                    self.handlers['settings_adb_network']()
            elif choice == '7':
                if 'settings_stay_awake' in self.handlers:
                    self.handlers['settings_stay_awake']()
            elif choice == '8':
                if 'settings_unknown_sources' in self.handlers:
                    self.handlers['settings_unknown_sources']()
            elif choice == '0' or choice == '':
                return
            else:
                self.ui.print_error('Invalid choice')
                self.ui.wait_for_key()

    def show_display_settings_menu(self):
        while self.running:
            self.breadcrumb = ['Main Menu', 'Display Settings']

            try:
                r = self.adb.shell_command('wm density')
                dpi = f' [{r.output.strip()}]' if r.success and r.output.strip() else ''
            except Exception:
                dpi = ''

            try:
                r = self.adb.shell_command('settings get system font_scale')
                font = f' [{r.output.strip()}x]' if r.success and r.output.strip() not in ('null', '') else ''
            except Exception:
                font = ''

            options = [
                f'📏 Screen Density{dpi}',
                f'🔤 Font Size{font}',
                '🔙 Back to Main Menu'
            ]

            self.ui.display_menu_with_breadcrumb(' > '.join(self.breadcrumb), options, 'Display Settings Options')

            choice = self.ui.get_input('Enter your choice (1-2, 0)', default='0')

            if choice == '1':
                if 'display_density' in self.handlers:
                    self.handlers['display_density']()
            elif choice == '2':
                if 'display_font' in self.handlers:
                    self.handlers['display_font']()
            elif choice == '0' or choice == '':
                return
            else:
                self.ui.print_error('Invalid choice')
                self.ui.wait_for_key()

    def show_screenshot_recording_menu(self):
        while self.running:
            self.breadcrumb = ['Main Menu', 'Screenshot & Recording']

            options = [
                '📸 Take Screenshot',
                '🎥 Record Screen',
                '🔙 Back to Main Menu'
            ]

            self.ui.display_menu_with_breadcrumb(' > '.join(self.breadcrumb), options, 'Screenshot & Recording Options')

            choice = self.ui.get_input('Enter your choice (1-2, 0)', default='0')

            if choice == '1':
                if 'screenshot_take' in self.handlers:
                    self.handlers['screenshot_take']()
            elif choice == '2':
                if 'recording_start' in self.handlers:
                    self.handlers['recording_start']()
            elif choice == '0' or choice == '':
                return
            else:
                self.ui.print_error('Invalid choice')
                self.ui.wait_for_key()

    def show_installation_helper_menu(self):
        while self.running:
            self.breadcrumb = ['Main Menu', 'Installation Helper']

            options = [
                '📺 SmartTube',
                '🚀 Launchers',
                '📡 IPTV Apps',
                '🏪 App Stores',
                '🔧 Shizuku',
                '🎬 Stremio',
                '🔙 Back to Main Menu'
            ]

            self.ui.display_menu_with_breadcrumb(' > '.join(self.breadcrumb), options, 'Installation Helper Options')

            choice = self.ui.get_input('Enter your choice (1-6, 0)', default='0')

            if choice == '1':
                if 'install_smarttube' in self.handlers:
                    self.handlers['install_smarttube']()
            elif choice == '2':
                if 'install_launchers' in self.handlers:
                    self.handlers['install_launchers']()
            elif choice == '3':
                if 'install_iptv' in self.handlers:
                    self.handlers['install_iptv']()
            elif choice == '4':
                if 'install_stores' in self.handlers:
                    self.handlers['install_stores']()
            elif choice == '5':
                if 'install_shizuku' in self.handlers:
                    self.handlers['install_shizuku']()
            elif choice == '6':
                if 'install_stremio' in self.handlers:
                    self.handlers['install_stremio']()
            elif choice == '0' or choice == '':
                return
            else:
                self.ui.print_error('Invalid choice')
                self.ui.wait_for_key()

    def show_optimizations_menu(self):
        while self.running:
            self.breadcrumb = ['Main Menu', 'Optimizations']

            options = [
                '🚫 Disable Animations',
                '🧹 Clear App Cache',
                '💾 Clear System Cache',
                '⛔ Force Stop Apps',
                '📊 Memory Usage',
                '🔙 Back to Main Menu'
            ]

            self.ui.display_menu_with_breadcrumb(' > '.join(self.breadcrumb), options, 'Optimization Options')

            choice = self.ui.get_input('Enter your choice (1-5, 0)', default='0')

            if choice == '1':
                if 'opt_disable_animations' in self.handlers:
                    self.handlers['opt_disable_animations']()
            elif choice == '2':
                if 'opt_clear_app_cache' in self.handlers:
                    self.handlers['opt_clear_app_cache']()
            elif choice == '3':
                if 'opt_clear_system_cache' in self.handlers:
                    self.handlers['opt_clear_system_cache']()
            elif choice == '4':
                if 'opt_force_stop' in self.handlers:
                    self.handlers['opt_force_stop']()
            elif choice == '5':
                if 'opt_memory_usage' in self.handlers:
                    self.handlers['opt_memory_usage']()
            elif choice == '0' or choice == '':
                return
            else:
                self.ui.print_error('Invalid choice')
                self.ui.wait_for_key()

    def show_voice_commands_menu(self):
        while self.running:
            self.breadcrumb = ['Main Menu', 'Voice Commands']

            options = [
                '🎤 Trigger Voice Input',
                '🗣️  Send Voice Command',
                '🔍 Voice Search',
                '🔙 Back to Main Menu'
            ]

            self.ui.display_menu_with_breadcrumb(' > '.join(self.breadcrumb), options, 'Voice Command Options')

            choice = self.ui.get_input('Enter your choice (1-3, 0)', default='0')

            if choice == '1':
                if 'voice_trigger' in self.handlers:
                    self.handlers['voice_trigger']()
            elif choice == '2':
                if 'voice_command' in self.handlers:
                    self.handlers['voice_command']()
            elif choice == '3':
                if 'voice_search' in self.handlers:
                    self.handlers['voice_search']()
            elif choice == '0' or choice == '':
                return
            else:
                self.ui.print_error('Invalid choice')
                self.ui.wait_for_key()

    def show_remote_control_menu(self):
        while self.running:
            self.breadcrumb = ['Main Menu', 'Remote Control']

            options = [
                '🎮 Launch scrcpy',
                '⌨️  Keyboard Remote',
                '🔋 Power Management',
                '💻 ADB Shell',
                '🔙 Back to Main Menu'
            ]

            self.ui.display_menu_with_breadcrumb(' > '.join(self.breadcrumb), options, 'Remote Control Options')

            choice = self.ui.get_input('Enter your choice (1-4, 0)', default='0')

            if choice == '1':
                if 'remote_scrcpy' in self.handlers:
                    self.handlers['remote_scrcpy']()
            elif choice == '2':
                if 'remote_keyboard' in self.handlers:
                    self.handlers['remote_keyboard']()
            elif choice == '3':
                if 'remote_power' in self.handlers:
                    self.handlers['remote_power']()
            elif choice == '4':
                if 'remote_shell' in self.handlers:
                    self.handlers['remote_shell']()
            elif choice == '0' or choice == '':
                return
            else:
                self.ui.print_error('Invalid choice')
                self.ui.wait_for_key()

    def show_ad_blocking_menu(self):
        while self.running:
            self.breadcrumb = ['Main Menu', 'Ad Blocking']

            options = [
                '🌐 Private DNS Configuration',
                '🛡️  Install AdGuard',
                '🔙 Back to Main Menu'
            ]

            self.ui.display_menu_with_breadcrumb(' > '.join(self.breadcrumb), options, 'Ad Blocking Options')

            choice = self.ui.get_input('Enter your choice (1-2, 0)', default='0')

            if choice == '1':
                if 'adblock_dns' in self.handlers:
                    self.handlers['adblock_dns']()
            elif choice == '2':
                if 'adblock_adguard' in self.handlers:
                    self.handlers['adblock_adguard']()
            elif choice == '0' or choice == '':
                return
            else:
                self.ui.print_error('Invalid choice')
                self.ui.wait_for_key()

    def run(self):
        while self.running:
            try:
                self.show_main_menu()
            except KeyboardInterrupt:
                print()
                if self.ui.confirm('Exit TV Tools for Linux?', default=False):
                    self.running = False
                else:
                    continue
            except Exception as e:
                self.ui.print_error(f'An error occurred: {str(e)}')
                self.ui.wait_for_key()


def create_menu_system(ui_manager: UIManager, adb_manager: ADBManager) -> MenuSystem:
    return MenuSystem(ui_manager, adb_manager)
