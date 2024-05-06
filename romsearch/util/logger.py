import logging
import math
import os
from logging.handlers import RotatingFileHandler
from pathvalidate import sanitize_filename

from .. import __version__


def setup_logger(log_level,
                 script_name,
                 additional_dir="",
                 max_logs=9,
                 ):
    """
    Set up the logger.

    Parameters:
        log_level (str): The log level to use
        script_name (str): The name of the script
        additional_dir (str): Any additional directories to keep log files tidy
        max_logs (int): Maximum number of log files to keep

    Returns:
        A logger object for logging messages.
    """

    # Sanitize the directories if we need to
    additional_dir = [sanitize_filename(f) for f in additional_dir.split(os.path.sep)]

    if os.environ.get('DOCKER_ENV'):
        config_dir = os.getenv('CONFIG_DIR', '/config')
        log_dir = os.path.join(config_dir, "logs", script_name, *additional_dir)
    else:
        log_dir = os.path.join(os.getcwd(), "logs", script_name, *additional_dir)

    if log_level not in ['debug', 'info', 'critical']:
        log_level = 'info'
        print(f"Invalid log level '{log_level}', defaulting to 'info'")

    # Create the log directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Define the log file path, and sanitize if needs be
    log_file = f"{log_dir}/{script_name}.log"

    # Check if log file already exists
    if os.path.isfile(log_file):
        for i in range(max_logs - 1, 0, -1):
            old_log = f"{log_dir}/{script_name}.log.{i}"
            new_log = f"{log_dir}/{script_name}.log.{i + 1}"
            if os.path.exists(old_log):
                if os.path.exists(new_log):
                    os.remove(new_log)
                os.rename(old_log, new_log)
        os.rename(log_file, f"{log_dir}/{script_name}.log.1")

    # Create a logger object with the script name
    logger = logging.getLogger(script_name)
    logger.propagate = False

    # Set the log level based on the provided parameter
    log_level = log_level.upper()
    if log_level == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    elif log_level == 'INFO':
        logger.setLevel(logging.INFO)
    elif log_level == 'CRITICAL':
        logger.setLevel(logging.CRITICAL)
    else:
        logger.critical(f"Invalid log level '{log_level}', defaulting to 'INFO'")
        logger.setLevel(logging.INFO)

    # Define the log message format
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%y %I:%M %p')

    # Create a RotatingFileHandler for log files
    handler = RotatingFileHandler(log_file, delay=True, mode="w", backupCount=max_logs)
    handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(handler)

    # Configure console logging with the specified log level
    console_handler = logging.StreamHandler()
    if log_level == 'DEBUG':
        console_handler.setLevel(logging.DEBUG)
    elif log_level == 'INFO':
        console_handler.setLevel(logging.INFO)
    elif log_level == 'CRITICAL':
        console_handler.setLevel(logging.CRITICAL)

    # Add the console handler to the logger
    logger.addHandler(console_handler)

    # Overwrite previous logger if exists
    logging.getLogger(script_name).handlers.clear()
    logging.getLogger(script_name).addHandler(handler)
    logging.getLogger(script_name).addHandler(console_handler)

    # Insert version number at the head of every log file
    name = script_name.replace("_", " ").upper()
    logger.info(create_bar(f"{name} Version: {__version__}"))

    return logger


def create_bar(middle_text):
    """
    Creates a separation bar with provided text in the center

    Args:
        middle_text (str): The text to place in the center of the separation bar

    Returns:
        str: The formatted separation bar
    """
    total_length = 80
    if len(middle_text) == 1:
        remaining_length = total_length - len(middle_text) - 2
        left_side_length = 0
        right_side_length = remaining_length
        return f"\n{middle_text * left_side_length}{middle_text}{middle_text * right_side_length}\n"
    else:
        remaining_length = total_length - len(middle_text) - 4
        left_side_length = math.floor(remaining_length / 2)
        right_side_length = remaining_length - left_side_length
        return f"\n{'*' * left_side_length} {middle_text} {'*' * right_side_length}\n"
