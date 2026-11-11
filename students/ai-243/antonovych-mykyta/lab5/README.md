# ЛР5 — RAG-агент: пошук по документах як інструмент

Антонович Микита, АІ-243 · Варіант №2 (кулінарія).

[Звіт](report.md) · [Документи майстерні](data/docs) · [Десять питань](rag_cases.json) · [Методичка](../../../../docs/lab5/Agents-lab5.md).

Робота використовує кулінарного агента та п’ять звичайних задач із ЛР4. Векторний пошук охоплює старі рецепти й п’ять нових вигаданих регламентів майстерні «Тепла миска». Реалізація FAISS та інструменти вимірювання адаптовані з `docs/lab5/python_example/`.

Запускайте команди з цього каталогу. Потрібні Python 3.12, `openai`, `pydantic`, `python-dotenv`, `langfuse>=4`, `numpy`, `faiss-cpu`, локальний Ollama, `qwen25-culinary-4k` з ЛР4 та `bge-m3`.

```bash
ollama create qwen25-culinary-4k -f Modelfile
ollama list
python check_cases.py
python check_no_docs.py
python embed_check.py
python show_chunks.py data/docs/d01.txt fixed 200
python show_chunks.py data/docs/d01.txt paragraphs 800
python check_retrieval.py
python check_retrieval.py scores
python build_index.py
python try_tool.py D1
python try_tool.py N1
python measure_rag.py all 3
python rag_report.py
python agent_runner.py
```

Звичайний прогін записується в `logs/lab5.log`; під час перевірки його збережено як `logs/run_rag.log`. Серія `measure_rag.py` має власні логи й CSV. Кеш ембедингів можна відновити, його немає в поданні. Кеш відповідей чат-моделі вимкнено. Ліміт генерації в RAG-вимірюванні — 192 токени на звернення. Для звичайних задач `agent_runner.py` лишає ті самі параметри генерації, що й ЛР4; використовуйте модель, створену командою вище.

Локальні прогони: задайте `LANGFUSE_TRACING_ENABLED=false`. Для трас використовуйте окреме оточення `lab5` у Langfuse та локальний `.env` у цьому каталозі. Для звіту потрібні дерева одного питання з викликом `search_docs` в обох серіях; у локальних логах такою парою є P2. Не додавайте ключі та середовища в Git.

Щоб записати тільки потрібні вимірювання з мітками `rag-B` і `rag-C`, виконайте `python measure_rag.py B 1 --case P2` і `python measure_rag.py C 1 --case P2`. Команди оновлюють тільки два рядки CSV і створюють окремі журнали вибраних задач.

Знімки вимірювань вже є у [звіті](report.md). Для повторного трасування використайте локальні змінні `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL` і `LANGFUSE_TRACING_ENVIRONMENT=lab5`. Виконуйте прогони з нової оболонки або задайте `LANGFUSE_TRACING_ENABLED=true`, якщо раніше вимкнули трасування у поточній оболонці.
