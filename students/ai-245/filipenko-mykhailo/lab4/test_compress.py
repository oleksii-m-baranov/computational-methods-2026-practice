
from compress import compress_messages


messages = [
    {"role": "system", "content": "Ти консультант."},
    {"role": "user", "content": "Порівняй ноутбуки."}
]

for index in range(10):
    call_id = f"call_{index}"

    messages.append({
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": call_id,
                "type": "function",
                "function": {
                    "name": "search_laptops",
                    "arguments": '{"query":"навчання"}'
                }
            }
        ]
    })

    messages.append({
        "role": "tool",
        "tool_call_id": call_id,
        "content": "StudyNova 14"
    })

compressed = compress_messages(messages, keep_last=6)

pending = set()
valid = True

for message in compressed:
    if message.get("role") == "assistant":
        for call in message.get("tool_calls") or []:
            pending.add(call["id"])

    elif message.get("role") == "tool":
        call_id = message.get("tool_call_id")

        if call_id not in pending:
            valid = False
        else:
            pending.remove(call_id)

if pending:
    valid = False

print(f"Повідомлень до: {len(messages)}")
print(f"Повідомлень після: {len(compressed)}")
print(f"Історія коректна: {valid}")
