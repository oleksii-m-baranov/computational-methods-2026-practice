"""Тести перевірки аргументів та диспетчера."""
from pathlib import Path
from dispatcher import call_tool, check_response
from schemas import SCHEMAS
from types import SimpleNamespace

CASES = [
    ("Зламаний JSON", "search_articles", '{"query": "дряпає"', "syntax"),
    ("Неправильний тип", "calc_food", '{"weight_kg": "п\'ять", "grams_per_kg": 25, "days": 30}', "schema"),
    ("Відсутнє обов'язкове поле", "calc_food", '{"weight_kg": 5, "days": 30}', "schema"),
    ("Вигадане поле", "search_articles", '{"query":"дряпає", "text":"зайве"}', "schema"),
    ("Неіснуючий інструмент", "delete_all", '{}', "name"),
    ("Заборонена дія", "book_vet", '{"date":"п’ятниця"}', "permission"),
    ("Значення немає в довіднику", "vaccine_info", '{"vaccine":"невідоме"}', "meaning"),
    ("Значення поза межами", "calc_food", '{"weight_kg": 0, "grams_per_kg": 25, "days": 30}', "schema"),
    ("Порожній зміст запиту", "search_articles", '{"query": "   "}', "meaning"),
    ("Правильний виклик", "calc_food", '{"weight_kg": 5, "grams_per_kg": 25, "days": 30}', "ok"),
]


def main():
    rows = []
    for label, name, raw, expected in CASES:
        level, text = call_tool(name, raw)
        assert level == expected, f"{label}: очікувалося {expected}, отримано {level}"
        assert isinstance(text, str) and text.strip(), label
        if label == 'Правильний виклик':
            assert text == '3750 г', text
        print(f"OK {label:30} → {level}")
        message = text.replace('|', r'\|').replace('\n', ' / ')
        call = f'{name}({raw})'.replace('|', r'\|')
        rows.append(f'| {label} | `{call}` | `{level}` | {message} |')

    sch = SCHEMAS[0]['function']['parameters']
    assert sch['additionalProperties'] is False and 'query' in sch['required']
    invalid = SimpleNamespace(finish_reason='stop', message=SimpleNamespace(tool_calls=None, content='<tool_call>{}</tool_call>'))
    length = SimpleNamespace(finish_reason='length', message=SimpleNamespace(tool_calls=None, content=None))
    assert check_response(invalid)[0] == 'syntax'
    assert check_response(length) == ('length', None)
    content = '\n'.join([
        '# Таблиця 2 — тести ланцюжка перевірок',
        '',
        '| Що перевіряємо | Виклик | Рівень | Повідомлення для моделі |',
        '|---|---|---|---|',
        *rows,
        '',
        'Офлайн-перевірка. Це не результати прогону Ollama або Langfuse.',
    ]) + '\n'
    (Path(__file__).resolve().parent / 'checks_results.md').write_text(content, encoding='utf-8')
    print('Перевірено 10 випадків + check_response + схему. Записано checks_results.md')


if __name__ == '__main__':
    main()
