import json
from types import SimpleNamespace
from unittest.mock import patch

import config
from agent import run_agent


with open("long_task.json", encoding="utf-8") as file:
    task = json.load(file)


def make_response(content):
    message = SimpleNamespace(
        content=content,
        tool_calls=None,
        model_dump=lambda exclude_none=True: {
            "role": "assistant",
            "content": content
        }
    )

    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=message,
                finish_reason="stop"
            )
        ],
        usage=SimpleNamespace(
            prompt_tokens=100,
            completion_tokens=30
        )
    )


responses = [
    make_response("Завдання виконано."),
    make_response("Завдання виконано.")
]

received_messages = []


def fake_model(messages, step, logger):
    received_messages.append(
        [dict(message) for message in messages]
    )

    return responses.pop(0), False


with patch("agent.call_model", side_effect=fake_model), \
     patch("agent.check_response", return_value=("ok", "OK")), \
     patch("agent.compress_history", side_effect=lambda messages, *args: messages):

    result = run_agent(
        task["question"],
        max_steps=2,
        logfile_name="logs/test_completion.log",
        log_overwrite=True,
        task_data=task
    )


feedback = [
    message["content"]
    for message in received_messages[1]
    if message.get("role") == "user"
    and "Задача ще не завершена" in message.get("content", "")
]

print()
print("ФІНАЛЬНА ВІДПОВІДЬ:", result)
print("АГЕНТ НЕ ПРИЙНЯВ ПЕРЕДЧАСНУ ВІДПОВІДЬ:", result is None)
print("ПОВІДОМЛЕННЯ ПРО НЕВИКОНАНІ ДІЇ:", bool(feedback))
print("ЗГАДАНО STUDYNOVA 15:", any("StudyNova 15" in item for item in feedback))
