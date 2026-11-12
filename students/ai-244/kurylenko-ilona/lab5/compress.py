"""Скорочення історії та відновлення стану задачі."""

import config
from context import trim
from summary import compress_by_summary


def attach_state(messages, task, state):
    """Додає збережені результати інструментів до запитання."""
    note = state.render()

    if note:
        messages[1] = {
            "role": "user",
            "content": task + "\n\n" + note,
        }

    return messages


def compress_by_trim(messages, task, used, state, logger):
    """Обрізає історію та за потреби додає стан задачі."""
    before = len(messages)

    messages = trim(messages, config.KEEP_LAST)

    if config.USE_STATE:
        messages = attach_state(messages, task, state)

    logger.info(
        f"  СТИСНЕННЯ: вхід був {used} токенів, "
        f"повідомлень {before} -> {len(messages)}"
        + (", стан додано" if config.USE_STATE else "")
    )

    if config.USE_STATE:
        logger.info(
            "  ПЕРШЕ ПОВІДОМЛЕННЯ КОРИСТУВАЧА ПІСЛЯ СТИСНЕННЯ:\n"
            + messages[1]["content"]
        )

    return messages


def compress_history(messages, task, used, state, logger):
    """Перевіряє поріг і обирає спосіб скорочення історії."""
    if used <= config.COMPRESS_AT:
        return messages

    if config.COMPRESS == "trim":
        return compress_by_trim(
            messages, task, used, state, logger
        )

    if config.COMPRESS == "summary":
        return compress_by_summary(
            messages, used, logger
        )

    return messages