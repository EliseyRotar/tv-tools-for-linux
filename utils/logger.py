import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json


class LogLevel:
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class Logger:
    def __init__(self, name: str = 'android-tv-tools', log_dir: Optional[str] = None):
        self.name = name

        if log_dir is None:
            home = Path.home()
            self.log_dir = home / '.android-tv-tools' / 'logs'
        else:
            self.log_dir = Path(log_dir)

        self._ensure_log_directory()

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            self._setup_handlers()

        self.device_history_file = self.log_dir.parent / 'device_history.txt'

    def _ensure_log_directory(self):
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f'Warning: Could not create log directory: {e}')

    def _setup_handlers(self):
        log_file = self.log_dir / f'{self.name}.log'

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        error_log_file = self.log_dir / f'{self.name}_errors.log'
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)

        self.file_handler = file_handler
        self.error_handler = error_handler

    def set_level(self, level: int):
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                if 'errors' not in str(handler.baseFilename):
                    handler.setLevel(level)

    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        if context:
            message = f'{message} | Context: {json.dumps(context)}'
        self.logger.debug(message)
        self._flush_handlers()

    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        if context:
            message = f'{message} | Context: {json.dumps(context)}'
        self.logger.info(message)
        self._flush_handlers()

    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        if context:
            message = f'{message} | Context: {json.dumps(context)}'
        self.logger.warning(message)
        self._flush_handlers()

    def error(self, message: str, context: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None):
        if context:
            message = f'{message} | Context: {json.dumps(context)}'

        if exception:
            message = f'{message} | Exception: {type(exception).__name__}: {str(exception)}'

        self.logger.error(message)
        self._flush_handlers()

    def critical(self, message: str, context: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None):
        if context:
            message = f'{message} | Context: {json.dumps(context)}'

        if exception:
            message = f'{message} | Exception: {type(exception).__name__}: {str(exception)}'

        self.logger.critical(message)
        self._flush_handlers()

    def log_event(self, event_type: str, description: str, context: Optional[Dict[str, Any]] = None):
        message = f'[{event_type}] {description}'
        self.info(message, context)

    def log_device_connection(self, ip_address: str, device_info: Optional[Dict[str, str]] = None):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        device_name = 'Unknown Device'
        if device_info:
            manufacturer = device_info.get('manufacturer', '')
            model = device_info.get('model', '')
            if manufacturer and model:
                device_name = f'{manufacturer} {model}'
            elif model:
                device_name = model

        log_entry = f'{timestamp} - {ip_address} - {device_name}\n'

        try:
            with open(self.device_history_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)

            self.log_event('DEVICE_CONNECTION', f'Connected to {ip_address}', {
                'ip': ip_address,
                'device': device_name,
                'timestamp': timestamp
            })

        except Exception as e:
            self.error('Failed to log device connection', exception=e)

    def get_device_history(self, limit: Optional[int] = None) -> list:
        history = []

        try:
            if not self.device_history_file.exists():
                return history

            with open(self.device_history_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                parts = line.split(' - ', 2)
                if len(parts) >= 2:
                    history.append({
                        'timestamp': parts[0],
                        'ip': parts[1],
                        'device': parts[2] if len(parts) > 2 else 'Unknown'
                    })

            if limit:
                history = history[-limit:]

            return history

        except Exception as e:
            self.error('Failed to read device history', exception=e)
            return []

    def get_last_connected_ip(self) -> Optional[str]:
        history = self.get_device_history(limit=1)
        if history:
            return history[0]['ip']
        return None

    def log_operation(self, operation: str, success: bool, details: Optional[str] = None,
                      context: Optional[Dict[str, Any]] = None):
        status = 'SUCCESS' if success else 'FAILED'
        message = f'Operation {operation} {status}'

        if details:
            message = f'{message}: {details}'

        if success:
            self.info(message, context)
        else:
            self.error(message, context)

    def log_command(self, command: str, exit_code: int, output: Optional[str] = None,
                    error: Optional[str] = None):
        context = {
            'command': command,
            'exit_code': exit_code
        }

        if output:
            context['output'] = output[:500]

        if error:
            context['error'] = error[:500]

        if exit_code == 0:
            self.debug(f'Command executed successfully: {command}', context)
        else:
            self.error(f'Command failed with exit code {exit_code}: {command}', context)

    def log_file_operation(self, operation: str, source: str, destination: Optional[str] = None,
                           success: bool = True, error: Optional[str] = None):
        context = {
            'operation': operation,
            'source': source
        }

        if destination:
            context['destination'] = destination

        if error:
            context['error'] = error

        message = f'File {operation}: {source}'
        if destination:
            message = f'{message} -> {destination}'

        if success:
            self.info(message, context)
        else:
            self.error(message, context)

    def log_package_operation(self, operation: str, package_name: str, success: bool,
                              error: Optional[str] = None):
        context = {
            'operation': operation,
            'package': package_name
        }

        if error:
            context['error'] = error

        message = f'Package {operation}: {package_name}'

        if success:
            self.info(message, context)
        else:
            self.error(message, context)

    def log_download(self, url: str, destination: str, success: bool,
                     size: Optional[int] = None, error: Optional[str] = None):
        context = {
            'url': url,
            'destination': destination
        }

        if size:
            context['size_bytes'] = size

        if error:
            context['error'] = error

        message = f'Download from {url} to {destination}'

        if success:
            self.info(message, context)
        else:
            self.error(message, context)

    def rotate_logs(self):
        for handler in self.logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                handler.doRollover()

        self.info('Log rotation performed')

    def clear_old_logs(self, days: int = 30):
        try:
            cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)

            for log_file in self.log_dir.glob('*.log*'):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    self.info(f'Deleted old log file: {log_file.name}')

        except Exception as e:
            self.error('Failed to clear old logs', exception=e)

    def get_log_files(self) -> list:
        try:
            log_files = []
            for log_file in self.log_dir.glob('*.log*'):
                log_files.append({
                    'name': log_file.name,
                    'path': str(log_file),
                    'size': log_file.stat().st_size,
                    'modified': datetime.fromtimestamp(log_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
            return sorted(log_files, key=lambda x: x['modified'], reverse=True)
        except Exception as e:
            self.error('Failed to get log files', exception=e)
            return []

    def _flush_handlers(self):
        for handler in self.logger.handlers:
            if hasattr(handler, 'flush'):
                handler.flush()

    def close(self):
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)


def create_logger(name: str = 'android-tv-tools', log_dir: Optional[str] = None) -> Logger:
    return Logger(name, log_dir)


_default_logger: Optional[Logger] = None


def get_default_logger() -> Logger:
    global _default_logger
    if _default_logger is None:
        _default_logger = create_logger()
    return _default_logger
