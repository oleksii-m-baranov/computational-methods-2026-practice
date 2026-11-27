"""Перевірка, чи вгадує модель відповіді без документів (крок 2 методички)."""
import json

from openai import OpenAI

import config

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
with open("rag_cases.json", encoding="utf-8") as f:
    cases = json.load(f)

for case in cases:
    if case["kind"] == "none":
        continue
    reply = client.chat.completions.create(
        model=config.MODEL, temperature=0,
        messages=[{"role": "user", "content": case["question"] + " Відповідай коротко, одним числом."}])
    answer = reply.choices[0].message.content.strip().replace("\n", " ")
    guessed = case["expected"] in answer
    print(f"{case['id']}: {case['question']}\n    модель: {answer}\n    очікується: {case['expected']} | вгадала: {'ТАК' if guessed else 'ні'}")
