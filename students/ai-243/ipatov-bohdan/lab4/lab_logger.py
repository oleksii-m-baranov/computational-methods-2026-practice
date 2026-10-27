import logging
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def custom_logger(name, overwrite=False):
    logger = logging.getLogger(name)
    if overwrite and logger.handlers:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')

        mode = 'w' if overwrite else 'a'
        if name in ["lab4", "lab3", "lab2"]:
            filename = f"{name}.log"
        elif "/" in name or "\\" in name:
            filename = f"{name}.log"
        else:
            os.makedirs("logs", exist_ok=True)
            filename = os.path.join("logs", f"{name}.log")

        fh = logging.FileHandler(filename, mode=mode, encoding='utf-8')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger
