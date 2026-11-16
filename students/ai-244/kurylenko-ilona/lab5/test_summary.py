"""Окрема перевірка підсумовування історії агента."""

import logging

import config
from summary import compress_by_summary


def make_messages():
    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": "Опрацюй шістьох котів."},
    ]

    results = [
        ("calc_food", "1500 г"),
        ("calc_food", "2250 г"),
        ("calc_food", "3000 г"),
        ("vaccine_info", "650 грн"),
        ("calc_food", "3750 г"),
        ("calc_food", "4500 г"),
        ("calc_food", "5250 г"),
    ]

    for i, (tool, result) in enumerate(results, start=1):
        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": f"call_{i}",
                "type": "function",
                "function": {
                    "name": tool,
                    "arguments": "{}",
                },
            }],
        })

        messages.append({
            "role": "tool",
            "tool_call_id": f"call_{i}",
            "content": result,
        })

    return messages


def main():
    logger = logging.getLogger("summary_test")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        logger.addHandler(logging.StreamHandler())

    messages = make_messages()

    print("ТЕСТ ПІДСУМОВУВАННЯ", flush=True)
    print("Модель:", config.MODEL, flush=True)
    print("Повідомлень до:", len(messages), flush=True)

    result = compress_by_summary(
        messages,
        config.COMPRESS_AT + 100,
        logger,
    )

    print("\nРЕЗУЛЬТАТ", flush=True)
    print("Повідомлень після:", len(result), flush=True)
    print(
        "Підсумок додано:",
        "Підсумок попередніх кроків:"
        in result[1]["content"],
        flush=True,
    )

    if len(result) >= len(messages):
        raise AssertionError("Історію не скорочено.")

    if "Підсумок попередніх кроків:" not in result[1]["content"]:
        raise AssertionError("Підсумок не додано.")

    print("Перевірка структури пройдена.", flush=True)
    print("Числову точність перевір за текстом підсумку.")


if __name__ == "__main__":
    main()