from langfuse.openai import OpenAI
from langfuse import observe

import config
from schemas import SCHEMAS
from dispatcher import call_tool, check_response, MODEL_ERRORS
from utils.lab_logger import custom_logger


client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY,
)

logger = custom_logger("lab3", f"lab3_{config.RUN_TAG}.log")


@observe()
def run_agent(task: str) -> str:
    messages = [
        {"role": "system", "content": config.SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    retries = 0

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

        response_error = check_response(response)

        if response_error:
            level, text = response_error
            retries += 1

            logger.warning(
                "Помилка відповіді моделі | level=%s | retries=%s | message=%s",
                level,
                retries,
                text,
            )

            if retries > config.MAX_RETRIES:
                return "Перевищено ліміт повторних спроб. " + text

            messages.append({
                "role": "user",
                "content": (
                    "Попередня відповідь була некоректною: "
                    + text
                    + " Спробуй ще раз."
                ),
            })
            continue

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
            level, result = call_tool(
                call.function.name,
                call.function.arguments,
            )

            logger.info(
                "Виклик інструмента: %s | Рівень: %s | Аргументи: %s | Результат: %s",
                call.function.name,
                level,
                call.function.arguments,
                result,
            )

            if level in MODEL_ERRORS:
                retries += 1

                logger.warning(
                    "Помилка моделі | level=%s | retries=%s",
                    level,
                    retries,
                )

                if retries > config.MAX_RETRIES:
                    return (
                        "Перевищено ліміт повторних спроб. "
                        + result
                    )

            elif level == "ok":
                retries = 0

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
