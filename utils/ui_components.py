import sys
import time
import threading


class BoxChars:
    TOP_LEFT = '╔'
    TOP_RIGHT = '╗'
    BOTTOM_LEFT = '╚'
    BOTTOM_RIGHT = '╝'
    HORIZONTAL = '═'
    VERTICAL = '║'
    T_DOWN = '╦'
    T_UP = '╩'
    T_RIGHT = '╠'
    T_LEFT = '╣'
    CROSS = '╬'

    LIGHT_TOP_LEFT = '┌'
    LIGHT_TOP_RIGHT = '┐'
    LIGHT_BOTTOM_LEFT = '└'
    LIGHT_BOTTOM_RIGHT = '┘'
    LIGHT_HORIZONTAL = '─'
    LIGHT_VERTICAL = '│'
    LIGHT_T_DOWN = '┬'
    LIGHT_T_UP = '┴'
    LIGHT_T_RIGHT = '├'
    LIGHT_T_LEFT = '┤'
    LIGHT_CROSS = '┼'


class Emoji:
    ROCKET = '🚀'
    PHONE = '📱'
    CHECK = '✅'
    CROSS = '❌'
    WARNING = '⚠️'
    INFO = 'ℹ️'
    FOLDER = '📁'
    PACKAGE = '📦'
    GEAR = '⚙️'
    DISPLAY = '🖥️'
    CAMERA = '📷'
    VIDEO = '🎥'
    DOWNLOAD = '⬇️'
    UPLOAD = '⬆️'
    TRASH = '🗑️'
    WRENCH = '🔧'
    SHIELD = '🛡️'
    SEARCH = '🔍'
    STAR = '⭐'
    FIRE = '🔥'
    LIGHTNING = '⚡'
    HOURGLASS = '⏳'
    CLOCK = '🕐'
    SAVE = '💾'
    LINK = '🔗'
    KEY = '🔑'
    LOCK = '🔒'
    UNLOCK = '🔓'
    BELL = '🔔'
    CHART = '📊'
    CLIPBOARD = '📋'
    PENCIL = '✏️'
    BOOK = '📖'
    BULB = '💡'
    HEART = '❤️'
    THUMBS_UP = '👍'
    THUMBS_DOWN = '👎'
    STOP = '🛑'
    RECORD = '⏺️'
    CLEAN = '🧹'
    SUCCESS = '🎉'


class ProgressBar:
    FILLED = '█'
    EMPTY = '░'

    def __init__(self, total=100, width=50):
        self.total = total
        self.width = width
        self.current = 0

    def update(self, current):
        self.current = current

    def display(self):
        if self.total == 0:
            percent = 100
        else:
            percent = int((self.current / self.total) * 100)

        filled_width = int((self.width * self.current) / self.total) if self.total > 0 else self.width
        bar = ProgressBar.FILLED * filled_width + ProgressBar.EMPTY * (self.width - filled_width)

        sys.stdout.write(f'[{bar}] {percent}%')

    @staticmethod
    def render(current, total, width=50, prefix='', suffix=''):
        if total == 0:
            percent = 100
        else:
            percent = int((current / total) * 100)

        filled_width = int((width * current) / total) if total > 0 else width
        bar = ProgressBar.FILLED * filled_width + ProgressBar.EMPTY * (width - filled_width)

        return f'{prefix} [{bar}] {percent}% {suffix}'

    @staticmethod
    def render_with_stats(current, total, width=40):
        percent = int((current / total) * 100) if total > 0 else 100
        filled_width = int((width * current) / total) if total > 0 else width
        bar = ProgressBar.FILLED * filled_width + ProgressBar.EMPTY * (width - filled_width)

        return f'[{bar}] {current}/{total} ({percent}%)'


class LoadingAnimation:
    def __init__(self, message='Loading'):
        self.message = message
        self.running = False
        self.thread = None
        self.frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.current_frame = 0

    def _animate(self):
        while self.running:
            frame = self.frames[self.current_frame % len(self.frames)]
            sys.stdout.write(f'\r{frame} {self.message}...')
            sys.stdout.flush()
            self.current_frame += 1
            time.sleep(0.1)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        sys.stdout.flush()


