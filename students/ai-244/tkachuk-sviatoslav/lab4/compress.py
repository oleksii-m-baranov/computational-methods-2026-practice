"""Обрізання історії з необов'язковим відновленням стану."""
import config
from context import trim
from summary import compress_by_summary


def compress_history(messages, task, used, state, logger):
    if used <= config.COMPRESS_AT or config.COMPRESS == "none":
        return messages
    if config.COMPRESS == "summary":
        return compress_by_summary(messages, used, logger)
    if config.COMPRESS != "trim":
        return messages
    before = len(messages)
    messages = trim(messages, config.KEEP_LAST)
    if config.USE_STATE:
        note = state.render()
        if note:
            messages[1] = {"role": "user", "content": task + "\n\n" + note}
    logger.info(f"  СТИСНЕННЯ: вхід був {used} токенів, повідомлень {before} -> {len(messages)}"
                + (", стан додано" if config.USE_STATE else ""))
    if config.USE_STATE:
        logger.info("  ПЕРШЕ ПОВІДОМЛЕННЯ КОРИСТУВАЧА ПІСЛЯ СТИСНЕННЯ:\n" + messages[1]["content"])
    return messages
