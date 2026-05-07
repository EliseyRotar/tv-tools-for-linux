from typing import Tuple, List, Optional, Dict
from pathlib import Path
from core.adb_manager import ADBManager
from utils.logger import Logger
from utils.colors import Colors
import datetime


class SystemDiagnostics:

    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None):
        self.adb = adb_manager
        self.logger = logger

    def view_logcat(self, lines: int = 100, priority: Optional[str]
                    = None, tag: Optional[str] = None) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📋 View Logcat                                 ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        cmd = f'logcat -d -t {lines}'

        if priority:
            priority = priority.upper()
            if priority in ['V', 'D', 'I', 'W', 'E', 'F']:
                cmd += f' *:{priority}'
            else:
                print(f"{Colors.WARNING}⚠️  Invalid priority: {priority}{Colors.ENDC}")
                print(f"{Colors.OKBLUE}   Valid: V (Verbose), D (Debug), I (Info), W (Warning), E (Error), F (Fatal){Colors.ENDC}\n")
                return False, f"Invalid priority: {priority}"

        if tag:
            cmd += f' -s {tag}'

        print(f"{Colors.OKBLUE}📊 Fetching logs...{Colors.ENDC}\n")

        result = self.adb.shell_command(cmd)

        if not result.success:
            print(f"{Colors.FAIL}❌ Failed to fetch logs{Colors.ENDC}")
            return False, "Failed to fetch logs"

        if not result.output:
            print(f"{Colors.WARNING}⚠️  No logs found{Colors.ENDC}")
            return True, "No logs found"

        print(f"{Colors.OKGREEN}✅ Logs retrieved{Colors.ENDC}\n")
        print(f"{Colors.HEADER}{'=' * 60}{Colors.ENDC}")
        print(result.output)
        print(f"{Colors.HEADER}{'=' * 60}{Colors.ENDC}\n")

        if self.logger:
            self.logger.log_event('view_logcat', f'Viewed {lines} lines')

        return True, result.output

    def clear_logs(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🗑️  Clear Logs                                 ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        print(f"{Colors.OKBLUE}🗑️  Clearing logs...{Colors.ENDC}")

        result = self.adb.shell_command('logcat -c')

        if result.success:
            print(f"{Colors.OKGREEN}✅ Logs cleared successfully{Colors.ENDC}\n")

            if self.logger:
                self.logger.log_event('clear_logs', 'Cleared device logs')

            return True, "Logs cleared"
        else:
            print(f"{Colors.FAIL}❌ Failed to clear logs{Colors.ENDC}")
            return False, "Failed to clear logs"

    def export_logs(self, output_file: Optional[str] = None) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           💾 Export Logs                                 ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        if not output_file:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'logcat_{timestamp}.txt'

        print(f"{Colors.OKBLUE}📥 Exporting logs to: {output_file}{Colors.ENDC}\n")

        result = self.adb.shell_command('logcat -d')

        if not result.success:
            print(f"{Colors.FAIL}❌ Failed to fetch logs{Colors.ENDC}")
            return False, "Failed to fetch logs"

        try:
            output_path = Path(output_file)
            output_path.write_text(result.output)

            print(f"{Colors.OKGREEN}✅ Logs exported successfully{Colors.ENDC}")
            print(f"{Colors.OKBLUE}   File: {output_path.absolute()}{Colors.ENDC}\n")

            if self.logger:
                self.logger.log_event('export_logs', f'Exported to {output_file}')

            return True, str(output_path.absolute())
        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to write file: {str(e)}{Colors.ENDC}")
            return False, f"Failed to write file: {str(e)}"

    def list_processes(self) -> Tuple[bool, List[Dict[str, str]]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📊 Running Processes                           ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, []

        print(f"{Colors.OKBLUE}📋 Fetching process list...{Colors.ENDC}\n")

        result = self.adb.shell_command('ps -A')

        if not result.success or not result.output:
            print(f"{Colors.FAIL}❌ Failed to list processes{Colors.ENDC}")
            return False, []

        processes = []
        lines = result.output.strip().split('\n')

        if len(lines) < 2:
            print(f"{Colors.WARNING}⚠️  No processes found{Colors.ENDC}")
            return True, []

        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 9:
                processes.append({
                    'user': parts[0],
                    'pid': parts[1],
                    'ppid': parts[2],
                    'vsz': parts[3],
                    'rss': parts[4],
                    'wchan': parts[5],
                    'addr': parts[6],
                    'stat': parts[7],
                    'name': ' '.join(parts[8:])
                })

        print(f"{Colors.OKGREEN}✅ Found {len(processes)} processes{Colors.ENDC}\n")

        print(f"{Colors.HEADER}{'PID':<8} {'USER':<12} {'NAME':<40}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'-' * 60}{Colors.ENDC}")

        for proc in processes[:20]:
            print(f"{Colors.OKBLUE}{proc['pid']:<8} {proc['user']:<12} {proc['name']:<40}{Colors.ENDC}")

        if len(processes) > 20:
            print(f"\n{Colors.WARNING}... and {len(processes) - 20} more{Colors.ENDC}\n")

        if self.logger:
            self.logger.log_event('list_processes', f'Listed {len(processes)} processes')

        return True, processes

    def get_process_info(self, pid: str) -> Tuple[bool, Dict[str, str]]:
        if not self.adb.is_connected():
            return False, {}

        result = self.adb.shell_command(f'ps -p {pid}')

        if not result.success or not result.output:
            return False, {}

        lines = result.output.strip().split('\n')
        if len(lines) < 2:
            return False, {}

        parts = lines[1].split()
        if len(parts) >= 9:
            return True, {
                'user': parts[0],
                'pid': parts[1],
                'ppid': parts[2],
                'vsz': parts[3],
                'rss': parts[4],
                'wchan': parts[5],
                'addr': parts[6],
                'stat': parts[7],
                'name': ' '.join(parts[8:])
            }

        return False, {}

    def kill_process(self, pid: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ⛔ Kill Process                                ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.adb.is_connected():
            print(f"{Colors.FAIL}❌ No device connected{Colors.ENDC}")
            return False, "No device connected"

        if not pid:
            print(f"{Colors.FAIL}❌ PID is required{Colors.ENDC}")
            return False, "PID is required"

        success, proc_info = self.get_process_info(pid)
        if success:
            print(f"{Colors.OKBLUE}📋 Process: {proc_info.get('name', 'Unknown')}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}   PID: {pid}{Colors.ENDC}\n")

        print(f"{Colors.WARNING}⚠️  Killing process {pid}...{Colors.ENDC}")

        result = self.adb.shell_command(f'kill {pid}')

        if result.success:
            print(f"{Colors.OKGREEN}✅ Process killed{Colors.ENDC}\n")

            if self.logger:
                self.logger.log_event('kill_process', f'Killed PID {pid}')

            return True, f"Process {pid} killed"
        else:
            print(f"{Colors.FAIL}❌ Failed to kill process{Colors.ENDC}")
            return False, "Failed to kill process"

    def close(self):
        pass


def create_system_diagnostics(adb_manager: ADBManager, logger: Optional[Logger] = None) -> SystemDiagnostics:
    return SystemDiagnostics(adb_manager, logger)


def get_default_system_diagnostics(adb_manager: ADBManager) -> SystemDiagnostics:
    from utils.logger import get_default_logger
    return SystemDiagnostics(adb_manager, get_default_logger())
