# Лабораторна робота № 5 — AI-243, варіант 7

**Студент:** Гладковський Іван Сергійович.  
**Тема:** RAG-агент: векторний пошук у документах як інструмент.  
**Предметна область:** Подорожі (вигаданий клуб «Південний Компас»).

## Що змінено від lab4

- Основа агента, його послідовний режим, система перевірок та старі функції `transport_info` і `calc_budget` збережені.
- Старий `search_routes` залишився у `tools.py`, але замість нього агенту дозволено `search_docs`.
- Додано 5 довгих документів до оригінальних 12 маршрутних анотацій і 10 питань (4+4+2).
- Додано векторний індекс FAISS, ембединги Ollama, оцінювання 6 нарізань і 3 описів інструмента.
- За методичкою застосовано `NUM_CTX=4096`. Модель — та сама родина `qwen2.5:3b`, але локальний тег `qwen25-4k` потрібно створити з доданого `Modelfile`. У lab4 кінцева конфігурація була `qwen25-3k`/3072; це **відмінність**, яку треба явно описати у звіті.
- Температуру 0.2 з lab4 збережено. Інструкцію агента збережено, окрім заміни назви застарілого `search_routes` на `search_docs` у послідовності викликів.
- У `logs/run_lab4.log` для порівняння лежить **реальний** файл із попереднього архіву `lab4/logs/main_none_r1.log`; він не є вигаданим результатом лаби 5.

## Windows PowerShell (з кореня `lab5`)

Вимоги: Python з підтримкою `faiss-cpu`, установлений Ollama, доступна модель `qwen2.5:3b` та вільне місце для `bge-m3`. Langfuse для трас потребує коректних ключів у локальному `.env` (не комітити).

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# У корені репозиторію, якщо встановлюєте спільний utils:
# python -m pip install -e .
ollama pull qwen2.5:3b
ollama create qwen25-4k -f Modelfile
ollama pull bge-m3
ollama list
python check_cases.py
python show_chunks.py data/docs/d01.txt fixed 200 0
python show_chunks.py data/docs/d01.txt fixed 500 100
python show_chunks.py data/docs/d01.txt paragraphs 800
python embed_check.py
python check_retrieval.py
python check_retrieval.py scores
```

**Після `check_retrieval.py scores`:** записати фактичне, обґрунтоване `MIN_SCORE` в `config.py`. За результатами таблиці нарізань можна змінити `CHUNK_METHOD`, `CHUNK_SIZE`, `CHUNK_OVERLAP` і `WITH_TITLE`, але зафіксувати ці параметри на всіх подальших вимірюваннях.

```powershell
python build_index.py
python try_tool.py D1
python try_tool.py N1
python ask.py D1
python measure_rag.py B 1
python measure_rag.py
python rag_report.py
python agent_runner.py
```

Ці команди створять власні файли `index/docs.faiss`, `index/chunks.json`, `index/meta.json`, `results/rag.csv`, а також логи. **Їх не можна заміняти показниками та індексом чужого варіанта з вхідного lab5.zip.** Результати й скріншоти Langfuse потрібно зняти на локальному комп'ютері. Якщо `check_retrieval.py scores` показав перекриття оцінок питання з відповіддю і без — не припускайте, що поріг досконалий; вибирайте компроміс.

В архіві вже є робоча структура коду й матеріали для тестів, але **немає фальсифікованих показників Ollama чи трас**. Звіт `report.md` містить місця для фактичних результатів.
