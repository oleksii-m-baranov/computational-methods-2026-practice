import logging
import sys


def custom_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:                 # не дублювати обробники
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(message)s")
    fh = logging.FileHandler(f"{name}.log", mode="a", encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger
