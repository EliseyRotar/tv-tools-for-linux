from typing import Tuple, Optional, List, Dict
from core.adb_manager import ADBManager
from utils.logger import Logger
from utils.colors import Colors


class VoiceCommands:

    PREDEFINED_COMMANDS = {
        'search': {
            'intent': 'android.intent.action.SEARCH',
            'description': 'Open voice search'
        },
        'assistant': {
            'intent': 'android.intent.action.VOICE_COMMAND',
            'description': 'Launch Google Assistant'
        },
        'home': {
            'keycode': 'KEYCODE_HOME',
            'description': 'Go to home screen'
        },
        'back': {
            'keycode': 'KEYCODE_BACK',
            'description': 'Go back'
        },
        'settings': {
            'intent': 'android.settings.SETTINGS',
            'description': 'Open settings'
        }
    }

    def __init__(self, adb_manager: ADBManager, logger: Optional[Logger] = None):
        self.adb = adb_manager
        self.logger = logger

    def trigger_voice_input(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🎤 Triggering Voice Input                      ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        result = self.adb.shell_command(
            'am start -a android.intent.action.VOICE_ASSIST'
        )

        if result.success or result.return_code == 0:
            print(f"{Colors.OKGREEN}✅ Voice input triggered{Colors.ENDC}")
            if self.logger:
                self.logger.log_event('voice_command', 'Triggered voice input')
            return True, "Voice input triggered successfully"
        else:
            print(f"{Colors.FAIL}❌ Failed to trigger voice input{Colors.ENDC}")
            return False, f"Failed to trigger voice input: {result.error}"

    def send_voice_command(self, command: str, query: Optional[str] = None) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🎤 Sending Voice Command                       ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if command not in self.PREDEFINED_COMMANDS:
            print(f"{Colors.FAIL}❌ Unknown command: {command}{Colors.ENDC}")
            return False, f"Unknown command: {command}"

        cmd_info = self.PREDEFINED_COMMANDS[command]
        print(f"{Colors.OKBLUE}ℹ️  Command: {cmd_info['description']}{Colors.ENDC}\n")

        if 'intent' in cmd_info:
            cmd = f"am start -a {cmd_info['intent']}"
            if query:
                cmd += f' --es query "{query}"'

            result = self.adb.shell_command(cmd)
        elif 'keycode' in cmd_info:
            result = self.adb.shell_command(f"input keyevent {cmd_info['keycode']}")
        else:
            return False, "Invalid command configuration"

        if result.success or result.return_code == 0:
            print(f"{Colors.OKGREEN}✅ Command sent successfully{Colors.ENDC}")
            if self.logger:
                self.logger.log_event('voice_command', f'Sent command: {command}')
            return True, f"Command '{command}' sent successfully"
        else:
            print(f"{Colors.FAIL}❌ Failed to send command{Colors.ENDC}")
            return False, f"Failed to send command: {result.error}"

    def voice_search(self, query: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🔍 Voice Search                                ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  Query: {query}{Colors.ENDC}\n")

        result = self.adb.shell_command(
            f'am start -a android.intent.action.WEB_SEARCH --es query "{query}"'
        )

        if result.success or result.return_code == 0:
            print(f"{Colors.OKGREEN}✅ Search initiated for: {query}{Colors.ENDC}")
            if self.logger:
                self.logger.log_event('voice_command', f'Voice search: {query}')
            return True, f"Search initiated for: {query}"
        else:
            print(f"{Colors.FAIL}❌ Failed to initiate search{Colors.ENDC}")
            return False, f"Failed to initiate search: {result.error}"

    def open_youtube_search(self, query: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📺 YouTube Search                              ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  Query: {query}{Colors.ENDC}\n")

        result = self.adb.shell_command(
            f'am start -a android.intent.action.SEARCH -n com.google.android.youtube.tv/.activity.ShellActivity --es query "{query}"')

        if result.success or result.return_code == 0:
            print(f"{Colors.OKGREEN}✅ YouTube search opened{Colors.ENDC}")
            if self.logger:
                self.logger.log_event('voice_command', f'YouTube search: {query}')
            return True, f"YouTube search opened for: {query}"
        else:
            print(f"{Colors.WARNING}⚠️  YouTube app may not be installed{Colors.ENDC}")
            return False, "YouTube app not found or search failed"

    def play_media(self, media_type: str, query: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ▶️  Play Media                                 ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  Type: {media_type}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  Query: {query}{Colors.ENDC}\n")

        media_types = {
            'music': 'audio/*',
            'video': 'video/*',
            'audio': 'audio/*'
        }

        mime_type = media_types.get(media_type.lower(), 'video/*')

        result = self.adb.shell_command(
            f'am start -a android.intent.action.VIEW -d "content://media/external/{media_type}/{query}" -t {mime_type}'
        )

        if result.success or result.return_code == 0:
            print(f"{Colors.OKGREEN}✅ Media playback initiated{Colors.ENDC}")
            if self.logger:
                self.logger.log_event('voice_command', f'Play {media_type}: {query}')
            return True, f"Playing {media_type}: {query}"
        else:
            print(f"{Colors.FAIL}❌ Failed to play media{Colors.ENDC}")
            return False, f"Failed to play media: {result.error}"

    def open_app_by_voice(self, app_name: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📱 Open App by Voice                           ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  App: {app_name}{Colors.ENDC}\n")

        result = self.adb.shell_command(
            f'am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n {app_name}'
        )

        if result.success or result.return_code == 0:
            print(f"{Colors.OKGREEN}✅ App opened: {app_name}{Colors.ENDC}")
            if self.logger:
                self.logger.log_event('voice_command', f'Opened app: {app_name}')
            return True, f"Opened app: {app_name}"
        else:
            print(f"{Colors.FAIL}❌ Failed to open app{Colors.ENDC}")
            return False, f"Failed to open app: {result.error}"

    def list_predefined_commands(self) -> List[Dict[str, str]]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           📋 Available Voice Commands                    ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        commands = []
        for cmd_name, cmd_info in self.PREDEFINED_COMMANDS.items():
            print(f"{Colors.OKBLUE}• {cmd_name:15} - {cmd_info['description']}{Colors.ENDC}")
            commands.append({
                'name': cmd_name,
                'description': cmd_info['description']
            })

        return commands

    def send_text_input(self, text: str) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           ⌨️  Send Text Input                            ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        print(f"{Colors.OKBLUE}ℹ️  Text: {text}{Colors.ENDC}\n")

        escaped_text = text.replace('"', '\\"').replace(' ', '%s')
        result = self.adb.shell_command(f'input text "{escaped_text}"')

        if result.success or result.return_code == 0:
            print(f"{Colors.OKGREEN}✅ Text input sent{Colors.ENDC}")
            if self.logger:
                self.logger.log_event('voice_command', f'Sent text input: {text}')
            return True, "Text input sent successfully"
        else:
            print(f"{Colors.FAIL}❌ Failed to send text input{Colors.ENDC}")
            return False, f"Failed to send text input: {result.error}"

    def trigger_google_assistant(self) -> Tuple[bool, str]:
        print(f"\n{Colors.HEADER}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}║           🤖 Triggering Google Assistant                 ║{Colors.ENDC}")
        print(f"{Colors.HEADER}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        commands_to_try = [
            'am start -a android.intent.action.VOICE_COMMAND',
            'am start -a android.intent.action.VOICE_ASSIST',
            'am start -n com.google.android.googlequicksearchbox/com.google.android.voicesearch.activity.VoiceSearchActivity']

        for cmd in commands_to_try:
            result = self.adb.shell_command(cmd)
            if result.success or result.return_code == 0:
                print(f"{Colors.OKGREEN}✅ Google Assistant triggered{Colors.ENDC}")
                if self.logger:
                    self.logger.log_event('voice_command', 'Triggered Google Assistant')
                return True, "Google Assistant triggered successfully"

        print(f"{Colors.FAIL}❌ Failed to trigger Google Assistant{Colors.ENDC}")
        return False, "Failed to trigger Google Assistant"

    def close(self):
        pass


def create_voice_commands(adb_manager: ADBManager, logger: Optional[Logger] = None) -> VoiceCommands:
    return VoiceCommands(adb_manager, logger)


def get_default_voice_commands(adb_manager: ADBManager) -> VoiceCommands:
    from utils.logger import get_default_logger
    return VoiceCommands(adb_manager, get_default_logger())
