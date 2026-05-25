import time
import sys
from typing import TYPE_CHECKING, Dict, List, Tuple, Optional

if TYPE_CHECKING:
    from core.adb_manager import ADBManager
    from core.ui_manager import UIManager


class SystemMonitor:

    def __init__(self, adb: 'ADBManager'):
        self.adb = adb
        self.running = False
        self.refresh_rate = 2

    def get_cpu_usage(self) -> Dict[str, str]:
        cpu_info = {}

        # Most reliable: parse /proc/stat directly (two samples for accurate reading)
        def read_stat():
            r = self.adb.shell_command('cat /proc/stat')
            if r.success and r.output:
                for line in r.output.split('\n'):
                    if line.startswith('cpu '):
                        vals = line.split()[1:]
                        try:
                            nums = [int(v) for v in vals[:8]]
                            idle = nums[3] + (nums[4] if len(nums) > 4 else 0)
                            total = sum(nums)
                            return idle, total
                        except (ValueError, IndexError):
                            pass
            return None, None

        idle1, total1 = read_stat()
        if idle1 is not None:
            import time as _time
            _time.sleep(0.5)
            idle2, total2 = read_stat()
            if idle2 is not None and total2 != total1:
                diff_idle = idle2 - idle1
                diff_total = total2 - total1
                used_pct = round((1 - diff_idle / diff_total) * 100, 1)
                cpu_info['usage'] = f"{used_pct}%"
                cpu_info['usage_percent'] = used_pct
                return cpu_info

        # Fallback: try top command
        result = self.adb.shell_command('top -n 1 | head -5')
        if result.success and result.output:
            for line in result.output.split('\n'):
                # Match patterns like "800%cpu  12%user  0%nice  ..." or "CPU: 25% usr ..."
                import re
                m = re.search(r'(\d+)%\s*(?:cpu|usr|user)', line, re.IGNORECASE)
                if m:
                    val = float(m.group(1))
                    cpu_info['usage'] = f"{val}%"
                    cpu_info['usage_percent'] = val
                    break

        return cpu_info

    def get_memory_info(self) -> Dict[str, str]:
        result = self.adb.shell_command('cat /proc/meminfo')
        if not result.success:
            return {}

        memory_info = {}
        lines = result.output.split('\n')
        
        for line in lines:
            if 'MemTotal:' in line:
                memory_info['total'] = line.split()[1]
            elif 'MemFree:' in line:
                memory_info['free'] = line.split()[1]
            elif 'MemAvailable:' in line:
                memory_info['available'] = line.split()[1]
            elif 'Cached:' in line and 'SwapCached' not in line:
                memory_info['cached'] = line.split()[1]
            elif 'Buffers:' in line:
                memory_info['buffers'] = line.split()[1]

        if 'total' in memory_info and 'available' in memory_info:
            total = int(memory_info['total'])
            available = int(memory_info['available'])
            used = total - available
            memory_info['used'] = str(used)
            memory_info['used_percent'] = f"{(used / total * 100):.1f}"

        return memory_info

    def get_storage_info(self) -> List[Dict[str, str]]:
        result = self.adb.shell_command('df -h')
        if not result.success:
            return []

        storage_list = []
        lines = result.output.split('\n')[1:]

        for line in lines:
            if not line.strip():
                continue
            
            parts = line.split()
            if len(parts) >= 6:
                storage_list.append({
                    'filesystem': parts[0],
                    'size': parts[1],
                    'used': parts[2],
                    'available': parts[3],
                    'use_percent': parts[4],
                    'mounted': ' '.join(parts[5:])
                })

        return storage_list

    def get_network_stats(self) -> Dict[str, Dict[str, str]]:
        result = self.adb.shell_command('cat /proc/net/dev')
        if not result.success:
            return {}

        network_stats = {}
        lines = result.output.split('\n')[2:]

        for line in lines:
            if ':' not in line:
                continue
            
            parts = line.split(':')
            if len(parts) != 2:
                continue
            
            interface = parts[0].strip()
            values = parts[1].split()
            
            if len(values) >= 9:
                network_stats[interface] = {
                    'rx_bytes': values[0],
                    'rx_packets': values[1],
                    'tx_bytes': values[8],
                    'tx_packets': values[9]
                }

        return network_stats

    def get_top_processes(self, limit: int = 10) -> List[Dict[str, str]]:
        result = self.adb.shell_command(f'top -n 1 -b | head -{limit + 7}')
        if not result.success:
            return []

        processes = []
        lines = result.output.split('\n')
        
        header_found = False
        for line in lines:
            if 'PID' in line and 'USER' in line:
                header_found = True
                continue
            
            if header_found and line.strip():
                parts = line.split()
                if len(parts) >= 9:
                    try:
                        processes.append({
                            'pid': parts[0],
                            'user': parts[1],
                            'cpu': parts[2] if '%' in parts[2] else parts[3],
                            'mem': parts[3] if '%' in parts[3] else parts[4],
                            'name': parts[-1]
                        })
                    except (IndexError, KeyError):
                        pass

        return processes[:limit]

    def get_battery_info(self) -> Dict[str, str]:
        result = self.adb.shell_command('dumpsys battery')
        if not result.success:
            return {}

        battery_info = {}
        lines = result.output.split('\n')

        # Check if device has a battery (some TVs/sticks report "present: false")
        for line in lines:
            if 'present:' in line:
                if 'false' in line.lower():
                    return {}  # No battery present
                break
        
        for line in lines:
            if 'level:' in line:
                battery_info['level'] = line.split(':')[1].strip()
            elif 'status:' in line:
                status_code = line.split(':')[1].strip()
                status_map = {'1': 'Unknown', '2': 'Charging', '3': 'Discharging', '4': 'Not charging', '5': 'Full'}
                battery_info['status'] = status_map.get(status_code, status_code)
            elif 'temperature:' in line:
                temp = line.split(':')[1].strip()
                try:
                    battery_info['temperature'] = f"{int(temp) / 10:.1f}°C"
                except (ValueError, TypeError):
                    battery_info['temperature'] = temp
            elif 'voltage:' in line:
                voltage = line.split(':')[1].strip()
                try:
                    battery_info['voltage'] = f"{int(voltage) / 1000:.2f}V"
                except (ValueError, TypeError):
                    battery_info['voltage'] = voltage

        return battery_info

    def get_temperature_info(self) -> Dict[str, str]:
        result = self.adb.shell_command('cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null')
        if not result.success:
            return {}

        temps = {}
        lines = result.output.split('\n')
        
        for i, line in enumerate(lines):
            if line.strip():
                try:
                    temp_value = int(line.strip())
                    if temp_value > 1000:
                        temp_value = temp_value / 1000
                    temps[f'zone{i}'] = f"{temp_value:.1f}°C"
                except (ValueError, TypeError):
                    pass

        return temps

    def format_bytes(self, kb: str) -> str:
        try:
            kb_val = int(kb)
            if kb_val < 1024:
                return f"{kb_val} KB"
            elif kb_val < 1024 * 1024:
                return f"{kb_val / 1024:.1f} MB"
            else:
                return f"{kb_val / 1024 / 1024:.2f} GB"
        except (ValueError, TypeError):
            return kb

    def create_progress_bar(self, percent: float, width: int = 30) -> str:
        filled = int(width * percent / 100)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}] {percent:.1f}%"

    def display_monitor(self, ui: 'UIManager'):
        self.running = True
        
        try:
            while self.running:
                ui.clear_screen()
                
                print("╔══════════════════════════════════════════════════════════════════════════════╗")
                print("║                    📊 Android TV System Monitor (btop)                       ║")
                print("║                    Press Ctrl+C to exit | Refresh: 2s                        ║")
                print("╚══════════════════════════════════════════════════════════════════════════════╝")
                print()

                cpu_info = self.get_cpu_usage()
                if cpu_info:
                    print("┌─ CPU ─────────────────────────────────────────────────────────────────────┐")
                    if 'usage' in cpu_info:
                        print(f"│ Usage: {cpu_info['usage']}")
                    else:
                        print("│ Usage: Calculating...")
                    print("└───────────────────────────────────────────────────────────────────────────┘")
                    print()

                memory_info = self.get_memory_info()
                if memory_info:
                    print("┌─ Memory ──────────────────────────────────────────────────────────────────┐")
                    if 'total' in memory_info:
                        total_mb = int(memory_info['total']) / 1024
                        used_mb = int(memory_info.get('used', 0)) / 1024
                        available_mb = int(memory_info.get('available', 0)) / 1024
                        used_percent = float(memory_info.get('used_percent', 0))
                        
                        print(f"│ Total: {total_mb:.0f} MB | Used: {used_mb:.0f} MB | Available: {available_mb:.0f} MB")
                        print(f"│ {self.create_progress_bar(used_percent)}")
                    print("└───────────────────────────────────────────────────────────────────────────┘")
                    print()

                storage_info = self.get_storage_info()
                if storage_info:
                    print("┌─ Storage ─────────────────────────────────────────────────────────────────┐")
                    for i, storage in enumerate(storage_info[:3]):
                        try:
                            mount = storage['mounted']
                            if isinstance(mount, list):
                                mount = ' '.join(mount)
                            
                            if mount in ['/data', '/sdcard', '/system', '/']:
                                use_percent = storage['use_percent'].replace('%', '')
                                try:
                                    use_val = float(use_percent)
                                    print(f"│ {mount:15} {storage['used']:>8} / {storage['size']:>8} ({storage['use_percent']})")
                                except (ValueError, TypeError):
                                    print(f"│ {mount:15} {storage['used']:>8} / {storage['size']:>8}")
                        except Exception as e:
                            continue
                    print("└───────────────────────────────────────────────────────────────────────────┘")
                    print()

                battery_info = self.get_battery_info()
                if battery_info:
                    print("┌─ Battery ─────────────────────────────────────────────────────────────────┐")
                    level = battery_info.get('level', 'N/A')
                    status = battery_info.get('status', 'N/A')
                    temp = battery_info.get('temperature', 'N/A')
                    voltage = battery_info.get('voltage', 'N/A')
                    
                    print(f"│ Level: {level}% | Status: {status} | Temp: {temp} | Voltage: {voltage}")
                    
                    try:
                        level_val = float(level)
                        print(f"│ {self.create_progress_bar(level_val)}")
                    except (ValueError, TypeError):
                        pass
                    
                    print("└───────────────────────────────────────────────────────────────────────────┘")
                    print()

                processes = self.get_top_processes(8)
                if processes:
                    print("┌─ Top Processes ───────────────────────────────────────────────────────────┐")
                    print("│ PID      USER       CPU%   MEM%   NAME")
                    print("│" + "─" * 77)
                    for proc in processes:
                        pid = proc['pid'][:8].ljust(8)
                        user = proc['user'][:10].ljust(10)
                        cpu = proc['cpu'][:6].ljust(6)
                        mem = proc['mem'][:6].ljust(6)
                        name = proc['name'][:40]
                        print(f"│ {pid} {user} {cpu} {mem} {name}")
                    print("└───────────────────────────────────────────────────────────────────────────┘")

                time.sleep(self.refresh_rate)

        except KeyboardInterrupt:
            self.running = False
            print()
            ui.print_info('Exiting system monitor...')

    def start_monitor(self, ui: 'UIManager'):
        ui.clear_screen()
        ui.print_info('Starting system monitor...')
        ui.print_info('Press Ctrl+C to exit')
        print()
        time.sleep(1)
        self.display_monitor(ui)
