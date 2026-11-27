"""Крок 2: чи вгадує модель відповіді без документів (аналог «ollama run» з трьома питаннями).

Запуск: python guess_check.py            (питання D1, D2, P1)
        python guess_check.py D3 P2 P4   (будь-які id з rag_cases.json)
"""
import json
import sys

from openai import OpenAI

import config

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
ids = sys.argv[1:] or ["D1", "D2", "P1"]

with open("rag_cases.json", encoding="utf-8") as f:
    cases = {c["id"]: c for c in json.load(f)}

for case_id in ids:
    case = cases[case_id]
    response = client.chat.completions.create(
        model=config.MODEL, temperature=config.TEMPERATURE,
        messages=[{"role": "user", "content": case["question"]}])   # без документів і без інструментів
    answer = response.choices[0].message.content.strip().replace("\n", " ")
    guessed = case["expected"] is not None and case["expected"] in answer
    print(f"{case_id} | {case['question']}\n    правильна: {case['expected']} | модель: {answer[:300]}"
          f"\n    вгадала: {'ТАК - замініть значення' if guessed else 'ні'}\n")
