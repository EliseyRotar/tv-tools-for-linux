from typing import Tuple, Optional, Dict
from core.adb_manager import ADBManager
from utils.logger import Logger
from utils.colors import Colors


class AdBlocking:

    DNS_PROVIDERS = {
        'adguard': {
            'name': 'AdGuard DNS',
            'hostname': 'dns.adguard.com',
            'description': 'Blocks ads, trackers, and phishing',
            'type': 'public'
        },
        'adguard_family': {
            'name': 'AdGuard DNS Family',
            'hostname': 'dns-family.adguard.com',
            'description': 'AdGuard DNS + adult content blocking',
            'type': 'public'
        },
        'controld': {
            'name': 'ControlD',
            'hostname': 'freedns.controld.com',
            'description': 'Blocks ads and malware',
            'type': 'public'
        },
        'controld_malware': {
            'name': 'ControlD Malware',
            'hostname': 'malware.controld.com',
            'description': 'Blocks malware only',
            'type': 'public'
        },
        'controld_family': {
            'name': 'ControlD Family',
            'hostname': 'family.controld.com',
            'description': 'Blocks ads, malware, and adult content',
            'type': 'public'
        },
        'cloudflare': {
            'name': 'Cloudflare DNS',
            'hostname': '1dot1dot1dot1.cloudflare-dns.com',
            'description': 'Fast and private DNS (no ad blocking)',
            'type': 'public'
        },
        'google': {
            'name': 'Google DNS',
            'hostname': 'dns.google',
            'description': 'Fast and reliable DNS (no ad blocking)',
            'type': 'public'
        }
    }

    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None):
        self.adb = adb_manager
        self.logger = logger

    def get_private_dns(self) -> Tuple[bool, Optional[str]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🔍 Getting Private DNS Configuration           ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, None

        mode_result = self.adb.shell_command('settings get global private_dns_mode')

        if mode_result.success and mode_result.output:
            mode = mode_result.output.strip()

            if mode == 'off':
                print(f"{Colors.WARNING}⚠️  Private DNS is disabled{Colors.ENDC}")
                return True, 'off'

            elif mode == 'hostname':
                hostname_result = self.adb.shell_command('settings get global private_dns_specifier')

                if hostname_result.success and hostname_result.output:
                    hostname = hostname_result.output.strip()
                    print(f"{Colors.OKGREEN}✅ Private DNS is enabled{Colors.ENDC}")
                    print(f"{Colors.OKBLUE}ℹ️  Mode: Custom hostname{Colors.ENDC}")
                    print(f"{Colors.OKBLUE}ℹ️  Hostname: {hostname}{Colors.ENDC}")

                    provider_name = self._identify_provider(hostname)
                    if provider_name:
                        print(f"{Colors.OKBLUE}ℹ️  Provider: {provider_name}{Colors.ENDC}")

                    return True, hostname
                else:
                    print(f"{Colors.WARNING}⚠️  Private DNS mode is hostname but no hostname set{Colors.ENDC}")
                    return True, 'hostname'

            elif mode == 'opportunistic':
                print(f"{Colors.OKBLUE}ℹ️  Private DNS is in automatic mode{Colors.ENDC}")
                return True, 'opportunistic'

            else:
                print(f"{Colors.OKBLUE}ℹ️  Private DNS mode: {mode}{Colors.ENDC}")
                return True, mode
        else:
            print(f"{Colors.FAIL}❌ Failed to get Private DNS configuration{Colors.ENDC}")
            return False, None

    def _identify_provider(self, hostname: str) -> Optional[str]:
        for key, provider in self.DNS_PROVIDERS.items():
            if provider['hostname'] == hostname:
                return provider['name']
        return None

    def disable_private_dns(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🚫 Disabling Private DNS                       ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        result = self.adb.shell_command('settings put global private_dns_mode off')

        if result.success or result.return_code == 0:
            print(f"{Colors.OKGREEN}✅ Private DNS disabled{Colors.ENDC}")

            if self.logger:
                self.logger.log_event('ad_blocking', 'Disabled private DNS')

            return True, "Private DNS disabled"
        else:
            print(f"{Colors.FAIL}❌ Failed to disable Private DNS{Colors.ENDC}")
            return False, f"Failed to disable: {result.error}"

    def enable_adguard_dns(self, family_mode: bool = False) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🛡️  Enabling AdGuard DNS                       ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        if family_mode:
            hostname = self.DNS_PROVIDERS['adguard_family']['hostname']
            provider_name = self.DNS_PROVIDERS['adguard_family']['name']
            description = self.DNS_PROVIDERS['adguard_family']['description']
        else:
            hostname = self.DNS_PROVIDERS['adguard']['hostname']
            provider_name = self.DNS_PROVIDERS['adguard']['name']
            description = self.DNS_PROVIDERS['adguard']['description']

        print(f"{Colors.OKBLUE}ℹ️  Provider: {provider_name}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Hostname: {hostname}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Features: {description}{Colors.ENDC}\n")

        return self._set_private_dns_hostname(hostname, provider_name)

    def enable_controld_dns(self, mode: str = 'default') -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🛡️  Enabling ControlD DNS                      ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        mode_key = f'controld_{mode}' if mode != 'default' else 'controld'

        if mode_key not in self.DNS_PROVIDERS:
            print(f"{Colors.FAIL}❌ Unknown ControlD mode: {mode}{Colors.ENDC}")
            return False, f"Unknown mode: {mode}"

        provider = self.DNS_PROVIDERS[mode_key]
        hostname = provider['hostname']
        provider_name = provider['name']
        description = provider['description']

        print(f"{Colors.OKBLUE}ℹ️  Provider: {provider_name}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Hostname: {hostname}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Features: {description}{Colors.ENDC}\n")

        return self._set_private_dns_hostname(hostname, provider_name)

    def enable_custom_dns(self, hostname: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🛡️  Enabling Custom DNS                        ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        if not hostname or not hostname.strip():
            print(f"{Colors.FAIL}❌ Invalid hostname{Colors.ENDC}")
            return False, "Invalid hostname"

        print(f"{Colors.OKBLUE}ℹ️  Hostname: {hostname}{Colors.ENDC}\n")

        return self._set_private_dns_hostname(hostname, "Custom DNS")

    def _set_private_dns_hostname(self, hostname: str, provider_name: str) -> Tuple[bool, str]:
        hostname_result = self.adb.shell_command(f'settings put global private_dns_specifier {hostname}')

        if not (hostname_result.success or hostname_result.return_code == 0):
            print(f"{Colors.FAIL}❌ Failed to set DNS hostname{Colors.ENDC}")
            return False, f"Failed to set hostname: {hostname_result.error}"

        mode_result = self.adb.shell_command('settings put global private_dns_mode hostname')

        if mode_result.success or mode_result.return_code == 0:
            print(f"{Colors.OKGREEN}✅ {provider_name} enabled{Colors.ENDC}")
            print(f"{Colors.OKBLUE}ℹ️  DNS hostname: {hostname}{Colors.ENDC}")

            if self.logger:
                self.logger.log_event('ad_blocking', f'Enabled {provider_name}: {hostname}')

            return True, f"{provider_name} enabled"
        else:
            print(f"{Colors.FAIL}❌ Failed to enable Private DNS mode{Colors.ENDC}")
            return False, f"Failed to enable mode: {mode_result.error}"

    def verify_dns_connection(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ✓ Verifying DNS Connection                     ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        success, current_dns = self.get_private_dns()

        if not success:
            return False, "Could not get DNS configuration"

        if current_dns == 'off':
            print(f"{Colors.WARNING}⚠️  Private DNS is disabled{Colors.ENDC}")
            return True, "DNS disabled"

        print(f"{Colors.OKBLUE}ℹ️  Testing DNS resolution...{Colors.ENDC}")

        result = self.adb.shell_command('ping -c 1 -W 2 google.com')

        if result.success or result.return_code == 0:
            print(f"{Colors.OKGREEN}✅ DNS is working correctly{Colors.ENDC}")
            return True, "DNS working"
        else:
            print(f"{Colors.WARNING}⚠️  DNS test failed or no internet connection{Colors.ENDC}")
            return False, "DNS test failed"

    def list_dns_providers(self) -> Dict[str, Dict[str, str]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📋 Available DNS Providers                     ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}🛡️  Ad-Blocking DNS Providers:{Colors.ENDC}\n")

        for key, provider in self.DNS_PROVIDERS.items():
            if 'adguard' in key or 'controld' in key:
                print(f"{Colors.OKBLUE}• {provider['name']:25} - {provider['description']}{Colors.ENDC}")
                print(f"{Colors.OKBLUE}  Hostname: {provider['hostname']}{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}🌐 Standard DNS Providers:{Colors.ENDC}\n")

        for key, provider in self.DNS_PROVIDERS.items():
            if key in ['cloudflare', 'google']:
                print(f"{Colors.OKBLUE}• {provider['name']:25} - {provider['description']}{Colors.ENDC}")
                print(f"{Colors.OKBLUE}  Hostname: {provider['hostname']}{Colors.ENDC}\n")

        return self.DNS_PROVIDERS.copy()

    def install_adguard_app(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📦 Installing AdGuard App                      ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        print(f"{Colors.OKBLUE}ℹ️  AdGuard for Android TV{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Official source: https://adguard.com{Colors.ENDC}\n")

        print(f"{Colors.WARNING}⚠️  Manual Installation Required{Colors.ENDC}")
        print(f"{Colors.OKBLUE}📋 Installation Steps:{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}1. Download AdGuard APK:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   • Visit: https://adguard.com/en/adguard-android/overview.html{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   • Download the latest APK for Android TV{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}2. Transfer APK to device:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   • Use file transfer feature in this tool{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   • Or use: adb push adguard.apk /sdcard/{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}3. Install APK:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   • Use package manager in this tool{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   • Or use: adb install adguard.apk{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}4. Configure AdGuard:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   • Launch AdGuard app on your TV{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   • Follow the setup wizard{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   • Enable local VPN for ad blocking{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}💡 Alternative: Use Private DNS{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   • Private DNS is easier to set up{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   • Use enable_adguard_dns() method{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   • No app installation required{Colors.ENDC}\n")

        if self.logger:
            self.logger.log_event('ad_blocking', 'Displayed AdGuard installation instructions')

        return True, "AdGuard installation instructions displayed"

    def launch_adguard_app(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🚀 Launching AdGuard App                       ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        adguard_packages = [
            'com.adguard.android',
            'com.adguard.android.contentblocker'
        ]

        print(f"{Colors.OKBLUE}ℹ️  Searching for AdGuard app...{Colors.ENDC}\n")

        for package in adguard_packages:
            check_result = self.adb.shell_command(f'pm list packages {package}')

            if check_result.success and package in check_result.output:
                print(f"{Colors.OKGREEN}✅ Found AdGuard: {package}{Colors.ENDC}")
                print(f"{Colors.OKBLUE}ℹ️  Launching app...{Colors.ENDC}\n")

                launch_result = self.adb.shell_command(f'monkey -p {package} -c android.intent.category.LAUNCHER 1')

                if launch_result.success or launch_result.return_code == 0:
                    print(f"{Colors.OKGREEN}✅ AdGuard launched{Colors.ENDC}")

                    if self.logger:
                        self.logger.log_event('ad_blocking', f'Launched AdGuard: {package}')

                    return True, f"Launched {package}"
                else:
                    print(f"{Colors.FAIL}❌ Failed to launch AdGuard{Colors.ENDC}")
                    return False, f"Failed to launch: {launch_result.error}"

        print(f"{Colors.WARNING}⚠️  AdGuard app not found{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Use install_adguard_app() for installation instructions{Colors.ENDC}")

        return False, "AdGuard app not installed"

    def check_adguard_installed(self) -> Tuple[bool, Optional[str]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🔍 Checking AdGuard Installation               ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, None

        adguard_packages = [
            'com.adguard.android',
            'com.adguard.android.contentblocker'
        ]

        for package in adguard_packages:
            result = self.adb.shell_command(f'pm list packages {package}')

            if result.success and package in result.output:
                print(f"{Colors.OKGREEN}✅ AdGuard is installed{Colors.ENDC}")
                print(f"{Colors.OKBLUE}ℹ️  Package: {package}{Colors.ENDC}")

                version_result = self.adb.shell_command(f'dumpsys package {package} | grep versionName')
                if version_result.success and version_result.output:
                    version = version_result.output.strip().split(
                        '=')[-1] if '=' in version_result.output else 'Unknown'
                    print(f"{Colors.OKBLUE}ℹ️  Version: {version}{Colors.ENDC}")

                return True, package

        print(f"{Colors.WARNING}⚠️  AdGuard is not installed{Colors.ENDC}")
        return False, None

    def get_adguard_configuration_guide(self) -> str:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📖 AdGuard Configuration Guide                 ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        guide = """
🛡️  AdGuard Configuration Steps:

1. Initial Setup:
   • Launch AdGuard app on your Android TV
   • Accept the license agreement
   • Grant necessary permissions

2. Enable Protection:
   • Tap "Enable Protection" button
   • Allow VPN connection (required for ad blocking)
   • AdGuard creates a local VPN to filter traffic

3. Configure Filters:
   • Go to Settings → Filters
   • Enable recommended filter lists:
     - AdGuard Base filter
     - AdGuard Mobile Ads filter
     - EasyList
   • Add custom filters if needed

4. DNS Settings:
   • Go to Settings → DNS filtering
   • Enable DNS filtering
   • Choose DNS server (AdGuard DNS recommended)
   • Enable DNS-over-HTTPS or DNS-over-TLS

5. App Management:
   • Go to Settings → Apps management
   • Configure per-app filtering
   • Whitelist apps that need direct connection

6. Advanced Settings:
   • HTTPS filtering (optional, requires certificate)
   • Firewall rules
   • Custom filtering rules
   • Statistics and logs

💡 Tips:
   • Keep AdGuard updated for latest filters
   • Check statistics to see blocked ads
   • Use whitelist for apps with connection issues
   • Combine with Private DNS for extra protection

⚠️  Note:
   • VPN-based ad blocking may affect some apps
   • Some streaming services may detect VPN
   • Battery usage may increase slightly
"""

        print(f"{Colors.OKBLUE}{guide}{Colors.ENDC}")

        return guide

    def close(self):
        pass


def create_ad_blocking(adb_manager: ADBManager, logger: Optional[Logger] = None) -> AdBlocking:
    return AdBlocking(adb_manager, logger)


def get_default_ad_blocking(adb_manager: ADBManager) -> AdBlocking:
    from utils.logger import get_default_logger
    return AdBlocking(adb_manager, get_default_logger())
