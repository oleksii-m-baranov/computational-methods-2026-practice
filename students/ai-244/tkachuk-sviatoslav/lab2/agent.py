"""Повноцінний цикл агента з інструментами та журналюванням."""
from pathlib import Path
import sys

import config
from dispatcher import call_tool
from schemas import SCHEMAS

# Корінь навчального репозиторію: необхідно для спільного utils.
# У наданому репозиторії немає setup.py / pyproject.toml, тому `pip install -e .`
# не працюватиме; цей шлях забезпечує імпорт без сторонніх змін.
REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from utils.lab_logger import custom_logger

logger = custom_logger("lab2")


def run_agent(task: str, client=None):
    """Виконує задачу; client можна замінити під час локальних тестів."""
    if client is None:
        from openai import OpenAI
        client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)

    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task},
    ]
    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")

    for step in range(1, config.MAX_STEPS + 1):
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=SCHEMAS,
            temperature=config.TEMPERATURE,
        )
        msg = response.choices[0].message
        usage = getattr(response, "usage", None)
        tokens = getattr(usage, "prompt_tokens", "н/д")
        logger.info(f"\n--- крок {step} | prompt_tokens={tokens}")

        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return msg.content

        messages.append(msg)
        for call in msg.tool_calls:
            logger.info(
                f"  виклик   : {call.function.name}({call.function.arguments})"
            )
            result = call_tool(call.function.name, call.function.arguments)
            logger.info(f"  результат: {result}")
            # Відповідь додається ОКРЕМО для кожного tool_call_id.
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })

    logger.info("СТОП: вичерпано ліміт кроків")
    return None


if __name__ == "__main__":
    run_agent("Кіт дряпає меблі, що робити?")
