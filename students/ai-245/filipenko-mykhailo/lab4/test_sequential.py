import json
from unittest.mock import patch
from types import SimpleNamespace

import config
from agent import run_agent


def tool_call(call_id, name, arguments):
    return SimpleNamespace(
        id=call_id,
        type="function",
        function=SimpleNamespace(
            name=name,
            arguments=json.dumps(arguments, ensure_ascii=False)
        )
    )


def make_response(calls=None, content=None):
    calls = calls or []

    message = SimpleNamespace(
        tool_calls=calls,
        content=content,
        model_dump=lambda exclude_none=True: {
            "role": "assistant",
            "content": content,
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments
                    }
                }
                for call in calls
            ] if calls else None
        }
    )

    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=message,
                finish_reason="tool_calls" if calls else "stop"
            )
        ],
        usage=SimpleNamespace(
            prompt_tokens=100,
            completion_tokens=50
        )
    )


responses = [
    make_response([
        tool_call(
            "call_1",
            "search_laptops",
            {"query": "StudyNova 14"}
        ),
        tool_call(
            "call_2",
            "laptop_info",
            {"model": "StudyNova 14"}
        )
    ]),
    make_response(content="Тест завершено.")
]

executed = []


def fake_model(messages, step, logger):
    return responses.pop(0), False


def fake_tool(name, arguments):
    executed.append(name)
    return "ok", "Тестовий результат"


with patch("agent.call_model", side_effect=fake_model), \
     patch("agent.call_tool", side_effect=fake_tool), \
     patch("agent.check_response", return_value=("ok", "OK")), \
     patch("agent.compress_history", side_effect=lambda messages, *args: messages):

    result = run_agent(
        "Тест послідовних викликів",
        max_steps=2,
        logfile_name="logs/test_sequential.log",
        log_overwrite=True
    )

print()
print("ВИКОНАНІ ІНСТРУМЕНТИ:", executed)
print("ЛИШЕ ОДИН ВИКЛИК:", executed == ["search_laptops"])
print("ВІДПОВІДЬ:", result)
