import logging

import config
from compress import compress_history
from state import TaskState


def main():
    config.COMPRESS = "trim"
    config.USE_STATE = True
    config.COMPRESS_AT = 2800
    config.KEEP_LAST = 6

    logger = logging.getLogger("state_test")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(message)s")
    )

    logger.handlers.clear()
    logger.addHandler(handler)

    task = (
        "Знайди інформацію про StudyNova 14, "
        "визнач ціну та розрахуй розстрочку."
    )

    state = TaskState("compression_test")

    state.record(
        "search_laptops",
        '{"query":"StudyNova 14"}',
        "StudyNova 14"
    )

    state.record(
        "laptop_info",
        '{"model":"StudyNova 14"}',
        "Ціна: 22000 грн, на складі: 5 шт."
    )

    messages = [
        {
            "role": "system",
            "content": config.SYSTEM
        },
        {
            "role": "user",
            "content": task
        }
    ]

    for index in range(10):
        messages.append({
            "role": "user",
            "content": (
                f"Проміжне повідомлення {index + 1}"
            )
        })

        messages.append({
            "role": "assistant",
            "content": (
                f"Проміжна відповідь {index + 1}"
            )
        })

    compressed = compress_history(
        messages=messages,
        task=task,
        used=3000,
        state=state,
        logger=logger
    )

    assert len(compressed) < len(messages), (
        "Історія не скоротилася"
    )

    first_user = compressed[1]["content"]

    assert "StudyNova 14" in first_user
    assert "22000 грн" in first_user
    assert "Збережені результати" in first_user

    print()
    print("ТЕСТ ПРОЙДЕНО")
    print(
        f"Повідомлень до стискання: "
        f"{len(messages)}"
    )
    print(
        f"Повідомлень після стискання: "
        f"{len(compressed)}"
    )
    print(
        f"Збережених записів: "
        f"{len(state.records)}"
    )


if __name__ == "__main__":
    main()
