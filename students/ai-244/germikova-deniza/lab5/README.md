# ЛР5 — RAG-агент, варіант 2

Звіт: [report.md](report.md). Вимірювання виконано 25.11.2026; первинні логи та CSV збережено. `results/rag_manual_review.csv` — окремий ручний аналіз. Модель і корпус експериментів не змінювалися після їх виконання.

## Запуск

З каталогу `lab5` (Python 3.12, запущений Ollama):

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
ollama pull llama3.2:3b
ollama create llama32-4k -f Modelfile_4k
ollama pull bge-m3
```

Для Chroma: `python -m pip install -r requirements-extra.txt`. Точні версії середовища збережено у `results/environment_final.txt`. Спільний логер доступний у локальному `utils/`; у корені репозиторію курсу за методичкою також можна встановити пакет `pip install -e .`. Для Langfuse створити власний `.env` з LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY та адресою сервера. Не комітити `.env`.

```bash
python check_cases.py
python check_no_docs.py
python embed_check.py
python show_chunks.py data/docs/d01.txt fixed 200 0
python show_chunks.py data/docs/d01.txt fixed 500 100
python show_chunks.py data/docs/d01.txt paragraphs 800
python show_chunks.py data/docs/d04.txt fixed 200 0
python check_retrieval.py
python check_retrieval.py scores
python build_index.py
python try_tool.py D1
python try_tool.py N1
python ask.py D1
python rag_report.py
python chroma_test.py
```

`python measure_rag.py` повторно виконає 90 прогонів і **перезапише** відповідні CSV та логи. Запускайте лише після резервного копіювання. Для відтворення двох регресійних прогонів з обмеженням очікування, також після збереження копій:

```bash
python -u -c 'import model, agent_runner; model.client = model.client.with_options(timeout=90.0, max_retries=0); agent_runner.main()' --baseline
python -u -c 'import model, agent_runner; model.client = model.client.with_options(timeout=90.0, max_retries=0); agent_runner.main()'
```

`logs/run_lab4.log` — новий контрольний прогін старого пошуку; `logs/archived_run_lab3.log` — історичний файл з архіву ЛР4. Див. обмеження у звіті. `data/corpus/` — оригінальні 12 рецептів із ЛР4; під час фінального аудиту каталог перейменовано з `data/recipes/` без змін даних. Змінено тільки відповідні шляхи й метадані, перевірено повну рівність усіх 99 чанків і незмінність бінарного індексу. Індекс не містить кешу ембедингів; він відновлюється `build_index.py`.
