
"""Стиснення контексту бібліотечного LLM-агента."""

import config
from context import trim_messages


def attach_state(messages, task, state):
    """Додає збережені результати до запитання користувача."""

    note = state.render()

    if note:
        messages[1] = {
            "role": "user",
            "content": task + "\n\n" + note,
        }

    return messages


def compress_by_trim(messages, task, used, state, logger):
    """Скорочує історію та за потреби додає стан."""

    before = len(messages)

    messages = trim_messages(
        messages,
        keep_last=config.KEEP_LAST,
    )

    if config.USE_STATE:
        messages = attach_state(messages, task, state)

    logger.info(
        f"  СТИСНЕННЯ: вхід був {used} токенів, "
        f"повідомлень {before} -> {len(messages)}"
        + (", стан додано" if config.USE_STATE else "")
    )

    if config.USE_STATE:
        logger.info(
            "  ПЕРШЕ ПОВІДОМЛЕННЯ КОРИСТУВАЧА "
            "ПІСЛЯ СТИСНЕННЯ:\n"
            + messages[1]["content"]
        )

    return messages


def compress_history(messages, task, used, state, logger):
    """Стискає історію після перевищення порога."""

    if used <= config.COMPRESS_AT:
        return messages

    if config.COMPRESS == "trim":
        return compress_by_trim(
            messages,
            task,
            used,
            state,
            logger,
        )

    return messages
