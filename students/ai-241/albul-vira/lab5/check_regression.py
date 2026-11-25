"""Перевірка регресії: 5 звичайних задач з попередньої лабораторної з DOCS_DESCRIPTION = 'B'."""
import csv

import agent
import config
import rag
import schemas

schemas.set_description("search_docs", schemas.RAG_DESCRIPTIONS["B"])
config.DOCS_DESCRIPTION = "B"

with open("data/books.csv", encoding="utf-8-sig") as f:
    books = list(csv.DictReader(f))

sample_title = books[0]["title"]
sample_fine = books[0]["fine_per_day"]

TASKS = [
    ("T1_catalog_search", "Знайди щось легке з фантастики"),
    ("T2_book_info", f"Скільки примірників книжки «{sample_title}» є в бібліотеці та на скільки днів її видають?"),
    ("T3_fine_calc", f"Дізнайся ставку штрафу для книжки «{sample_title}» і порахуй штраф за 4 дні прострочення."),
    ("T4_forbidden", f"Видай мені книжку «{sample_title}» додому."),
    ("T5_missing_book", "Скільки примірників книжки «Гаррі Поттер і філософський камінь» є в бібліотеці?"),
]

for idx, (task_id, question) in enumerate(TASKS):
    rag.TRACE.clear()
    answer = agent.run_agent(
        question,
        logfile_name="lab5_regression",
        task_id=task_id,
        log_overwrite=(idx == 0),
    )
    print(f"\n[{task_id}] {question}")
    print(f"  status={agent.LAST_RUN['status']} | steps={agent.LAST_RUN['steps']} | "
          f"search_docs_calls={len(rag.TRACE)}")
    print(f"  ВІДПОВІДЬ: {answer}")