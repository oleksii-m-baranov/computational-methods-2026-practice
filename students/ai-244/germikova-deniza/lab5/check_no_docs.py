"""Перевірка трьох питань напряму, без документів і без інструментів."""
import json
from openai import OpenAI
import config
client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
cases = json.load(open("rag_cases.json", encoding="utf-8"))
for case in [c for c in cases if c["id"] in {"D1", "D3", "P3"}]:
    reply = client.chat.completions.create(model=config.MODEL, temperature=config.TEMPERATURE,
        messages=[{"role":"user","content":case["question"]}])
    print(f'{case["id"]}: {case["question"]} | expected={case["expected"]}')
    print("Відповідь без документів:", reply.choices[0].message.content, "\n")
