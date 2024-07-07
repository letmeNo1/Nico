import logging


class CustomFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.is_debug_enabled = False

    def filter(self, record):
        # If debug logging is turned off and the current logging level is DEBUG, do not print logging
        if not self.is_debug_enabled and record.levelno == logging.DEBUG:
            return False
        return True

    def enable_debug(self):
        # close debug log
        self.is_debug_enabled = True

    def disable_debug(self):
        # close debug log
        self.is_debug_enabled = False


logger = logging.getLogger('Nico')
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s Nico - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

custom_filter = CustomFilter()

console_handler.addFilter(custom_filter)

logger.addHandler(console_handler)

custom_filter.disable_debug()