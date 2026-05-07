import json
import re
import os
from typing import List, Dict, Optional, Tuple
from utils.colors import Colors
from utils.ui_components import Emoji, BoxChars


class ErrorSolution:
    def __init__(self, title: str, description: str, solutions: List[str],
                 troubleshooting_guide: Optional[str] = None):
        self.title = title
        self.description = description
        self.solutions = solutions
        self.troubleshooting_guide = troubleshooting_guide


class ErrorHandler:
    def __init__(self, solutions_db_path: str = None):
        if solutions_db_path is None:
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            solutions_db_path = os.path.join(current_dir, 'data', 'error_solutions.json')

        self.solutions_db_path = solutions_db_path
        self.error_patterns = {}
        self._load_error_database()

    def _load_error_database(self):
        try:
            with open(self.solutions_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for error_key, error_data in data.items():
                    pattern = error_data.get('pattern', '')
                    self.error_patterns[error_key] = {
                        'pattern': re.compile(pattern, re.IGNORECASE),
                        'title': error_data.get('title', 'Error'),
                        'description': error_data.get('description', ''),
                        'solutions': error_data.get('solutions', []),
                        'troubleshooting_guide': error_data.get('troubleshooting_guide')
                    }
        except FileNotFoundError:
            self.error_patterns = {}
        except json.JSONDecodeError:
            self.error_patterns = {}

    def match_error(self, error_message: str) -> Optional[ErrorSolution]:
        if not error_message:
            return None

        for error_key, error_data in self.error_patterns.items():
            if error_key == 'generic_error':
                continue

            pattern = error_data['pattern']
            if pattern.search(error_message):
                return ErrorSolution(
                    title=error_data['title'],
                    description=error_data['description'],
                    solutions=error_data['solutions'],
                    troubleshooting_guide=error_data['troubleshooting_guide']
                )

        if 'generic_error' in self.error_patterns:
            generic = self.error_patterns['generic_error']
            return ErrorSolution(
                title=generic['title'],
                description=generic['description'],
                solutions=generic['solutions'],
                troubleshooting_guide=generic['troubleshooting_guide']
            )

        return None

    def get_solutions(self, error_message: str, max_solutions: int = 5) -> List[str]:
        solution = self.match_error(error_message)
        if solution:
            return solution.solutions[:max_solutions]
        return []

    def display_error_with_solutions(self, error_message: str,
                                     original_error: str = None,
                                     max_solutions: int = 5,
                                     terminal_width: int = 80):
        solution = self.match_error(error_message)

        if not solution:
            self._display_simple_error(error_message, terminal_width)
            return

        self._display_beautiful_error(
            title=solution.title,
            description=solution.description,
            error_details=original_error or error_message,
            solutions=solution.solutions[:max_solutions],
            troubleshooting_guide=solution.troubleshooting_guide,
            terminal_width=terminal_width
        )

    def _display_simple_error(self, error_message: str, terminal_width: int = 80):
        width = min(terminal_width, 80)
        inner_width = width - 4

        print(f'\n{Colors.FAIL}{BoxChars.TOP_LEFT}{BoxChars.HORIZONTAL * (width - 2)}{BoxChars.TOP_RIGHT}{Colors.ENDC}')

        error_line = f'{Emoji.CROSS} {error_message}'
        lines = self._wrap_text(error_line, inner_width)

        for i, line in enumerate(lines):
            padding = inner_width - len(line)
            if i == 0:
                print(
                    f'{
                        Colors.FAIL}{
                        BoxChars.VERTICAL}{
                        Colors.ENDC} {line}{
                        " " *
                        padding} {
                        Colors.FAIL}{
                            BoxChars.VERTICAL}{
                                Colors.ENDC}')
            else:
                print(
                    f'{
                        Colors.FAIL}{
                        BoxChars.VERTICAL}{
                        Colors.ENDC}   {line}{
                        " " *
                        (
                            padding -
                            2)} {
                            Colors.FAIL}{
                                BoxChars.VERTICAL}{
                                    Colors.ENDC}')

        print(f'{Colors.FAIL}{BoxChars.BOTTOM_LEFT}{BoxChars.HORIZONTAL * (width - 2)}{BoxChars.BOTTOM_RIGHT}{Colors.ENDC}\n')

    def _display_beautiful_error(self, title: str, description: str,
                                 error_details: str, solutions: List[str],
                                 troubleshooting_guide: Optional[str],
                                 terminal_width: int = 80):
        width = min(terminal_width, 80)
        inner_width = width - 4

        print(f'\n{Colors.FAIL}{BoxChars.TOP_LEFT}{BoxChars.HORIZONTAL * (width - 2)}{BoxChars.TOP_RIGHT}{Colors.ENDC}')

        title_line = f'{Emoji.CROSS} {title}'
        padding = (inner_width - len(title_line)) // 2
        print(
            f'{
                Colors.FAIL}{
                BoxChars.VERTICAL}{
                Colors.ENDC}{
                    " " *
                    padding}{
                        Colors.BOLD}{title_line}{
                            Colors.ENDC}{
                                " " *
                                (
                                    inner_width -
                                    len(title_line) -
                                    padding)}{
                                        Colors.FAIL}{
                                            BoxChars.VERTICAL}{
                                                Colors.ENDC}')

        if description:
            print(f'{Colors.FAIL}{BoxChars.T_RIGHT}{BoxChars.HORIZONTAL * (width - 2)}{BoxChars.T_LEFT}{Colors.ENDC}')
            desc_lines = self._wrap_text(description, inner_width)
            for line in desc_lines:
                padding = inner_width - len(line)
                print(
                    f'{
                        Colors.FAIL}{
                        BoxChars.VERTICAL}{
                        Colors.ENDC} {line}{
                        " " *
                        padding} {
                        Colors.FAIL}{
                            BoxChars.VERTICAL}{
                                Colors.ENDC}')

        if error_details:
            print(f'{Colors.FAIL}{BoxChars.T_RIGHT}{BoxChars.HORIZONTAL * (width - 2)}{BoxChars.T_LEFT}{Colors.ENDC}')
            error_label = f'{Colors.WARNING}Error Details:{Colors.ENDC}'
            padding = inner_width - len('Error Details:')
            print(
                f'{
                    Colors.FAIL}{
                    BoxChars.VERTICAL}{
                    Colors.ENDC} {error_label}{
                    " " *
                    padding} {
                        Colors.FAIL}{
                            BoxChars.VERTICAL}{
                                Colors.ENDC}')

            detail_lines = self._wrap_text(error_details, inner_width - 2)
            for line in detail_lines:
                padding = inner_width - len(line) - 2
                print(
                    f'{
                        Colors.FAIL}{
                        BoxChars.VERTICAL}{
                        Colors.ENDC}   {
                        Colors.OKBLUE}{line}{
                        Colors.ENDC}{
                            " " *
                            padding} {
                                Colors.FAIL}{
                                    BoxChars.VERTICAL}{
                                        Colors.ENDC}')

        print(f'{Colors.FAIL}{BoxChars.BOTTOM_LEFT}{BoxChars.HORIZONTAL * (width - 2)}{BoxChars.BOTTOM_RIGHT}{Colors.ENDC}')

        if solutions:
            print(f'\n{Colors.BOLD}{Colors.HEADER}{Emoji.BULB} Possible Solutions:{Colors.ENDC}\n')
            for i, solution in enumerate(solutions, 1):
                solution_lines = self._wrap_text(solution, width - 6)
                for j, line in enumerate(solution_lines):
                    if j == 0:
                        print(f'{Colors.OKGREEN}{i}. {line}{Colors.ENDC}')
                    else:
                        print(f'{Colors.OKGREEN}   {line}{Colors.ENDC}')

        if troubleshooting_guide:
            print(f'\n{Colors.OKCYAN}{Emoji.BOOK} Troubleshooting Guide: {troubleshooting_guide}{Colors.ENDC}')

        print()

    def _wrap_text(self, text: str, width: int) -> List[str]:
        if len(text) <= width:
            return [text]

        lines = []
        words = text.split()
        current_line = ''

        for word in words:
            if len(current_line) + len(word) + 1 <= width:
                current_line += word + ' '
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + ' '

        if current_line:
            lines.append(current_line.strip())

        return lines

    def handle_adb_error(self, error_output: str, command: str = None) -> Tuple[bool, str]:
        if not error_output:
            return True, ''

        error_lower = error_output.lower()

        if 'success' in error_lower and 'fail' not in error_lower:
            return True, ''

        if any(
            keyword in error_lower for keyword in [
                'error',
                'failed',
                'fail',
                'denied',
                'not found',
                'timeout',
                'refused']):
            self.display_error_with_solutions(
                error_message=error_output,
                original_error=f'Command: {command}\nOutput: {error_output}' if command else error_output
            )
            return False, error_output

        return True, ''

    def handle_exception(self, exception: Exception, context: str = None):
        error_message = str(exception)

        if context:
            full_message = f'{context}: {error_message}'
        else:
            full_message = error_message

        self.display_error_with_solutions(
            error_message=full_message,
            original_error=f'{type(exception).__name__}: {error_message}'
        )

    def get_error_info(self, error_message: str) -> Optional[Dict]:
        solution = self.match_error(error_message)
        if solution:
            return {
                'title': solution.title,
                'description': solution.description,
                'solutions': solution.solutions,
                'troubleshooting_guide': solution.troubleshooting_guide
            }
        return None


_global_error_handler = None


def get_error_handler() -> ErrorHandler:
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def display_error(error_message: str, original_error: str = None, max_solutions: int = 5):
    handler = get_error_handler()
    handler.display_error_with_solutions(error_message, original_error, max_solutions)


def handle_adb_error(error_output: str, command: str = None) -> Tuple[bool, str]:
    handler = get_error_handler()
    return handler.handle_adb_error(error_output, command)


def handle_exception(exception: Exception, context: str = None):
    handler = get_error_handler()
    handler.handle_exception(exception, context)
