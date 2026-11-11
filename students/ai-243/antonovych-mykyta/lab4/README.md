# ЛР4 — Контекст, стан і кеш агента

Антонович Микита, АІ-243 · Варіант №2 (кулінарія).

[Звіт](report.md) · [Довга задача та еталон](long_task.json) · [Методичка](../../../../docs/lab4/Agents-lab4.md).

Використано агента, корпус, довідник і правила валідації ЛР3. Пошук у довгій задачі повертає повні рецепти, щоб вимірювання відображало ріст контексту. Скрипти аналізу й експерименту адаптовано з прикладу викладача в `docs/lab4/python_example/`.

Запускайте команди з цього каталогу. Потрібні Python 3.12, `openai`, `pydantic`, `python-dotenv`, `langfuse>=4` і локальний Ollama.

```bash
ollama create qwen25-culinary-3k -f Modelfile
ollama show qwen25-culinary-3k --parameters
python make_task.py
python agent_runner.py
python measure.py all 1 probe
python analyze.py logs/probe_none_r1.log steps
python measure.py all 3 main
python measure.py none 1 cache1
python measure.py none 1 cache2
```

Для холодної серії `cache1` використайте робочу копію без попереднього каталогу `cache/`. У `cache2` залиште його. Повторні команди вимірювання перезаписують відповідні логи та CSV; збережіть попередні матеріали, якщо вони потрібні.

Локальні прогони: задайте `LANGFUSE_TRACING_ENABLED=false`. Для відтворення трас використовуйте окреме оточення `lab4` у Langfuse і локальний файл `.env` у цьому каталозі. Файли `.env` і каталоги середовища та кешу не додавайте в Git. Команда `python measure.py all 3 main` записує потрібні для звіту дерева `long-main_none_r1` та `long-main_trim+state_r1` у серії `main`.

Для початкової перевірки та порівняння з ЛР5 залишено `Modelfile_4k`. Звичайний прогін на 4096 токенах збережено як `logs/lab4_4k.log`.

Знімки серії `main` вже є у [звіті](report.md). Для повторного трасування використайте локальні змінні `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL` і `LANGFUSE_TRACING_ENVIRONMENT=lab4`. Виконуйте прогони з нової оболонки або задайте `LANGFUSE_TRACING_ENABLED=true`, якщо раніше вимкнули трасування у поточній оболонці.
