
import config
from context import trim


def attach_state(messages, task, state):
    if state is None or not state.records:
        return messages

    result = list(messages)

    state_text = state.render()

    result[1] = {
        "role": "user",
        "content": (
            f"{task}\n\n"
            f"Збережені результати попередніх викликів інструментів:\n"
            f"{state_text}\n\n"
            f"Використовуй ці результати для продовження задачі. "
            f"Не повторюй уже виконані виклики без потреби."
        )
    }

    return result


def compress_history(messages, task, used, state, logger):
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

    if config.USE_STATE:
        logger.info(
            f"  СТАН: збережено {len(state.records)} "
            f"результатів інструментів"
        )

    return compressed
