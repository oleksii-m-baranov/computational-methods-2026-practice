
"""Стиснення контексту агента для лабораторної №4."""

import config
from context import trim_messages


def compress_messages(messages, prompt_tokens):
    """
    Скорочує історію повідомлень залежно від режиму.

    none — без стиснення;
    trim — видалення старих груп повідомлень.
    """

    mode = config.COMPRESS

    if mode == "none":
        return messages

    if prompt_tokens < config.COMPRESS_AT:
        return messages

    if mode == "trim":
        return trim_messages(
            messages,
            keep_last=config.KEEP_LAST,
        )

    raise ValueError(
        f"Невідомий режим стиснення: {mode}"
    )
