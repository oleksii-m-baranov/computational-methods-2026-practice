"""Налаштування журналювання роботи агента."""

import logging


def custom_logger(name: str) -> logging.Logger:
    """Створює логер для запису роботи агента у файл і термінал."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        file_handler = logging.FileHandler(
            "lab2.log", mode="w", encoding="utf-8"
        )
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger