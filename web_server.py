#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, render_template, jsonify, request, session, redirect, url_for, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import os
import secrets
import json
from datetime import datetime, timedelta
from collections import deque
from threading import Lock

from core.adb_manager import ADBManager
from core.config_manager import ConfigManager
from core.system_monitor import SystemMonitor
from core.device_info import DeviceInfo
from core.package_manager import PackageManager
from core.file_transfer import FileTransfer
from core.settings_manager import SettingsManager
from core.remote_control import RemoteControl
from core.backup_restore import BackupRestore
from core.bloatware_removal import BloatwareRemoval
from core.app_launcher import AppLauncher
from core.keyboard_remote import KeyboardRemote
from core.power_management import PowerManagement
from core.network_scanner import NetworkScanner
from core.optimization import OptimizationModule
from core.voice_commands import VoiceCommands
from core.permission_manager import PermissionManager
from core.storage_manager import StorageManager
from core.system_diagnostics import SystemDiagnostics
from core.wireless_adb import WirelessADB
from core.ime_manager import IMEManager
from core.accessibility import Accessibility
from core.ad_blocking import AdBlocking
from core.adb_shell import ADBShell
from core.icon_generator import IconGenerator
from core.install_helper import InstallHelper
from core.update_checker import UpdateChecker
from utils.logger import Logger


VERSION = "1.0"
AUTHOR = "@eli6"


class MetricsHistory:
    """Store historical metrics data for charts"""
    def __init__(self, max_points=60):
        self.max_points = max_points
        self.cpu = deque(maxlen=max_points)
        self.memory = deque(maxlen=max_points)
        self.storage = deque(maxlen=max_points)
        self.battery = deque(maxlen=max_points)
        self.timestamps = deque(maxlen=max_points)
        self.lock = Lock()
    
    def add_data_point(self, cpu, memory, storage, battery):
        with self.lock:
            self.cpu.append(cpu)
            self.memory.append(memory)
            self.storage.append(storage)
            self.battery.append(battery)
            self.timestamps.append(datetime.now().isoformat())
    
    def get_history(self):
        with self.lock:
            return {
                'cpu': list(self.cpu),
                'memory': list(self.memory),
                'storage': list(self.storage),
                'battery': list(self.battery),
                'timestamps': list(self.timestamps)
            }
    
    def clear(self):
        with self.lock:
            self.cpu.clear()
            self.memory.clear()
            self.storage.clear()
            self.battery.clear()
            self.timestamps.clear()


class WebServer:
    
    def __init__(self):
        self.app = Flask(__name__, 
                        template_folder='web/templates',
                        static_folder='web/static')
        
        self.config_dir = Path.home() / '.android-tv-tools'
        self.app.secret_key = self._load_or_create_secret_key()
        self.app.config['SESSION_COOKIE_HTTPONLY'] = True
        self.app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

        self._generated_password = None
        self._username, self._password_hash = self._load_or_create_credentials()

        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()
        self.adb = ADBManager(default_timeout=self.config.default_timeout)
        self.logger = Logger()
        self.system_monitor = None
        self.package_manager = None
        self.file_transfer = None
        self.settings_manager = None
        self.remote_control = None
        self.backup_restore = None
        self.bloatware_removal = None
        self.app_launcher = None
        self.keyboard_remote = None
        self.power_management = None
        self.network_scanner = None
        self.optimization = None
        self.voice_commands = None
        self.permission_manager = None
        self.storage_manager = None
        self.system_diagnostics = None
        self.wireless_adb = None
        self.ime_manager = None
        self.accessibility = None
        self.ad_blocking = None
        self.adb_shell = None
        self.icon_generator = None
        self.install_helper = None
        self.update_checker = None
        self.connected_devices = {}
        self.metrics_history = {}  # device_id -> MetricsHistory
        self.screenshots_cache = {}  # device_id -> list of screenshots
        
        # Try to enable CORS if available
        try:
            from flask_cors import CORS
            CORS(self.app)
        except ImportError:
            print("⚠️  Flask-CORS not installed. CORS support disabled.")
            print("   Install with: pip install Flask-CORS or sudo pacman -S python-flask-cors")
        
        self.setup_routes()
        
    def setup_routes(self):
        
        @self.app.route('/')
        def index():
            if not self.is_authenticated():
                return redirect(url_for('login'))
            return render_template('dashboard.html', 
                                 version=VERSION,
                                 author=AUTHOR)
        
        @self.app.route('/apps')
        def apps():
            if not self.is_authenticated():
                return redirect(url_for('login'))
            return render_template('apps.html',
                                 version=VERSION,
                                 author=AUTHOR)
        
        @self.app.route('/files')
        def files():
            if not self.is_authenticated():
                return redirect(url_for('login'))
            return render_template('files.html',
                                 version=VERSION,
                                 author=AUTHOR)
        
        @self.app.route('/settings')
        def settings():
            if not self.is_authenticated():
                return redirect(url_for('login'))
            return render_template('settings.html',
                                 version=VERSION,
                                 author=AUTHOR)
        
        @self.app.route('/devices')
        def devices():
            if not self.is_authenticated():
                return redirect(url_for('login'))
            return render_template('devices.html',
                                 version=VERSION,
                                 author=AUTHOR)
        
        @self.app.route('/advanced')
        def advanced():
            if not self.is_authenticated():
                return redirect(url_for('login'))
            return render_template('advanced.html',
                                 version=VERSION,
                                 author=AUTHOR)
        
        @self.app.route('/tools')
        def tools():
            if not self.is_authenticated():
                return redirect(url_for('login'))
            return render_template('tools.html',
                                 version=VERSION,
                                 author=AUTHOR)
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                data = request.get_json()
                username = data.get('username')
                password = data.get('password')
                
                if self.authenticate(username, password):
                    session['authenticated'] = True
                    session['username'] = username
                    session.permanent = True
                    return jsonify({'success': True})
                else:
                    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
            
            return render_template('login.html')
        
        @self.app.route('/logout')
        def logout():
            session.clear()
            return redirect(url_for('login'))
        
        @self.app.route('/api/devices/connect', methods=['POST'])
        def connect_device():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            data = request.get_json()
            ip_address = data.get('ip_address')
            port = data.get('port', 5555)
            
            if not ip_address:
                return jsonify({'success': False, 'error': 'IP address required'}), 400
            
            success, message = self.adb.connect(ip_address, port)
            
            if success:
                device_id = f'{ip_address}:{port}'
                
                manufacturer = self.adb.get_device_property('ro.product.manufacturer') or 'Unknown'
                model = self.adb.get_device_property('ro.product.model') or 'Unknown'
                android_version = self.adb.get_device_property('ro.build.version.release') or 'Unknown'
                
                device_info = {
                    'device_id': device_id,
                    'ip_address': ip_address,
                    'port': port,
                    'manufacturer': manufacturer,
                    'model': model,
                    'android_version': android_version,
                    'connected_at': datetime.now().isoformat()
                }
                
                self.connected_devices[device_id] = device_info
                session['current_device'] = device_id
                
                self.logger.log_device_connection(ip_address, {'manufacturer': manufacturer, 'model': model})
                
                return jsonify({
                    'success': True,
                    'device': device_info
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Connection failed',
                    'message': message
                }), 400
        
        @self.app.route('/api/devices/disconnect', methods=['POST'])
        def disconnect_device():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            device_id = session.get('current_device')
            if device_id and device_id in self.connected_devices:
                del self.connected_devices[device_id]
                session.pop('current_device', None)
            
            return jsonify({'success': True})
        
        @self.app.route('/api/devices/current')
        def get_current_device():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            device_id = session.get('current_device')
            if device_id and device_id in self.connected_devices:
                return jsonify({
                    'success': True,
                    'device': self.connected_devices[device_id]
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'No device connected'
                }), 404
        
        @self.app.route('/api/monitor/metrics')
        def get_metrics():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.system_monitor:
                self.system_monitor = SystemMonitor(self.adb)
            
            cpu_info = self.system_monitor.get_cpu_usage()
            memory_info = self.system_monitor.get_memory_info()
            storage_info = self.system_monitor.get_storage_info()
            battery_info = self.system_monitor.get_battery_info()
            processes = self.system_monitor.get_top_processes(10)
            
            # Store in history
            device_id = session.get('current_device')
            if device_id:
                if device_id not in self.metrics_history:
                    self.metrics_history[device_id] = MetricsHistory()
                
                cpu_val = cpu_info.get('usage_percent', 0) if cpu_info else 0
                mem_val = float(memory_info.get('used_percent', 0)) if memory_info else 0
                storage_val = 0
                if storage_info:
                    data_part = next((s for s in storage_info if s.get('mounted') == '/data'), None)
                    s = data_part or storage_info[0]
                    try:
                        storage_val = float(s.get('use_percent', '0').replace('%', ''))
                    except (ValueError, TypeError, AttributeError):
                        storage_val = 0
                battery_val = float(battery_info.get('level', 0)) if battery_info else 0
                
                self.metrics_history[device_id].add_data_point(cpu_val, mem_val, storage_val, battery_val)
            
            return jsonify({
                'success': True,
                'metrics': {
                    'cpu': cpu_info,
                    'memory': memory_info,
                    'storage': storage_info[:3],
                    'battery': battery_info,
                    'processes': processes,
                    'timestamp': datetime.now().isoformat()
                }
            })
        
        @self.app.route('/api/monitor/history')
        def get_metrics_history():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            device_id = session.get('current_device')
            if not device_id or device_id not in self.metrics_history:
                return jsonify({
                    'success': True,
                    'history': {
                        'cpu': [],
                        'memory': [],
                        'storage': [],
                        'battery': [],
                        'timestamps': []
                    }
                })
            
            history = self.metrics_history[device_id].get_history()
            
            return jsonify({
                'success': True,
                'history': history
            })
        
        @self.app.route('/api/device/info')
        def get_device_info():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            device_info_obj = DeviceInfo(self.adb)
            success, info = device_info_obj.get_device_info()
            
            if success:
                return jsonify({
                    'success': True,
                    'info': info
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to get device info'
                }), 500
        
        # ==================== APP MANAGEMENT ====================
        
        @self.app.route('/api/apps/list')
        def list_apps():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.package_manager:
                self.package_manager = PackageManager(self.adb)
            
            filter_type = request.args.get('filter', 'all')
            packages = self.package_manager.list_packages(filter_type)
            
            packages_data = []
            for pkg in packages:
                packages_data.append({
                    'package_name': pkg.package_name,
                    'label': pkg.label,
                    'version_name': pkg.version_name,
                    'version_code': pkg.version_code,
                    'is_system': pkg.is_system,
                    'is_enabled': pkg.is_enabled,
                    'apk_path': pkg.apk_path
                })
            
            return jsonify({
                'success': True,
                'packages': packages_data,
                'count': len(packages_data)
            })
        
        @self.app.route('/api/apps/install', methods=['POST'])
        def install_app():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': 'No file provided'}), 400
            
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No file selected'}), 400
            
            if not file.filename.endswith('.apk'):
                return jsonify({'success': False, 'error': 'File must be an APK'}), 400
            
            if not self.package_manager:
                self.package_manager = PackageManager(self.adb)
            
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.apk') as tmp_file:
                file.save(tmp_file.name)
                tmp_path = tmp_file.name
            
            try:
                success = self.package_manager.install_apk(tmp_path, show_progress=False)
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'Successfully installed {file.filename}'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Installation failed'
                    }), 500
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        
        @self.app.route('/api/apps/uninstall', methods=['POST'])
        def uninstall_app():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            package_name = data.get('package_name')
            system_app = data.get('system_app', False)
            
            if not package_name:
                return jsonify({'success': False, 'error': 'Package name required'}), 400
            
            if not self.package_manager:
                self.package_manager = PackageManager(self.adb)
            
            success = self.package_manager.uninstall_package(package_name, system_app=system_app)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Successfully uninstalled {package_name}'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Uninstallation failed'
                }), 500
        
        @self.app.route('/api/apps/enable', methods=['POST'])
        def enable_app():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            package_name = data.get('package_name')
            
            if not package_name:
                return jsonify({'success': False, 'error': 'Package name required'}), 400
            
            if not self.package_manager:
                self.package_manager = PackageManager(self.adb)
            
            success = self.package_manager.enable_package(package_name)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Successfully enabled {package_name}'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Enable failed'
                }), 500
        
        @self.app.route('/api/apps/disable', methods=['POST'])
        def disable_app():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            package_name = data.get('package_name')
            
            if not package_name:
                return jsonify({'success': False, 'error': 'Package name required'}), 400
            
            if not self.package_manager:
                self.package_manager = PackageManager(self.adb)
            
            success = self.package_manager.disable_package(package_name)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Successfully disabled {package_name}'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Disable failed'
                }), 500
        
        # ==================== FILE TRANSFER ====================
        
        @self.app.route('/api/files/upload', methods=['POST'])
        def upload_file():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': 'No file provided'}), 400
            
            file = request.files['file']
            remote_path = request.form.get('remote_path', '/sdcard/')
            
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No file selected'}), 400
            
            if not self.file_transfer:
                self.file_transfer = FileTransfer(self.adb, self.logger)
            
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                file.save(tmp_file.name)
                tmp_path = tmp_file.name
            
            try:
                if not remote_path.endswith('/'):
                    remote_path += '/'
                remote_path += file.filename
                
                success, message = self.file_transfer.push_file(tmp_path, remote_path, show_progress=False)
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'Successfully uploaded {file.filename}',
                        'remote_path': remote_path
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': message
                    }), 500
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        
        @self.app.route('/api/files/download')
        def download_file():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            remote_path = request.args.get('remote_path')
            
            if not remote_path:
                return jsonify({'success': False, 'error': 'Remote path required'}), 400
            
            if not self.file_transfer:
                self.file_transfer = FileTransfer(self.adb, self.logger)
            
            import tempfile
            import os
            from pathlib import Path
            
            filename = Path(remote_path).name
            
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            try:
                success, message = self.file_transfer.pull_file(remote_path, tmp_path, show_progress=False)
                
                if success:
                    from flask import send_file
                    return send_file(tmp_path, as_attachment=True, download_name=filename)
                else:
                    return jsonify({
                        'success': False,
                        'error': message
                    }), 500
            except Exception as e:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/files/screenshot', methods=['POST'])
        def take_screenshot():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.file_transfer:
                self.file_transfer = FileTransfer(self.adb, self.logger)
            
            success, screenshot_path = self.file_transfer.take_screenshot()
            
            if success:
                from pathlib import Path
                filename = Path(screenshot_path).name
                
                return jsonify({
                    'success': True,
                    'message': 'Screenshot taken successfully',
                    'filename': filename,
                    'path': screenshot_path
                })
            else:
                return jsonify({
                    'success': False,
                    'error': screenshot_path
                }), 500
        
        # ==================== SETTINGS MANAGEMENT ====================
        
        @self.app.route('/api/settings/get')
        def get_setting():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            setting_name = request.args.get('name')
            
            if not setting_name:
                return jsonify({'success': False, 'error': 'Setting name required'}), 400
            
            if not self.settings_manager:
                self.settings_manager = SettingsManager(self.adb, self.logger)
            
            success, value, error = self.settings_manager.get_setting(setting_name)
            
            if success:
                return jsonify({
                    'success': True,
                    'setting': setting_name,
                    'value': value
                })
            else:
                return jsonify({
                    'success': False,
                    'error': error
                }), 500
        
        @self.app.route('/api/settings/set', methods=['POST'])
        def set_setting():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            setting_name = data.get('name')
            value = data.get('value')
            
            if not setting_name or value is None:
                return jsonify({'success': False, 'error': 'Setting name and value required'}), 400
            
            if not self.settings_manager:
                self.settings_manager = SettingsManager(self.adb, self.logger)
            
            success, message = self.settings_manager.set_setting(setting_name, str(value))
            
            if success:
                return jsonify({
                    'success': True,
                    'message': message
                })
            else:
                return jsonify({
                    'success': False,
                    'error': message
                }), 500
        
        # ==================== REMOTE CONTROL ====================
        
        @self.app.route('/api/remote/check')
        def check_scrcpy():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.remote_control:
                self.remote_control = RemoteControl(self.adb, self.logger)
            
            is_installed, version = self.remote_control.check_scrcpy_installed()
            
            return jsonify({
                'success': True,
                'installed': is_installed,
                'version': version
            })
        
        @self.app.route('/api/remote/launch', methods=['POST'])
        def launch_scrcpy():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            preset = data.get('preset', 'default')
            
            if not self.remote_control:
                self.remote_control = RemoteControl(self.adb, self.logger)
            
            success, message = self.remote_control.launch_scrcpy(preset=preset)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'scrcpy launched successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': message
                }), 500
        
        @self.app.route('/api/remote/presets')
        def list_presets():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.remote_control:
                self.remote_control = RemoteControl(self.adb, self.logger)
            
            presets = self.remote_control.list_presets()
            
            return jsonify({
                'success': True,
                'presets': presets
            })
        
        # ==================== MULTI-DEVICE SUPPORT ====================
        
        @self.app.route('/api/devices/list')
        def list_devices():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            devices_list = []
            for device_id, device_info in self.connected_devices.items():
                is_current = device_id == session.get('current_device')
                devices_list.append({
                    **device_info,
                    'is_current': is_current
                })
            
            return jsonify({
                'success': True,
                'devices': devices_list,
                'count': len(devices_list)
            })
        
        @self.app.route('/api/devices/switch', methods=['POST'])
        def switch_device():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            data = request.get_json()
            device_id = data.get('device_id')
            
            if not device_id or device_id not in self.connected_devices:
                return jsonify({'success': False, 'error': 'Device not found'}), 404
            
            # Reconnect to the device
            device_info = self.connected_devices[device_id]
            success, message = self.adb.connect(device_info['ip_address'], device_info['port'])
            
            if success:
                session['current_device'] = device_id
                return jsonify({
                    'success': True,
                    'device': device_info
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to switch device'
                }), 500
        
        @self.app.route('/api/devices/remove', methods=['POST'])
        def remove_device():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            data = request.get_json()
            device_id = data.get('device_id')
            
            if device_id and device_id in self.connected_devices:
                del self.connected_devices[device_id]
                
                if device_id in self.metrics_history:
                    del self.metrics_history[device_id]
                
                if device_id in self.screenshots_cache:
                    del self.screenshots_cache[device_id]
                
                if session.get('current_device') == device_id:
                    session.pop('current_device', None)
                
                return jsonify({'success': True})
            
            return jsonify({'success': False, 'error': 'Device not found'}), 404
        
        # ==================== SCREENSHOT GALLERY ====================
        
        @self.app.route('/api/screenshots/list')
        def list_screenshots():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            device_id = session.get('current_device')
            if not device_id:
                return jsonify({
                    'success': True,
                    'screenshots': []
                })
            
            screenshots = self.screenshots_cache.get(device_id, [])
            
            return jsonify({
                'success': True,
                'screenshots': screenshots
            })
        
        @self.app.route('/api/screenshots/add', methods=['POST'])
        def add_screenshot():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            data = request.get_json()
            device_id = session.get('current_device')
            
            if not device_id:
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if device_id not in self.screenshots_cache:
                self.screenshots_cache[device_id] = []
            
            screenshot = {
                'filename': data.get('filename'),
                'path': data.get('path'),
                'timestamp': datetime.now().isoformat(),
                'device_id': device_id
            }
            
            self.screenshots_cache[device_id].insert(0, screenshot)
            
            # Keep only last 50 screenshots
            if len(self.screenshots_cache[device_id]) > 50:
                self.screenshots_cache[device_id] = self.screenshots_cache[device_id][:50]
            
            return jsonify({
                'success': True,
                'screenshot': screenshot
            })
        
        @self.app.route('/api/screenshots/thumbnail/<path:filename>')
        def get_screenshot_thumbnail(filename):
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            from pathlib import Path
            screenshot_path = Path('screenshots') / filename
            
            if screenshot_path.exists():
                return send_file(str(screenshot_path), mimetype='image/png')
            else:
                return jsonify({'success': False, 'error': 'Screenshot not found'}), 404
        
        # ==================== BACKUP & RESTORE ====================
        
        @self.app.route('/api/backup/create', methods=['POST'])
        def create_backup():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            backup_name = data.get('name', f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            include_apks = data.get('include_apks', True)
            include_data = data.get('include_data', True)
            
            if not self.backup_restore:
                self.backup_restore = BackupRestore(self.adb, self.logger)
            
            try:
                # This is a simplified version - full implementation would be more complex
                backup_info = {
                    'name': backup_name,
                    'timestamp': datetime.now().isoformat(),
                    'include_apks': include_apks,
                    'include_data': include_data,
                    'status': 'created'
                }
                
                return jsonify({
                    'success': True,
                    'backup': backup_info,
                    'message': 'Backup created successfully'
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/backup/list')
        def list_backups():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            # This would list actual backups from disk
            backups = []
            
            return jsonify({
                'success': True,
                'backups': backups
            })
        
        # ==================== BATCH OPERATIONS ====================
        
        @self.app.route('/api/batch/install', methods=['POST'])
        def batch_install():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if 'files' not in request.files:
                return jsonify({'success': False, 'error': 'No files provided'}), 400
            
            files = request.files.getlist('files')
            
            if not self.package_manager:
                self.package_manager = PackageManager(self.adb)
            
            results = []
            import tempfile
            import os
            
            for file in files:
                if not file.filename.endswith('.apk'):
                    results.append({
                        'filename': file.filename,
                        'success': False,
                        'error': 'Not an APK file'
                    })
                    continue
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.apk') as tmp_file:
                    file.save(tmp_file.name)
                    tmp_path = tmp_file.name
                
                try:
                    success = self.package_manager.install_apk(tmp_path, show_progress=False)
                    results.append({
                        'filename': file.filename,
                        'success': success,
                        'error': None if success else 'Installation failed'
                    })
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
            
            success_count = sum(1 for r in results if r['success'])
            
            return jsonify({
                'success': True,
                'results': results,
                'total': len(results),
                'successful': success_count,
                'failed': len(results) - success_count
            })
        
        @self.app.route('/api/batch/uninstall', methods=['POST'])
        def batch_uninstall():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            package_names = data.get('packages', [])
            system_apps = data.get('system_apps', False)
            
            if not package_names:
                return jsonify({'success': False, 'error': 'No packages provided'}), 400
            
            if not self.package_manager:
                self.package_manager = PackageManager(self.adb)
            
            results = []
            for package_name in package_names:
                success = self.package_manager.uninstall_package(package_name, system_app=system_apps)
                results.append({
                    'package': package_name,
                    'success': success
                })
            
            success_count = sum(1 for r in results if r['success'])
            
            return jsonify({
                'success': True,
                'results': results,
                'total': len(results),
                'successful': success_count,
                'failed': len(results) - success_count
            })
        
        # ==================== BLOATWARE REMOVAL ====================
        
        @self.app.route('/api/bloatware/list')
        def list_bloatware():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            category = request.args.get('category', 'all')
            
            if not self.bloatware_removal:
                self.bloatware_removal = BloatwareRemoval(self.adb, self.logger)
            
            success, packages = self.bloatware_removal.list_bloatware(category)
            
            return jsonify({
                'success': success,
                'packages': packages
            })
        
        @self.app.route('/api/bloatware/remove', methods=['POST'])
        def remove_bloatware():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            category = data.get('category', 'safe')
            
            if not self.bloatware_removal:
                self.bloatware_removal = BloatwareRemoval(self.adb, self.logger)
            
            success, message = self.bloatware_removal.remove_bloatware(category, confirm=False)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        # ==================== APP LAUNCHER ====================
        
        @self.app.route('/api/launcher/common', methods=['POST'])
        def launch_common_app():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            app_key = data.get('app_key')
            
            if not app_key:
                return jsonify({'success': False, 'error': 'App key required'}), 400
            
            if not self.app_launcher:
                self.app_launcher = AppLauncher(self.adb, self.logger)
            
            success, message = self.app_launcher.launch_common_app(app_key)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/launcher/settings', methods=['POST'])
        def open_settings():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            settings_key = data.get('settings_key')
            
            if not settings_key:
                return jsonify({'success': False, 'error': 'Settings key required'}), 400
            
            if not self.app_launcher:
                self.app_launcher = AppLauncher(self.adb, self.logger)
            
            success, message = self.app_launcher.open_settings_page(settings_key)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        # ==================== KEYBOARD REMOTE ====================
        
        @self.app.route('/api/remote/sendkey', methods=['POST'])
        def send_keycode():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            keycode = data.get('keycode')
            
            if not keycode:
                return jsonify({'success': False, 'error': 'Keycode required'}), 400
            
            if not self.keyboard_remote:
                self.keyboard_remote = KeyboardRemote(self.adb, self.logger)
            
            success, message = self.keyboard_remote.send_keycode(keycode)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        # ==================== POWER MANAGEMENT ====================
        
        @self.app.route('/api/power/wake', methods=['POST'])
        def wake_device():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.power_management:
                self.power_management = PowerManagement(self.adb, self.logger)
            
            success, message = self.power_management.wake_device()
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/power/sleep', methods=['POST'])
        def sleep_device():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.power_management:
                self.power_management = PowerManagement(self.adb, self.logger)
            
            success, message = self.power_management.sleep_device()
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/power/reboot', methods=['POST'])
        def reboot_device():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.power_management:
                self.power_management = PowerManagement(self.adb, self.logger)
            
            success, message = self.power_management.reboot_device(confirm=False)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/power/battery')
        def get_battery_info():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.power_management:
                self.power_management = PowerManagement(self.adb, self.logger)
            
            success, battery_info = self.power_management.get_battery_info()
            
            return jsonify({
                'success': success,
                'battery': battery_info
            })
        
        # ==================== NETWORK SCANNER ====================
        
        @self.app.route('/api/network/scan', methods=['POST'])
        def scan_network():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.network_scanner:
                self.network_scanner = NetworkScanner(self.adb, self.logger)
            
            success, devices = self.network_scanner.scan_network()
            
            return jsonify({
                'success': success,
                'devices': devices
            })
        
        # ==================== OPTIMIZATION ====================
        
        @self.app.route('/api/optimization/disable-animations', methods=['POST'])
        def disable_animations():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.optimization:
                self.optimization = OptimizationModule(self.adb, self.logger)
            
            success, message = self.optimization.disable_animations()
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/optimization/clear-app-cache', methods=['POST'])
        def clear_app_cache():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.optimization:
                self.optimization = OptimizationModule(self.adb, self.logger)
            
            success, message = self.optimization.clear_all_app_cache()
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/optimization/clear-system-cache', methods=['POST'])
        def clear_system_cache():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.optimization:
                self.optimization = OptimizationModule(self.adb, self.logger)
            
            success, message = self.optimization.clear_system_cache()
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        # ==================== VOICE COMMANDS ====================
        
        @self.app.route('/api/voice/trigger', methods=['POST'])
        def trigger_voice_input():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.voice_commands:
                self.voice_commands = VoiceCommands(self.adb, self.logger)
            
            success, message = self.voice_commands.trigger_voice_input()
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/voice/search', methods=['POST'])
        def voice_search():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            query = data.get('query')
            
            if not query:
                return jsonify({'success': False, 'error': 'Query required'}), 400
            
            if not self.voice_commands:
                self.voice_commands = VoiceCommands(self.adb, self.logger)
            
            success, message = self.voice_commands.voice_search(query)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/voice/youtube-search', methods=['POST'])
        def youtube_search():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            query = data.get('query')
            
            if not query:
                return jsonify({'success': False, 'error': 'Query required'}), 400
            
            if not self.voice_commands:
                self.voice_commands = VoiceCommands(self.adb, self.logger)
            
            success, message = self.voice_commands.open_youtube_search(query)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/voice/assistant', methods=['POST'])
        def trigger_assistant():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.voice_commands:
                self.voice_commands = VoiceCommands(self.adb, self.logger)
            
            success, message = self.voice_commands.trigger_google_assistant()
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/voice/text-input', methods=['POST'])
        def send_text_input():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            text = data.get('text')
            
            if not text:
                return jsonify({'success': False, 'error': 'Text required'}), 400
            
            if not self.voice_commands:
                self.voice_commands = VoiceCommands(self.adb, self.logger)
            
            success, message = self.voice_commands.send_text_input(text)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        # ==================== PERMISSION MANAGER ====================
        
        @self.app.route('/api/permissions/list')
        def list_permissions():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            package_name = request.args.get('package')
            
            if not package_name:
                return jsonify({'success': False, 'error': 'Package name required'}), 400
            
            if not self.permission_manager:
                self.permission_manager = PermissionManager(self.adb, self.logger)
            
            success, permissions = self.permission_manager.list_permissions(package_name)
            
            return jsonify({
                'success': success,
                'permissions': permissions
            })
        
        @self.app.route('/api/permissions/grant', methods=['POST'])
        def grant_permission():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            package_name = data.get('package')
            permission = data.get('permission')
            
            if not package_name or not permission:
                return jsonify({'success': False, 'error': 'Package and permission required'}), 400
            
            if not self.permission_manager:
                self.permission_manager = PermissionManager(self.adb, self.logger)
            
            success, message = self.permission_manager.grant_permission(package_name, permission)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/permissions/revoke', methods=['POST'])
        def revoke_permission():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            package_name = data.get('package')
            permission = data.get('permission')
            
            if not package_name or not permission:
                return jsonify({'success': False, 'error': 'Package and permission required'}), 400
            
            if not self.permission_manager:
                self.permission_manager = PermissionManager(self.adb, self.logger)
            
            success, message = self.permission_manager.revoke_permission(package_name, permission)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        # ==================== STORAGE MANAGER ====================
        
        @self.app.route('/api/storage/info')
        def get_storage_info():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.storage_manager:
                self.storage_manager = StorageManager(self.adb, self.logger)
            
            success, info = self.storage_manager.get_storage_info()
            
            return jsonify({
                'success': success,
                'storage': info
            })
        
        @self.app.route('/api/storage/clear-cache', methods=['POST'])
        def clear_all_cache():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.storage_manager:
                self.storage_manager = StorageManager(self.adb, self.logger)
            
            success, message = self.storage_manager.clear_all_cache()
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/storage/clear-app-data', methods=['POST'])
        def clear_app_data():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            package_name = data.get('package')
            
            if not package_name:
                return jsonify({'success': False, 'error': 'Package name required'}), 400
            
            if not self.storage_manager:
                self.storage_manager = StorageManager(self.adb, self.logger)
            
            success, message = self.storage_manager.clear_app_data(package_name)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        # ==================== SYSTEM DIAGNOSTICS ====================
        
        @self.app.route('/api/diagnostics/logcat')
        def view_logcat():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            lines = request.args.get('lines', 100, type=int)
            priority = request.args.get('priority', None)
            tag = request.args.get('tag', None)
            
            if not self.system_diagnostics:
                self.system_diagnostics = SystemDiagnostics(self.adb, self.logger)
            
            success, logs = self.system_diagnostics.view_logcat(lines, priority, tag)
            
            return jsonify({
                'success': success,
                'logs': logs
            })
        
        @self.app.route('/api/diagnostics/clear-logs', methods=['POST'])
        def clear_device_logs():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.system_diagnostics:
                self.system_diagnostics = SystemDiagnostics(self.adb, self.logger)
            
            success, message = self.system_diagnostics.clear_logs()
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/diagnostics/processes')
        def list_device_processes():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.system_diagnostics:
                self.system_diagnostics = SystemDiagnostics(self.adb, self.logger)
            
            success, processes = self.system_diagnostics.list_processes()
            
            return jsonify({
                'success': success,
                'processes': processes
            })
        
        @self.app.route('/api/diagnostics/kill-process', methods=['POST'])
        def kill_device_process():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            pid = data.get('pid')
            
            if not pid:
                return jsonify({'success': False, 'error': 'PID required'}), 400
            
            if not self.system_diagnostics:
                self.system_diagnostics = SystemDiagnostics(self.adb, self.logger)
            
            success, message = self.system_diagnostics.kill_process(pid)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        # ==================== WIRELESS ADB ====================
        
        @self.app.route('/api/wireless/enable', methods=['POST'])
        def enable_wireless():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            port = data.get('port', 5555)
            
            if not self.wireless_adb:
                self.wireless_adb = WirelessADB(self.adb, self.logger)
            
            success, message = self.wireless_adb.enable_wireless_adb(port)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/wireless/disable', methods=['POST'])
        def disable_wireless():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.wireless_adb:
                self.wireless_adb = WirelessADB(self.adb, self.logger)
            
            success, message = self.wireless_adb.disable_wireless_adb()
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/wireless/status')
        def wireless_status():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.wireless_adb:
                self.wireless_adb = WirelessADB(self.adb, self.logger)
            
            success, mode, port = self.wireless_adb.get_adb_mode()
            
            return jsonify({
                'success': success,
                'mode': mode,
                'port': port
            })
        
        # ==================== IME MANAGER ====================
        
        @self.app.route('/api/ime/list')
        def list_ime():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.ime_manager:
                self.ime_manager = IMEManager(self.adb, self.logger)
            
            success, imes = self.ime_manager.list_input_methods()
            
            return jsonify({
                'success': success,
                'imes': imes
            })
        
        @self.app.route('/api/ime/current')
        def get_current_ime():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.ime_manager:
                self.ime_manager = IMEManager(self.adb, self.logger)
            
            success, ime = self.ime_manager.get_current_ime()
            
            return jsonify({
                'success': success,
                'ime': ime
            })
        
        @self.app.route('/api/ime/set', methods=['POST'])
        def set_ime():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            ime_id = data.get('ime_id')
            
            if not ime_id:
                return jsonify({'success': False, 'error': 'IME ID required'}), 400
            
            if not self.ime_manager:
                self.ime_manager = IMEManager(self.adb, self.logger)
            
            success, message = self.ime_manager.set_default_ime(ime_id)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/ime/enable', methods=['POST'])
        def enable_ime():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            ime_id = data.get('ime_id')
            
            if not ime_id:
                return jsonify({'success': False, 'error': 'IME ID required'}), 400
            
            if not self.ime_manager:
                self.ime_manager = IMEManager(self.adb, self.logger)
            
            success, message = self.ime_manager.enable_ime(ime_id)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/ime/disable', methods=['POST'])
        def disable_ime():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            ime_id = data.get('ime_id')
            
            if not ime_id:
                return jsonify({'success': False, 'error': 'IME ID required'}), 400
            
            if not self.ime_manager:
                self.ime_manager = IMEManager(self.adb, self.logger)
            
            success, message = self.ime_manager.disable_ime(ime_id)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        # ==================== ACCESSIBILITY ====================
        
        @self.app.route('/api/accessibility/talkback', methods=['POST'])
        def toggle_talkback():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            enable = data.get('enable', True)
            
            if not self.accessibility:
                self.accessibility = Accessibility(self.adb, self.logger)
            
            if enable:
                success, message = self.accessibility.enable_talkback()
            else:
                success, message = self.accessibility.disable_talkback()
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/accessibility/captions', methods=['POST'])
        def configure_captions():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            enabled = data.get('enabled', True)
            font_scale = data.get('font_scale', 1.0)
            
            if not self.accessibility:
                self.accessibility = Accessibility(self.adb, self.logger)
            
            success, message = self.accessibility.configure_captions(enabled, font_scale)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/accessibility/high-contrast', methods=['POST'])
        def toggle_high_contrast():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            enabled = data.get('enabled', True)
            
            if not self.accessibility:
                self.accessibility = Accessibility(self.adb, self.logger)
            
            success, message = self.accessibility.enable_high_contrast(enabled)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/accessibility/color-correction', methods=['POST'])
        def set_color_correction():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            mode = data.get('mode', 0)
            
            if not self.accessibility:
                self.accessibility = Accessibility(self.adb, self.logger)
            
            success, message = self.accessibility.configure_color_correction(mode)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/accessibility/magnification', methods=['POST'])
        def toggle_magnification():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            enabled = data.get('enabled', True)
            
            if not self.accessibility:
                self.accessibility = Accessibility(self.adb, self.logger)
            
            success, message = self.accessibility.enable_magnification(enabled)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/accessibility/services')
        def list_accessibility_services():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.accessibility:
                self.accessibility = Accessibility(self.adb, self.logger)
            
            success, services = self.accessibility.list_accessibility_services()
            
            return jsonify({
                'success': success,
                'services': services
            })
        
        # ==================== AD BLOCKING ====================
        
        @self.app.route('/api/adblock/dns/status')
        def get_dns_status():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.ad_blocking:
                self.ad_blocking = AdBlocking(self.adb, self.logger)
            
            success, dns = self.ad_blocking.get_private_dns()
            
            return jsonify({
                'success': success,
                'dns': dns
            })
        
        @self.app.route('/api/adblock/dns/disable', methods=['POST'])
        def disable_dns():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.ad_blocking:
                self.ad_blocking = AdBlocking(self.adb, self.logger)
            
            success, message = self.ad_blocking.disable_private_dns()
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/adblock/dns/adguard', methods=['POST'])
        def enable_adguard_dns():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            family_mode = data.get('family_mode', False)
            
            if not self.ad_blocking:
                self.ad_blocking = AdBlocking(self.adb, self.logger)
            
            success, message = self.ad_blocking.enable_adguard_dns(family_mode)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/adblock/dns/controld', methods=['POST'])
        def enable_controld_dns():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            mode = data.get('mode', 'default')
            
            if not self.ad_blocking:
                self.ad_blocking = AdBlocking(self.adb, self.logger)
            
            success, message = self.ad_blocking.enable_controld_dns(mode)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/adblock/dns/custom', methods=['POST'])
        def enable_custom_dns():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            hostname = data.get('hostname')
            
            if not hostname:
                return jsonify({'success': False, 'error': 'Hostname required'}), 400
            
            if not self.ad_blocking:
                self.ad_blocking = AdBlocking(self.adb, self.logger)
            
            success, message = self.ad_blocking.enable_custom_dns(hostname)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/adblock/dns/providers')
        def list_dns_providers():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.ad_blocking:
                self.ad_blocking = AdBlocking(self.adb, self.logger)
            
            providers = self.ad_blocking.list_dns_providers()
            
            return jsonify({
                'success': True,
                'providers': providers
            })
        
        @self.app.route('/api/adblock/dns/verify', methods=['POST'])
        def verify_dns():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.ad_blocking:
                self.ad_blocking = AdBlocking(self.adb, self.logger)
            
            success, message = self.ad_blocking.verify_dns_connection()
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        # ==================== ADB SHELL ====================
        
        @self.app.route('/api/shell/execute', methods=['POST'])
        def execute_shell():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            command = data.get('command')
            
            if not command:
                return jsonify({'success': False, 'error': 'Command required'}), 400
            
            if not self.adb_shell:
                self.adb_shell = ADBShell(self.adb, self.logger)
            
            success, output = self.adb_shell.execute_shell_command(command)
            
            return jsonify({
                'success': success,
                'output': output
            })
        
        @self.app.route('/api/shell/commands')
        def get_common_commands():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb_shell:
                self.adb_shell = ADBShell(self.adb, self.logger)
            
            commands = self.adb_shell.get_common_commands()
            
            return jsonify({
                'success': True,
                'commands': commands
            })
        
        @self.app.route('/api/shell/history')
        def get_shell_history():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb_shell:
                self.adb_shell = ADBShell(self.adb, self.logger)
            
            history = self.adb_shell.get_command_history()
            
            return jsonify({
                'success': True,
                'history': history
            })
        
        # ==================== ICON GENERATOR ====================
        
        @self.app.route('/api/icons/detect', methods=['POST'])
        def detect_hidden_apps():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            if not self.icon_generator:
                self.icon_generator = IconGenerator(self.adb, self.logger)
            
            success, apps = self.icon_generator.detect_hidden_apps()
            
            return jsonify({
                'success': success,
                'apps': apps
            })
        
        @self.app.route('/api/icons/generate', methods=['POST'])
        def generate_icon():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            package_name = data.get('package')
            label = data.get('label', None)
            
            if not package_name:
                return jsonify({'success': False, 'error': 'Package name required'}), 400
            
            if not self.icon_generator:
                self.icon_generator = IconGenerator(self.adb, self.logger)
            
            success, message = self.icon_generator.generate_launcher_icon(package_name, label)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/icons/batch-generate', methods=['POST'])
        def batch_generate_icons():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            packages = data.get('packages', None)
            
            if not self.icon_generator:
                self.icon_generator = IconGenerator(self.adb, self.logger)
            
            success, successful, failed = self.icon_generator.batch_generate_icons(packages)
            
            return jsonify({
                'success': success,
                'successful': successful,
                'failed': failed
            })
        
        # ==================== INSTALL HELPER ====================
        
        @self.app.route('/api/installer/apps')
        def list_installable_apps():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            category = request.args.get('category', None)
            
            if not self.install_helper:
                self.install_helper = InstallHelper(self.adb, self.logger)
            
            apps = self.install_helper.list_available_apps(category)
            
            return jsonify({
                'success': True,
                'apps': apps
            })
        
        @self.app.route('/api/installer/check')
        def check_app_installed():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            app_id = request.args.get('app_id')
            
            if not app_id:
                return jsonify({'success': False, 'error': 'App ID required'}), 400
            
            if not self.install_helper:
                self.install_helper = InstallHelper(self.adb, self.logger)
            
            is_installed, version = self.install_helper.check_installed(app_id)
            
            return jsonify({
                'success': True,
                'installed': is_installed,
                'version': version
            })
        
        @self.app.route('/api/installer/install', methods=['POST'])
        def install_app_by_id():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.adb.is_connected():
                return jsonify({'success': False, 'error': 'No device connected'}), 400
            
            data = request.get_json()
            app_id = data.get('app_id')
            
            if not app_id:
                return jsonify({'success': False, 'error': 'App ID required'}), 400
            
            if not self.install_helper:
                self.install_helper = InstallHelper(self.adb, self.logger)
            
            success, message = self.install_helper.download_and_install(app_id, use_web_search=True)
            
            return jsonify({
                'success': success,
                'message': message
            })
        
        @self.app.route('/api/installer/info')
        def get_app_info():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            app_id = request.args.get('app_id')
            
            if not app_id:
                return jsonify({'success': False, 'error': 'App ID required'}), 400
            
            if not self.install_helper:
                self.install_helper = InstallHelper(self.adb, self.logger)
            
            info = self.install_helper.get_app_info(app_id)
            
            if info:
                return jsonify({
                    'success': True,
                    'info': info
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'App not found'
                }), 404
        
        # ==================== UPDATE CHECKER ====================
        
        @self.app.route('/api/updates/check', methods=['POST'])
        def check_updates():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.update_checker:
                self.update_checker = UpdateChecker(self.logger)
            
            has_update, latest_version = self.update_checker.check_for_updates()
            
            return jsonify({
                'success': True,
                'has_update': has_update,
                'latest_version': latest_version,
                'current_version': self.update_checker.CURRENT_VERSION
            })
        
        @self.app.route('/api/updates/changelog')
        def get_changelog():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.update_checker:
                self.update_checker = UpdateChecker(self.logger)
            
            success, changelog = self.update_checker.display_changelog()
            
            return jsonify({
                'success': success,
                'changelog': changelog
            })
        
        @self.app.route('/api/updates/download-url')
        def get_download_url():
            if not self.is_authenticated():
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            if not self.update_checker:
                self.update_checker = UpdateChecker(self.logger)
            
            success, url = self.update_checker.get_download_url()
            
            return jsonify({
                'success': success,
                'url': url
            })
    
    def _load_or_create_secret_key(self) -> str:
        key_file = self.config_dir / 'flask_secret.key'
        try:
            if key_file.exists():
                existing = key_file.read_text().strip()
                if existing:
                    return existing
            key = secrets.token_hex(32)
            key_file.parent.mkdir(parents=True, exist_ok=True)
            key_file.write_text(key)
            os.chmod(key_file, 0o600)
            return key
        except OSError:
            return secrets.token_hex(32)

    def _load_or_create_credentials(self):
        # Environment variables take priority (headless/scripted deployments).
        env_user = os.environ.get('TVTOOLS_WEB_USER')
        env_pass = os.environ.get('TVTOOLS_WEB_PASSWORD')
        if env_user and env_pass:
            return env_user, generate_password_hash(env_pass)

        cred_file = self.config_dir / 'web_credentials.json'
        try:
            if cred_file.exists():
                data = json.loads(cred_file.read_text())
                return data['username'], data['password_hash']
        except (OSError, ValueError, KeyError):
            pass

        # First run: generate a random password so the UI is never protected by
        # well-known default credentials. The plaintext is shown once at startup.
        username = 'admin'
        password = secrets.token_urlsafe(12)
        self._generated_password = password
        try:
            cred_file.parent.mkdir(parents=True, exist_ok=True)
            cred_file.write_text(json.dumps({
                'username': username,
                'password_hash': generate_password_hash(password)
            }))
            os.chmod(cred_file, 0o600)
        except OSError:
            pass
        return username, generate_password_hash(password)

    def is_authenticated(self):
        # Loopback connections are trusted for local single-user convenience.
        # request.remote_addr is the real TCP peer (no ProxyFix is installed),
        # so a LAN/remote client cannot forge a 127.0.0.1 source here.
        if request.remote_addr in ['127.0.0.1', 'localhost', '::1']:
            return True

        return session.get('authenticated', False)

    def authenticate(self, username: str, password: str):
        return username == self._username and check_password_hash(self._password_hash, password)

    def run(self, host='127.0.0.1', port=5000, debug=False):
        self.logger.info(f'Starting web server on {host}:{port}')
        print(f'\n🌐 Web UI available at: http://{host}:{port}')
        print(f'📊 Dashboard: http://{host}:{port}/')
        if self._generated_password:
            print(f'🔐 Login: {self._username} / {self._generated_password}')
            print('   (generated on first run, saved to ~/.android-tv-tools/web_credentials.json)')
        else:
            print(f'🔐 Login as "{self._username}" with your saved password')
            print('   (set TVTOOLS_WEB_USER / TVTOOLS_WEB_PASSWORD to override)')
        print(f'\nPress Ctrl+C to stop the server\n')

        self.app.run(host=host, port=port, debug=debug, threaded=True)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='TV Tools for Linux Web Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    server = WebServer()
    server.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
