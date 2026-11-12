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
    logger.setLevel(logging.DEBUG)  # Can be changed to logging.INFO if needed

    # Clear handlers if a logger with this name was already created
    # (prevents duplicate log lines upon accidental multiple calls)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Common output format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # 2. Console handler (sys.stdout - the same stream as standard print)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 3. File handler
    file_mode = 'w' if overwrite else 'a'
    file_handler = logging.FileHandler(log_file_path, mode=file_mode, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# === Usage Example ===
if __name__ == "__main__":
    # Logger appending to the file (default)
    logger1 = custom_logger('lab1')
    logger1.info("This message will appear in the console and be appended to lab1.log")

    # Logger clearing the file on start
    logger2 = custom_logger('lab2', True)
    logger2.warning("File lab2.log was cleared before writing this line")