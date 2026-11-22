"""Діагностика порожніх відповідей: що саме згенерувала модель на питання D1 з описом B.
Запуск: python diag.py   (результат - у logs/diag.txt)"""
import json
import sys
import urllib.request

import config
import schemas
from model import client

sys.stdout = open("logs/diag.txt", "w", encoding="utf-8")   # пишемо одразу у файл (UTF-8)

schemas.set_description("search_docs", schemas.RAG_DESCRIPTIONS["B"])
question = "Кожні скільки кілометрів пробігу виконується ТО-1?"
messages = [{"role": "system", "content": config.SYSTEM}, {"role": "user", "content": question}]


def post(path, body):
    req = urllib.request.Request("http://localhost:11434" + path, data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read().decode("utf-8"))


print("=== 1. OpenAI-сумісний API (як в агенті)")
r = client.chat.completions.create(model=config.MODEL, messages=messages, tools=schemas.SCHEMAS,
                                   temperature=0, max_tokens=config.MAX_TOKENS)
print(json.dumps(r.choices[0].model_dump(), ensure_ascii=False, indent=1))

print("\n=== 2. Рідний API Ollama /api/chat")
r = post("/api/chat", {"model": config.MODEL, "messages": messages, "tools": schemas.SCHEMAS, "stream": False,
                       "options": {"temperature": 0, "num_predict": config.MAX_TOKENS}})
print(json.dumps(r.get("message"), ensure_ascii=False, indent=1), "| done_reason:", r.get("done_reason"))

print("\n=== 3. Сирий текст моделі (той самий запит, але без розбору викликів)")
# промпт у форматі шаблону qwen2.5 (так його будує Ollama)
tools_text = "\n".join(json.dumps(t, ensure_ascii=False) for t in schemas.SCHEMAS)
prompt = ("<|im_start|>system\n" + config.SYSTEM + "\n\n# Tools\n\nYou may call one or more functions to assist with the user query.\n\n"
          "You are provided with function signatures within <tools></tools> XML tags:\n<tools>\n" + tools_text +
          "\n</tools>\n\nFor each function call, return a json object with function name and arguments within "
          "<tool_call></tool_call> XML tags:\n<tool_call>\n{\"name\": <function-name>, \"arguments\": <args-json-object>}\n"
          "</tool_call><|im_end|>\n<|im_start|>user\n" + question + "<|im_end|>\n<|im_start|>assistant\n")
r = post("/api/generate", {"model": config.MODEL, "prompt": prompt, "raw": True, "stream": False,
                           "options": {"temperature": 0, "num_predict": config.MAX_TOKENS}})
print(repr(r.get("response")))
