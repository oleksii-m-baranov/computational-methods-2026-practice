"""Окремий експеримент з ЛР5: три питання моделі без документів та інструментів.

Запуск із папки lab5: python no_docs_probe.py
Потрібна запущена Ollama з моделлю config.MODEL.
Записує фактичні відповіді в results/no_docs_probe.txt та report.md.
НЕ викликає RAG, агента, пошукові інструменти, не читає corpus/docs.
"""
from pathlib import Path
import json
import re
from datetime import datetime

from openai import OpenAI
import config

ROOT = Path(__file__).resolve().parent
CASES = ROOT / "rag_cases.json"
REPORT = ROOT / "report.md"
OUTPUT = ROOT / "results" / "no_docs_probe.txt"

# Три заздалегідь зафіксовані питання з різних документів.
IDS = ("D1", "D2", "P2")
ANCHOR = "Окремого експерименту «модель без документів» із трьома питаннями у наданих результатах **не зафіксовано**; прогони без виклику пошуку в таблиці 6 не є його повною заміною."
NEW_HEADING = "### Окремий експеримент: модель без документів"


def numeric_occurrence(answer, expected):
    # Лише текстовий збіг, НЕ висновок про коректність міркувань моделі.
    return bool(re.search(rf"(?<!\d){re.escape(str(expected))}(?!\d)", answer))


def main():
    all_cases = {row["id"]: row for row in json.loads(CASES.read_text(encoding="utf-8"))}
    client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY, timeout=180.0)
    rows = []
    print(f"Модель без документів: {config.MODEL} | температура {config.TEMPERATURE}")
    for ident in IDS:
        case = all_cases[ident]
        print(f"\n[{ident}] {case['question']}", flush=True)
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=[{"role": "user", "content": case["question"]}],
            temperature=config.TEMPERATURE,
        )
        answer = (response.choices[0].message.content or "").strip()
        if not answer:
            answer = "(порожня відповідь)"
        row = {"id": ident, "question": case["question"], "expected": str(case["expected"]),
               "answer": answer, "contains_expected": numeric_occurrence(answer, case["expected"])}
        rows.append(row)
        print(f"Відповідь: {answer}", flush=True)

    OUTPUT.parent.mkdir(exist_ok=True)
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    content = [f"Дата запуску: {timestamp}", f"Модель: {config.MODEL}",
               f"Температура: {config.TEMPERATURE}",
               "Доступ до документів: НІ; інструменти: НІ; пошук: НІ", ""]
    for r in rows:
        content += [f"{r['id']}. {r['question']}", f"Очікуване значення з документа: {r['expected']}",
                    f"Фактична відповідь моделі: {r['answer']}",
                    f"Число {r['expected']} зустрілося у відповіді: {'так' if r['contains_expected'] else 'ні'}", ""]
    OUTPUT.write_text("\n".join(content), encoding="utf-8")

    def cell(text):
        return " ".join(text.split()).replace("|", "\\|")

    table = [NEW_HEADING, "",
             f"Модель `{config.MODEL}` (температура {config.TEMPERATURE}); дата локального запуску: {timestamp}. "
             "Моделі передано лише текст питання. Документи, контекст RAG, агент і функції пошуку не використовувалися.",
             "", "| ID | Запитання | Правильне значення з документа | Відповідь моделі без документів | Число вгадане? |",
             "|---|---|---:|---|---|" ]
    for r in rows:
        table.append(f"| {r['id']} | {cell(r['question'])} | {r['expected']} | {cell(r['answer'])} | "
                     f"{'Так (число присутнє)' if r['contains_expected'] else 'Ні'} |")
    guessed = sum(r['contains_expected'] for r in rows)
    table += ["", f"За буквальним збігом чисел: **{guessed}/3**. "
              "Значення є вигаданими даними навчальних документів, тому правильні числа модель не могла перевірити за джерелом. "
              "Автоматичний збіг числа не замінює ручного аналізу відповіді: якщо число згадане лише як припущення, це слід зазначити окремо.", ""]

    report = REPORT.read_text(encoding="utf-8")
    if NEW_HEADING in report:
        print(f"\nЗвіт уже містить підрозділ {NEW_HEADING}; автоматично не перезаписую його.")
    elif ANCHOR in report:
        report = report.replace(ANCHOR, "\n\n" + "\n".join(table), 1)
        report = report.replace("**Обмеження:** відсутній окремий зафіксований тест вгадування без документів і скріншот повністю розгорнутого дерева Langfuse;",
                                "**Обмеження:** відсутній скріншот повністю розгорнутого дерева Langfuse;", 1)
        REPORT.write_text(report, encoding="utf-8")
        print("\nПідрозділ з фактичними відповідями додано до report.md.")
    else:
        print("\nНе знайдено очікуваного тексту в report.md: додай дані вручну з results/no_docs_probe.txt.")
    print("Сирий результат:", OUTPUT)


if __name__ == "__main__":
    main()
