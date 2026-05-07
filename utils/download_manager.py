import os
import time
import hashlib
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
from utils.colors import Colors
from utils.ui_components import Emoji, ProgressBar
from utils.logger import get_default_logger


class DownloadProgress:
    def __init__(self, url: str, filename: str, total_size: int):
        self.url = url
        self.filename = filename
        self.total_size = total_size
        self.downloaded_size = 0
        self.speed = 0.0
        self.eta = 0
        self.status = 'pending'
        self.start_time = time.time()

    def update(self, downloaded: int):
        self.downloaded_size = downloaded
        elapsed = time.time() - self.start_time

        if elapsed > 0:
            self.speed = self.downloaded_size / elapsed

            if self.speed > 0:
                remaining = self.total_size - self.downloaded_size
                self.eta = int(remaining / self.speed)

    def get_percentage(self) -> int:
        if self.total_size == 0:
            return 0
        return int((self.downloaded_size / self.total_size) * 100)

    def get_speed_str(self) -> str:
        if self.speed < 1024:
            return f'{self.speed:.2f} B/s'
        elif self.speed < 1024 * 1024:
            return f'{self.speed / 1024:.2f} KB/s'
        else:
            return f'{self.speed / (1024 * 1024):.2f} MB/s'

    def get_eta_str(self) -> str:
        if self.eta < 60:
            return f'{self.eta}s'
        elif self.eta < 3600:
            minutes = self.eta // 60
            seconds = self.eta % 60
            return f'{minutes}m {seconds}s'
        else:
            hours = self.eta // 3600
            minutes = (self.eta % 3600) // 60
            return f'{hours}h {minutes}m'

    def get_size_str(self, size: int) -> str:
        if size < 1024:
            return f'{size} B'
        elif size < 1024 * 1024:
            return f'{size / 1024:.2f} KB'
        elif size < 1024 * 1024 * 1024:
            return f'{size / (1024 * 1024):.2f} MB'
        else:
            return f'{size / (1024 * 1024 * 1024):.2f} GB'


class DownloadObserver:
    def on_progress(self, progress: DownloadProgress):
        pass

    def on_complete(self, filename: str, filepath: str):
        pass

    def on_error(self, error: str):
        pass

    def on_start(self, filename: str, total_size: int):
        pass


class ConsoleDownloadObserver(DownloadObserver):
    def __init__(self):
        self.last_update = 0
        self.update_interval = 0.5

    def on_start(self, filename: str, total_size: int):
        size_str = DownloadProgress('', '', total_size).get_size_str(total_size)
        print(f'\n{Colors.OKCYAN}{Emoji.DOWNLOAD} Starting download: {filename} ({size_str}){Colors.ENDC}')

    def on_progress(self, progress: DownloadProgress):
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return

        self.last_update = current_time

        speed = progress.get_speed_str()
        eta = progress.get_eta_str()
        downloaded = progress.get_size_str(progress.downloaded_size)
        total = progress.get_size_str(progress.total_size)

        bar = ProgressBar.render(
            progress.downloaded_size,
            progress.total_size,
            width=40
        )

        status_line = f'\r{bar} | {downloaded}/{total} | {speed} | ETA: {eta}'
        print(status_line, end='', flush=True)

    def on_complete(self, filename: str, filepath: str):
        print(f'\n{Colors.OKGREEN}{Emoji.CHECK} Download complete: {filename}{Colors.ENDC}')
        print(f'{Colors.OKBLUE}Saved to: {filepath}{Colors.ENDC}')

    def on_error(self, error: str):
        print(f'\n{Colors.FAIL}{Emoji.CROSS} Download failed: {error}{Colors.ENDC}')


