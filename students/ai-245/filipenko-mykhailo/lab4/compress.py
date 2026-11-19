import config
from context import trim, estimate_tokens


def attach_state(messages, task, state):
    """Додає збережений стан до початкової задачі."""
    if state is None or not state.records:
        return messages

    result = list(messages)

    if len(result) < 2:
        return result

    state_text = state.render()

    result[1] = {
        "role": "user",
        "content": (
            f"{task}\n\n"
            "Збережені результати попередніх "
            "викликів інструментів:\n"
            f"{state_text}\n\n"
            "Використовуй ці результати для "
            "продовження задачі. "
            "Не повторюй уже виконані виклики "
            "без потреби."
        )
    }

    return result


def compress_history(messages, task, used, state, logger):
    """Скорочує історію та додає стан за потреби."""

    if config.COMPRESS != "trim":
        return messages

    if used <= config.COMPRESS_AT:
        return messages

    before = len(messages)

    compressed = trim(
        messages,
        keep_last=config.KEEP_LAST
    )

    if config.USE_STATE:
        compressed = attach_state(
            compressed,
            task,
            state
        )

    logger.info(
        f"  СТИСНЕННЯ: вхід був {used} токенів, "
        f"повідомлень {before} -> {len(compressed)}"
    )

    if config.USE_STATE and state is not None:
        logger.info(
            f"  СТАН: збережено {len(state.records)} "
            "результатів інструментів"
        )

        if len(compressed) > 1:
            first_user = compressed[1].get("content", "")

            logger.info(
                "  ПЕРШЕ ПОВІДОМЛЕННЯ КОРИСТУВАЧА "
                "ПІСЛЯ СТИСНЕННЯ:"
            )
            logger.info(first_user)

            logger.info(
                "  ОЦІНКА ТОКЕНІВ ПІСЛЯ СТИСНЕННЯ: "
                f"{estimate_tokens(compressed)}"
            )

    return compressed
