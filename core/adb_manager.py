import subprocess
import shutil
import re
from typing import Optional, Tuple
from pathlib import Path
from dataclasses import dataclass


@dataclass
class CommandResult:
    success: bool
    output: str
    error: str
    return_code: int


class ADBManager:
    def __init__(self, default_timeout: int = 30):
        self.default_timeout = default_timeout
        self.connected_device: Optional[str] = None
        self.adb_path = self._find_adb_path()

    def _find_adb_path(self) -> Optional[str]:
        adb_path = shutil.which('adb')
        return adb_path

    def check_adb_installed(self) -> bool:
        return self.adb_path is not None

    def get_adb_version(self) -> Optional[str]:
        if not self.check_adb_installed():
            return None

        try:
            result = subprocess.run(
                [self.adb_path, 'version'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                version_match = re.search(r'Android Debug Bridge version (\d+\.\d+\.\d+)', result.stdout)
                if version_match:
                    return version_match.group(1)
                return result.stdout.strip().split('\n')[0]
            return None
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return None

    def kill_server(self) -> bool:
        if not self.check_adb_installed():
            return False

        try:
            result = subprocess.run(
                [self.adb_path, 'kill-server'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False

    def start_server(self) -> bool:
        if not self.check_adb_installed():
            return False

        try:
            result = subprocess.run(
                [self.adb_path, 'start-server'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False

    def connect(self, ip: str, port: int = 5555, timeout: int = 30) -> Tuple[bool, str]:
        if not self.check_adb_installed():
            return False, "ADB is not installed"

        if not self._validate_ip_address(ip):
            return False, f"Invalid IP address: {ip}"

        if not self._validate_port(port):
            return False, f"Invalid port: {port}"

        self.kill_server()
        self.start_server()

        try:
            address = f"{ip}:{port}"
            result = subprocess.run(
                [self.adb_path, 'connect', address],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            output = result.stdout.strip()
            error = result.stderr.strip()

            if result.returncode == 0 and ('connected' in output.lower() or 'already connected' in output.lower()):
                self.connected_device = address
                return True, output
            else:
                error_message = error if error else output
                return False, error_message

        except subprocess.TimeoutExpired:
            return False, f"Connection timeout after {timeout} seconds"
        except subprocess.SubprocessError as e:
            return False, f"Connection error: {str(e)}"

    def disconnect(self) -> Tuple[bool, str]:
        if not self.check_adb_installed():
            return False, "ADB is not installed"

        try:
            result = subprocess.run(
                [self.adb_path, 'disconnect'],
                capture_output=True,
                text=True,
                timeout=10
            )

            output = result.stdout.strip()
            self.connected_device = None

            if result.returncode == 0:
                return True, output
            else:
                return False, result.stderr.strip()

        except subprocess.TimeoutExpired:
            return False, "Disconnect timeout"
        except subprocess.SubprocessError as e:
            return False, f"Disconnect error: {str(e)}"

    def is_connected(self) -> bool:
        if not self.check_adb_installed():
            return False

        try:
            result = subprocess.run(
                [self.adb_path, 'get-state'],
                capture_output=True,
                text=True,
                timeout=5
            )

            return result.returncode == 0 and 'device' in result.stdout.lower()

        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False

    def execute_command(self, cmd: list, timeout: Optional[int] = None) -> CommandResult:
        if not self.check_adb_installed():
            return CommandResult(
                success=False,
                output="",
                error="ADB is not installed",
                return_code=-1
            )

        if timeout is None:
            timeout = self.default_timeout

        try:
            full_cmd = [self.adb_path] + cmd
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return CommandResult(
                success=result.returncode == 0,
                output=result.stdout.strip(),
                error=result.stderr.strip(),
                return_code=result.returncode
            )

        except subprocess.TimeoutExpired:
            return CommandResult(
                success=False,
                output="",
                error=f"Command timeout after {timeout} seconds",
                return_code=-1
            )
        except subprocess.SubprocessError as e:
            return CommandResult(
                success=False,
                output="",
                error=f"Command error: {str(e)}",
                return_code=-1
            )

    def shell_command(self, cmd: str, timeout: Optional[int] = None) -> CommandResult:
        sanitized_cmd = self._sanitize_shell_input(cmd)
        return self.execute_command(['shell', sanitized_cmd], timeout=timeout)

    def get_device_property(self, prop: str) -> Optional[str]:
        result = self.shell_command(f'getprop {prop}')
        if result.success:
            return result.output.strip()
        return None

    def push_file(self, local_path: str, remote_path: str, timeout: Optional[int] = None) -> Tuple[bool, str]:
        local_file = Path(local_path)

        if not local_file.exists():
            return False, f"Local file not found: {local_path}"

        if not local_file.is_file():
            return False, f"Path is not a file: {local_path}"

        result = self.execute_command(['push', str(local_file), remote_path], timeout=timeout)

        if result.success:
            return True, result.output
        else:
            error_msg = result.error if result.error else result.output
            return False, error_msg

    def pull_file(self, remote_path: str, local_path: str, timeout: Optional[int] = None) -> Tuple[bool, str]:
        result = self.execute_command(['pull', remote_path, local_path], timeout=timeout)

        if result.success:
            return True, result.output
        else:
            error_msg = result.error if result.error else result.output
            return False, error_msg

    def install_apk(self, apk_path: str, reinstall: bool = True, timeout: Optional[int] = None) -> Tuple[bool, str]:
        apk_file = Path(apk_path)

        if not apk_file.exists():
            return False, f"APK file not found: {apk_path}"

        if not apk_file.is_file():
            return False, f"Path is not a file: {apk_path}"

        if not apk_path.lower().endswith('.apk'):
            return False, f"File is not an APK: {apk_path}"

        if timeout is None:
            timeout = 60

        cmd = ['install']
        if reinstall:
            cmd.append('-r')
        cmd.append(str(apk_file))

        result = self.execute_command(cmd, timeout=timeout)

        if result.success and 'Success' in result.output:
            return True, result.output
        else:
            error_msg = result.error if result.error else result.output
            return False, error_msg

    def uninstall_package(self, package: str, timeout: Optional[int] = None) -> Tuple[bool, str]:
        if not package:
            return False, "Package name cannot be empty"

        result = self.execute_command(['uninstall', package], timeout=timeout)

        if result.success and 'Success' in result.output:
            return True, result.output
        else:
            error_msg = result.error if result.error else result.output
            return False, error_msg

    def _validate_ip_address(self, ip: str) -> bool:
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False

        octets = ip.split('.')
        return all(0 <= int(octet) <= 255 for octet in octets)

    def _validate_port(self, port: int) -> bool:
        return 1 <= port <= 65535

    def _sanitize_shell_input(self, input_str: str) -> str:
        # Commands are passed to subprocess with shell=False, so there is no
        # host-side shell injection. Pipes/redirects ($ | ( ) etc.) are required
        # by legitimate device commands like `dumpsys wifi | grep`, so they must
        # be preserved. Only strip control characters that cannot appear in a
        # single-line `adb shell` argument and could be used to splice commands.
        return input_str.replace('\x00', '').replace('\r', '').replace('\n', '')
