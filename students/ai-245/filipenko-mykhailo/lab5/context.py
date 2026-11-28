import json


def message_text(message):
    if isinstance(message, dict):
        data = message
    elif hasattr(message, "model_dump"):
        data = message.model_dump(exclude_none=True)
    else:
        return str(message)

    return json.dumps(data, ensure_ascii=False, default=str)


def estimate_tokens(messages):
    return sum(
        max(1, len(message_text(message)) // 4)
        for message in messages
    )


def context_usage(messages, num_ctx=4096):
    tokens = estimate_tokens(messages)

    return {
        "estimated_tokens": tokens,
        "num_ctx": num_ctx,
        "usage_percent": round(tokens / num_ctx * 100, 2),
        "remaining_tokens": max(0, num_ctx - tokens)
    }


def trim(messages, keep_last=6):
    if len(messages) <= 2:
        return list(messages)

    head = list(messages[:2])
    tail = list(messages[2:])[-keep_last:]

    valid_ids = set()

    for message in tail:
        if message.get("role") == "assistant":
            for call in message.get("tool_calls") or []:
                if isinstance(call, dict):
                    call_id = call.get("id")
                else:
                    call_id = getattr(call, "id", None)

                if call_id:
                    valid_ids.add(call_id)

    tail = [
        message
        for message in tail
        if message.get("role") != "tool"
        or message.get("tool_call_id") in valid_ids
    ]

    pending_ids = set()
    cleaned_tail = []

    for message in tail:
        if message.get("role") == "assistant":
            calls = message.get("tool_calls") or []

            if calls:
                call_ids = {
                    call.get("id")
                    if isinstance(call, dict)
                    else getattr(call, "id", None)
                    for call in calls
                }

                available_ids = {
                    item.get("tool_call_id")
                    for item in tail
                    if item.get("role") == "tool"
                }

                if not call_ids.issubset(available_ids):
                    continue

                pending_ids.update(call_ids)

        if message.get("role") == "tool":
            if message.get("tool_call_id") not in pending_ids:
                continue

        cleaned_tail.append(message)

    return head + cleaned_tail


if __name__ == "__main__":
    sample = [
        {"role": "system", "content": "Ти консультант ноутбуків."},
        {"role": "user", "content": "Порадь ноутбук для навчання."}
    ]

    print(context_usage(sample))
