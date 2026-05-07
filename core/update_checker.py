from typing import Tuple, Optional, Dict
import requests
import re
from packaging import version
from utils.logger import Logger
from utils.colors import Colors


class UpdateChecker:

    GITHUB_API_URL = "https://api.github.com/repos/{owner}/{repo}/releases/latest"
    CURRENT_VERSION = "1.0.0"
    GITHUB_OWNER = "eli6"
    GITHUB_REPO = "android-tv-tools-linux"

    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger
        self.latest_version: Optional[str] = None
        self.latest_release_url: Optional[str] = None
        self.changelog: Optional[str] = None

    def check_for_updates(self, current_version: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🔄 Checking for Updates                        ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if current_version is None:
            current_version = self.CURRENT_VERSION

        print(f"{Colors.OKBLUE}ℹ️  Current version: {current_version}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Checking GitHub for updates...{Colors.ENDC}\n")

        try:
            api_url = self.GITHUB_API_URL.format(
                owner=self.GITHUB_OWNER,
                repo=self.GITHUB_REPO
            )

            response = requests.get(api_url, timeout=10)

            if response.status_code == 404:
                print(f"{Colors.WARNING}⚠️  Repository not found or no releases available{Colors.ENDC}")
                return False, None

            if response.status_code != 200:
                print(f"{Colors.FAIL}❌ Failed to check for updates (HTTP {response.status_code}){Colors.ENDC}")
                return False, None

            release_data = response.json()

            latest_tag = release_data.get('tag_name', '')
            latest_version = self._extract_version(latest_tag)

            if not latest_version:
                print(f"{Colors.WARNING}⚠️  Could not parse version from tag: {latest_tag}{Colors.ENDC}")
                return False, None

            self.latest_version = latest_version
            self.latest_release_url = release_data.get('html_url', '')
            self.changelog = release_data.get('body', '')

            print(f"{Colors.OKBLUE}ℹ️  Latest version: {latest_version}{Colors.ENDC}\n")

            if self._is_newer_version(current_version, latest_version):
                print(f"{Colors.OKGREEN}🎉 New version available!{Colors.ENDC}")
                print(f"{Colors.OKGREEN}   Current: {current_version}{Colors.ENDC}")
                print(f"{Colors.OKGREEN}   Latest:  {latest_version}{Colors.ENDC}\n")

                if self.logger:
                    self.logger.log_event('update_checker', f'Update available: {latest_version}')

                return True, latest_version
            else:
                print(f"{Colors.OKGREEN}✅ You are using the latest version{Colors.ENDC}")
                return False, latest_version

        except requests.exceptions.Timeout:
            print(f"{Colors.FAIL}❌ Request timed out{Colors.ENDC}")
            return False, None

        except requests.exceptions.ConnectionError:
            print(f"{Colors.FAIL}❌ Connection error - check your internet connection{Colors.ENDC}")
            return False, None

        except Exception as e:
            print(f"{Colors.FAIL}❌ Error checking for updates: {e}{Colors.ENDC}")
            return False, None

    def _extract_version(self, tag: str) -> Optional[str]:
        match = re.search(r'(\d+\.\d+\.\d+)', tag)
        return match.group(1) if match else None

    def _is_newer_version(self, current: str, latest: str) -> bool:
        try:
            return version.parse(latest) > version.parse(current)
        except Exception:
            return False

    def display_changelog(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📋 Changelog                                   ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.changelog:
            print(f"{Colors.WARNING}⚠️  No changelog available{Colors.ENDC}")
            print(f"{Colors.OKBLUE}ℹ️  Run check_for_updates() first{Colors.ENDC}")
            return False, "No changelog available"

        if not self.latest_version:
            print(f"{Colors.WARNING}⚠️  Version information not available{Colors.ENDC}")
            return False, "Version not available"

        print(f"{Colors.OKBLUE}📦 Version: {self.latest_version}{Colors.ENDC}\n")
        print(f"{Colors.OKBLUE}{self.changelog}{Colors.ENDC}\n")

        if self.latest_release_url:
            print(f"{Colors.OKBLUE}🔗 Release URL: {self.latest_release_url}{Colors.ENDC}")

        return True, self.changelog

    def get_download_url(self) -> Tuple[bool, Optional[str]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📥 Download Information                        ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.latest_release_url:
            print(f"{Colors.WARNING}⚠️  No release URL available{Colors.ENDC}")
            print(f"{Colors.OKBLUE}ℹ️  Run check_for_updates() first{Colors.ENDC}")
            return False, None

        print(f"{Colors.OKBLUE}📦 Latest version: {self.latest_version}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}🔗 Release page: {self.latest_release_url}{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}💡 To update:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   1. Visit the release page above{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   2. Download the latest version{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   3. Follow installation instructions{Colors.ENDC}\n")

        return True, self.latest_release_url

    def download_update(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📥 Download Update                             ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.latest_release_url:
            print(f"{Colors.WARNING}⚠️  No update available{Colors.ENDC}")
            print(f"{Colors.OKBLUE}ℹ️  Run check_for_updates() first{Colors.ENDC}")
            return False, "No update available"

        print(f"{Colors.OKBLUE}📦 Version: {self.latest_version}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}🔗 URL: {self.latest_release_url}{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}💡 Manual download required:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   Visit: {self.latest_release_url}{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}📋 Installation steps:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   1. Download the latest release{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   2. Extract the archive{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   3. Run: ./install.sh{Colors.ENDC}")
        print(f"{Colors.OKBLUE}   4. Restart the application{Colors.ENDC}\n")

        if self.logger:
            self.logger.log_event('update_checker', f'Download info displayed for {self.latest_version}')

        return True, f"Download available: {self.latest_release_url}"

    def get_version_comparison(self, current_version: Optional[str] = None) -> Dict[str, str]:
        if current_version is None:
            current_version = self.CURRENT_VERSION

        return {
            'current': current_version,
            'latest': self.latest_version or 'Unknown',
            'update_available': str(
                self._is_newer_version(
                    current_version,
                    self.latest_version) if self.latest_version else False),
            'release_url': self.latest_release_url or ''}

    def set_github_repo(self, owner: str, repo: str):
        self.GITHUB_OWNER = owner
        self.GITHUB_REPO = repo

    def close(self):
        pass


def create_update_checker(logger: Optional[Logger] = None) -> UpdateChecker:
    return UpdateChecker(logger)


def get_default_update_checker() -> UpdateChecker:
    from utils.logger import get_default_logger
    return UpdateChecker(get_default_logger())
