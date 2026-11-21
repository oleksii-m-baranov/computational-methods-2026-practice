"""Offline checks of Variant 7 data and helper logic (NO Ollama, NO Langfuse runs).

Usage: python verify_local.py
These checks are NOT model benchmarks and should not populate measured report tables.
"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import sys
import types

from tools import search_routes, find_route_price, calc_budget, transport_info
from make_task import ITEMS, QUESTION, MIN_CALLS, compute
from context import trim
from state import TaskState, shorten
from logparse import parse_log
from metrics import describe


def check(cond, message):
    if not cond:
        raise AssertionError(message)
    print('PASS:', message)


def main():
    total = 0
    for route, people in ITEMS:
        price = find_route_price(route)
        check(price is not None and price > 0, f'ціна маршруту {route}')
        check(route.lower() in search_routes(route).lower(), f'повний запис для {route}')
        check('Вартість проїзду:' in transport_info(route), f'довідник {route}')
        expected = round(price * people, 2)
        check(float(calc_budget(price, people, 0).split()[0]) == expected,
              f'обчислення {route}: {expected:g} грн')
        total += expected
    check(total == 8890.0 and compute() == 8890.0, 'загальний бюджет 8890 грн')
    check(len(ITEMS) == 6 and MIN_CALLS == 18 and all(x in QUESTION for x, _ in ITEMS),
          'шість позицій та мінімум 18 викликів')
    task = json.loads(Path('long_task.json').read_text(encoding='utf-8'))
    check(task['expected'] == '8890' and task['min_calls'] == 18, 'long_task.json')

    msg = [
        {'role': 'system', 'content': 'system'},
        {'role': 'user', 'content': 'task'},
        {'role': 'assistant', 'content': 'older'},
        {'role': 'tool', 'tool_call_id': 'old', 'content': 'older result'},
        {'role': 'assistant', 'tool_calls': [{'id':'new'}]},
        {'role': 'tool', 'tool_call_id':'new', 'content': 'new result'},
    ]
    shortened = trim(msg, 3)
    check(len(shortened) == 4 and shortened[2]['role'] == 'assistant',
          'trim прибирає початковий orphan tool')
    check(shorten('abcdef', 3) == 'abc...', 'state обмежує текст результату')
    with TemporaryDirectory() as tmp:
        orig = os.getcwd()
        try:
            os.chdir(tmp)
            state = TaskState('unit-test')
            state.record('calc_budget', '{"price_per_person":420,"people":3,"extra":0}', '1260.0 грн')
            check(len(state.results) == 1 and '1260.0 грн' in state.render(), 'стан зберігає результат')
            check(Path('state/unit-test.json').exists(), 'стан записаний у JSON')
        finally:
            os.chdir(orig)

    sample = '''2026-11-17 20:00:00 - INFO - ЗАДАЧА: приклад
2026-11-17 20:00:01 - INFO - \n--- крок 1 | помилок поспіль=0 | prompt_tokens=320 | completion_tokens=30
2026-11-17 20:00:01 - INFO -   виклик   : transport_info({"route":"Львів"})
2026-11-17 20:00:01 - INFO -   результат: Вартість проїзду: 500 грн
2026-11-17 20:00:02 - INFO - \n--- крок 2 | помилок поспіль=0 | prompt_tokens=500 | completion_tokens=10
2026-11-17 20:00:02 - INFO - ВІДПОВІДЬ: результат
'''
    runs = parse_log(sample)
    check(len(runs) == 1 and describe(runs[0])['status'] == 'final', 'парсер тестового лога')
    check(describe(runs[0])['prompt_tokens'] == 820, 'сума токенів у штучному тесті')
    print('\nЛокальні перевірки пройдено. Це НЕ запуск Ollama або Langfuse.')

if __name__ == '__main__':
    main()
