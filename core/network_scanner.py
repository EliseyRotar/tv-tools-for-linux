from typing import Tuple, Optional, List, Dict
import subprocess
import socket
import ipaddress
import concurrent.futures
from core.adb_manager import ADBManager
from utils.logger import Logger
from utils.colors import Colors


class NetworkScanner:

    ADB_PORT = 5555

    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None):
        self.adb = adb_manager
        self.logger = logger
        self.discovered_devices: List[Dict[str, str]] = []

    def get_local_ip(self) -> Tuple[bool, Optional[str]]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return True, local_ip
        except Exception:
            return False, None

    def get_network_range(self) -> Tuple[bool, Optional[str]]:
        success, local_ip = self.get_local_ip()

        if not success or not local_ip:
            return False, None

        try:
            network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
            return True, str(network)
        except Exception:
            return False, None

    def scan_network(self, network_range: Optional[str] = None, timeout: int = 1) -> Tuple[bool, List[Dict[str, str]]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🔍 Scanning Network for Devices                ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if network_range is None:
            success, network_range = self.get_network_range()
            if not success:
                print(f"{Colors.FAIL}❌ Could not determine network range{Colors.ENDC}")
                return False, []

        print(f"{Colors.OKBLUE}ℹ️  Network range: {network_range}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Scanning for devices on port {self.ADB_PORT}...{Colors.ENDC}\n")

        try:
            network = ipaddress.IPv4Network(network_range, strict=False)
            hosts = list(network.hosts())

            print(f"{Colors.OKBLUE}ℹ️  Scanning {len(hosts)} hosts...{Colors.ENDC}\n")

            devices = []

            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                future_to_ip = {executor.submit(self._check_host, str(ip), timeout): str(ip) for ip in hosts}

                completed = 0
                for future in concurrent.futures.as_completed(future_to_ip):
                    completed += 1
                    if completed % 50 == 0:
                        print(f"{Colors.OKBLUE}⏳ Progress: {completed}/{len(hosts)}{Colors.ENDC}")

                    result = future.result()
                    if result:
                        devices.append(result)
                        print(f"{Colors.OKGREEN}✅ Found device: {result['ip']}{Colors.ENDC}")

            print(f"\n{Colors.OKGREEN}✅ Scan complete{Colors.ENDC}")
            print(f"{Colors.OKBLUE}ℹ️  Found {len(devices)} device(s){Colors.ENDC}\n")

            self.discovered_devices = devices

            if devices:
                self._display_devices(devices)

            if self.logger:
                self.logger.log_event('network_scanner', f'Scanned network, found {len(devices)} devices')

            return True, devices

        except Exception as e:
            print(f"{Colors.FAIL}❌ Scan failed: {e}{Colors.ENDC}")
            return False, []

    def _check_host(self, ip: str, timeout: int) -> Optional[Dict[str, str]]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, self.ADB_PORT))
            sock.close()

            if result == 0:
                hostname = self._get_hostname(ip)
                return {
                    'ip': ip,
                    'port': str(self.ADB_PORT),
                    'hostname': hostname or 'Unknown'
                }
        except Exception:
            pass

        return None

    def _get_hostname(self, ip: str) -> Optional[str]:
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except Exception:
            return None

    def _display_devices(self, devices: List[Dict[str, str]]):
        print(f"{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📱 Discovered Devices                          ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        for i, device in enumerate(devices, 1):
            print(f"{Colors.OKBLUE}{i}. IP Address: {device['ip']}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}   Port: {device['port']}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}   Hostname: {device['hostname']}{Colors.ENDC}\n")

    def scan_with_nmap(self, network_range: Optional[str] = None) -> Tuple[bool, List[Dict[str, str]]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🔍 Scanning with Nmap                          ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self._check_nmap_installed():
            print(f"{Colors.WARNING}⚠️  Nmap is not installed{Colors.ENDC}")
            print(f"{Colors.OKBLUE}ℹ️  Falling back to built-in scanner...{Colors.ENDC}\n")
            return self.scan_network(network_range)

        if network_range is None:
            success, network_range = self.get_network_range()
            if not success:
                print(f"{Colors.FAIL}❌ Could not determine network range{Colors.ENDC}")
                return False, []

        print(f"{Colors.OKBLUE}ℹ️  Network range: {network_range}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Scanning with nmap...{Colors.ENDC}\n")

        try:
            cmd = ['nmap', '-p', str(self.ADB_PORT), '--open', network_range]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                print(f"{Colors.FAIL}❌ Nmap scan failed{Colors.ENDC}")
                return False, []

            devices = self._parse_nmap_output(result.stdout)

            print(f"{Colors.OKGREEN}✅ Scan complete{Colors.ENDC}")
            print(f"{Colors.OKBLUE}ℹ️  Found {len(devices)} device(s){Colors.ENDC}\n")

            self.discovered_devices = devices

            if devices:
                self._display_devices(devices)

            if self.logger:
                self.logger.log_event('network_scanner', f'Nmap scan found {len(devices)} devices')

            return True, devices

        except subprocess.TimeoutExpired:
            print(f"{Colors.FAIL}❌ Nmap scan timed out{Colors.ENDC}")
            return False, []

        except Exception as e:
            print(f"{Colors.FAIL}❌ Nmap scan failed: {e}{Colors.ENDC}")
            return False, []

    def _check_nmap_installed(self) -> bool:
        try:
            result = subprocess.run(['nmap', '--version'], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False

    def _parse_nmap_output(self, output: str) -> List[Dict[str, str]]:
        devices = []
        lines = output.split('\n')

        current_ip = None
        for line in lines:
            if 'Nmap scan report for' in line:
                parts = line.split()
                if len(parts) >= 5:
                    current_ip = parts[-1].strip('()')

            elif current_ip and f'{self.ADB_PORT}/tcp' in line and 'open' in line:
                hostname = self._get_hostname(current_ip)
                devices.append({
                    'ip': current_ip,
                    'port': str(self.ADB_PORT),
                    'hostname': hostname or 'Unknown'
                })
                current_ip = None

        return devices

    def connect_to_device(self, ip: str, port: int = 5555) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🔌 Connecting to Device                        ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  IP: {ip}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Port: {port}{Colors.ENDC}\n")

        success, message = self.adb.connect(f"{ip}:{port}")

        if success:
            print(f"{Colors.OKGREEN}✅ Connected to {ip}:{port}{Colors.ENDC}")

            if self.logger:
                self.logger.log_event('network_scanner', f'Connected to {ip}:{port}')
        else:
            print(f"{Colors.FAIL}❌ Failed to connect: {message}{Colors.ENDC}")

        return success, message

    def get_discovered_devices(self) -> List[Dict[str, str]]:
        return self.discovered_devices.copy()

    def close(self):
        pass


def create_network_scanner(adb_manager: ADBManager, logger: Optional[Logger] = None) -> NetworkScanner:
    return NetworkScanner(adb_manager, logger)


def get_default_network_scanner(adb_manager: ADBManager) -> NetworkScanner:
    from utils.logger import get_default_logger
    return NetworkScanner(adb_manager, get_default_logger())
