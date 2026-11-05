"""Цикл агента (Бібліотека)"""
import sys
from pathlib import Path

current_dir = Path(__file__).resolve()
for parent in [current_dir] + list(current_dir.parents):
    if (parent / "utils").is_dir():
        if str(parent) not in sys.path:
            sys.path.insert(0, str(parent))
        break

try:
    from utils.lab_logger import custom_logger
except ModuleNotFoundError:
    import logging
    def custom_logger(name):
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(message)s'))
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

from openai import OpenAI
import config
from schemas import SCHEMAS
from dispatcher import call_tool

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
logger = custom_logger('lab2')

def run_agent(task):
    """task – питання користувача.
    Повертає текст відповіді або None, якщо вичерпано ліміт."""

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

        logger.info(f"\n--- крок {step} | prompt_tokens={response.usage.prompt_tokens}")

        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return msg.content

        messages.append(msg)

        for call in msg.tool_calls:
            logger.info(f"  виклик   : {call.function.name}({call.function.arguments})")

            result = call_tool(call.function.name, call.function.arguments)

            logger.info(f"  результат: {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })

    logger.info("СТОП: вичерпано ліміт кроків")
    return None


if __name__ == "__main__":
    print("--- ТЕСТ 1: Однокрокова задача (Z1) ---")
    run_agent("Знайди щось легке з фантастики")
    
    print("\n--- ТЕСТ 2: Багатокрокова задача (Z3) ---")
    run_agent("Я затримав книжку про алгоритми на 5 днів. Скільки штраф?")