class Table:
    @staticmethod
    def render(headers, rows, column_widths=None):
        if not rows:
            return ''

        if column_widths is None:
            column_widths = []
            for i, header in enumerate(headers):
                max_width = len(str(header))
                for row in rows:
                    if i < len(row):
                        max_width = max(max_width, len(str(row[i])))
                column_widths.append(max_width)

        lines = []

        header_line = BoxChars.LIGHT_VERTICAL + ' '
        for i, header in enumerate(headers):
            header_line += str(header).ljust(column_widths[i]) + ' ' + BoxChars.LIGHT_VERTICAL + ' '
        lines.append(header_line.rstrip())

        separator = BoxChars.LIGHT_T_RIGHT
        for width in column_widths:
            separator += BoxChars.LIGHT_HORIZONTAL * (width + 2) + BoxChars.LIGHT_CROSS
        separator = separator[:-1] + BoxChars.LIGHT_T_LEFT
        lines.append(separator)

        for row in rows:
            row_line = BoxChars.LIGHT_VERTICAL + ' '
            for i, cell in enumerate(row):
                if i < len(column_widths):
                    row_line += str(cell).ljust(column_widths[i]) + ' ' + BoxChars.LIGHT_VERTICAL + ' '
            lines.append(row_line.rstrip())

        top_border = BoxChars.LIGHT_TOP_LEFT
        for width in column_widths:
            top_border += BoxChars.LIGHT_HORIZONTAL * (width + 2) + BoxChars.LIGHT_T_DOWN
        top_border = top_border[:-1] + BoxChars.LIGHT_TOP_RIGHT

        bottom_border = BoxChars.LIGHT_BOTTOM_LEFT
        for width in column_widths:
            bottom_border += BoxChars.LIGHT_HORIZONTAL * (width + 2) + BoxChars.LIGHT_T_UP
        bottom_border = bottom_border[:-1] + BoxChars.LIGHT_BOTTOM_RIGHT

        return '\n'.join([top_border] + lines + [bottom_border])

    @staticmethod
    def render_simple(headers, rows):
        if not rows:
            return ''

        column_widths = []
        for i, header in enumerate(headers):
            max_width = len(str(header))
            for row in rows:
                if i < len(row):
                    max_width = max(max_width, len(str(row[i])))
            column_widths.append(max_width)

        lines = []

        header_line = ''
        for i, header in enumerate(headers):
            header_line += str(header).ljust(column_widths[i]) + '  '
        lines.append(header_line.rstrip())

        separator = ''
        for width in column_widths:
            separator += BoxChars.LIGHT_HORIZONTAL * width + '  '
        lines.append(separator.rstrip())

        for row in rows:
            row_line = ''
            for i, cell in enumerate(row):
                if i < len(column_widths):
                    row_line += str(cell).ljust(column_widths[i]) + '  '
            lines.append(row_line.rstrip())

        return '\n'.join(lines)


def create_table(headers, rows, title=''):
    from utils.colors import Colors

    if not rows:
        return f"{Colors.WARNING}No data to display{Colors.ENDC}"

    column_widths = []
    for i, header in enumerate(headers):
        max_width = len(str(header))
        for row in rows:
            if i < len(row):
                max_width = max(max_width, len(str(row[i])))
        column_widths.append(min(max_width, 50))

    total_width = sum(column_widths) + len(headers) * 3 + 1

    lines = []

    if title:
        lines.append(
            f"{Colors.HEADER}{BoxChars.TOP_LEFT}{BoxChars.HORIZONTAL * (total_width - 2)}{BoxChars.TOP_RIGHT}{Colors.ENDC}")
        title_padding = (total_width - len(title) - 4) // 2
        lines.append(f"{Colors.HEADER}{BoxChars.VERTICAL}{' ' *
                                                          title_padding}{title}{' ' *
                                                                                (total_width -
                                                                                 len(title) -
                                                                                    title_padding -
                                                                                    2)}{BoxChars.VERTICAL}{Colors.ENDC}")
        lines.append(
            f"{Colors.HEADER}{BoxChars.T_RIGHT}{BoxChars.HORIZONTAL * (total_width - 2)}{BoxChars.T_LEFT}{Colors.ENDC}")
    else:
        lines.append(
            f"{Colors.HEADER}{BoxChars.TOP_LEFT}{BoxChars.HORIZONTAL * (total_width - 2)}{BoxChars.TOP_RIGHT}{Colors.ENDC}")

    header_line = f"{Colors.HEADER}{BoxChars.VERTICAL}{Colors.ENDC} "
    for i, header in enumerate(headers):
        header_line += f"{
            Colors.BOLD}{
            str(header).ljust(
                column_widths[i])}{
                Colors.ENDC} {
                    Colors.HEADER}{
                        BoxChars.VERTICAL}{
                            Colors.ENDC} "
    lines.append(header_line.rstrip())

    separator = f"{Colors.HEADER}{BoxChars.T_RIGHT}"
    for width in column_widths:
        separator += BoxChars.HORIZONTAL * (width + 2) + BoxChars.CROSS
    separator = separator[:-1] + BoxChars.T_LEFT + Colors.ENDC
    lines.append(separator)

    for row in rows:
        row_line = f"{Colors.HEADER}{BoxChars.VERTICAL}{Colors.ENDC} "
        for i, cell in enumerate(row):
            if i < len(column_widths):
                cell_str = str(cell)[:column_widths[i]]
                row_line += cell_str.ljust(column_widths[i]) + f" {Colors.HEADER}{BoxChars.VERTICAL}{Colors.ENDC} "
        lines.append(row_line.rstrip())

    bottom_border = f"{Colors.HEADER}{BoxChars.BOTTOM_LEFT}{BoxChars.HORIZONTAL *
                                                            (total_width -
                                                             2)}{BoxChars.BOTTOM_RIGHT}{Colors.ENDC}"
    lines.append(bottom_border)

    return '\n'.join(lines)


def create_progress_bar(current, total, width=50, prefix='Progress'):
    from utils.colors import Colors

    if total == 0:
        percent = 100
    else:
        percent = int((current / total) * 100)

    filled_width = int((width * current) / total) if total > 0 else width
    bar = ProgressBar.FILLED * filled_width + ProgressBar.EMPTY * (width - filled_width)

    if percent == 100:
        color = Colors.OKGREEN
    elif percent >= 50:
        color = Colors.OKCYAN
    else:
        color = Colors.WARNING

    return f'{prefix}: {color}[{bar}] {percent}%{Colors.ENDC}'
