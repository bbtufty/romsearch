import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import colorlog
from pathvalidate import sanitize_filename


def setup_logger(log_level,
                 script_name,
                 log_dir,
                 additional_dir="",
                 max_logs=9,
                 ):
    """
    Set up the logger.

    Parameters:
        log_level (str): The log level to use
        script_name (str): The name of the script
        log_dir (str): The directory to save logs to
        additional_dir (str): Any additional directories to keep log files tidy
        max_logs (int): Maximum number of log files to keep

    Returns:
        A logger object for logging messages.
    """

    # Sanitize the directories if we need to
    additional_dir = [sanitize_filename(f) for f in additional_dir.split(os.path.sep)]

    if os.environ.get('DOCKER_ENV'):
        log_dir = os.path.join(log_dir, script_name, *additional_dir)
    else:
        log_dir = os.path.join(log_dir, script_name, *additional_dir)

    if log_level not in ['debug', 'info', 'critical']:
        log_level = 'info'
        print(f"Invalid log level '{log_level}', defaulting to 'info'")

    # Create the log directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Define the log file path, and sanitize if needs be
    log_file = os.path.join(log_dir, f"{script_name}.log")

    # Check if log file already exists
    if os.path.isfile(log_file):
        for i in range(max_logs - 1, 0, -1):
            old_log = f"{log_dir}/{script_name}.log.{i}"
            new_log = f"{log_dir}/{script_name}.log.{i + 1}"
            if os.path.exists(old_log):
                if os.path.exists(new_log):
                    os.remove(new_log)
                os.rename(old_log, new_log)
        os.rename(log_file, os.path.join(log_dir, f"{script_name}.log.1"))

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

    # Define the log message format for the log files
    logfile_formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%y %I:%M %p')

    # Create a RotatingFileHandler for log files
    handler = RotatingFileHandler(log_file, delay=True, mode="w", backupCount=max_logs)
    handler.setFormatter(logfile_formatter)

    # Add the file handler to the logger
    logger.addHandler(handler)

    # Configure console logging with the specified log level
    console_handler = colorlog.StreamHandler(sys.stdout)
    if log_level == 'DEBUG':
        console_handler.setLevel(logging.DEBUG)
    elif log_level == 'INFO':
        console_handler.setLevel(logging.INFO)
    elif log_level == 'CRITICAL':
        console_handler.setLevel(logging.CRITICAL)

    # Add the console handler to the logger
    console_handler.setFormatter(colorlog.ColoredFormatter("%(log_color)s%(levelname)s: %(message)s"))
    logger.addHandler(console_handler)

    # Overwrite previous logger if exists
    logging.getLogger(script_name).handlers.clear()
    logging.getLogger(script_name).addHandler(handler)
    logging.getLogger(script_name).addHandler(console_handler)

    return logger
