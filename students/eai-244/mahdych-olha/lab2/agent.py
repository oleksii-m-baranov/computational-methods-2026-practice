"""Цикл агента; історія та сирі відповіді зберігаються для перевірки."""
from openai import OpenAI
import config
from schemas import SCHEMAS
from dispatcher import call_tool
from utils.lab_logger import custom_logger

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY,
                timeout=600.0, max_retries=0)
logger = custom_logger('lab2')


def run_agent(task, trace=None):
    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task},
    ]
    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")
    for step in range(1, config.MAX_STEPS + 1):
        response = client.chat.completions.create(
            model=config.MODEL, messages=messages, tools=SCHEMAS,
            temperature=config.TEMPERATURE,
        )
        msg = response.choices[0].message
        tokens = response.usage.prompt_tokens if response.usage else None
        event = {"step": step, "prompt_tokens": tokens,
                 "response": response.model_dump(mode="json"), "calls": []}
        if trace is not None:
            trace.append(event)
        logger.info(f"\n--- крок {step} | prompt_tokens={tokens}")
        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return msg.content
        messages.append(msg.model_dump(exclude_none=True))
        for call in msg.tool_calls:
            logger.info(f"  виклик   : {call.function.name}({call.function.arguments})")
            result = call_tool(call.function.name, call.function.arguments)
            logger.info(f"  результат: {result}")
            event["calls"].append({"name": call.function.name,
                                   "arguments": call.function.arguments,
                                   "result": result})
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": result})
    logger.info("СТОП: вичерпано ліміт кроків")
    return None
