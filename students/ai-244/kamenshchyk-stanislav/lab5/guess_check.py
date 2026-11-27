"""Чи вгадує модель відповіді без документів (крок 2): три питання напряму, без інструментів.
Запуск: python guess_check.py"""
import json

from openai import OpenAI

import config

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
with open("rag_cases.json", encoding="utf-8") as f:
    cases = {c["id"]: c for c in json.load(f)}

for case_id in ["D1", "D3", "P2"]:
    case = cases[case_id]
    response = client.chat.completions.create(
        model=config.MODEL, temperature=0,
        messages=[{"role": "user", "content": case["question"]}])
    answer = response.choices[0].message.content.strip().replace("\n", " ")
    print(f"{case_id} | {case['question']}\n   правильно: {case['expected']} | модель: {answer}\n")