class DownloadManager:
    def __init__(self, temp_dir: Optional[str] = None):
        self.logger = get_default_logger()

        if temp_dir is None:
            home = Path.home()
            self.temp_dir = home / '.android-tv-tools' / 'downloads'
        else:
            self.temp_dir = Path(temp_dir)

        self._ensure_temp_directory()

        self.observers: List[DownloadObserver] = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        self.chunk_size = 8192
        self.timeout = 30
        self.max_retries = 3

    def _ensure_temp_directory(self):
        try:
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f'Temp directory ensured: {self.temp_dir}')
        except Exception as e:
            self.logger.error(f'Failed to create temp directory: {e}', exception=e)
            raise

    def add_observer(self, observer: DownloadObserver):
        self.observers.append(observer)

    def remove_observer(self, observer: DownloadObserver):
        if observer in self.observers:
            self.observers.remove(observer)

    def _notify_start(self, filename: str, total_size: int):
        for observer in self.observers:
            try:
                observer.on_start(filename, total_size)
            except Exception as e:
                self.logger.error(f'Observer error on_start: {e}', exception=e)

    def _notify_progress(self, progress: DownloadProgress):
        for observer in self.observers:
            try:
                observer.on_progress(progress)
            except Exception as e:
                self.logger.error(f'Observer error on_progress: {e}', exception=e)

    def _notify_complete(self, filename: str, filepath: str):
        for observer in self.observers:
            try:
                observer.on_complete(filename, filepath)
            except Exception as e:
                self.logger.error(f'Observer error on_complete: {e}', exception=e)

    def _notify_error(self, error: str):
        for observer in self.observers:
            try:
                observer.on_error(error)
            except Exception as e:
                self.logger.error(f'Observer error on_error: {e}', exception=e)

    def _get_filename_from_url(self, url: str) -> str:
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)

        if not filename or filename == '/':
            filename = 'download.apk'

        return filename

    def _get_file_size(self, url: str) -> Optional[int]:
        try:
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)

            if response.status_code == 200:
                content_length = response.headers.get('Content-Length')
                if content_length:
                    return int(content_length)

            response = self.session.get(url, stream=True, timeout=self.timeout)
            content_length = response.headers.get('Content-Length')
            if content_length:
                return int(content_length)

            return None

        except Exception as e:
            self.logger.warning(f'Failed to get file size: {e}')
            return None

    def _supports_resume(self, url: str) -> bool:
        try:
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
            return 'Accept-Ranges' in response.headers and response.headers['Accept-Ranges'] == 'bytes'
        except Exception:
            return False

    def download_file(self, url: str, destination: Optional[str] = None,
                      resume: bool = True, verify_integrity: bool = True,
                      expected_hash: Optional[str] = None) -> bool:
        try:
            filename = self._get_filename_from_url(url)

            if destination is None:
                filepath = self.temp_dir / filename
            else:
                filepath = Path(destination)
                if filepath.is_dir():
                    filepath = filepath / filename

            self.logger.info(f'Starting download: {url} -> {filepath}')

            total_size = self._get_file_size(url)
            if total_size is None:
                self.logger.warning('Could not determine file size')
                total_size = 0

            existing_size = 0
            if resume and filepath.exists():
                existing_size = filepath.stat().st_size

                if existing_size == total_size and total_size > 0:
                    self.logger.info('File already downloaded completely')
                    self._notify_complete(filename, str(filepath))
                    return True

                if not self._supports_resume(url):
                    self.logger.info('Server does not support resume, starting fresh')
                    existing_size = 0
                    filepath.unlink()

            progress = DownloadProgress(url, filename, total_size)
            progress.downloaded_size = existing_size

            self._notify_start(filename, total_size)

            headers = {}
            if existing_size > 0 and resume:
                headers['Range'] = f'bytes={existing_size}-'
                self.logger.info(f'Resuming download from byte {existing_size}')

            mode = 'ab' if existing_size > 0 and resume else 'wb'

            response = self.session.get(url, stream=True, headers=headers, timeout=self.timeout)

            if response.status_code not in [200, 206]:
                error_msg = f'HTTP {response.status_code}: {response.reason}'
                self.logger.error(f'Download failed: {error_msg}')
                self._notify_error(error_msg)
                return False

            with open(filepath, mode) as f:
                for chunk in response.iter_content(chunk_size=self.chunk_size):
                    if chunk:
                        f.write(chunk)
                        progress.downloaded_size += len(chunk)
                        progress.update(progress.downloaded_size)
                        self._notify_progress(progress)

            progress.status = 'completed'
            self._notify_progress(progress)

            if verify_integrity:
                if expected_hash:
                    if not self.verify_file(str(filepath), expected_hash):
                        self.logger.error('File integrity verification failed')
                        self._notify_error('File integrity verification failed')
                        filepath.unlink()
                        return False
                else:
                    self.logger.debug('No expected hash provided, skipping integrity check')

            self.logger.info(f'Download completed successfully: {filepath}')
            self._notify_complete(filename, str(filepath))

            return True

        except requests.exceptions.Timeout:
            error_msg = f'Download timeout after {self.timeout} seconds'
            self.logger.error(error_msg)
            self._notify_error(error_msg)
            return False

        except requests.exceptions.ConnectionError as e:
            error_msg = f'Connection error: {str(e)}'
            self.logger.error(error_msg, exception=e)
            self._notify_error(error_msg)
            return False

        except Exception as e:
            error_msg = f'Download failed: {str(e)}'
            self.logger.error(error_msg, exception=e)
            self._notify_error(error_msg)
            return False

    def verify_file(self, filepath: str, expected_hash: str, algorithm: str = 'sha256') -> bool:
        try:
            self.logger.info(f'Verifying file integrity: {filepath}')

            if algorithm == 'sha256':
                hasher = hashlib.sha256()
            elif algorithm == 'md5':
                hasher = hashlib.md5()
            elif algorithm == 'sha1':
                hasher = hashlib.sha1()
            else:
                self.logger.error(f'Unsupported hash algorithm: {algorithm}')
                return False

            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    hasher.update(chunk)

            file_hash = hasher.hexdigest()

            if file_hash.lower() == expected_hash.lower():
                self.logger.info('File integrity verification passed')
                return True
            else:
                self.logger.error(f'Hash mismatch: expected {expected_hash}, got {file_hash}')
                return False

        except Exception as e:
            self.logger.error(f'File verification failed: {e}', exception=e)
            return False

    def calculate_hash(self, filepath: str, algorithm: str = 'sha256') -> Optional[str]:
        try:
            if algorithm == 'sha256':
                hasher = hashlib.sha256()
            elif algorithm == 'md5':
                hasher = hashlib.md5()
            elif algorithm == 'sha1':
                hasher = hashlib.sha1()
            else:
                self.logger.error(f'Unsupported hash algorithm: {algorithm}')
                return None

            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    hasher.update(chunk)

            return hasher.hexdigest()

        except Exception as e:
            self.logger.error(f'Hash calculation failed: {e}', exception=e)
            return None

    def cleanup_temp_files(self, older_than_days: Optional[int] = None):
        try:
            self.logger.info('Cleaning up temporary files')

            if not self.temp_dir.exists():
                return

            cutoff_time = None
            if older_than_days is not None:
                cutoff_time = time.time() - (older_than_days * 24 * 60 * 60)

            deleted_count = 0
            deleted_size = 0

            for file_path in self.temp_dir.iterdir():
                if file_path.is_file():
                    if cutoff_time is None or file_path.stat().st_mtime < cutoff_time:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        deleted_count += 1
                        deleted_size += file_size
                        self.logger.debug(f'Deleted temp file: {file_path.name}')

            if deleted_count > 0:
                size_str = DownloadProgress('', '', deleted_size).get_size_str(deleted_size)
                self.logger.info(f'Cleaned up {deleted_count} files ({size_str})')
                print(f'{Colors.OKGREEN}{Emoji.CLEAN} Cleaned up {deleted_count} temporary files ({size_str}){Colors.ENDC}')
            else:
                self.logger.info('No temporary files to clean up')

        except Exception as e:
            self.logger.error(f'Cleanup failed: {e}', exception=e)

    def get_temp_files(self) -> List[Dict[str, Any]]:
        try:
            files = []

            if not self.temp_dir.exists():
                return files

            for file_path in self.temp_dir.iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        'name': file_path.name,
                        'path': str(file_path),
                        'size': stat.st_size,
                        'modified': stat.st_mtime
                    })

            return sorted(files, key=lambda x: x['modified'], reverse=True)

        except Exception as e:
            self.logger.error(f'Failed to get temp files: {e}', exception=e)
            return []

    def close(self):
        self.session.close()


def create_download_manager(temp_dir: Optional[str] = None) -> DownloadManager:
    return DownloadManager(temp_dir)


_default_download_manager: Optional[DownloadManager] = None


def get_default_download_manager() -> DownloadManager:
    global _default_download_manager
    if _default_download_manager is None:
        _default_download_manager = create_download_manager()
    return _default_download_manager
