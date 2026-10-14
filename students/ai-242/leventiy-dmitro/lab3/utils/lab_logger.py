import logging
import sys


def custom_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        for h in (logging.FileHandler(f"{name}.log", "w", encoding="utf-8"),
                  logging.StreamHandler(sys.stdout)):
            h.setFormatter(logging.Formatter("%(message)s"))
            logger.addHandler(h)
    return logger
