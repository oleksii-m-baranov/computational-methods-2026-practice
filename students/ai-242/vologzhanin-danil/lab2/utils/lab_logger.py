"""Логгер: пише і в консоль, і у файл <name>.log (поточний каталог)."""
import logging
import sys


def custom_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:            # не дублюємо обробники при повторному виклику
        return logger
    logger.setLevel(logging.INFO)
    logger.propagate = False
    fmt = logging.Formatter("%(message)s")

    fh = logging.FileHandler(f"{name}.log", mode="a", encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    return logger
