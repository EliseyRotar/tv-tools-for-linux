import os
import sys
import time
from pathlib import Path
from typing import Optional, Tuple, Callable
from core.adb_manager import ADBManager
from utils.logger import Logger
from utils.colors import Colors
from utils.ui_components import Emoji, ProgressBar, BoxChars
from utils.error_handler import ErrorHandler


class FileTransfer:
    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None,
                 error_handler: Optional[ErrorHandler] = None):
        self.adb = adb_manager
        self.logger = logger
        self.error_handler = error_handler or ErrorHandler()

    def check_ftp_server(self) -> Tuple[bool, str]:
        if not self.adb.is_connected():
            error_msg = 'Device not connected'
            if self.logger:
                self.logger.error(error_msg)
            if self.error_handler:
                self.error_handler.display_error_with_solutions(
                    error_message='Device not connected',
                    original_error='Cannot check FTP server: No device connected via ADB'
                )
            return False, error_msg

        print(f'\n{Colors.OKCYAN}{Emoji.SEARCH} Checking for FTP server apps on device...{Colors.ENDC}\n')

        ftp_server_packages = [
            'com.theolivetree.ftpserver',
            'com.medhaapps.wififtpserver',
            'com.smarterdroid.wififiletransfer',
            'com.beansoft.ftpserver',
            'com.icecoldapps.ftpserver'
        ]

        found_servers = []

        for package in ftp_server_packages:
            result = self.adb.shell_command(f'pm list packages {package}')
            if result.success and package in result.output:
                found_servers.append(package)

        if found_servers:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} Found FTP server app(s):{Colors.ENDC}')
            for server in found_servers:
                server_name = self._get_ftp_server_name(server)
                print(f'{Colors.OKGREEN}  • {server_name} ({server}){Colors.ENDC}')
            print()

            if self.logger:
                self.logger.log_operation('check_ftp_server', True,
                                          f'Found {len(found_servers)} FTP server(s)')

            return True, ', '.join(found_servers)
        else:
            print(f'{Colors.WARNING}{Emoji.INFO} No FTP server apps found on device{Colors.ENDC}')
            print(f'{Colors.WARNING}You can install an FTP server app from Google Play Store:{Colors.ENDC}')
            print(f'{Colors.WARNING}  • FTP Server by The Olive Tree{Colors.ENDC}')
            print(f'{Colors.WARNING}  • WiFi FTP Server by Medha Apps{Colors.ENDC}')
            print()

            if self.logger:
                self.logger.log_operation('check_ftp_server', False, 'No FTP server found')

            return False, 'No FTP server apps found'

    def install_ftp_server(self) -> Tuple[bool, str]:
        print(f'\n{Colors.OKCYAN}{Emoji.INFO} FTP Server Installation{Colors.ENDC}\n')
        print(f'{Colors.OKBLUE}FTP server apps must be installed from Google Play Store or sideloaded.{Colors.ENDC}\n')
        print(f'{Colors.OKBLUE}Recommended FTP server apps for Android TV:{Colors.ENDC}')
        print(f'{Colors.OKBLUE}  1. FTP Server by The Olive Tree{Colors.ENDC}')
        print(f'{Colors.OKBLUE}     Package: com.theolivetree.ftpserver{Colors.ENDC}')
        print(f'{Colors.OKBLUE}  2. WiFi FTP Server by Medha Apps{Colors.ENDC}')
        print(f'{Colors.OKBLUE}     Package: com.medhaapps.wififtpserver{Colors.ENDC}')
        print()
        print(f'{Colors.WARNING}To install:{Colors.ENDC}')
        print(f'{Colors.WARNING}  • Open Google Play Store on your Android TV{Colors.ENDC}')
        print(f'{Colors.WARNING}  • Search for "FTP Server"{Colors.ENDC}')
        print(f'{Colors.WARNING}  • Install one of the recommended apps{Colors.ENDC}')
        print(f'{Colors.WARNING}  • Or use Option 2 to sideload an FTP server APK{Colors.ENDC}')
        print()

        if self.logger:
            self.logger.log_operation('install_ftp_server', True,
                                      'Displayed FTP server installation instructions')

        return True, 'Installation instructions displayed'

    def enable_ftp_server(self, package_name: Optional[str] = None) -> Tuple[bool, str]:
        if not self.adb.is_connected():
            error_msg = 'Device not connected'
            if self.logger:
                self.logger.error(error_msg)
            if self.error_handler:
                self.error_handler.display_error_with_solutions(
                    error_message='Device not connected',
                    original_error='Cannot enable FTP server: No device connected via ADB'
                )
            return False, error_msg

        if not package_name:
            has_server, found_packages = self.check_ftp_server()
            if not has_server:
                return False, 'No FTP server app found. Please install one first.'

            package_name = found_packages.split(',')[0].strip()

        print(f'\n{Colors.OKCYAN}{Emoji.ROCKET} Launching FTP server app...{Colors.ENDC}\n')

        server_name = self._get_ftp_server_name(package_name)
        print(f'{Colors.OKBLUE}Starting: {server_name}{Colors.ENDC}\n')

        result = self.adb.shell_command(f'monkey -p {package_name} -c android.intent.category.LAUNCHER 1')

        if result.success:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} FTP server app launched!{Colors.ENDC}\n')
            print(f'{Colors.WARNING}{Emoji.INFO} Manual steps required:{Colors.ENDC}')
            print(f'{Colors.WARNING}  1. On your TV, open the FTP server app{Colors.ENDC}')
            print(f'{Colors.WARNING}  2. Start the FTP server{Colors.ENDC}')
            print(f'{Colors.WARNING}  3. Note the FTP address (usually ftp://device_ip:port){Colors.ENDC}')
            print(f'{Colors.WARNING}  4. Use an FTP client on your PC to connect{Colors.ENDC}')
            print()

            device_ip = self._get_device_ip()
            if device_ip:
                print(f'{Colors.OKGREEN}Device IP: {device_ip}{Colors.ENDC}')
                print(f'{Colors.OKGREEN}Typical FTP URL: ftp://{device_ip}:2221{Colors.ENDC}')
                print()

            if self.logger:
                self.logger.log_operation('enable_ftp_server', True,
                                          f'Launched {package_name}')

            return True, f'FTP server app launched: {package_name}'
        else:
            print(f'{Colors.FAIL}{Emoji.CROSS} Failed to launch FTP server app{Colors.ENDC}\n')

            if self.logger:
                self.logger.log_operation('enable_ftp_server', False, result.error)

            if self.error_handler:
                self.error_handler.display_error_with_solutions(
                    error_message='Failed to launch FTP server app',
                    original_error=result.error
                )

            return False, result.error

    def disable_ftp_server(self, package_name: Optional[str] = None) -> Tuple[bool, str]:
        if not self.adb.is_connected():
            error_msg = 'Device not connected'
            if self.logger:
                self.logger.error(error_msg)
            if self.error_handler:
                self.error_handler.display_error_with_solutions(
                    error_message='Device not connected',
                    original_error='Cannot disable FTP server: No device connected via ADB'
                )
            return False, error_msg

        if not package_name:
            has_server, found_packages = self.check_ftp_server()
            if not has_server:
                return False, 'No FTP server app found'

            package_name = found_packages.split(',')[0].strip()

        print(f'\n{Colors.OKCYAN}{Emoji.STOP} Stopping FTP server app...{Colors.ENDC}\n')

        server_name = self._get_ftp_server_name(package_name)
        print(f'{Colors.OKBLUE}Stopping: {server_name}{Colors.ENDC}\n')

        result = self.adb.shell_command(f'am force-stop {package_name}')

        if result.success:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} FTP server app stopped!{Colors.ENDC}\n')

            if self.logger:
                self.logger.log_operation('disable_ftp_server', True,
                                          f'Stopped {package_name}')

            return True, f'FTP server app stopped: {package_name}'
        else:
            print(f'{Colors.FAIL}{Emoji.CROSS} Failed to stop FTP server app{Colors.ENDC}\n')

            if self.logger:
                self.logger.log_operation('disable_ftp_server', False, result.error)

            if self.error_handler:
                self.error_handler.display_error_with_solutions(
                    error_message='Failed to stop FTP server app',
                    original_error=result.error
                )

            return False, result.error

    def _get_ftp_server_name(self, package_name: str) -> str:
        ftp_server_names = {
            'com.theolivetree.ftpserver': 'FTP Server (The Olive Tree)',
            'com.medhaapps.wififtpserver': 'WiFi FTP Server (Medha Apps)',
            'com.smarterdroid.wififiletransfer': 'WiFi File Transfer',
            'com.beansoft.ftpserver': 'FTP Server (BeanSoft)',
            'com.icecoldapps.ftpserver': 'FTP Server (Ice Cold Apps)'
        }
        return ftp_server_names.get(package_name, package_name)

    def _get_device_ip(self) -> Optional[str]:
        if not self.adb.is_connected():
            return None

        result = self.adb.shell_command('ip addr show wlan0')
        if result.success and 'inet ' in result.output:
            import re
            match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', result.output)
            if match:
                return match.group(1)

        result = self.adb.shell_command('getprop dhcp.wlan0.ipaddress')
        if result.success and result.output.strip():
            return result.output.strip()

        return None

    def push_file(self, local_path: str, remote_path: str,
                  show_progress: bool = True,
                  progress_callback: Optional[Callable[[int, int], None]] = None) -> Tuple[bool, str]:
        local_file = Path(local_path)

        if not local_file.exists():
            error_msg = f'Local file not found: {local_path}'
            if self.logger:
                self.logger.error(error_msg)
            if self.error_handler:
                self.error_handler.display_error_with_solutions(
                    error_message='File not found',
                    original_error=error_msg
                )
            return False, error_msg

        if not local_file.is_file():
            error_msg = f'Path is not a file: {local_path}'
            if self.logger:
                self.logger.error(error_msg)
            return False, error_msg

        if not self.adb.is_connected():
            error_msg = 'Device not connected'
            if self.logger:
                self.logger.error(error_msg)
            if self.error_handler:
                self.error_handler.display_error_with_solutions(
                    error_message='Device not connected',
                    original_error='Cannot push file: No device connected via ADB'
                )
            return False, error_msg

        file_size = local_file.stat().st_size
        file_size_mb = file_size / (1024 * 1024)

        if show_progress:
            print(f'\n{Colors.OKCYAN}{Emoji.UPLOAD} Pushing file to device...{Colors.ENDC}')
            print(f'{Colors.OKBLUE}Source: {local_path}{Colors.ENDC}')
            print(f'{Colors.OKBLUE}Destination: {remote_path}{Colors.ENDC}')
            print(f'{Colors.OKBLUE}Size: {file_size_mb:.2f} MB{Colors.ENDC}\n')

        if self.logger:
            self.logger.log_file_operation('push', local_path, remote_path)

        start_time = time.time()

        success, output = self.adb.push_file(str(local_file), remote_path)

        elapsed_time = time.time() - start_time

        if success:
            if show_progress:
                speed_mbps = file_size_mb / elapsed_time if elapsed_time > 0 else 0
                print(f'{Colors.OKGREEN}{Emoji.CHECK} File pushed successfully!{Colors.ENDC}')
                print(f'{Colors.OKGREEN}Time: {elapsed_time:.2f}s | Speed: {speed_mbps:.2f} MB/s{Colors.ENDC}\n')

            if self.logger:
                self.logger.log_file_operation('push', local_path, remote_path, success=True)

            return True, output
        else:
            if show_progress:
                print(f'{Colors.FAIL}{Emoji.CROSS} File push failed!{Colors.ENDC}\n')

            if self.logger:
                self.logger.log_file_operation('push', local_path, remote_path,
                                               success=False, error=output)

            if self.error_handler:
                self.error_handler.display_error_with_solutions(
                    error_message='File push failed',
                    original_error=output
                )

            return False, output

    def pull_file(self, remote_path: str, local_path: str,
                  show_progress: bool = True,
                  progress_callback: Optional[Callable[[int, int], None]] = None) -> Tuple[bool, str]:
        if not self.adb.is_connected():
            error_msg = 'Device not connected'
            if self.logger:
                self.logger.error(error_msg)
            if self.error_handler:
                self.error_handler.display_error_with_solutions(
                    error_message='Device not connected',
                    original_error='Cannot pull file: No device connected via ADB'
                )
            return False, error_msg

        local_file = Path(local_path)
        local_dir = local_file.parent

        if not local_dir.exists():
            try:
                local_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                error_msg = f'Failed to create directory: {str(e)}'
                if self.logger:
                    self.logger.error(error_msg, exception=e)
                return False, error_msg

        if show_progress:
            print(f'\n{Colors.OKCYAN}{Emoji.DOWNLOAD} Pulling file from device...{Colors.ENDC}')
            print(f'{Colors.OKBLUE}Source: {remote_path}{Colors.ENDC}')
            print(f'{Colors.OKBLUE}Destination: {local_path}{Colors.ENDC}\n')

        if self.logger:
            self.logger.log_file_operation('pull', remote_path, local_path)

        start_time = time.time()

        success, output = self.adb.pull_file(remote_path, str(local_file))

        elapsed_time = time.time() - start_time

        if success:
            if local_file.exists():
                file_size = local_file.stat().st_size
                file_size_mb = file_size / (1024 * 1024)
                speed_mbps = file_size_mb / elapsed_time if elapsed_time > 0 else 0

                if show_progress:
                    print(f'{Colors.OKGREEN}{Emoji.CHECK} File pulled successfully!{Colors.ENDC}')
                    print(
                        f'{Colors.OKGREEN}Size: {file_size_mb:.2f} MB | Time: {elapsed_time:.2f}s | Speed: {speed_mbps:.2f} MB/s{Colors.ENDC}\n')
            else:
                if show_progress:
                    print(f'{Colors.OKGREEN}{Emoji.CHECK} File pulled successfully!{Colors.ENDC}')
                    print(f'{Colors.OKGREEN}Time: {elapsed_time:.2f}s{Colors.ENDC}\n')

            if self.logger:
                self.logger.log_file_operation('pull', remote_path, local_path, success=True)

            return True, output
        else:
            if show_progress:
                print(f'{Colors.FAIL}{Emoji.CROSS} File pull failed!{Colors.ENDC}\n')

            if self.logger:
                self.logger.log_file_operation('pull', remote_path, local_path,
                                               success=False, error=output)

            if self.error_handler:
                self.error_handler.display_error_with_solutions(
                    error_message='File pull failed',
                    original_error=output
                )

            return False, output

    def send_text_to_clipboard(self, text: str) -> Tuple[bool, str]:
        if not self.adb.is_connected():
            error_msg = 'Device not connected'
            if self.logger:
                self.logger.error(error_msg)
            if self.error_handler:
                self.error_handler.display_error_with_solutions(
                    error_message='Device not connected',
                    original_error='Cannot send text: No device connected via ADB'
                )
            return False, error_msg

        if not text:
            error_msg = 'Text cannot be empty'
            return False, error_msg

        print(f'\n{Colors.OKCYAN}{Emoji.CLIPBOARD} Sending text to device clipboard...{Colors.ENDC}\n')

        escaped_text = self._escape_text_for_shell(text)

        result = self.adb.shell_command(f'input text "{escaped_text}"')

        if result.success:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} Text sent successfully!{Colors.ENDC}\n')

            if self.logger:
                self.logger.log_operation('send_text_to_clipboard', True,
                                          f'Sent {len(text)} characters')

            return True, result.output
        else:
            print(f'{Colors.FAIL}{Emoji.CROSS} Failed to send text!{Colors.ENDC}\n')

            if self.logger:
                self.logger.log_operation('send_text_to_clipboard', False, result.error)

            if self.error_handler:
                self.error_handler.display_error_with_solutions(
                    error_message='Failed to send text to device',
                    original_error=result.error
                )

            return False, result.error

    def take_screenshot(self, output_dir: str = 'screenshots') -> Tuple[bool, str]:
        from datetime import datetime

        if not self.adb.is_connected():
            error_msg = 'Device not connected'
            if self.logger:
                self.logger.error(error_msg)
            if self.error_handler:
                self.error_handler.display_error_with_solutions(
                    error_message='Device not connected',
                    original_error='Cannot take screenshot: No device connected via ADB'
                )
            return False, error_msg

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        remote_filename = f'screenshot_{timestamp}.png'
        remote_path = f'/sdcard/{remote_filename}'

        local_dir = Path(output_dir)
        if not local_dir.exists():
            try:
                local_dir.mkdir(parents=True, exist_ok=True)
                if self.logger:
                    self.logger.log_operation('create_directory', True, f'Created {output_dir}')
            except Exception as e:
                error_msg = f'Failed to create screenshots directory: {str(e)}'
                if self.logger:
                    self.logger.error(error_msg, exception=e)
                if self.error_handler:
                    self.error_handler.display_error_with_solutions(
                        error_message='Failed to create screenshots directory',
                        original_error=str(e)
                    )
                return False, error_msg

        local_path = local_dir / remote_filename

        print(f'\n{Colors.OKCYAN}{Emoji.CAMERA} Taking screenshot...{Colors.ENDC}\n')

        result = self.adb.shell_command(f'screencap -p {remote_path}')

        if not result.success:
            print(f'{Colors.FAIL}{Emoji.CROSS} Failed to capture screenshot!{Colors.ENDC}\n')
            if self.logger:
                self.logger.log_operation('take_screenshot', False, result.error)
            if self.error_handler:
                self.error_handler.display_error_with_solutions(
                    error_message='Screenshot capture failed',
                    original_error=result.error
                )
            return False, result.error

        print(f'{Colors.OKGREEN}{Emoji.CHECK} Screenshot captured on device{Colors.ENDC}')
        print(f'{Colors.OKBLUE}Remote path: {remote_path}{Colors.ENDC}\n')

        print(f'{Colors.OKCYAN}{Emoji.DOWNLOAD} Pulling screenshot to PC...{Colors.ENDC}\n')

        pull_success, pull_output = self.pull_file(remote_path, str(local_path), show_progress=False)

        if not pull_success:
            print(f'{Colors.FAIL}{Emoji.CROSS} Failed to pull screenshot from device!{Colors.ENDC}\n')

            cleanup_result = self.adb.shell_command(f'rm {remote_path}')
            if cleanup_result.success:
                print(f'{Colors.WARNING}{Emoji.INFO} Cleaned up screenshot from device{Colors.ENDC}\n')

            if self.logger:
                self.logger.log_operation('take_screenshot', False,
                                          f'Pull failed: {pull_output}')

            return False, pull_output

        print(f'{Colors.OKGREEN}{Emoji.CHECK} Screenshot saved to PC{Colors.ENDC}')
        print(f'{Colors.OKGREEN}Location: {local_path.absolute()}{Colors.ENDC}\n')

        print(f'{Colors.OKCYAN}{Emoji.CLEAN} Cleaning up device...{Colors.ENDC}\n')

        cleanup_result = self.adb.shell_command(f'rm {remote_path}')

        if cleanup_result.success:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} Screenshot removed from device{Colors.ENDC}\n')
        else:
            print(f'{Colors.WARNING}{Emoji.WARNING} Could not remove screenshot from device{Colors.ENDC}')
            print(f'{Colors.WARNING}You may need to manually delete: {remote_path}{Colors.ENDC}\n')

        if local_path.exists():
            file_size = local_path.stat().st_size
            file_size_kb = file_size / 1024
            print(f'{Colors.OKGREEN}{Emoji.SUCCESS} Screenshot complete!{Colors.ENDC}')
            print(f'{Colors.OKGREEN}File: {local_path.name}{Colors.ENDC}')
            print(f'{Colors.OKGREEN}Size: {file_size_kb:.2f} KB{Colors.ENDC}')
            print(f'{Colors.OKGREEN}Path: {local_path.absolute()}{Colors.ENDC}\n')

        if self.logger:
            self.logger.log_operation('take_screenshot', True,
                                      f'Screenshot saved to {local_path}')

        return True, str(local_path.absolute())

    def start_recording(self, duration: int = 30, bitrate: int = 4,
                        output_dir: str = 'recordings') -> Tuple[bool, str]:
        from datetime import datetime
        import threading

        if duration < 1 or duration > 180:
            error_msg = f'Duration must be between 1 and 180 seconds (got {duration})'
            if self.logger:
                self.logger.error(error_msg)
            return False, error_msg

        if bitrate < 1 or bitrate > 20:
            error_msg = f'Bitrate must be between 1 and 20 Mbps (got {bitrate})'
            if self.logger:
                self.logger.error(error_msg)
            return False, error_msg

        if not self.adb.is_connected():
            error_msg = 'Device not connected'
            if self.logger:
                self.logger.error(error_msg)
            if self.error_handler:
                self.error_handler.display_error_with_solutions(
                    error_message='Device not connected',
                    original_error='Cannot start recording: No device connected via ADB'
                )
            return False, error_msg

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        remote_filename = f'recording_{timestamp}.mp4'
        remote_path = f'/sdcard/{remote_filename}'

        local_dir = Path(output_dir)
        if not local_dir.exists():
            try:
                local_dir.mkdir(parents=True, exist_ok=True)
                if self.logger:
                    self.logger.log_operation('create_directory', True, f'Created {output_dir}')
            except Exception as e:
                error_msg = f'Failed to create recordings directory: {str(e)}'
                if self.logger:
                    self.logger.error(error_msg, exception=e)
                if self.error_handler:
                    self.error_handler.display_error_with_solutions(
                        error_message='Failed to create recordings directory',
                        original_error=str(e)
                    )
                return False, error_msg

        local_path = local_dir / remote_filename

        print(f'\n{Colors.OKCYAN}{Emoji.VIDEO} Starting screen recording...{Colors.ENDC}\n')
        print(f'{Colors.OKBLUE}Duration: {duration} seconds{Colors.ENDC}')
        print(f'{Colors.OKBLUE}Quality: {bitrate} Mbps{Colors.ENDC}')
        print(f'{Colors.OKBLUE}Output: {remote_filename}{Colors.ENDC}\n')

        bitrate_value = bitrate * 1000000

        recording_complete = threading.Event()
        recording_error = None

        def run_recording():
            nonlocal recording_error
            result = self.adb.shell_command(
                f'screenrecord --time-limit {duration} --bit-rate {bitrate_value} {remote_path}',
                timeout=duration + 10
            )
            if not result.success:
                recording_error = result.error
            recording_complete.set()

        recording_thread = threading.Thread(target=run_recording, daemon=True)
        recording_thread.start()

        print(f'{Colors.OKGREEN}{Emoji.RECORD} Recording in progress...{Colors.ENDC}\n')

        progress_bar = ProgressBar(total=duration, width=50)

        for elapsed in range(duration + 1):
            if recording_complete.is_set():
                break

            progress_bar.update(elapsed)
            remaining = duration - elapsed
            mins, secs = divmod(remaining, 60)

            sys.stdout.write(f'\r{Colors.OKCYAN}')
            progress_bar.display()
            sys.stdout.write(f' {Colors.OKBLUE}Time remaining: {mins:02d}:{secs:02d}{Colors.ENDC}')
            sys.stdout.flush()

            if elapsed < duration:
                time.sleep(1)

        recording_complete.wait(timeout=5)

        sys.stdout.write('\n\n')
        sys.stdout.flush()

        if recording_error:
            print(f'{Colors.FAIL}{Emoji.CROSS} Recording failed!{Colors.ENDC}\n')
            if self.logger:
                self.logger.log_operation('start_recording', False, recording_error)
            if self.error_handler:
                self.error_handler.display_error_with_solutions(
                    error_message='Screen recording failed',
                    original_error=recording_error
                )
            return False, recording_error

        print(f'{Colors.OKGREEN}{Emoji.CHECK} Recording completed on device{Colors.ENDC}')
        print(f'{Colors.OKBLUE}Remote path: {remote_path}{Colors.ENDC}\n')

        time.sleep(1)

        print(f'{Colors.OKCYAN}{Emoji.DOWNLOAD} Pulling recording to PC...{Colors.ENDC}\n')

        pull_success, pull_output = self.pull_file(remote_path, str(local_path), show_progress=False)

        if not pull_success:
            print(f'{Colors.FAIL}{Emoji.CROSS} Failed to pull recording from device!{Colors.ENDC}\n')

            cleanup_result = self.adb.shell_command(f'rm {remote_path}')
            if cleanup_result.success:
                print(f'{Colors.WARNING}{Emoji.INFO} Cleaned up recording from device{Colors.ENDC}\n')

            if self.logger:
                self.logger.log_operation('start_recording', False,
                                          f'Pull failed: {pull_output}')

            return False, pull_output

        print(f'{Colors.OKGREEN}{Emoji.CHECK} Recording saved to PC{Colors.ENDC}')
        print(f'{Colors.OKGREEN}Location: {local_path.absolute()}{Colors.ENDC}\n')

        print(f'{Colors.OKCYAN}{Emoji.CLEAN} Cleaning up device...{Colors.ENDC}\n')

        cleanup_result = self.adb.shell_command(f'rm {remote_path}')

        if cleanup_result.success:
            print(f'{Colors.OKGREEN}{Emoji.CHECK} Recording removed from device{Colors.ENDC}\n')
        else:
            print(f'{Colors.WARNING}{Emoji.WARNING} Could not remove recording from device{Colors.ENDC}')
            print(f'{Colors.WARNING}You may need to manually delete: {remote_path}{Colors.ENDC}\n')

        if local_path.exists():
            file_size = local_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            print(f'{Colors.OKGREEN}{Emoji.SUCCESS} Recording complete!{Colors.ENDC}')
            print(f'{Colors.OKGREEN}File: {local_path.name}{Colors.ENDC}')
            print(f'{Colors.OKGREEN}Size: {file_size_mb:.2f} MB{Colors.ENDC}')
            print(f'{Colors.OKGREEN}Duration: {duration} seconds{Colors.ENDC}')
            print(f'{Colors.OKGREEN}Path: {local_path.absolute()}{Colors.ENDC}\n')

        if self.logger:
            self.logger.log_operation('start_recording', True,
                                      f'Recording saved to {local_path}')

        return True, str(local_path.absolute())

    def validate_local_file(self, file_path: str) -> Tuple[bool, str]:
        file = Path(file_path)

        if not file.exists():
            return False, f'File does not exist: {file_path}'

        if not file.is_file():
            return False, f'Path is not a file: {file_path}'

        if not os.access(file_path, os.R_OK):
            return False, f'File is not readable: {file_path}'

        return True, 'File is valid'

    def validate_remote_path(self, remote_path: str) -> Tuple[bool, str]:
        if not remote_path:
            return False, 'Remote path cannot be empty'

        if not remote_path.startswith('/'):
            return False, 'Remote path must be absolute (start with /)'

        return True, 'Remote path is valid'

    def get_file_info(self, local_path: str) -> Optional[dict]:
        try:
            file = Path(local_path)
            if not file.exists():
                return None

            stat = file.stat()
            return {
                'path': str(file.absolute()),
                'name': file.name,
                'size': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'modified': time.ctime(stat.st_mtime),
                'is_readable': os.access(local_path, os.R_OK),
                'is_writable': os.access(local_path, os.W_OK)
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f'Failed to get file info: {str(e)}', exception=e)
            return None

    def _escape_text_for_shell(self, text: str) -> str:
        escaped = text.replace('\\', '\\\\')
        escaped = escaped.replace('"', '\\"')
        escaped = escaped.replace("'", "\\'")
        escaped = escaped.replace('$', '\\$')
        escaped = escaped.replace('`', '\\`')
        escaped = escaped.replace('!', '\\!')
        escaped = escaped.replace(' ', '%s')

        return escaped

    def display_transfer_summary(self, operations: list):
        if not operations:
            print(f'{Colors.WARNING}No file transfer operations to display{Colors.ENDC}')
            return

        print(f'\n{Colors.HEADER}{BoxChars.TOP_LEFT}{BoxChars.HORIZONTAL * 78}{BoxChars.TOP_RIGHT}{Colors.ENDC}')
        print(f'{Colors.HEADER}{BoxChars.VERTICAL}{Colors.ENDC} {Colors.BOLD}File Transfer Summary{Colors.ENDC}' +
              ' ' * 55 + f'{Colors.HEADER}{BoxChars.VERTICAL}{Colors.ENDC}')
        print(f'{Colors.HEADER}{BoxChars.T_RIGHT}{BoxChars.HORIZONTAL * 78}{BoxChars.T_LEFT}{Colors.ENDC}')

        for i, op in enumerate(operations, 1):
            op_type = op.get('type', 'unknown')
            success = op.get('success', False)
            source = op.get('source', 'N/A')
            dest = op.get('destination', 'N/A')

            status_icon = Emoji.CHECK if success else Emoji.CROSS
            status_color = Colors.OKGREEN if success else Colors.FAIL

            print(
                f'{Colors.HEADER}{BoxChars.VERTICAL}{Colors.ENDC} {status_color}{status_icon}{Colors.ENDC} {op_type.upper()}: {source[:30]}... -> {dest[:30]}...')

        print(f'{Colors.HEADER}{BoxChars.BOTTOM_LEFT}{BoxChars.HORIZONTAL * 78}{BoxChars.BOTTOM_RIGHT}{Colors.ENDC}\n')

        success_count = sum(1 for op in operations if op.get('success', False))
        fail_count = len(operations) - success_count

        print(f'{Colors.OKGREEN}Successful: {success_count}{Colors.ENDC} | {Colors.FAIL}Failed: {fail_count}{Colors.ENDC}\n')
