class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    DIM = '\033[2m'
    ITALIC = '\033[3m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    STRIKETHROUGH = '\033[9m'

    @staticmethod
    def disable():
        Colors.HEADER = ''
        Colors.OKBLUE = ''
        Colors.OKCYAN = ''
        Colors.OKGREEN = ''
        Colors.WARNING = ''
        Colors.FAIL = ''
        Colors.ENDC = ''
        Colors.BOLD = ''
        Colors.UNDERLINE = ''
        Colors.BLACK = ''
        Colors.RED = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.BLUE = ''
        Colors.MAGENTA = ''
        Colors.CYAN = ''
        Colors.WHITE = ''
        Colors.BRIGHT_BLACK = ''
        Colors.BRIGHT_RED = ''
        Colors.BRIGHT_GREEN = ''
        Colors.BRIGHT_YELLOW = ''
        Colors.BRIGHT_BLUE = ''
        Colors.BRIGHT_MAGENTA = ''
        Colors.BRIGHT_CYAN = ''
        Colors.BRIGHT_WHITE = ''
        Colors.BG_BLACK = ''
        Colors.BG_RED = ''
        Colors.BG_GREEN = ''
        Colors.BG_YELLOW = ''
        Colors.BG_BLUE = ''
        Colors.BG_MAGENTA = ''
        Colors.BG_CYAN = ''
        Colors.BG_WHITE = ''
        Colors.DIM = ''
        Colors.ITALIC = ''
        Colors.BLINK = ''
        Colors.REVERSE = ''
        Colors.HIDDEN = ''
        Colors.STRIKETHROUGH = ''

    @staticmethod
    def colorize(text: str, color: str) -> str:
        return f'{color}{text}{Colors.ENDC}'

    @staticmethod
    def success(text: str) -> str:
        return f'{Colors.OKGREEN}{text}{Colors.ENDC}'

    @staticmethod
    def error(text: str) -> str:
        return f'{Colors.FAIL}{text}{Colors.ENDC}'

    @staticmethod
    def warning(text: str) -> str:
        return f'{Colors.WARNING}{text}{Colors.ENDC}'

    @staticmethod
    def info(text: str) -> str:
        return f'{Colors.OKBLUE}{text}{Colors.ENDC}'

    @staticmethod
    def header(text: str) -> str:
        return f'{Colors.HEADER}{text}{Colors.ENDC}'

    @staticmethod
    def bold(text: str) -> str:
        return f'{Colors.BOLD}{text}{Colors.ENDC}'

    @staticmethod
    def underline(text: str) -> str:
        return f'{Colors.UNDERLINE}{text}{Colors.ENDC}'
