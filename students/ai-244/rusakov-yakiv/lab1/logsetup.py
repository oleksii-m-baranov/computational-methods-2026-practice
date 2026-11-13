"""Журнал виконання: усе, що скрипти друкують, потрапляє і в консоль, і в lab1.log.

Скрипти підключають його рядком `from logsetup import print`. Файл lab1.log
створюється поруч зі скриптами й дописується (append) при кожному запуску.
"""
import builtins

from utils.lab_logger import custom_logger

_logger = custom_logger("lab1")


def print(*args, sep=" ", end="\n", **_):  # noqa: A001 (свідомо підміняє builtin)
    text = sep.join(str(a) for a in args)
    _logger.info(text)
