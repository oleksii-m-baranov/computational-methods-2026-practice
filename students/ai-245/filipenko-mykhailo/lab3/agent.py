"""AI-агент для вибору ноутбука. Варіант 9. ЛР3."""

import json
import re

from langfuse import observe, get_client, propagate_attributes
from openai import OpenAI

import config
from schemas import SCHEMAS
from tools import TOOLS
from dispatcher import call_tool, check_response
from lab_logger import custom_logger


client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY
)

logger = custom_logger(config.LAB_LOGFILE_NAME)

RUN_TAG = getattr(config, "RUN_TAG", "checks").lower()

MODEL_ERRORS = {
    "name",
    "permission",
    "syntax",
    "schema",
    "meaning",
    "response",
    "length"
}


def baseline_call_tool(name: str, args_raw: str) -> str:
    """
    Початкова логіка dispatcher.py із ЛР2.
    Без додаткових перевірок ЛР3.
    """
    if name not in TOOLS:
        return (
            f"Помилка: інструмента '{name}' не існує. "
            f"Доступні: {', '.join(TOOLS)}"
        )

    try:
        args = json.loads(args_raw)
        return str(TOOLS[name](**args))

    except json.JSONDecodeError:
        return "Помилка: аргументи не є коректним JSON."

    except TypeError as error:
        return f"Помилка в аргументах: {error}"

    except Exception as error:
        return f"Помилка виконання: {error}"


def extract_verified_price(result):
    """
    Отримує ціну з успішної відповіді laptop_info.

    Наприклад:
    'Ціна: 22000 грн, на складі: 5 шт.'
    """
    match = re.search(
        r"Ціна:\s*(\d+(?:[.,]\d+)?)\s*грн",
        str(result),
        flags=re.IGNORECASE
    )

    if match is None:
        return None

    return float(match.group(1).replace(",", "."))


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

    tokens = (
        response.usage.prompt_tokens
        if response.usage else "невідомо"
    )

    logger.info(
        f"\n--- крок {step} | prompt_tokens={tokens}"
    )

    if RUN_TAG == "baseline":
        return response, "ok", ""

    status, explanation = check_response(response)

    logger.info(f"Перевірка відповіді: {status}")

    if explanation:
        logger.info(f"Пояснення: {explanation}")

    return response, status, explanation


@observe(name="run_agent")
def run_agent(task):
    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task}
    ]

    retries = 0

    # Окремий контекст для кожного завдання.
    # У режимі baseline не використовується.
    context = {}

    logger.info("\n" + "=" * 60)
    logger.info(f"РЕЖИМ: {RUN_TAG}")
    logger.info(f"ЗАДАЧА: {task}")

    for step in range(1, config.MAX_STEPS + 1):

        response, status, explanation = agent_step(
            messages,
            step
        )

        # Перевірка структури відповіді моделі.
        if RUN_TAG == "checks" and status != "ok":
            retries += 1

            logger.warning(
                f"Помилка відповіді моделі: {status}"
            )

            if retries > config.MAX_RETRIES:
                logger.error(
                    "Перевищено ліміт повторних спроб."
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

        if not response.choices:
            logger.error("Модель не повернула відповідь.")
            return None

        msg = response.choices[0].message

        if not msg.tool_calls:
            answer = msg.content

            if RUN_TAG == "checks" and not (answer or "").strip():
                retries += 1

                if retries > config.MAX_RETRIES:
                    logger.error(
                        "Перевищено ліміт повторних спроб."
                    )
                    return None

                messages.append({
                    "role": "user",
                    "content": (
                        "Попередня відповідь була порожньою. "
                        "Виправ відповідь або виклич інструмент."
                    )
                })

                continue

            logger.info(f"ВІДПОВІДЬ: {answer}")
            return answer

        messages.append(msg)

        has_model_error = False
        has_tool_error = False
        has_successful_call = False

        # Ціна, підтверджена ДО поточного кроку.
        # Нові результати цього кроку стануть доступними
        # для перевірок лише на наступному кроці.
        step_context = context.copy()
        pending_context = context.copy()

        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            arguments = tool_call.function.arguments

            logger.info(
                f"  виклик   : {name}({arguments})"
            )

            if RUN_TAG == "baseline":
                result = baseline_call_tool(
                    name,
                    arguments
                )
                level = "baseline"

            else:
                level, result = call_tool(
                    name,
                    arguments,
                    context=step_context
                )

            logger.info(f"  рівень   : {level}")
            logger.info(f"  результат: {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

            if RUN_TAG == "checks":

                if level in MODEL_ERRORS:
                    has_model_error = True

                elif level == "tool":
                    has_tool_error = True

                elif level == "ok":
                    has_successful_call = True

                    # Зберігаємо лише підтверджену ціну
                    # після успішного laptop_info.
                    if name == "laptop_info":
                        verified_price = extract_verified_price(
                            result
                        )

                        if verified_price is not None:
                            pending_context["verified_price"] = (
                                verified_price
                            )

                            logger.info(
                                "  підтверджена ціна: "
                                f"{verified_price} грн"
                            )

        if RUN_TAG == "checks":
            context = pending_context

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

            elif has_tool_error:
                logger.warning(
                    "Помилка виконання інструмента. "
                    "Не враховується в MAX_RETRIES."
                )

            elif has_successful_call:
                retries = 0

    logger.info("СТОП: вичерпано ліміт кроків")
    return None


if __name__ == "__main__":
    task = "Потрібен ноутбук для навчання"

    with propagate_attributes(
        trace_name=f"lab3-{RUN_TAG}-real-agent",
        tags=["lab3", RUN_TAG]
    ):
        result = run_agent(task)

    get_client().flush()

    print("\n" + "=" * 60)
    print("РЕЖИМ:", RUN_TAG)
    print("РЕЗУЛЬТАТ:")
    print(result)
    print("=" * 60)
