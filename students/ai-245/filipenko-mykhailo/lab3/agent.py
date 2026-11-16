
from langfuse import observe, get_client, propagate_attributes
from openai import OpenAI

import config
from schemas import SCHEMAS
from dispatcher import call_tool, check_response
from lab_logger import custom_logger


client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY
)

logger = custom_logger(config.LAB_LOGFILE_NAME)

# Помилки моделі, які враховуються в MAX_RETRIES.
# Помилка "tool" не входить до цього переліку.
MODEL_ERRORS = {
    "name",
    "permission",
    "syntax",
    "schema",
    "meaning",
    "response",
    "length"
}


@observe(name="agent_step")
def agent_step(messages, step):
    with get_client().start_as_current_observation(
        as_type="generation",
        name="ollama_generation",
        model=config.MODEL,
        input=messages,
        model_parameters={
            "temperature": config.TEMPERATURE
        }
    ) as generation:

        response = client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=SCHEMAS,
            temperature=config.TEMPERATURE
        )

        usage_details = {}

        if response.usage is not None:
            usage_details = {
                "input": response.usage.prompt_tokens or 0,
                "output": response.usage.completion_tokens or 0
            }

        generation.update(
            output=response.model_dump(),
            usage_details=usage_details
        )

    status, explanation = check_response(response)

    choice = response.choices[0] if response.choices else None
    message = choice.message if choice else None

    logger.info(f"\n--- КРОК {step} ---")
    logger.info(f"Перевірка відповіді: {status}")

    if explanation:
        logger.info(f"Пояснення: {explanation}")

    if response.usage is not None:
        logger.info(
            f"ТОКЕНИ: вхід={response.usage.prompt_tokens}, "
            f"вихід={response.usage.completion_tokens}"
        )

    if message and message.tool_calls:
        for tool_call in message.tool_calls:
            logger.info(
                f"Рішення моделі: {tool_call.function.name}"
            )

    return response, status, explanation


@observe(name="run_agent")
def run_agent(task):
    messages = [
        {
            "role": "system",
            "content": config.SYSTEM
        },
        {
            "role": "user",
            "content": task
        }
    ]

    retries = 0

    logger.info("\n" + "=" * 60)
    logger.info(f"ЗАВДАННЯ: {task}")

    for step in range(1, config.MAX_STEPS + 1):
        response, status, explanation = agent_step(
            messages,
            step
        )

        # Перевірка відповіді мовної моделі
        if status != "ok":
            if status in MODEL_ERRORS:
                retries += 1

            logger.warning(
                f"Помилка відповіді моделі: {status}"
            )

            if retries > config.MAX_RETRIES:
                logger.error(
                    "Перевищено кількість повторних спроб."
                )
                return None

            messages.append({
                "role": "user",
                "content": (
                    f"Попередня відповідь містила помилку "
                    f"'{status}'. {explanation or ''} "
                    "Виправ відповідь."
                )
            })

            continue

        message = response.choices[0].message

        # Якщо модель не викликала інструмент
        if not message.tool_calls:
            answer = (message.content or "").strip()

            if not answer:
                retries += 1

                if retries > config.MAX_RETRIES:
                    logger.error(
                        "Модель повернула порожню відповідь."
                    )
                    return None

                messages.append({
                    "role": "user",
                    "content": (
                        "Попередня відповідь була порожньою. "
                        "Дай змістовну відповідь або "
                        "використай потрібний інструмент."
                    )
                })

                continue

            logger.info(f"ВІДПОВІДЬ: {answer}")
            return answer

        # Зберігаємо справжнє рішення моделі
        messages.append(message)

        has_model_error = False
        has_tool_error = False
        has_successful_call = False

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            arguments = tool_call.function.arguments

            logger.info(
                f"ВИКЛИК: {name}({arguments})"
            )

            level, result = call_tool(name, arguments)

            logger.info(f"РІВЕНЬ: {level}")
            logger.info(f"РЕЗУЛЬТАТ: {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

            if level in MODEL_ERRORS:
                has_model_error = True

            elif level == "tool":
                has_tool_error = True

            elif level == "ok":
                has_successful_call = True

        # Помилки моделі враховуємо в ліміті
        if has_model_error:
            retries += 1

            logger.warning(
                "Помилка перевірки виклику. "
                "Результат передано моделі."
            )

            if retries > config.MAX_RETRIES:
                logger.error(
                    "Перевищено ліміт помилок моделі."
                )
                return None

        # Помилки інструмента не зараховуємо моделі
        elif has_tool_error:
            logger.warning(
                "Помилка виконання інструмента. "
                "Повідомлення передано моделі. "
                "Помилка не враховується в MAX_RETRIES."
            )

        # Після успішного виклику обнуляємо лічильник
        elif has_successful_call:
            retries = 0

    logger.error(
        "Вичерпано ліміт кроків агента."
    )

    return None


if __name__ == "__main__":
    task = (
        "Знайди ноутбук для навчання, "
        "перевір його ціну та наявність."
    )

    with propagate_attributes(
        trace_name="lab3-real-agent",
        tags=["lab3", "real-tool-calling"]
    ):
        result = run_agent(task)

    get_client().flush()

    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ:")
    print(result)
    print("=" * 60)
