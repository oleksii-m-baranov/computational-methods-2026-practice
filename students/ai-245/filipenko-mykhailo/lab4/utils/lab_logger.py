import logging
from pathlib import Path


def custom_logger(name, overwrite=False):
    path = Path(name)

    if path.suffix.lower() != ".log":
        path = path.with_suffix(".log")

    path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(str(path.resolve()))
    logger.setLevel(logging.INFO)
    logger.propagate = False

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    formatter = logging.Formatter("%(message)s")

    file_handler = logging.FileHandler(
        path,
        mode="w" if overwrite else "a",
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
