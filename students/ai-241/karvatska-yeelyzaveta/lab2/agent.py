import sys
from pathlib import Path

from openai import OpenAI

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import config
from schemas import SCHEMAS
from dispatcher import call_tool
from utils.lab_logger import custom_logger


client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY,
)

logger = custom_logger("lab2")


def run_agent(task: str) -> str:
    messages = [
        {"role": "system", "content": config.SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    for step in range(1, config.MAX_STEPS + 1):
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=SCHEMAS,
            temperature=config.TEMPERATURE,
        )

        usage = getattr(response, "usage", None)
        logger.info(
            "Token usage | task=%s | step=%s | prompt_tokens=%s | completion_tokens=%s",
            task,
            step,
            getattr(usage, "prompt_tokens", None),
            getattr(usage, "completion_tokens", None),
        )

        message = response.choices[0].message

        if not message.tool_calls:
            answer = (message.content or "").strip()

            if not answer:
                logger.warning(
                    "Порожня відповідь моделі | task=%s | step=%s",
                    task,
                    step,
                )
                return "Модель повернула порожню відповідь. Завдання не виконано."

            logger.info(
                "Завдання: %s | Кроків: %s | Відповідь: %s",
                task,
                step,
                answer,
            )
            return answer

        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in message.tool_calls
            ],
        })

        for call in message.tool_calls:
            result = call_tool(
                call.function.name,
                call.function.arguments,
            )

            logger.info(
                "Виклик інструмента: %s | Аргументи: %s | Результат: %s",
                call.function.name,
                call.function.arguments,
                result,
            )

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })

    logger.warning(
        "Досягнуто ліміт кроків (%s). Завдання: %s",
        config.MAX_STEPS,
        task,
    )

    return "Не вдалося завершити завдання в межах ліміту кроків."


if __name__ == "__main__":
    print(run_agent("Знайди щось із куркою"))
