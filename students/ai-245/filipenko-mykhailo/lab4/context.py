import json


def message_dict(message):
    """Перетворення повідомлення на словник."""
    if isinstance(message, dict):
        return message

    if hasattr(message, "model_dump"):
        return message.model_dump(exclude_none=True)

    return {
        "role": getattr(message, "role", "unknown"),
        "content": str(message)
    }


def message_text(message):
    """Текстове представлення повідомлення."""
    return json.dumps(
        message_dict(message),
        ensure_ascii=False,
        default=str
    )


def estimate_tokens(messages):
    """Приблизна оцінка кількості токенів."""
    return sum(
        max(1, len(message_text(message)) // 4)
        for message in messages
    )


def context_usage(messages, num_ctx=4096):
    """Оцінювання використання контекстного вікна."""
    tokens = estimate_tokens(messages)

    return {
        "estimated_tokens": tokens,
        "num_ctx": num_ctx,
        "usage_percent": (
            round(tokens / num_ctx * 100, 2)
            if num_ctx > 0 else 0
        ),
        "remaining_tokens": max(0, num_ctx - tokens)
    }


def get_tool_call_ids(message):
    """Отримання ID викликів інструментів."""
    data = message_dict(message)
    ids = set()

    for call in data.get("tool_calls") or []:
        if isinstance(call, dict):
            call_id = call.get("id")
        else:
            call_id = getattr(call, "id", None)

        if call_id:
            ids.add(call_id)

    return ids


def split_groups(messages):
    """Розбиття історії на цілісні групи повідомлень."""
    groups = []
    current = []
    pending_ids = set()

    for message in messages:
        data = message_dict(message)
        role = data.get("role")

        if role == "assistant" and not pending_ids:
            if current:
                groups.append(current)
                current = []

        current.append(message)

        if role == "assistant":
            pending_ids.update(get_tool_call_ids(message))

        elif role == "tool":
            call_id = data.get("tool_call_id")

            if call_id:
                pending_ids.discard(call_id)

        if role == "tool" and not pending_ids:
            groups.append(current)
            current = []

    if current:
        groups.append(current)

    return groups


def valid_tool_links(messages):
    """Перевірка відповідності викликів та результатів."""
    expected = set()
    received = set()

    for message in messages:
        data = message_dict(message)

        if data.get("role") == "assistant":
            expected.update(get_tool_call_ids(message))

        elif data.get("role") == "tool":
            call_id = data.get("tool_call_id")

            if not call_id or call_id not in expected:
                return False

            if call_id in received:
                return False

            received.add(call_id)

    return expected == received


def trim(messages, keep_last=6):
    """Скорочення історії зі збереженням груп інструментів.

    Зберігаємо:
    - перші два повідомлення;
    - останні цілісні групи;
    - зв'язки між assistant.tool_calls та tool.tool_call_id.
    """
    messages = list(messages)

    if len(messages) <= 2:
        return messages

    keep_last = max(0, int(keep_last))

    if keep_last == 0:
        return messages[:2]

    head = messages[:2]
    body = messages[2:]

    if len(body) <= keep_last:
        return messages

    groups = split_groups(body)

    selected = []
    count = 0

    for group in reversed(groups):
        if count >= keep_last:
            break

        selected.insert(0, group)
        count += len(group)

    tail = [
        message
        for group in selected
        for message in group
    ]

    if not valid_tool_links(tail):
        # Якщо остання група неповна, не відправляємо
        # її як некоректну історію до моделі.
        while selected:
            selected.pop(0)

            tail = [
                message
                for group in selected
                for message in group
            ]

            if valid_tool_links(tail):
                break

    return head + tail


if __name__ == "__main__":
    sample = [
        {
            "role": "system",
            "content": "Ти консультант ноутбуків."
        },
        {
            "role": "user",
            "content": "Порадь ноутбук для навчання."
        },
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "search_laptops",
                        "arguments": '{"query":"StudyNova 14"}'
                    }
                }
            ]
        },
        {
            "role": "tool",
            "tool_call_id": "call_1",
            "content": "StudyNova 14"
        }
    ]

    print("Використання контексту:")
    print(context_usage(sample))

    print("\nПеревірка зв'язків інструментів:")
    print(valid_tool_links(sample[2:]))

    print("\nРезультат trim:")
    result = trim(sample, keep_last=2)

    for item in result:
        print(message_text(item))
