
from langfuse import observe, get_client, propagate_attributes
from langfuse.openai import OpenAI

import config
from schemas import SCHEMAS
from dispatcher import call_tool, check_response
from lab_logger import custom_logger

client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY
)

logger = custom_logger(config.LAB_LOGFILE_NAME)

VALIDATION_ERRORS = {
    "name",
    "permission",
    "syntax",
    "schema",
    "meaning"
}


def required_tools(task):
    text = task.lower()

    if any(word in text for word in (
        "зарезерв", "резервув", "забронюв"
    )):
        return []

    if "8k" in text or "8к" in text:
        return ["search_laptops"]

    if any(word in text for word in (
        "розстроч", "щомісяч", "платіж"
    )):
        return [
            "search_laptops",
            "laptop_info",
            "calc_installment"
        ]

    if any(word in text for word in (
        "ціна", "ціну", "кошту", "склад", "наявн"
    )):
        return ["search_laptops", "laptop_info"]

    return ["search_laptops"]


@observe()
def run_agent(task):
    text = task.lower()

    if any(word in text for word in (
        "зарезерв", "резервув", "забронюв"
    )):
        logger.info("\n" + "=" * 60)
        logger.info(f"ЗАДАЧА: {task}")
        logger.warning(
            "ЗАБОРОНЕНО: резервування недоступне"
        )

        result = (
            "Вибачте, я не можу зарезервувати ноутбук, "
            "оскільки функція резервування недоступна."
        )

        logger.info(f"ВІДПОВІДЬ: {result}")
        return result

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
    completed_tools = set()
    required = required_tools(task)
    search_found = False

    logger.info("\n" + "=" * 60)
    logger.info(f"ЗАДАЧА: {task}")
    logger.info(
        f"НЕОБХІДНІ ІНСТРУМЕНТИ: {required}"
    )

    for step in range(1, config.MAX_STEPS + 1):
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=SCHEMAS,
            temperature=config.TEMPERATURE
        )

        choice = response.choices[0]
        msg = choice.message

        tokens = (
            response.usage.prompt_tokens
            if response.usage
            else "невідомо"
        )

        logger.info(
            f"\n--- крок {step} "
            f"| помилок поспіль={retries} "
            f"| prompt_tokens={tokens}"
        )

        status, explanation = check_response(response)

        if status != "ok":
            logger.warning(
                f"ПОМИЛКА ВІДПОВІДІ: "
                f"{status} | {explanation}"
            )

            retries += 1

            if retries > config.MAX_RETRIES:
                logger.error(
                    "СТОП: перевищено ліміт помилок моделі"
                )
                return None

            messages.append({
                "role": "assistant",
                "content": msg.content or ""
            })

            messages.append({
                "role": "user",
                "content": (
                    f"Попередня відповідь містить "
                    f"помилку {status}. "
                    f"{explanation or ''} "
                    "Виправ помилку та продовж "
                    "виконання завдання."
                )
            })

            continue

        if not msg.tool_calls:
            missing = [
                name for name in required
                if name not in completed_tools
            ]

            if (
                not search_found
                and "search_laptops" in completed_tools
            ):
                missing = []

            if missing:
                retries += 1

                logger.warning(
                    "НЕЗАВЕРШЕНЕ ЗАВДАННЯ: "
                    f"бракує {missing}"
                )

                if retries > config.MAX_RETRIES:
                    logger.error(
                        "СТОП: перевищено ліміт "
                        "повторних спроб"
                    )
                    return None

                messages.append({
                    "role": "assistant",
                    "content": msg.content or ""
                })

                messages.append({
                    "role": "user",
                    "content": (
                        f"Початкове завдання: {task}\n"
                        "Ти ще не виконав інструменти: "
                        f"{', '.join(missing)}. "
                        "Виклич необхідні інструменти. "
                        "Для search_laptops використовуй "
                        "короткий запит. "
                        "Для laptop_info використовуй "
                        "точну назву моделі. "
                        "Для calc_installment використовуй "
                        "ціну з laptop_info."
                    )
                })

                continue

            if (
                not msg.content
                or not msg.content.strip()
            ):
                retries += 1

                logger.warning(
                    "ПОМИЛКА: порожня відповідь, "
                    f"спроба {retries}"
                )

                if retries > config.MAX_RETRIES:
                    logger.error(
                        "СТОП: перевищено ліміт "
                        "порожніх відповідей"
                    )
                    return None

                messages.append({
                    "role": "assistant",
                    "content": ""
                })

                messages.append({
                    "role": "user",
                    "content": (
                        f"Початкове завдання: {task}\n"
                        "Попередня відповідь була "
                        "порожньою. Виконай потрібні "
                        "інструменти або дай змістовну "
                        "відповідь українською."
                    )
                })

                continue

            logger.info(
                f"ВІДПОВІДЬ: {msg.content}"
            )

            return msg.content

        messages.append(msg)

        model_failed = False
        tool_succeeded = False

        for call in msg.tool_calls:
            name = call.function.name
            arguments = call.function.arguments

            logger.info(
                f"  виклик   : "
                f"{name}({arguments})"
            )

            level, result = call_tool(
                name,
                arguments
            )

            logger.info(
                f"  рівень   : {level}"
            )

            logger.info(
                f"  результат: {result}"
            )

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result)
            })

            if level in VALIDATION_ERRORS:
                model_failed = True

                logger.warning(
                    f"ВАЛІДАЦІЯ: {level}. "
                    "Модель отримає повідомлення "
                    "для виправлення."
                )

            elif level == "ok":
                completed_tools.add(name)
                tool_succeeded = True

                if name == "search_laptops":
                    result_text = str(result).lower()

                    search_found = (
                        "нічого не знайдено"
                        not in result_text
                        and "порожній"
                        not in result_text
                    )

            elif level == "tool":
                messages.append({
                    "role": "system",
                    "content": (
                        f"Інструмент {name} "
                        f"не спрацював: {result}. "
                        "Не повторюй цей виклик "
                        "автоматично. "
                        "Поясни користувачу проблему."
                    )
                })

        if model_failed:
            retries += 1

            if retries > config.MAX_RETRIES:
                logger.error(
                    "СТОП: перевищено ліміт "
                    "помилок моделі"
                )
                return None

        elif tool_succeeded:
            retries = 0

    logger.info(
        "СТОП: вичерпано ліміт кроків"
    )

    return None


if __name__ == "__main__":
    with propagate_attributes(
        trace_name="recovery-test-2",
        tags=["recovery-test"]
    ):
        result = run_agent(
            "Перевір характеристики ноутбука "
            "UnknownLaptop999 через laptop_info. "
            "Якщо інструмент повідомить, що такої "
            "моделі немає, обов'язково виклич "
            "search_laptops із запитом 'навчання', "
            "вибери модель із результатів і "
            "повторно виклич laptop_info з її "
            "точною назвою. "
            "Не вигадуй характеристики."
        )

    get_client().flush()

    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ ТЕСТУ:")
    print(result)
    print("=" * 60)
