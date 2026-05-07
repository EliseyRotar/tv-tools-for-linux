import os
import sys
from typing import List
from utils.colors import Colors
from utils.ui_components import BoxChars, Emoji, ProgressBar, LoadingAnimation, Table


class UIManager:
    def __init__(self, color_enabled=True):
        self.color_enabled = color_enabled
        if not color_enabled:
            Colors.disable()
        self.terminal_width = self._get_terminal_width()

    def _get_terminal_width(self):
        try:
            return os.get_terminal_size().columns
        except Exception:
            return 80

    def clear_screen(self):
        os.system('clear' if os.name != 'nt' else 'cls')

    def print_header(self, title='TV Tools for Linux v1.0',
                     author='@eli6',
                     github='https://github.com/EliseyRotar',
                     device_info=None):
        width = min(self.terminal_width, 80)
        inner_width = width - 2

        print(f'{Colors.OKCYAN}{BoxChars.TOP_LEFT}{BoxChars.HORIZONTAL * inner_width}{BoxChars.TOP_RIGHT}{Colors.ENDC}')

        title_line = f'{Emoji.ROCKET} {title}'
        padding = (inner_width - len(title_line)) // 2
        print(
            f'{
                Colors.OKCYAN}{
                BoxChars.VERTICAL}{
                Colors.ENDC}{
                    " " *
                    padding}{
                        Colors.BOLD}{
                            Colors.HEADER}{title_line}{
                                Colors.ENDC}{
                                    " " *
                                    (
                                        inner_width -
                                        len(title_line) -
                                        padding)}{
                                            Colors.OKCYAN}{
                                                BoxChars.VERTICAL}{
                                                    Colors.ENDC}')

        author_line = f'Author: {author} | {github}'
        padding = (inner_width - len(author_line)) // 2
        print(
            f'{
                Colors.OKCYAN}{
                BoxChars.VERTICAL}{
                Colors.ENDC}{
                    " " *
                    padding}{author_line}{
                        " " *
                        (
                            inner_width -
                            len(author_line) -
                            padding)}{
                                Colors.OKCYAN}{
                                    BoxChars.VERTICAL}{
                                        Colors.ENDC}')

        if device_info:
            print(f'{Colors.OKCYAN}{BoxChars.T_RIGHT}{BoxChars.HORIZONTAL * inner_width}{BoxChars.T_LEFT}{Colors.ENDC}')
            device_line = f'{Emoji.PHONE} Connected: {device_info}'
            padding_left = 2
            print(
                f'{
                    Colors.OKCYAN}{
                    BoxChars.VERTICAL}{
                    Colors.ENDC}{
                    " " *
                    padding_left}{
                        Colors.OKGREEN}{device_line}{
                            Colors.ENDC}{
                                " " *
                                (
                                    inner_width -
                                    len(device_line) -
                                    padding_left)}{
                                        Colors.OKCYAN}{
                                            BoxChars.VERTICAL}{
                                                Colors.ENDC}')

        print(f'{Colors.OKCYAN}{BoxChars.T_RIGHT}{BoxChars.HORIZONTAL * inner_width}{BoxChars.T_LEFT}{Colors.ENDC}')

    def print_menu(self, options: List[str], title='', show_numbers=True):
        width = min(self.terminal_width, 80)
        inner_width = width - 2

        if title:
            title_line = f' {title} '
            padding = (inner_width - len(title_line)) // 2
            print(
                f'{
                    Colors.OKCYAN}{
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
                                        Colors.OKCYAN}{
                                            BoxChars.VERTICAL}{
                                                Colors.ENDC}')
            print(f'{Colors.OKCYAN}{BoxChars.T_RIGHT}{BoxChars.HORIZONTAL * inner_width}{BoxChars.T_LEFT}{Colors.ENDC}')

        for i, option in enumerate(options):
            if show_numbers:
                if i < len(options) - 1:
                    option_line = f'  {i + 1:2}  {option}'
                else:
                    option_line = f'  0  {option}'
            else:
                option_line = f'  {option}'

            print(
                f'{
                    Colors.OKCYAN}{
                    BoxChars.VERTICAL}{
                    Colors.ENDC}{option_line}{
                    " " *
                    (
                        inner_width -
                        len(option_line))}{
                            Colors.OKCYAN}{
                                BoxChars.VERTICAL}{
                                    Colors.ENDC}')

        print(
            f'{
                Colors.OKCYAN}{
                BoxChars.BOTTOM_LEFT}{
                BoxChars.HORIZONTAL *
                inner_width}{
                    BoxChars.BOTTOM_RIGHT}{
                        Colors.ENDC}')

    def get_input(self, prompt='Enter your choice', default='', validator=None):
        if default:
            prompt_text = f'{Colors.OKBLUE}{Emoji.INFO} {prompt} [{default}]: {Colors.ENDC}'
        else:
            prompt_text = f'{Colors.OKBLUE}{Emoji.INFO} {prompt}: {Colors.ENDC}'

        while True:
            try:
                user_input = input(prompt_text).strip()
                if not user_input and default:
                    user_input = default

                if validator:
                    is_valid, error_message = validator(user_input)
                    if not is_valid:
                        self.print_error(error_message)
                        continue

                return user_input
            except KeyboardInterrupt:
                print()
                raise
            except EOFError:
                print()
                return default if default else ''

    def confirm(self, message='Are you sure?', default=False):
        default_str = 'Y/n' if default else 'y/N'
        prompt = f'{Colors.WARNING}{Emoji.WARNING} {message} [{default_str}]: {Colors.ENDC}'

        try:
            response = input(prompt).strip().lower()
            if not response:
                return default
            return response in ['y', 'yes']
        except KeyboardInterrupt:
            print()
            return False
        except EOFError:
            print()
            return default

    def print_success(self, message):
        print(f'{Colors.OKGREEN}{Emoji.CHECK} {message}{Colors.ENDC}')

    def print_error(self, message):
        print(f'{Colors.FAIL}{Emoji.CROSS} {message}{Colors.ENDC}')

    def print_warning(self, message):
        print(f'{Colors.WARNING}{Emoji.WARNING} {message}{Colors.ENDC}')

    def print_info(self, message):
        print(f'{Colors.OKBLUE}{Emoji.INFO} {message}{Colors.ENDC}')

    def show_progress(self, current, total, prefix='Progress', suffix=''):
        bar = ProgressBar.render(current, total, width=40, prefix=prefix, suffix=suffix)
        sys.stdout.write(f'\r{bar}')
        sys.stdout.flush()
        if current >= total:
            print()

    def show_progress_with_stats(self, current, total, message=''):
        bar = ProgressBar.render_with_stats(current, total, width=40)
        if message:
            output = f'{message}: {bar}'
        else:
            output = bar
        sys.stdout.write(f'\r{output}')
        sys.stdout.flush()
        if current >= total:
            print()

    def wait_for_key(self, message='Press Enter to continue...'):
        try:
            input(f'\n{Colors.OKCYAN}{message}{Colors.ENDC}')
        except KeyboardInterrupt:
            print()
        except EOFError:
            print()

    def print_table(self, headers, rows, title=''):
        if title:
            print(f'\n{Colors.BOLD}{Colors.HEADER}{title}{Colors.ENDC}\n')

        table = Table.render(headers, rows)
        print(table)

    def print_simple_table(self, headers, rows, title=''):
        if title:
            print(f'\n{Colors.BOLD}{Colors.HEADER}{title}{Colors.ENDC}\n')

        table = Table.render_simple(headers, rows)
        print(table)

    def create_loading_animation(self, message='Loading'):
        return LoadingAnimation(message)

    def print_separator(self, char=None):
        if char is None:
            char = BoxChars.HORIZONTAL
        width = min(self.terminal_width, 80)
        print(f'{Colors.OKCYAN}{char * width}{Colors.ENDC}')

    def print_box(self, message, box_type='info'):
        width = min(self.terminal_width, 80)
        inner_width = width - 4

        lines = []
        words = message.split()
        current_line = ''

        for word in words:
            if len(current_line) + len(word) + 1 <= inner_width:
                current_line += word + ' '
            else:
                lines.append(current_line.strip())
                current_line = word + ' '
        if current_line:
            lines.append(current_line.strip())

        if box_type == 'error':
            color = Colors.FAIL
            icon = Emoji.CROSS
        elif box_type == 'warning':
            color = Colors.WARNING
            icon = Emoji.WARNING
        elif box_type == 'success':
            color = Colors.OKGREEN
            icon = Emoji.CHECK
        else:
            color = Colors.OKBLUE
            icon = Emoji.INFO

        print(f'{color}{BoxChars.TOP_LEFT}{BoxChars.HORIZONTAL * (width - 2)}{BoxChars.TOP_RIGHT}{Colors.ENDC}')

        for i, line in enumerate(lines):
            if i == 0:
                display_line = f'{icon} {line}'
            else:
                display_line = f'  {line}'
            padding = width - len(display_line) - 4
            print(
                f'{color}{
                    BoxChars.VERTICAL}{
                    Colors.ENDC} {display_line}{
                    " " *
                    padding} {color}{
                    BoxChars.VERTICAL}{
                        Colors.ENDC}')

        print(f'{color}{BoxChars.BOTTOM_LEFT}{BoxChars.HORIZONTAL * (width - 2)}{BoxChars.BOTTOM_RIGHT}{Colors.ENDC}')

    def print_error_with_solutions(self, error_message, solutions):
        self.print_box(error_message, box_type='error')

        if solutions:
            print(f'\n{Colors.BOLD}{Colors.HEADER}Possible Solutions:{Colors.ENDC}\n')
            for i, solution in enumerate(solutions, 1):
                print(f'{Colors.OKBLUE}{i}. {solution}{Colors.ENDC}')
            print()

    def display_menu_with_breadcrumb(self, breadcrumb, options, title=''):
        self.clear_screen()
        self.print_header()

        if breadcrumb:
            print(f'{Colors.OKCYAN}{Emoji.LINK} {breadcrumb}{Colors.ENDC}\n')

        self.print_menu(options, title=title)
