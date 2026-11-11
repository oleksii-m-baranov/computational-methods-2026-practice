"""Перевірка коректності історії після обрізання."""

from context import trim


def validate_history(messages):
    """Перевіряє відповідність викликів інструментів їхнім результатам."""
    pending = set()

    for message in messages:
        role = message["role"]

        if role == "assistant":
            if pending:
                raise AssertionError(
                    f"Немає результатів для викликів: {pending}"
                )

            for call in message.get("tool_calls", []):
                pending.add(call["id"])

        elif role == "tool":
            call_id = message["tool_call_id"]

            if call_id not in pending:
                raise AssertionError(
                    f"Результат без відповідного виклику: {call_id}"
                )

            pending.remove(call_id)

        elif pending:
            raise AssertionError(
                f"Немає результатів для викликів: {pending}"
            )

    if pending:
        raise AssertionError(
            f"Незавершені виклики інструментів: {pending}"
        )

    return True


def make_messages():
    messages = [
        {"role": "system", "content": "Тестова інструкція"},
        {"role": "user", "content": "Тестова задача"},
    ]

    for i in range(1, 9):
        call_id = f"call_{i}"

        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": call_id,
                "type": "function",
                "function": {
                    "name": "calc_food",
                    "arguments": '{"weight_kg":2,"grams_per_kg":25,"days":30}',
                },
            }],
        })

        messages.append({
            "role": "tool",
            "tool_call_id": call_id,
            "content": f"{i * 750} г",
        })

    return messages


def main():
    original = make_messages()

    print("Перевірка початкової історії:", validate_history(original))

    shortened = trim(original, 6)

    print("Повідомлень до:", len(original))
    print("Повідомлень після:", len(shortened))
    print("Перевірка скороченої історії:", validate_history(shortened))

    assert len(shortened) < len(original)
    assert shortened[0]["role"] == "system"
    assert shortened[1]["role"] == "user"

    print("ТЕСТ ПРОЙДЕНО")


if __name__ == "__main__":
    main()