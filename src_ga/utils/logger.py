'''Functions to handle logs'''
import datetime
import logging
import os

ANSI_RESET = "\033[0m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_RED = "\033[91m"
ANSI_GRAY = "\033[90m"


def load_logger(name):
    '''
    This function creates and returns a custom logger object.

    Args:
      param_name: the name of the logger. It is used to identify the logger.

    Returns:
      A logger object that has been configured with a console handler and a specific
    log level and formatter.
    '''
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = ColoredFormatter(
        "[%(colored_levelname)s] %(colored_timestamp)s - %(colored_name)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    log_folder = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
    os.makedirs(log_folder, exist_ok=True)

    log_file = os.path.join(log_folder, 'app.log')

    file_formatter = logging.Formatter(
        "[%(levelname)s] %(timestamp)s - %(name)s - %(message)s")

    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setFormatter(file_formatter)

    logger.addHandler(file_handler)

    return logger


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        '''
        This function formats log records with colored level names.

        Args:
          param record: the log record that is being formatted. It contains information about the
        log message such as the log level, message, timestamp, and logger name

        Returns:
          The formatted log record with added color codes for the levelname, logger name, and
        timestamp.
        '''
        if record.levelno == logging.ERROR:
            record.colored_levelname = f"{ANSI_RED}{record.levelname}{ANSI_RESET}"
        elif record.levelno == logging.WARNING:
            record.colored_levelname = f"{ANSI_YELLOW}{record.levelname}{ANSI_RESET}"
        elif record.levelno == logging.INFO:
            record.colored_levelname = f"{ANSI_GREEN}{record.levelname}{ANSI_RESET}"

        record.colored_name = f"{ANSI_GRAY}{record.name}{ANSI_RESET}"
        timestamp = datetime.datetime.now()
        record.colored_timestamp = f"{ANSI_GRAY}{timestamp}{ANSI_RESET}"

        record.levelname = record.levelname
        record.name = record.name
        record.timestamp = timestamp

        return super().format(record)


logger = load_logger(__name__)
