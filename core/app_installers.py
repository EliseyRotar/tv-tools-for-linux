from typing import Tuple, Optional
from core.install_helper import InstallHelper
from core.adb_manager import ADBManager
from utils.logger import Logger
from utils.colors import Colors


class AppInstallers:

    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None):
        self.adb = adb_manager
        self.logger = logger
        self.helper = InstallHelper(adb_manager, logger)

    def install_smarttube(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📺 SmartTube Installation                     ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  SmartTube: Ad-free YouTube client for Android TV{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Features: No ads, SponsorBlock, 4K, Background playback{Colors.ENDC}\n")

        return self.helper.download_and_install('smarttube')

    def install_projectivy(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🚀 Projectivy Launcher Installation            ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  Projectivy: Customizable launcher for Android TV{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Features: Ad-free, Highly customizable, Smooth{Colors.ENDC}\n")

        return self.helper.download_and_install('projectivy_launcher')

    def install_flauncher(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🎯 FLauncher Installation                      ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  FLauncher: Minimalist open-source launcher{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Features: Simple, Fast, Open source, No ads{Colors.ENDC}\n")

        return self.helper.download_and_install('flauncher')

    def install_google_tv_launcher(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📱 Google TV Launcher Installation             ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  Google TV Launcher: Official Google TV home screen{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Features: Content recommendations, Google Assistant{Colors.ENDC}\n")

        return self.helper.download_and_install('google_tv_launcher')

    def install_atv_launcher_pro(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ⚡ ATV Launcher Pro Installation               ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  ATV Launcher Pro: Fast and elegant launcher{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Features: Fast, Ad-free, Customizable widgets{Colors.ENDC}\n")

        return self.helper.download_and_install('atv_launcher_pro')

    def get_current_launcher(self) -> Optional[str]:
        result = self.adb.shell_command(
            'cmd package resolve-activity --brief -c android.intent.category.HOME | tail -n 1')
        if result.success and result.output:
            return result.output.strip()
        return None

    def set_default_launcher(self, package_name: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🏠 Set Default Launcher                        ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        current = self.get_current_launcher()
        if current:
            print(f"{Colors.OKBLUE}ℹ️  Current launcher: {current}{Colors.ENDC}\n")

        result = self.adb.shell_command(f'cmd package set-home-activity {package_name}')

        if result.success:
            print(f"{Colors.OKGREEN}✅ Default launcher set to: {package_name}{Colors.ENDC}")
            return True, f"Default launcher set to {package_name}"
        else:
            print(f"{Colors.FAIL}❌ Failed to set default launcher{Colors.ENDC}")
            return False, f"Failed to set default launcher: {result.error}"

    def install_tivimate(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📡 TiviMate IPTV Installation                  ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  TiviMate: Feature-rich IPTV player{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Features: EPG, Multiple playlists, Recording{Colors.ENDC}\n")

        return self.helper.download_and_install('tivimate')

    def install_kodi(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🎬 Kodi Media Center Installation              ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  Kodi: Open-source media center{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Features: Media library, Addons, Network streaming{Colors.ENDC}\n")

        return self.helper.download_and_install('kodi')

    def install_tdtchannels(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📺 TDTChannels Installation                    ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  TDTChannels: Spanish free-to-air TV channels{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Features: Spanish TV, Free content, EPG support{Colors.ENDC}\n")

        return self.helper.download_and_install('tdtchannels')

    def upload_m3u_list(self, local_path: str, remote_path: str = '/sdcard/playlist.m3u') -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📋 Upload M3U Playlist                         ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        import os
        if not os.path.exists(local_path):
            print(f"{Colors.FAIL}❌ File not found: {local_path}{Colors.ENDC}")
            return False, f"File not found: {local_path}"

        if not local_path.lower().endswith('.m3u'):
            print(f"{Colors.YELLOW}⚠️  Warning: File does not have .m3u extension{Colors.ENDC}")

        print(f"{Colors.OKBLUE}ℹ️  Uploading: {local_path}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Destination: {remote_path}{Colors.ENDC}\n")

        success, message = self.adb.push_file(local_path, remote_path)

        if success:
            print(f"{Colors.OKGREEN}✅ M3U playlist uploaded successfully{Colors.ENDC}")
            return True, "M3U playlist uploaded successfully"
        else:
            print(f"{Colors.FAIL}❌ Failed to upload M3U playlist{Colors.ENDC}")
            return False, f"Failed to upload: {message}"

    def install_aurora_store(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🌟 Aurora Store Installation                   ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  Aurora Store: Open-source Play Store alternative{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Features: No Google account, Anonymous downloads{Colors.ENDC}\n")

        return self.helper.download_and_install('aurora_store')

    def install_aptoide_tv(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🏪 Aptoide TV Installation                     ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  Aptoide TV: Independent app store for Android TV{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Features: TV-optimized, No registration required{Colors.ENDC}\n")

        return self.helper.download_and_install('aptoide_tv')

    def install_play_store(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🛒 Google Play Store Installation              ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.YELLOW}⚠️  Note: Play Store requires Google Services Framework{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  This will install Play Store and dependencies{Colors.ENDC}\n")

        print(f"{Colors.HEADER}Step 1/2: Installing Google Services Framework...{Colors.ENDC}")
        gsf_result = self.adb.shell_command('pm list packages | grep com.google.android.gsf')

        if not gsf_result.success or 'com.google.android.gsf' not in gsf_result.output:
            print(f"{Colors.YELLOW}⚠️  Google Services Framework not found{Colors.ENDC}")
            print(f"{Colors.OKBLUE}ℹ️  Please install GSF manually or use Aurora Store{Colors.ENDC}\n")
        else:
            print(f"{Colors.OKGREEN}✅ Google Services Framework already installed{Colors.ENDC}\n")

        print(f"{Colors.HEADER}Step 2/2: Installing Play Store...{Colors.ENDC}")
        return self.helper.download_and_install('play_store')

    def install_shizuku(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🔧 Shizuku Installation                        ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  Shizuku: System API access without root{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Features: No root required, ADB-based permissions{Colors.ENDC}\n")

        success, message = self.helper.download_and_install('shizuku')

        if success:
            print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
            print(f"{Colors.HEADER}║           📋 Shizuku Setup Instructions                  ║{Colors.ENDC}")
            print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

            print(f"{Colors.YELLOW}To start Shizuku service:{Colors.ENDC}")
            print(f"{Colors.OKBLUE}1. Open Shizuku app on your device{Colors.ENDC}")
            print(f"{Colors.OKBLUE}2. Follow the on-screen instructions{Colors.ENDC}")
            print(f"{Colors.OKBLUE}3. Or run: adb shell sh /sdcard/Android/data/moe.shizuku.privileged.api/start.sh{Colors.ENDC}\n")

        return success, message

    def start_shizuku_service(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🚀 Starting Shizuku Service                    ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        result = self.adb.shell_command('sh /sdcard/Android/data/moe.shizuku.privileged.api/start.sh')

        if result.success:
            print(f"{Colors.OKGREEN}✅ Shizuku service started successfully{Colors.ENDC}")
            print(f"{Colors.OKBLUE}ℹ️  Open Shizuku app to grant permissions{Colors.ENDC}")
            return True, "Shizuku service started"
        else:
            print(f"{Colors.FAIL}❌ Failed to start Shizuku service{Colors.ENDC}")
            print(f"{Colors.YELLOW}⚠️  Make sure Shizuku is installed first{Colors.ENDC}")
            return False, f"Failed to start service: {result.error}"

    def install_stremio(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🎥 Stremio Installation                        ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  Stremio: Video streaming with addon support{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Features: Torrent streaming, Library management{Colors.ENDC}\n")

        success, message = self.helper.download_and_install('stremio')

        if success:
            print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
            print(f"{Colors.HEADER}║           🔌 Torrentio Addon Configuration               ║{Colors.ENDC}")
            print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

            print(f"{Colors.YELLOW}To install Torrentio addon:{Colors.ENDC}")
            print(f"{Colors.OKBLUE}1. Visit: https://torrentio.strem.fun/configure{Colors.ENDC}")
            print(f"{Colors.OKBLUE}2. Configure your preferences{Colors.ENDC}")
            print(f"{Colors.OKBLUE}3. Click 'Install' to add to Stremio{Colors.ENDC}\n")

        return success, message

    def open_torrentio_config(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🌐 Opening Torrentio Configuration             ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        url = 'https://torrentio.strem.fun/configure'
        result = self.adb.shell_command(f'am start -a android.intent.action.VIEW -d "{url}"')

        if result.success:
            print(f"{Colors.OKGREEN}✅ Opened Torrentio configuration in browser{Colors.ENDC}")
            return True, "Torrentio config opened"
        else:
            print(f"{Colors.FAIL}❌ Failed to open browser{Colors.ENDC}")
            print(f"{Colors.OKBLUE}ℹ️  Manual URL: {url}{Colors.ENDC}")
            return False, f"Failed to open browser: {result.error}"

    def close(self):
        if self.helper:
            self.helper.close()


def create_app_installers(adb_manager: ADBManager, logger: Optional[Logger] = None) -> AppInstallers:
    return AppInstallers(adb_manager, logger)


def get_default_app_installers(adb_manager: ADBManager) -> AppInstallers:
    from utils.logger import get_default_logger
    return AppInstallers(adb_manager, get_default_logger())
