"""Скорочення історії, коли вхід став завеликим."""
import config
from context import trim
from summary import compress_by_summary


def attach_state(messages, task, state):
    """Дописує до запитання користувача список збережених результатів (див. state.py)."""
    note = state.render()
    if note:                                     # якщо в стані вже щось є
        # messages[1] - це запитання користувача (друге повідомлення в історії)
        messages[1] = {"role": "user", "content": task + "\n\n" + note}
    return messages


def compress_by_trim(messages, task, used, state, logger):
    """Обрізає історію і, якщо ввімкнено стан, додає його до запитання."""
    before = len(messages)
    messages = trim(messages, config.KEEP_LAST)
    if config.USE_STATE:
        messages = attach_state(messages, task, state)
    logger.info(f"  СТИСНЕННЯ: вхід був {used} токенів, повідомлень {before} -> {len(messages)}"
        + (", стан додано" if config.USE_STATE else ""))
    if config.USE_STATE:
        logger.info("  ПЕРШЕ ПОВІДОМЛЕННЯ КОРИСТУВАЧА ПІСЛЯ СТИСНЕННЯ:\n" + messages[1]["content"])
    return messages


def compress_history(messages, task, used, state, logger):
    """Скорочує історію, якщо вхід перевищив поріг COMPRESS_AT. Повертає (нову) історію."""
    if used <= config.COMPRESS_AT:               # вхід ще малий: нічого не робимо
        return messages
    if config.COMPRESS == "trim":
        return compress_by_trim(messages, task, used, state, logger)
    if config.COMPRESS == "summary":
        return compress_by_summary(messages, used, logger)
    return messages                              # COMPRESS = "none": історія росте далі