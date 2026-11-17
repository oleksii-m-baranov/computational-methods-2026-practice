import logging
import sys
import os
import inspect


def custom_logger(name: str, overwrite: bool = False) -> logging.Logger:
    """
    Creates and configures a logger that outputs to the console (stdout) and a file.

    :param name: Name of the logger (will also be used as the filename, e.g., 'lab1' -> 'lab1.log').
    :param overwrite: If True, the log file will be overwritten on start. Defaults to False (append mode).
    :return: Configured logging.Logger instance.
    """
    # 1. Determine the path to the file from which this function was called
    caller_frame = inspect.stack()[1]
    caller_filename = caller_frame.filename
    caller_dir = os.path.dirname(os.path.abspath(caller_filename))

    # Construct the full path to the log file
    log_file_path = os.path.join(caller_dir, f"{name}.log")

    # Create the logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Clear handlers if a logger with this name was already created
    if logger.hasHandlers():
        logger.handlers.clear()

    # Common output format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # 2. Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 3. File handler
    file_mode = 'w' if overwrite else 'a'
    file_handler = logging.FileHandler(log_file_path, mode=file_mode, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
