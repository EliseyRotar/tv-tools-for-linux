import time
from typing import Optional, List, Dict, Tuple
from urllib.parse import urlparse
import urllib.request
import urllib.error
import json


class RateLimiter:
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: List[float] = []

    def can_make_request(self) -> bool:
        current_time = time.time()
        self.requests = [req_time for req_time in self.requests
                         if current_time - req_time < self.time_window]
        return len(self.requests) < self.max_requests

    def record_request(self):
        self.requests.append(time.time())

    def wait_if_needed(self):
        if not self.can_make_request():
            oldest_request = min(self.requests)
            wait_time = self.time_window - (time.time() - oldest_request)
            if wait_time > 0:
                time.sleep(wait_time + 0.1)
        self.record_request()


class WebSearch:
    OFFICIAL_DOMAINS = {
        'github.com',
        'gitlab.com',
        'google.com',
        'android.com',
        'projectivy.app',
        'smarttube.app',
        'adguard.com',
        'stremio.com',
        'kodi.tv',
        'f-droid.org'
    }

    RELIABLE_DOMAINS = {
        'apkmirror.com',
        'apkpure.com',
        'uptodown.com',
        'androidfilehost.com'
    }

    def __init__(self):
        self.rate_limiter = RateLimiter(max_requests=10, time_window=60)
        self.user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'

    def _make_request(self, url: str, timeout: int = 10) -> Optional[str]:
        self.rate_limiter.wait_if_needed()

        try:
            req = urllib.request.Request(url, headers={'User-Agent': self.user_agent})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read().decode('utf-8', errors='ignore')
        except urllib.error.URLError:
            return None
        except Exception:
            return None

    def is_official_source(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            for official_domain in self.OFFICIAL_DOMAINS:
                if domain == official_domain or domain.endswith('.' + official_domain):
                    return True

            return False
        except Exception:
            return False

    def is_reliable_source(self, url: str) -> bool:
        if self.is_official_source(url):
            return True

        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            for reliable_domain in self.RELIABLE_DOMAINS:
                if domain == reliable_domain or domain.endswith('.' + reliable_domain):
                    return True

            return False
        except Exception:
            return False

    def find_latest_apk_url(self, app_name: str, github_repo: Optional[str] = None) -> Optional[Dict[str, str]]:
        if github_repo:
            return self._find_github_release(github_repo)

        return None

    def _find_github_release(self, repo: str) -> Optional[Dict[str, str]]:
        api_url = f'https://api.github.com/repos/{repo}/releases/latest'

        try:
            req = urllib.request.Request(api_url, headers={
                'User-Agent': self.user_agent,
                'Accept': 'application/vnd.github.v3+json'
            })

            self.rate_limiter.wait_if_needed()

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))

                if 'assets' in data and len(data['assets']) > 0:
                    for asset in data['assets']:
                        if asset['name'].endswith('.apk'):
                            return {
                                'url': asset['browser_download_url'],
                                'name': asset['name'],
                                'version': data.get('tag_name', 'unknown'),
                                'size': asset.get('size', 0)
                            }

                if 'tag_name' in data:
                    tag = data['tag_name']
                    apk_patterns = [
                        f'https://github.com/{repo}/releases/download/{tag}/*.apk',
                        f'https://github.com/{repo}/releases/latest/download/*.apk'
                    ]

                    return {
                        'url': apk_patterns[1].replace('*.apk', f'{repo.split("/")[1]}.apk'),
                        'name': f'{repo.split("/")[1]}.apk',
                        'version': tag,
                        'size': 0
                    }

        except Exception:
            pass

        return None

    def find_error_solution(self, error_message: str, error_type: str = 'general') -> List[Dict[str, str]]:
        solutions = []

        error_lower = error_message.lower()

        if 'connection' in error_lower or 'connect' in error_lower:
            solutions.extend([
                {
                    'title': 'Verify IP Address',
                    'description': 'Ensure the IP address is correct and the device is on the same network'
                },
                {
                    'title': 'Enable USB Debugging',
                    'description': 'Go to Settings > Developer Options > USB Debugging and enable it'
                },
                {
                    'title': 'Enable Network Debugging',
                    'description': 'Go to Settings > Developer Options > Network Debugging and enable it'
                },
                {
                    'title': 'Check Firewall',
                    'description': 'Ensure port 5555 is not blocked by firewall on either device'
                },
                {
                    'title': 'Restart ADB Server',
                    'description': 'Try killing and restarting the ADB server'
                }
            ])

        elif 'permission' in error_lower or 'denied' in error_lower:
            solutions.extend([
                {
                    'title': 'Grant USB Debugging Permission',
                    'description': 'Accept the USB debugging authorization prompt on your TV device'
                },
                {
                    'title': 'Check File Permissions',
                    'description': 'Ensure you have read/write permissions for the file or directory'
                },
                {
                    'title': 'Run with Elevated Privileges',
                    'description': 'Some operations may require root access on the device'
                }
            ])

        elif 'install' in error_lower or 'package' in error_lower:
            solutions.extend([
                {
                    'title': 'Enable Unknown Sources',
                    'description': 'Go to Settings > Security > Unknown Sources and enable it'
                },
                {
                    'title': 'Check Storage Space',
                    'description': 'Ensure the device has enough free storage space'
                },
                {
                    'title': 'Verify APK File',
                    'description': 'Ensure the APK file is not corrupted and is compatible with your device'
                },
                {
                    'title': 'Uninstall Previous Version',
                    'description': 'If updating, try uninstalling the old version first'
                }
            ])

        elif 'timeout' in error_lower or 'timed out' in error_lower:
            solutions.extend([
                {
                    'title': 'Check Network Connection',
                    'description': 'Ensure both devices have stable network connectivity to avoid timeout'
                },
                {
                    'title': 'Increase Timeout Duration',
                    'description': 'The operation may need more time to complete, increase timeout setting'
                },
                {
                    'title': 'Restart Device',
                    'description': 'Try restarting the Android TV device to resolve timeout issues'
                }
            ])

        elif 'not found' in error_lower or 'no such' in error_lower:
            solutions.extend([
                {
                    'title': 'Verify Path',
                    'description': 'Check that the file or directory path is correct'
                },
                {
                    'title': 'Check Package Name',
                    'description': 'Ensure the package name is spelled correctly'
                },
                {
                    'title': 'Install Missing Dependency',
                    'description': 'The required tool or package may not be installed'
                }
            ])

        else:
            solutions.extend([
                {
                    'title': 'Check ADB Connection',
                    'description': 'Verify that the device is properly connected via ADB'
                },
                {
                    'title': 'Review Error Details',
                    'description': 'Check the full error message for specific information'
                },
                {
                    'title': 'Consult Documentation',
                    'description': 'Refer to the troubleshooting guide for more information'
                }
            ])

        return solutions[:5]

    def search_apk_source(self, app_name: str) -> List[Dict[str, str]]:
        results = []

        known_sources = {
            'smarttube': {
                'name': 'SmartTube',
                'github': 'yuliskov/SmartTube',
                'url': 'https://github.com/yuliskov/SmartTube/releases/latest'
            },
            'projectivy': {
                'name': 'Projectivy Launcher',
                'url': 'https://projectivy.app/download/launcher.apk'
            },
            'flauncher': {
                'name': 'FLauncher',
                'gitlab': 'flauncher/flauncher',
                'url': 'https://gitlab.com/flauncher/flauncher/-/releases'
            },
            'shizuku': {
                'name': 'Shizuku',
                'github': 'RikkaApps/Shizuku',
                'url': 'https://github.com/RikkaApps/Shizuku/releases/latest'
            },
            'stremio': {
                'name': 'Stremio',
                'url': 'https://www.stremio.com/downloads'
            }
        }

        app_lower = app_name.lower().replace(' ', '').replace('-', '')

        for key, info in known_sources.items():
            if key in app_lower or app_lower in key:
                result = {
                    'name': info['name'],
                    'url': info['url'],
                    'source_type': 'official'
                }

                if 'github' in info:
                    github_info = self._find_github_release(info['github'])
                    if github_info:
                        result['download_url'] = github_info['url']
                        result['version'] = github_info['version']

                results.append(result)

        return results

    def validate_url(self, url: str) -> Tuple[bool, str]:
        if not url:
            return False, 'URL is empty'

        try:
            parsed = urlparse(url)

            if not parsed.scheme:
                return False, 'URL missing protocol (http/https)'

            if parsed.scheme not in ['http', 'https']:
                return False, 'URL must use HTTP or HTTPS protocol'

            if not parsed.netloc:
                return False, 'URL missing domain name'

            if not self.is_reliable_source(url):
                return False, 'URL is not from a known reliable source'

            return True, 'URL is valid'

        except Exception as e:
            return False, f'Invalid URL format: {str(e)}'

    def check_url_accessible(self, url: str) -> Tuple[bool, str]:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': self.user_agent})
            req.get_method = lambda: 'HEAD'

            self.rate_limiter.wait_if_needed()

            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return True, 'URL is accessible'
                else:
                    return False, f'URL returned status code {response.status}'

        except urllib.error.HTTPError as e:
            return False, f'HTTP error {e.code}: {e.reason}'
        except urllib.error.URLError as e:
            return False, f'URL error: {str(e.reason)}'
        except Exception as e:
            return False, f'Error accessing URL: {str(e)}'


def create_web_search() -> WebSearch:
    return WebSearch()
