import json
import tarfile
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List, Dict

from models.backup import BackupMetadata
from core.adb_manager import ADBManager
from core.package_manager import PackageManager
from core.file_transfer import FileTransfer
from utils.logger import Logger
from utils.colors import Colors
from utils.ui_components import Emoji
from utils.error_handler import ErrorHandler


class BackupRestore:
    def __init__(self, adb_manager: ADBManager, package_manager: PackageManager,
                 file_transfer: FileTransfer, logger: Optional[Logger] = None,
                 error_handler: Optional[ErrorHandler] = None,
                 backup_dir: Optional[str] = None):
        self.adb = adb_manager
        self.package_manager = package_manager
        self.file_transfer = file_transfer
        self.logger = logger or Logger()
        self.error_handler = error_handler or ErrorHandler()

        if backup_dir:
            self.backup_dir = Path(backup_dir)
        else:
            home = Path.home()
            self.backup_dir = home / '.android-tv-tools' / 'backups'

        self._ensure_backup_directory()

    def _ensure_backup_directory(self) -> bool:
        try:
            if not self.backup_dir.exists():
                self.backup_dir.mkdir(parents=True, exist_ok=True)
                self.logger.log_operation('create_backup_directory', True,
                                          f'Created {self.backup_dir}')
            return True
        except Exception as e:
            self.logger.error(f'Failed to create backup directory: {str(e)}', exception=e)
            return False

    def backup_apk(self, package_name, package_info, backup_path):
        try:
            if not package_info.apk_path:
                result = self.adb.shell_command(f'pm path {package_name}')
                if result.success and 'package:' in result.output:
                    apk_path = result.output.replace('package:', '').strip()
                    package_info.apk_path = apk_path
                else:
                    return False, 0

            apk_path = package_info.apk_path
            apk_filename = f'{package_name}.apk'
            local_apk_path = backup_path / apk_filename

            print(f'{Colors.OKBLUE}{Emoji.DOWNLOAD} Backing up APK...{Colors.ENDC}')
            print(f'{Colors.OKBLUE}Source: {apk_path}{Colors.ENDC}')

            success, output = self.file_transfer.pull_file(
                apk_path,
                str(local_apk_path),
                show_progress=False
            )

            if success and local_apk_path.exists():
                apk_size = local_apk_path.stat().st_size
                apk_size_mb = apk_size / (1024 * 1024)
                print(f'{Colors.OKGREEN}{Emoji.CHECK} APK backed up ({apk_size_mb:.2f} MB){Colors.ENDC}')
                return True, apk_size
            else:
                print(f'{Colors.FAIL}{Emoji.CROSS} Failed to backup APK{Colors.ENDC}')
                return False, 0

        except Exception as e:
            self.logger.error(f'Failed to backup APK for {package_name}: {str(e)}', exception=e)
            print(f'{Colors.FAIL}{Emoji.CROSS} Error backing up APK: {str(e)}{Colors.ENDC}')
            return False, 0

    def list_backups(self):
        try:
            if not self.backup_dir.exists():
                print(f'{Colors.WARNING}{Emoji.INFO} No backups directory found{Colors.ENDC}')
                return []

            backup_files = list(self.backup_dir.glob('*.tar.gz'))

            if not backup_files:
                print(f'{Colors.WARNING}{Emoji.INFO} No backups found{Colors.ENDC}')
                return []

            backups = []

            for backup_file in backup_files:
                try:
                    with tarfile.open(backup_file, 'r:gz') as tar:
                        metadata_member = None
                        for member in tar.getmembers():
                            if member.name == 'metadata.json' or member.name.endswith('/metadata.json'):
                                metadata_member = member
                                break

                        if metadata_member:
                            metadata_file = tar.extractfile(metadata_member)
                            if metadata_file:
                                metadata_dict = json.load(metadata_file)
                                metadata = BackupMetadata.from_dict(metadata_dict)
                                backups.append((str(backup_file), metadata))
                except Exception as e:
                    self.logger.debug(f'Could not read metadata from {backup_file.name}: {str(e)}')
                    continue

            backups.sort(key=lambda x: x[1].backup_timestamp, reverse=True)

            return backups

        except Exception as e:
            self.logger.error(f'Failed to list backups: {str(e)}', exception=e)
            return []

    def backup_data(self, package_name: str, backup_path: Path) -> Tuple[bool, int]:
        try:
            print(f'{Colors.OKBLUE}{Emoji.INFO} Attempting to backup app data...{Colors.ENDC}')
            data_dir = f'/data/data/{package_name}'
            result = self.adb.shell_command(f'ls {data_dir}')
            if not result.success or 'No such file' in result.output:
                print(f'{Colors.WARNING}{Emoji.WARNING} No app data found or no permission{Colors.ENDC}')
                return False, 0
            print(f'{Colors.WARNING}{Emoji.INFO} App data backup requires root access{Colors.ENDC}')
            return False, 0
        except Exception as e:
            self.logger.debug(f'Data backup failed for {package_name}: {str(e)}')
            print(f'{Colors.WARNING}{Emoji.WARNING} Data backup not available{Colors.ENDC}')
            return False, 0

    def create_backup_archive(self, package_name: str, backup_path: Path,
                              metadata: BackupMetadata) -> Tuple[bool, str]:
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archive_name = f'{package_name}_{timestamp}.tar.gz'
            archive_path = self.backup_dir / archive_name
            print(f'\n{Colors.OKCYAN}{Emoji.PACKAGE} Creating backup archive...{Colors.ENDC}')
            metadata_file = backup_path / 'metadata.json'
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata.to_dict(), f, indent=2)
            with tarfile.open(archive_path, 'w:gz') as tar:
                for item in backup_path.iterdir():
                    tar.add(item, arcname=item.name)
            if archive_path.exists():
                _ = archive_path.stat().st_size / (1024 * 1024)
                print(f'{Colors.OKGREEN}{Emoji.CHECK} Archive created: {archive_name}{Colors.ENDC}')
                import shutil
                shutil.rmtree(backup_path)
                return True, str(archive_path)
            else:
                return False, 'Archive creation failed'
        except Exception as e:
            self.logger.error(f'Failed to create archive for {package_name}: {str(e)}', exception=e)
            return False, str(e)

    def backup_package(self, package_name: str) -> Tuple[bool, Optional[BackupMetadata]]:
        if not self.adb.is_connected():
            error_msg = 'Device not connected'
            self.logger.error(error_msg)
            return False, None
        print(f'\n{Colors.OKCYAN}{Emoji.SEARCH} Getting package information...{Colors.ENDC}')
        package_info = self.package_manager.get_package_info(package_name)
        if not package_info:
            error_msg = f'Package not found: {package_name}'
            print(f'{Colors.FAIL}{Emoji.CROSS} {error_msg}{Colors.ENDC}')
            self.logger.error(error_msg)
            return False, None
        display_name = package_info.label if package_info.label else package_name
        print(f'{Colors.OKGREEN}{Emoji.CHECK} Found: {display_name}{Colors.ENDC}')
        timestamp = datetime.now()
        temp_backup_path = self.backup_dir / f'temp_{package_name}_{timestamp.strftime("%Y%m%d_%H%M%S")}'
        try:
            temp_backup_path.mkdir(parents=True, exist_ok=True)
            apk_success, apk_size = self.backup_apk(package_name, package_info, temp_backup_path)
            if not apk_success:
                print(f'\n{Colors.FAIL}{Emoji.CROSS} Backup failed: Could not backup APK{Colors.ENDC}\n')
                import shutil
                if temp_backup_path.exists():
                    shutil.rmtree(temp_backup_path)
                return False, None
            data_success, data_size = self.backup_data(package_name, temp_backup_path)
            metadata = BackupMetadata(
                package_name=package_name,
                label=display_name,
                version_code=package_info.version_code,
                version_name=package_info.version_name,
                backup_timestamp=timestamp,
                has_data=data_success,
                apk_size=apk_size,
                data_size=data_size,
                backup_path=''
            )
            archive_success, archive_path = self.create_backup_archive(
                package_name, temp_backup_path, metadata
            )
            if archive_success:
                metadata.backup_path = archive_path
                print(f'\n{Colors.OKGREEN}{Emoji.SUCCESS} Backup completed successfully!{Colors.ENDC}\n')
                self.logger.log_operation('backup_package', True,
                                          f'Backed up {package_name} to {archive_path}')
                return True, metadata
            else:
                print(f'\n{Colors.FAIL}{Emoji.CROSS} Backup failed: Could not create archive{Colors.ENDC}\n')
                return False, None
        except Exception as e:
            self.logger.error(f'Backup failed for {package_name}: {str(e)}', exception=e)
            print(f'\n{Colors.FAIL}{Emoji.CROSS} Backup failed: {str(e)}{Colors.ENDC}\n')
            import shutil
            if temp_backup_path.exists():
                shutil.rmtree(temp_backup_path)
            return False, None

    def batch_backup(self, package_names: List[str]) -> Dict[str, Tuple[bool, Optional[BackupMetadata]]]:
        results = {}
        total = len(package_names)
        print(f'\n{Colors.HEADER}Batch Backup ({total} packages){Colors.ENDC}\n')
        successful_backups = []
        failed_backups = []
        for idx, package_name in enumerate(package_names, 1):
            print(f'{Colors.OKCYAN}[{idx}/{total}] Backing up: {package_name}{Colors.ENDC}')
            try:
                success, metadata = self.backup_package(package_name)
                results[package_name] = (success, metadata)
                if success:
                    successful_backups.append(package_name)
                else:
                    failed_backups.append(package_name)
            except Exception as e:
                self.logger.error(f'Error during batch backup of {package_name}: {str(e)}', exception=e)
                results[package_name] = (False, None)
                failed_backups.append(package_name)
        print(f'\n{Colors.OKGREEN}✓ Successful: {len(successful_backups)}{Colors.ENDC}')
        print(f'{Colors.FAIL}✗ Failed: {len(failed_backups)}{Colors.ENDC}\n')
        self.logger.log_operation('batch_backup', True,
                                  f'Backed up {len(successful_backups)}/{total} packages')
        return results

    def display_backups(self) -> List[Tuple[str, BackupMetadata]]:
        print(f'\n{Colors.HEADER}Available Backups{Colors.ENDC}\n')
        backups = self.list_backups()
        if not backups:
            print(f'{Colors.WARNING}{Emoji.INFO} No backups found in {self.backup_dir}{Colors.ENDC}\n')
            return []
        print(f'{Colors.OKCYAN}Backup directory: {self.backup_dir}{Colors.ENDC}\n')
        for idx, (backup_path, metadata) in enumerate(backups, 1):
            backup_file = Path(backup_path)
            file_size_mb = backup_file.stat().st_size / (1024 * 1024)
            timestamp_str = metadata.backup_timestamp.strftime('%Y-%m-%d %H:%M:%S')
            data_icon = f'{Colors.OKGREEN}✓{Colors.ENDC}' if metadata.has_data else f'{Colors.WARNING}✗{Colors.ENDC}'
            print(f'{Colors.OKBLUE}[{idx}] {metadata.label}{Colors.ENDC}')
            print(f'    Package: {metadata.package_name}')
            print(f'    Version: {metadata.version_name}')
            print(f'    Date: {timestamp_str}')
            print(f'    Size: {file_size_mb:.2f} MB')
            print(f'    Data: {data_icon}')
            print()
        print(f'{Colors.OKCYAN}Total backups: {len(backups)}{Colors.ENDC}\n')
        return backups

    def delete_backup(self, backup_path: str) -> bool:
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                print(f'{Colors.FAIL}{Emoji.CROSS} Backup not found: {backup_path}{Colors.ENDC}')
                return False
            backup_file.unlink()
            print(f'{Colors.OKGREEN}{Emoji.CHECK} Backup deleted: {backup_file.name}{Colors.ENDC}')
            self.logger.log_operation('delete_backup', True, f'Deleted {backup_path}')
            return True
        except Exception as e:
            self.logger.error(f'Failed to delete backup {backup_path}: {str(e)}', exception=e)
            print(f'{Colors.FAIL}{Emoji.CROSS} Failed to delete backup: {str(e)}{Colors.ENDC}')
            return False
