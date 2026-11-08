# Лабораторна робота № 5. RAG-агент: пошук по документах як інструмент

## Мета

Замінити примітивний пошук підрядком з лабораторної роботи № 2 векторним. 
Під'єднати його до агента як звичайний інструмент.
Перевірити якість пошуку окремо від агента.
Побачити, як розмір чанка та опис інструмента впливають на поведінку агента, і виміряти це кількома повторами.

## Що треба зробити

У лабораторній роботі № 2 агент шукав по корпусу збігом слів. Це працює, поки запит містить ті самі слова, що й документ. У цій роботі ви:

1. доповнюєте корпус довгими документами й складаєте питання, відповіді на які є лише в них;
2. пишете нарізання документів на чанки, обчислення ембедингів і індекс на FAISS;
3. перевіряєте пошук **без агента**: частка питань, для яких потрібний фрагмент потрапив у top-k, при шести способах нарізання;
4. підбираєте поріг схожості, щоб на питання без відповіді пошук казав «нічого не знайдено»;
5. підключаєте пошук до агента інструментом `search_docs` і перевіряєте його через диспетчер;
6. вимірюєте агента з трьома різними описами цього інструмента, по три повтори кожен;
7. розбираєте за логами й трасами, **де саме** ламається відповідь: агент не шукав, пошук не знайшов, чи знайдене не використано.

## Що потрібно мати перед початком

Виконану лабораторну роботу № 4 з усіма файлами: `agent.py`, `agent_runner.py`, `arguments.py`, `cache.py`, `checks.py`, `compress.py`, `config.py`, `context.py`, `dispatcher.py`, `model.py`, `schemas.py`, `state.py`, `summary.py`, `tasks.json`, `tools.py`, каталог `data/` (з `data/corpus/` і довідником) і лог прогону `logs/lab4.log`. Потрібні запущений Ollama, акаунт Langfuse і модель `llama32-4k` з лабораторної роботи № 4.

Дані (корпус і довідник), інструменти, п'ять задач з `tasks.json`, температура, системне повідомлення і розмір вікна (4096) **не змінюються**. Змінюється пошук по корпусу та з'являються нові документи.

Роботу виконують на **локальній моделі**, тій самій, що в лабораторній роботі № 4. Скорочення історії, стан і кеш викликів з минулої роботи тут не потрібні: задачі короткі, у вікно вміщуються. Їх вимкнено в налаштуваннях (крок 1).

Нові терміни (ембединг, чанк, індекс, top-k, hit rate) пояснено в лекції 9, а чому агент іноді не звертається до пошуку - у лекції 10. Нижче вони нагадуються там, де використовуються.

### Правила вимірювань

Діють ті самі правила, що в лабораторній роботі № 4:

- питання й правильні відповіді фіксують **до** першого прогону й після перегляду результатів не змінюють;
- кожну конфігурацію агента проганяють **тричі**, у таблицях наводять **медіану** (середнє з трьох значень після відкидання найменшого й найбільшого) або кількість із трьох;
- змінюють лише одну річ за раз: між двома конфігураціями відрізняється один параметр;
- вибірка мала (десять питань, три повтори), тому висновки формулюють обережно: «у цьому прогоні…», а не «завжди…».

Нове правило: **пошук вимірюють окремо від агента**. Якщо дивитися лише на кінцеву відповідь, не розрізнити три причини помилки: агент не звернувся до пошуку, пошук не знайшов потрібне, або знайдене модель проігнорувала. Тому спершу (крок 5) міряють сам пошук, а потім (кроки 7–8) агента.

## Хід роботи

### Крок 1. Підготовка проєкту

1. Створіть каталог `lab5` і скопіюйте в нього весь вміст каталогу `lab4`, крім `venv/`, `cache/`, `state/`, `results/` і `logs/`. Створіть порожні каталоги `logs/` і `results/`.
2. Скопіюйте `lab4/logs/lab4.log` у `lab5/logs/` і перейменуйте в `run_lab4.log`: це база для порівняння в кроці 9.
3. Створіть у `lab5` нове віртуальне середовище й установіть бібліотеки:

   ```
   pip install openai pydantic python-dotenv "langfuse>=4" numpy faiss-cpu
   ```

   Потім установіть спільний пакет `utils` з логером `custom_logger`: з активованим середовищем перейдіть у **корінь репозиторію** й виконайте

   ```
   pip install -e .
   ```

   Після цього `from utils.lab_logger import custom_logger` працює з будь-якого каталогу, і скрипти можна запускати прямо з каталогу `lab5`. Для середовища, створеного через `uv`: `uv pip install -e .`

4. Завантажте модель ембедингів. Це окрема невелика модель, яка не розмовляє, а перетворює текст на список чисел (лекція 9, п. 9.5). Вона займає близько 1,2 ГБ:

   ```
   ollama pull bge-m3
   ```

   Якщо місця на диску мало, можна взяти `qwen3-embedding:0.6b` (близько 640 МБ): тоді впишіть її назву в `EMBED_MODEL` нижче і вкажіть це у звіті.

5. Додайте у `.gitignore` рядки `index/embeddings_cache.json` і `chroma_db/`: кеш ембедингів великий, у репозиторій він не потрапляє (сам індекс здається разом з роботою).
6. У `config.py` замініть рядок, що починається з `LAB_LOGFILE_NAME =`, на:

   ```python
   LAB_LOGFILE_NAME = "lab5"   # ім'я лога для agent.py і agent_runner.py: logs/lab5.log
   ```

   Додайте в кінець `config.py` нові параметри й переконайтеся, що скорочення, стан і кеш вимкнено:

   ```python
   COMPRESS = "none"           # скорочення історії вимкнено (лабораторна № 4)
   USE_STATE = False
   USE_CACHE = False

   EMBED_MODEL = "bge-m3"                   # модель ембедингів
   DOC_DIRS = ["data/corpus", "data/docs"]  # де лежать документи
   INDEX_DIR = "index"                      # куди зберігається індекс
   CHUNK_METHOD = "paragraphs"              # "fixed" (за кількістю символів) або "paragraphs" (за абзацами)
   CHUNK_SIZE = 800                         # розмір чанка в символах
   CHUNK_OVERLAP = 0                        # перекриття чанків (для "fixed")
   WITH_TITLE = False                       # дописувати назву документа до кожного чанка
   TOP_K = 3                                # скільки чанків повертає пошук
   MIN_SCORE = 0.0                          # поріг схожості: у кроці 5 ви підберете значення
   DOCS_DESCRIPTION = "B"                   # який опис search_docs використовувати: "A", "B" або "C"
   ```

   Значення `CHUNK_*` і `MIN_SCORE` тимчасові, їх ви виберете в кроці 5. Адреса Ollama в `BASE_URL` і `API_KEY` лишаються з попередніх робіт: ембединги йдуть на той самий сервер.

### Крок 2. Документи і питання

**Навіщо нові документи.** Корпус з лабораторної роботи № 2 складається з коротких анотацій по 2–3 речення, тобто 200–400 символів. Кожна анотація сама має розмір одного чанка, тож експерименти з розміром чанка на ній безглузді: різати нічого. Крім того, увесь такий корпус вміщується у вікно моделі, і пошук не потрібен. Тому ви додаєте до корпусу **п'ять довгих документів**, а старий корпус лишається як є і індексується разом з ними.

#### Генерація документів

Відкрийте чат-бот і надішліть запит такого вигляду. Тематику п'яти документів візьміть зі свого рядка табл. 8:

```
Згенеруй 5 навчальних документів для вигаданої організації в області
«Бібліотека». Усі дані вигадані.

Теми документів:
1. Правила користування бібліотекою; 
2. читальна зала й електронні ресурси; 
3. міжбібліотечний абонемент;
4. формування й списання фонду;
5. гуртки та заходи при бібліотеці

Вимоги до кожного документа:
- перший рядок - назва документа, далі порожній рядок;
- 7-9 абзаців, між абзацами порожній рядок, кожен абзац 2-4 речення;
- обсяг 3000-4000 символів;
- не менше 6 конкретних вигаданих значень (терміни, суми, ліміти, кількості),
  записаних ЦИФРАМИ ("7", а не "сім");
- значення мають бути нетиповими (не "30 днів" і не "100 грн"), щоб їх
  не можна було вгадати з загальних знань;
- одне й те саме значення не повторюється в різних документах;
- без таблиць, списків і markdown-розмітки: лише суцільний текст з абзаців.

Видай кожен документ окремим блоком: "Документ 1", "Документ 2" тощо.
```

Збережіть кожен документ в окремий файл `.txt` у каталозі `data/docs/` (`d01.txt` ... `d05.txt`), кодування UTF-8. Приберіть зайве: службові слова чат-бота, розмітку, нумерацію абзаців. **Перший рядок файла має бути назвою документа**: за нею пошук потім підписуватиме чанки.

Приклад початку файла `data/docs/d01.txt` для варіанта 1:

```
Правила користування бібліотекою

Читачем бібліотеки може стати кожен, хто досяг шістнадцяти років і пред'явив паспорт. Читацький квиток видається безкоштовно в день звернення і діє два роки з дня видачі.

Книжки з відкритого фонду видаються на 21 день. Підручники з абонемента видаються на 9 днів, оскільки їх бракує на всіх. Одночасно читач може тримати не більше 7 видань.
```

#### Питання

Складіть **десять** питань за своїми документами і збережіть у файлі `rag_cases.json`:

- **чотири прямих** (`direct`): питання використовує ті самі ключові слова, що й речення з відповіддю;
- **чотири перефразованих** (`paraphrase`): питання описує те саме іншими словами, і в ньому немає ключових слів із речення з відповіддю. Наприклад, у документі «штраф 4 грн за кожен день», а питання: «Скільки доведеться доплатити за кожен день, якщо книжку не повернули вчасно?». Саме на таких питаннях пошук підрядком мовчить, а векторний працює;
- **два без відповіді** (`none`): питання на тему документів, відповіді на які в документах **немає**. Наприклад, у документах немає ціни річного квитка, а питання про неї є. Переконайтеся, що ключових слів питання справді немає в текстах.

Відповідь на кожне питання з відповіддю має бути **одним числом або одним словом**, записаним цифрами, і міститися в документах лише в одному місці. Формат запису:

```json
[
  {"id": "D1", "kind": "direct",     "question": "На скільки днів видаються підручники з абонемента?",
   "must_contain": "видаються на 9 днів", "expected": "9"},
  {"id": "P1", "kind": "paraphrase", "question": "Скільки доведеться доплатити за кожен день, якщо книжку не повернули вчасно?",
   "must_contain": "штраф 4 грн", "expected": "4"},
  {"id": "N1", "kind": "none",       "question": "Скільки коштує річний читацький квиток?",
   "must_contain": null, "expected": null}
]
```

- `must_contain` - **дослівна** фраза з документа (3–6 слів разом з числом), яка зустрічається в усіх документах **рівно один раз**. За нею скрипти визначають, чи потрапив потрібний фрагмент у результат пошуку;
- `expected` - значення, яке має бути у відповіді агента (з крапкою як десятковим роздільником). Воно має міститися в `must_contain`;
- для питань без відповіді обидва поля - `null`.

Правильні відповіді фіксуються **до** першого прогону й далі не змінюються.

#### Перевірка

Скрипт `check_cases.py` перевіряє файл питань і обсяг документів:

```python
"""Перевірка файла rag_cases.json: кожен факт має бути в документах рівно в одному місці."""
import collections
import json
import re
import sys

import chunking
import config


def norm(text):
    return re.sub(r"\s+", " ", text).strip()


with open("rag_cases.json", encoding="utf-8") as f:
    cases = json.load(f)

docs = chunking.load_documents(config.DOC_DIRS)
whole = " ".join(norm(d["text"]) for d in docs)
problems = []

ids = [c["id"] for c in cases]
if len(ids) != len(set(ids)):
    problems.append("Повторюються id питань")
kinds = collections.Counter(c["kind"] for c in cases)
for kind, need in [("direct", 4), ("paraphrase", 4), ("none", 2)]:
    if kinds[kind] != need:
        problems.append(f"Питань виду {kind}: {kinds[kind]}, а треба {need}")

for case in cases:
    if case["kind"] == "none":
        if case["must_contain"] is not None or case["expected"] is not None:
            problems.append(f"{case['id']}: у питання без відповіді must_contain і expected мають бути null")
        continue
    found = whole.count(norm(case["must_contain"]))
    if found != 1:
        problems.append(f"{case['id']}: фраза '{case['must_contain']}' зустрічається в документах {found} раз(ів), а треба рівно 1")
    if case["expected"] not in case["must_contain"]:
        problems.append(f"{case['id']}: expected '{case['expected']}' не міститься у must_contain")

total_chars = sum(len(d["text"]) for d in docs)
tokens = total_chars / 2.5
print(f"Документів: {len(docs)}; символів: {total_chars}; приблизно токенів: {tokens:.0f} (вікно {config.NUM_CTX})")
if tokens < config.NUM_CTX:
    problems.append("Усі документи вміщуються у вікно моделі: додайте текст, інакше пошук не потрібен")
print(f"Питань: {len(cases)} ({dict(kinds)})")
if problems:
    print("\nПроблеми:")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("Усе гаразд")
```

```
python check_cases.py
```

Він має вивести «Усе гаразд». Особливо важлива перевірка обсягу: якщо всі документи разом вміщуються у вікно (приблизно 2,5 символа на токен), додайте текст, інакше пошук не потрібен і вся робота безглузда.

Ще одна перевірка вручну. Переконайтеся, що відповіді **не можна вгадати**: поставте три питання моделі напряму, без документів (`ollama run llama32-4k` і введіть питання). Якщо модель відповіла правильно, значення занадто типове: замініть його в документі й у питанні. Результат перевірки (питання - відповідь моделі) наведіть у звіті.

### Крок 3. Нарізання на чанки

**Чанк** - фрагмент документа, який індексується й повертається як одиниця пошуку (лекція 9, п. 9.8). Створіть файл `chunking.py`:

```python
"""Нарізання документів на чанки."""
import glob
import os
import re


def split_fixed(text, size, overlap=0):
    """Ріже текст на шматки по size символів; наступний шматок починається на overlap символів раніше."""
    if overlap >= size:
        raise ValueError("overlap має бути меншим за size")
    step = size - overlap
    return [text[i:i + size] for i in range(0, len(text), step) if text[i:i + size].strip()]


def split_paragraphs(text, size):
    """Ріже за порожніми рядками (абзацами); сусідні абзаци склеює, поки вони вміщуються в size."""
    parts = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, current = [], ""
    for p in parts:
        if current and len(current) + 2 + len(p) > size:
            chunks.append(current)
            current = p
        else:
            current = (current + "\n\n" + p) if current else p
    if current:
        chunks.append(current)
    return chunks


def load_documents(dirs):
    """Читає всі .txt з каталогів. Перший рядок файла - назва документа."""
    docs = []
    for directory in dirs:
        for path in sorted(glob.glob(os.path.join(directory, "*.txt"))):
            with open(path, encoding="utf-8") as f:
                text = f.read().strip()
            docs.append({"source": os.path.basename(path), "title": text.split("\n", 1)[0].strip(), "text": text})
    return docs


def make_chunks(docs, method, size, overlap=0, with_title=False):
    """Повертає список чанків: {"source": файл, "chunk": номер, "text": текст}."""
    chunks = []
    for doc in docs:
        if method == "fixed":
            parts = split_fixed(doc["text"], size, overlap)
        elif method == "paragraphs":
            parts = split_paragraphs(doc["text"], size)
        else:
            raise ValueError(f"Невідомий спосіб нарізання: {method}")
        for number, part in enumerate(parts):
            if with_title and not part.startswith(doc["title"]):
                part = doc["title"] + "\n" + part          # заголовок документа в кожному чанку (лекція 9)
            chunks.append({"source": doc["source"], "chunk": number, "text": part})
    return chunks
```

Функції `split_fixed` і `split_paragraphs` ріжуть текст двома способами, `load_documents` читає всі `.txt` з каталогів, а `make_chunks` повертає чанки з іменем файла й номером. Параметр `with_title` дописує назву документа до чанків, що з неї не починаються (так чанк «пам'ятає», звідки він).

Подивіться на нарізання одного документа. Скрипт `show_chunks.py` показує чанки й позначає ті, що закінчуються посеред речення:

```python
"""Показує, як документ нарізається на чанки.
Запуск: python show_chunks.py data/docs/d01.txt fixed 200 0
        python show_chunks.py data/docs/d01.txt paragraphs 800"""
import sys

import chunking

path, method, size = sys.argv[1], sys.argv[2], int(sys.argv[3])
overlap = int(sys.argv[4]) if len(sys.argv) > 4 else 0

with open(path, encoding="utf-8") as f:
    text = f.read().strip()
parts = chunking.split_fixed(text, size, overlap) if method == "fixed" else chunking.split_paragraphs(text, size)

cut = 0
for number, part in enumerate(parts, 1):
    ends_ok = part.rstrip().endswith((".", "!", "?", "…", ":"))
    cut += 0 if ends_ok else 1
    print(f"--- чанк {number}, {len(part)} символів" + ("" if ends_ok else "  [закінчується посеред речення]"))
    print(part)
print(f"\nУсього чанків: {len(parts)}; закінчуються посеред речення: {cut}")
```

Проженіть його на одному зі своїх документів трьома способами:

```
python show_chunks.py data/docs/d01.txt fixed 200 0
python show_chunks.py data/docs/d01.txt fixed 500 100
python show_chunks.py data/docs/d01.txt paragraphs 800
```

Заповніть табл. 1 і знайдіть у виводі чанк, у якому **факт розрізано** між двома чанками (число відокремлено від того, до чого воно належить).

Таблиця 1 - Нарізання одного документа

| Спосіб                       | Чанків | Закінчуються посеред речення | Довжина найбільшого, символів |
|------------------------------|--------|------------------------------|-------------------------------|
| `fixed`, 200, перекриття 0   |        |                              |                               |
| `fixed`, 500, перекриття 100 |        |                              |                               |
| `paragraphs`, 800            |        |                              |                               |

### Крок 4. Ембединги й індекс

**Ембединг** - список чисел фіксованої довжини, у який модель ембедингів перетворює текст так, що тексти зі схожим змістом дістають близькі списки (лекція 9, п. 9.5). **Індекс** - структура, що зберігає ці списки й за запитом знаходить найближчі (п. 9.7). Тут індекс будує FAISS, а ваш код відповідає за все навколо нього (лекція 9, табл. 9.4).

Створіть три файли. 
`embedder.py` - перший обчислює ембединги через Ollama і кешує їх на диску: один і той самий текст не рахується вдруге. Це інший кеш, ніж кеш викликів моделі з лабораторної № 4: тут зберігаються вектори чанків, а не відповіді моделі.

```python
"""Ембединги через Ollama з кешем на диску (однаковий текст не рахується вдруге)."""
import hashlib
import json
import os

from openai import OpenAI

import config

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
CACHE_PATH = os.path.join(config.INDEX_DIR, "embeddings_cache.json")
_cache = None


def _load_cache():
    global _cache
    if _cache is None:
        _cache = {}
        if os.path.exists(CACHE_PATH):
            with open(CACHE_PATH, encoding="utf-8") as f:
                _cache = json.load(f)
    return _cache


def _key(text):
    return hashlib.sha256((config.EMBED_MODEL + "\n" + text).encode("utf-8")).hexdigest()


def embed(texts, batch=16):
    """Повертає список векторів, по одному на кожен текст."""
    cache = _load_cache()
    missing = [t for t in dict.fromkeys(texts) if _key(t) not in cache]   # унікальні, яких ще немає
    for start in range(0, len(missing), batch):
        part = missing[start:start + batch]
        response = client.embeddings.create(model=config.EMBED_MODEL, input=part)
        for text, item in zip(part, sorted(response.data, key=lambda d: d.index)):
            cache[_key(text)] = item.embedding
    if missing:
        os.makedirs(config.INDEX_DIR, exist_ok=True)
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    return [cache[_key(t)] for t in texts]
```

`rag.py` - другий містить клас індексу. Зверніть увагу на три місця, що відповідають пасткам з лекції 9: вектори **нормалізуються** (тоді скалярний добуток дорівнює косинусній схожості); номер `-1`, який FAISS повертає, коли чанків менше за k, **відкидається** (інакше `chunks[-1]` мовчки поверне останній чанк); разом з індексом зберігаються **параметри**, з якими він збудований, і при розбіжності з `config.py` завантаження зупиняється з поясненням (індекс, збудований однією моделлю чи нарізанням, не можна використовувати з іншими).

```python
"""Векторний індекс на FAISS: побудова, збереження, завантаження, пошук."""
import json
import os

import faiss
import numpy as np

import chunking
import config
import embedder

TRACE = []        # записи про виклики пошуку; їх читає measure_rag.py
_index = None     # поточний індекс, який використовує інструмент search_docs


def settings():
    """Параметри, від яких залежить індекс. Зберігаються разом з ним."""
    return {"embed_model": config.EMBED_MODEL, "method": config.CHUNK_METHOD,
            "size": config.CHUNK_SIZE, "overlap": config.CHUNK_OVERLAP,
            "with_title": config.WITH_TITLE, "dirs": config.DOC_DIRS}


class Index:
    def __init__(self, chunks, vectors, meta=None):
        self.chunks = chunks
        self.meta = meta or {}
        matrix = np.array(vectors, dtype="float32")
        faiss.normalize_L2(matrix)                      # довжина кожного вектора стає 1
        self.faiss = faiss.IndexFlatIP(matrix.shape[1])  # IP = скалярний добуток = косинус для нормалізованих
        self.faiss.add(matrix)

    @classmethod
    def build(cls, chunks):
        vectors = embedder.embed([c["text"] for c in chunks])
        return cls(chunks, vectors, settings())

    def search(self, query, k=3):
        """Повертає до k найближчих чанків: [{"score", "source", "chunk", "text"}], від найближчого."""
        q = np.array(embedder.embed([query]), dtype="float32")
        faiss.normalize_L2(q)
        scores, ids = self.faiss.search(q, k)
        result = []
        for score, i in zip(scores[0], ids[0]):
            if i == -1:                                  # чанків менше за k: FAISS заповнює -1
                continue
            result.append({"score": float(score), **self.chunks[i]})
        return result

    def save(self, directory=None):
        directory = directory or config.INDEX_DIR
        os.makedirs(directory, exist_ok=True)
        faiss.write_index(self.faiss, os.path.join(directory, "docs.faiss"))
        with open(os.path.join(directory, "chunks.json"), "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=1)
        with open(os.path.join(directory, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=1)

    @classmethod
    def load(cls, directory=None):
        directory = directory or config.INDEX_DIR
        with open(os.path.join(directory, "meta.json"), encoding="utf-8") as f:
            meta = json.load(f)
        if meta != settings():
            raise RuntimeError("Індекс збудовано з іншими параметрами, ніж у config.py. "
                               f"В індексі: {meta}. У config.py: {settings()}. Перебудуйте: python build_index.py")
        obj = cls.__new__(cls)
        obj.faiss = faiss.read_index(os.path.join(directory, "docs.faiss"))
        with open(os.path.join(directory, "chunks.json"), encoding="utf-8") as f:
            obj.chunks = json.load(f)
        obj.meta = meta
        return obj


def build_from_config():
    docs = chunking.load_documents(config.DOC_DIRS)
    chunks = chunking.make_chunks(docs, config.CHUNK_METHOD, config.CHUNK_SIZE,
                                  config.CHUNK_OVERLAP, config.WITH_TITLE)
    return Index.build(chunks)


def set_index(index):
    global _index
    _index = index


def get_index():
    global _index
    if _index is None:
        _index = Index.load()
    return _index
```

`build_index.py` - третій будує індекс за параметрами з `config.py` і зберігає в каталог `index/`:

```python
"""Будує індекс за параметрами з config.py і зберігає в каталог index/."""
import config
import rag


index = rag.build_from_config()
index.save()
lengths = [len(c["text"]) for c in index.chunks]
print(f"Чанків: {len(index.chunks)}; середня довжина {sum(lengths) / len(lengths):.0f} символів; "
      f"найкоротший {min(lengths)}, найдовший {max(lengths)}")
print(f"Модель: {config.EMBED_MODEL}; довжина вектора: {index.faiss.d}")
```

Спершу перевірте саму модель ембедингів. Скрипт `embed_check.py` виводить довжину вектора, його норму й близькість трьох фраз (запит про вартість відправлення, фраза про тариф і фраза про графік роботи кур'єрів):

```python
"""Перевірка моделі ембедингів: довжина вектора, норма, близькість трьох текстів."""
import time

import numpy as np

import embedder

texts = ["Скільки коштує відправити посилку?", "Тариф на доставку", "Графік роботи кур'єрів"]
started = time.time()
vectors = np.array(embedder.embed(texts), dtype="float32")
print(f"Час: {time.time() - started:.1f} с (з кешем буде майже 0)")
print(f"Довжина вектора: {vectors.shape[1]}")
print(f"Довжина (норма) першого вектора: {np.linalg.norm(vectors[0]):.3f}  (1.000 - вектори вже нормалізовані)")

unit = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
print(f"Запит - 'Тариф на доставку'      : {float(unit[0] @ unit[1]):.3f}")
print(f"Запит - 'Графік роботи кур'єрів' : {float(unit[0] @ unit[2]):.3f}")
```

```
python embed_check.py
```

Для `bge-m3` довжина вектора має бути 1024. Запит має бути ближчим до фрази про тариф, ніж до фрази про графік. Якщо ні, перевірте, що `EMBED_MODEL` збігається з завантаженою моделлю. Запишіть у звіт довжину вектора, норму й обидва числа. Потім побудуйте індекс:

```
python build_index.py
```

Скрипт виведе кількість чанків і їх довжини. Якщо Ollama повертає помилку або відповідає дуже довго, перевірте, що сервер запущений і що модель завантажена (`ollama list`). Перший запуск повільніший, наступні беруть вектори з `index/embeddings_cache.json`.

Якщо `faiss-cpu` не встановлюється на вашій версії Python, замініть у `rag.py` рядки з FAISS на індекс на `numpy` з лекції 9 (п. 9.7): клас має той самий інтерфейс.

### Крок 5. Перевірка пошуку без агента

Тут агент не потрібен: `check_retrieval.py` перевіряє лише те, чи потрапляє потрібний фрагмент у результат пошуку. Для кожного з восьми питань з відповіддю пошук має знайти чанк, що містить фразу `must_contain`. Частку питань, для яких це вдалося, називають **hit rate** («частка влучань»; лекція 9, п. 9.10). Запис `hit@3` означає: потрібний чанк є серед трьох найближчих.

```python
"""Перевірка пошуку без агента.
Запуск: python check_retrieval.py            таблиця конфігурацій нарізання
        python check_retrieval.py scores     оцінки схожості для поточних параметрів з config.py"""
import json
import re
import sys

import chunking
import config
import rag

CONFIGS = [
    {"name": "fixed-200-0",       "method": "fixed",      "size": 200,  "overlap": 0,   "title": False},
    {"name": "fixed-500-0",       "method": "fixed",      "size": 500,  "overlap": 0,   "title": False},
    {"name": "fixed-500-100",     "method": "fixed",      "size": 500,  "overlap": 100, "title": False},
    {"name": "fixed-1500-0",      "method": "fixed",      "size": 1500, "overlap": 0,   "title": False},
    {"name": "paragraphs-800",    "method": "paragraphs", "size": 800,  "overlap": 0,   "title": False},
    {"name": "paragraphs-800+title", "method": "paragraphs", "size": 800, "overlap": 0, "title": True},
]
KS = [1, 3, 5]


def norm(text):
    return re.sub(r"\s+", " ", text).strip()


with open("rag_cases.json", encoding="utf-8") as f:
    cases = json.load(f)
answerable = [c for c in cases if c["kind"] != "none"]
docs = chunking.load_documents(config.DOC_DIRS)

if len(sys.argv) > 1 and sys.argv[1] == "scores":
    index = rag.Index.build(chunking.make_chunks(docs, config.CHUNK_METHOD, config.CHUNK_SIZE,
                                                  config.CHUNK_OVERLAP, config.WITH_TITLE))
    print(f"Параметри: {config.CHUNK_METHOD}, розмір {config.CHUNK_SIZE}, перекриття {config.CHUNK_OVERLAP}, "
          f"заголовок {config.WITH_TITLE}\n")
    print("id   вид         схожість першого результату   чи містить потрібну фразу")
    good, bad = [], []
    for case in cases:
        top = index.search(case["question"], 1)[0]
        has = case["must_contain"] is not None and norm(case["must_contain"]) in norm(top["text"])
        (bad if case["kind"] == "none" else good).append(top["score"])
        mark = "-" if case["kind"] == "none" else ("так" if has else "НІ")
        print(f"{case['id']:4} {case['kind']:11} {top['score']:.3f}                         {mark}")
    print(f"\nНайнижча схожість серед питань з відповіддю: {min(good):.3f}")
    print(f"Найвища схожість серед питань без відповіді: {max(bad):.3f}")
    if max(bad) < min(good):
        print(f"Межі не перекриваються: поріг MIN_SCORE можна вибрати між {max(bad):.3f} і {min(good):.3f}")
    else:
        print("Межі перекриваються: жоден поріг не розділяє питання ідеально, виберіть компроміс і опишіть його")
    sys.exit(0)

print(f"{'конфігурація':22} {'чанків':>6} {'сер.довжина':>11} " + " ".join(f"{'hit@' + str(k):>6}" for k in KS)
      + f" {'hit@3 прямі':>12} {'hit@3 перефр.':>14} {'токенів (k=3)':>14}")


def hit_rate(index, subset, k):
    hits = sum(1 for case in subset
               if any(norm(case["must_contain"]) in norm(r["text"]) for r in index.search(case["question"], k)))
    return hits / len(subset)


direct = [c for c in answerable if c["kind"] == "direct"]
paraphrase = [c for c in answerable if c["kind"] == "paraphrase"]
for cfg in CONFIGS:
    chunks = chunking.make_chunks(docs, cfg["method"], cfg["size"], cfg["overlap"], cfg["title"])
    index = rag.Index.build(chunks)
    mean_len = sum(len(c["text"]) for c in chunks) / len(chunks)
    row = [hit_rate(index, answerable, k) for k in KS]
    print(f"{cfg['name']:22} {len(chunks):6} {mean_len:11.0f} " + " ".join(f"{h:6.2f}" for h in row)
          + f" {hit_rate(index, direct, 3):12.2f} {hit_rate(index, paraphrase, 3):14.2f} {3 * mean_len / 2.5:14.0f}")
```

#### Нарізання і розмір результату

Скрипт будує шість індексів із різним нарізанням (для кожного ембединги чанків рахуються, а повторювані тексти беруться з кешу) і виводить таблицю:

```
python check_retrieval.py
```

Заповніть табл. 2 числами зі свого виводу. Колонка «Токенів (k=3)» - оцінка розміру результату пошуку, який потрапить в історію агента: три чанки по середній довжині, 2,5 символа на токен (лекція 7, п. 7.3). Що довше результат, то менше викликів моделі вміщується у вікно (лекція 9, п. 9.9).

Таблиця 2 - Пошук при різному нарізанні

| Конфігурація           | Чанків | Сер. довжина | hit@1 | hit@3 | hit@5 | hit@3 прямі | hit@3 перефр. | Токенів (k=3) |
|------------------------|--------|--------------|-------|-------|-------|-------------|---------------|---------------|
| `fixed-200-0`          |        |              |       |       |       |             |               |               |
| `fixed-500-0`          |        |              |       |       |       |             |               |               |
| `fixed-500-100`        |        |              |       |       |       |             |               |               |
| `fixed-1500-0`         |        |              |       |       |       |             |               |               |
| `paragraphs-800`       |        |              |       |       |       |             |               |               |
| `paragraphs-800+title` |        |              |       |       |       |             |               |               |

Виберіть конфігурацію для подальшої роботи: найвищий `hit@3`, а за рівності - та, що має менший розмір результату. 
Впишіть її параметри в `CHUNK_METHOD`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `WITH_TITLE` у `config.py`. 
Для питань, де в обраній конфігурації `hit@3` не досягло повного, подивіться, що саме повернув пошук і чому потрібного чанка там немає (чанк розрізано, у чанка немає назви документа, питання надто далеке за змістом). Висновок підтвердіть прикладом.

#### Поріг схожості

Пошук **завжди** повертає k найближчих чанків, навіть коли відповіді в документах немає: він не знає, чи знайдене справді відповідає запиту (лекція 9, п. 9.9). Захист - поріг: результати з низькою схожістю відкидаються, і агент отримує «нічого не знайдено». Поріг залежить від моделі, тож його підбирають на своїх даних. Запустіть скрипт, що виводить схожість **першого** результату для кожного питання при параметрах з `config.py`:

```
python check_retrieval.py scores
```

Скрипт позначає питання з відповіддю та без неї, виводить найнижчу схожість серед перших і найвищу серед других і підказує, чи їх можна розділити порогом. Заповніть табл. 3 і запишіть вибране значення в `MIN_SCORE`. Якщо межі перекриваються, поріг ідеально не розділить питання: виберіть компроміс і поясніть у звіті, що вам важливіше (не пропустити відповідь чи не вигадувати відповідь, якої немає).

Таблиця 3 - Схожість першого результату

| id  | Вид    | Схожість | Перший результат містить потрібну фразу |
|-----|--------|----------|-----------------------------------------|
| D1  | direct |          |                                         |
| ... |        |          |                                         |
| N1  | none   |          | -                                       |
| N2  | none   |          | -                                       |

Нарешті збудуйте індекс остаточно за вибраними параметрами:

```
python build_index.py
```

### Крок 6. Пошук як інструмент агента

Для агента пошук - звичайний інструмент у списку, поряд з довідником і обчисленням (лекція 10). 
Усю роботу з індексом вже зроблено в `rag.py`, тож інструмент короткий.

1. **`tools.py`.** Додайте на початок файла `import config` і `import rag`, а перед реєстром `TOOLS` - функцію:

   ```python
   def search_docs(query: str) -> str:
       """Векторний пошук по документах: повертає фрагменти разом з назвами файлів."""
       candidates = rag.get_index().search(query, config.TOP_K)
       found = [r for r in candidates if r["score"] >= config.MIN_SCORE]
       rag.TRACE.append({"query": query,
                         "top_score": candidates[0]["score"] if candidates else None,
                         "results": found})
       if not found:
           return "У документах нічого схожого не знайдено."
       return "\n\n".join(f"[{n}] Джерело: {r['source']}\n{r['text']}" for n, r in enumerate(found, 1))
   ```

   і додайте її в реєстр: `"search_docs": search_docs`. Запис у `rag.TRACE` потрібен лише скриптам вимірювання: модель його не бачить. Для моделі функція повертає текст: фрагменти з іменами файлів або повідомлення, що нічого не знайдено.

2. **`arguments.py`.** Додайте клас аргументів і запис у `ARGS`:

   ```python
   class DocsArgs(BaseModel):
       model_config = ConfigDict(extra="forbid")
       query: str = Field(min_length=3, max_length=300,
                          description="Що знайти: одне-два речення українською, словами користувача")
   ```

   ```python
   ARGS["search_docs"] = DocsArgs      # або додайте ключ "search_docs" у словник ARGS
   ```

3. **`schemas.py`.** Ми порівнюватимемо три тексти опису інструмента (табл. 4). Додайте в `schemas.py` після словника `DESCRIPTIONS`, але **до** циклу, що будує `SCHEMAS`, словник описів:

   ```python
   RAG_DESCRIPTIONS = {
       "A": "Шукає книжки за темою, жанром або рівнем складності. "
            "Використовуй, коли користувач описує, яку книжку хоче, але не називає точної назви. "
            "Повертає назви знайдених книжок одним рядком",
       "B": ("ЄДИНЕ джерело даних про роботу бібліотеки. Викликай ЗАВЖДИ, коли питання стосується будь-якої "                                                                                                                           
             "послуги, ціни, суми, застави, терміну, ліміту чи правила бібліотеки, навіть якщо тема здається незвичною. "                                                                                                               
             "Ніколи не відповідай «немає інформації» чи «немає інструмента», не викликавши спершу цей інструмент. "                                                                                                                    
             "Документи охоплюють: реєстрацію й читацький квиток, правила видачі, продовження, штрафи; "                                                                                                                                
             "читальну залу, комп'ютери, копіювання, обладнання й прилади для читачів; "                                                                                                                                                
             "міжбібліотечний абонемент: замовлення книжок з інших міст і бібліотек, доставку, збори, бронювання, сповіщення; "                                                                                                         
             "фонд: комплектування, сховище, депозитарій, списання; гуртки, клуби, заходи, оренду залів. "                                                                                                                              
             "Запит формулюй повним реченням. Відповідай лише за знайденими фрагментами; "                                                                                                                                              
             "якщо потрібного там немає, так і скажи користувачу."),
       "C": "Шукає інформацію.",
   }
   DESCRIPTIONS["search_docs"] = RAG_DESCRIPTIONS[config.DOCS_DESCRIPTION]
   ```

   і функцію підміни опису в кінець файла:

   ```python
   def set_description(name, text):
       """Підміняє опис інструмента в SCHEMAS: це той самий список, який читає agent.py."""
       for item in SCHEMAS:
           if item["function"]["name"] == name:
               item["function"]["description"] = text
   ```

   Опис **A** - це текст опису вашого старого інструмента пошуку з `DESCRIPTIONS` (скопіюйте його без змін). 

   Опис **C** - навмисно мінімальний.

   Опис **B** напишіть за зразком так, щоб він містив:
   - у яких документах шукає (теми зі свого рядка табл. 8); 
   - для яких питань його **треба** використовувати і чому з пам'яті відповідати не можна; 
   - що робити, якщо нічого не знайдено. 
    
   У прикладі вище опис для варіанта 1.

4. **`config.py`.** У списку `ALLOWED` замініть назву старого інструмента пошуку на `"search_docs"`, інші інструменти лишіть. Старий інструмент залишається в `tools.py`, але агентові більше недоступний.

5. **`checks.py`** змінювати не треба: для інструмента без правил змісту `check_meaning` повертає `None`. Перевірте, що це справді так.

Перевірте інструмент через диспетчер, **без моделі**. Скрипт `try_tool.py` ставить питання, виводить результат, а потім перевіряє, що занадто короткий запит відхиляється схемою:

```python
"""Перевірка інструмента search_docs через диспетчер, без моделі.
Запуск: python try_tool.py D1"""
import json
import sys

import dispatcher

with open("rag_cases.json", encoding="utf-8") as f:
    cases = {c["id"]: c for c in json.load(f)}

question = cases[sys.argv[1]]["question"]
print("ПИТАННЯ:", question, "\n")
level, text = dispatcher.call_tool("search_docs", json.dumps({"query": question}, ensure_ascii=False))
print(f"рівень: {level}\n{text}\n")

level, text = dispatcher.call_tool("search_docs", '{"query": "а"}')
print(f"Занадто короткий запит -> рівень: {level}\n{text}")
```

```
python try_tool.py D1
python try_tool.py N1
```

Для питання з відповіддю мають бути фрагменти з іменами файлів, для питання без відповіді - «У документах нічого схожого не знайдено» (якщо поріг підібрано правильно). Запишіть обидва виводи у звіт.

Тепер перевірте весь ланцюжок з моделлю. Скрипт ставить агентові одне питання за його номером:

```python
"""Одне питання з rag_cases.json агентові.
Запуск: python ask.py D1"""
import json
import sys

import agent

with open("rag_cases.json", encoding="utf-8") as f:
    cases = {c["id"]: c for c in json.load(f)}

answer = agent.run_agent(cases[sys.argv[1]]["question"])
print("\nВІДПОВІДЬ:", answer)
```

Кроки агента пишуться через `custom_logger` у консоль і в `logs/lab5.log`.

```
python ask.py D1
```

У лозі має бути виклик `search_docs`, його результат і відповідь. Якщо агент не викликав пошук або відповів неправильно - це не обов'язково помилка вашого коду: саме це ми й вимірюємо в наступному кроці.

### Крок 7. Три описи інструмента

**Ключове спостереження цієї роботи:** агент сам вирішує, чи звертатися до пошуку, і часто не здогадується (лекція 10). Єдине, що він знає про інструмент, - його опис. Тому порівнюємо три описи на тих самих десяти питаннях (табл. 4):

Таблиця 4 - Конфігурації агента

| Назва | Опис `search_docs`                                                  | Нарізання, `TOP_K`, `MIN_SCORE` |
|-------|---------------------------------------------------------------------|---------------------------------|
| `A`   | Опис вашого старого пошуку з лабораторної № 2                       | З `config.py` (не змінюється)   |
| `B`   | Докладний: де шукати, коли обов'язково, що робити, якщо не знайдено | Ті самі                         |
| `C`   | «Шукає інформацію.»                                                 | Ті самі                         |

Скрипту вимірювання потрібні підсумки кожного прогону агента: як він закінчився, скільки було кроків і токенів, скільки тривав. Додайте їх в `agent.py`. На початок файла - `import time`, після імпортів - словник і функцію:

```python
# НОВЕ: підсумок останнього прогону; його читає measure_rag.py
# status: final | server_error | retry_limit | step_limit (як у lab4/logparse.py)
LAST_RUN = {}


def _finish(status, answer, steps, prompt_tokens, completion_tokens, started):
    """Записує підсумок прогону в LAST_RUN і повертає відповідь."""
    LAST_RUN.clear()
    LAST_RUN.update({
        "status": status,
        "steps": steps,                              # скільки разів модель відповіла
        "prompt_tokens": prompt_tokens,              # сума входів за прогін
        "completion_tokens": completion_tokens,
        "seconds": round(time.time() - started, 1),
    })
    return answer
```

У `run_agent` перед циклом `for step in ...` додайте лічильники і коротку функцію завершення:

```python
    started = time.time()                                             # НОВЕ: для LAST_RUN
    steps = prompt_total = completion_total = 0

    def finish(status, answer=None):
        return _finish(status, answer, steps, prompt_total, completion_total, started)
```

а в циклі одразу після рядка `used = response.usage.prompt_tokens` - підрахунок:

```python
        steps += 1
        prompt_total += response.usage.prompt_tokens
        completion_total += response.usage.completion_tokens
```

Нарешті замініть кожен `return` у `run_agent` на `return finish(...)` зі статусом:

| Де                                     | Було                 | Стало                                 |
|----------------------------------------|----------------------|---------------------------------------|
| помилка сервера (`response is None`)   | `return None`        | `return finish("server_error")`       |
| обидва місця «СТОП: модель не змогла…» | `return None`        | `return finish("retry_limit")`        |
| відповідь без виклику інструмента      | `return msg.content` | `return finish("final", msg.content)` |
| «СТОП: вичерпано ліміт кроків»         | `return None`        | `return finish("step_limit")`         |

Що повертає `run_agent`, не змінюється: текст відповіді або `None`.

Скрипт `measure_rag.py` вимірювання проганяє всі десять питань для кожного опису по три рази, записує лог у `logs/rag_<опис>-r<повтор>.log`, а підсумки в `results/rag.csv`. Кожна пара «опис + повтор» пише свій лог: файл очищається на початку серії, а агент дописує в нього всі десять питань (`log_overwrite=False`).
Для кожного прогону він визначає: 
- чи викликав агент пошук (`searches`)?
- чи потрапив потрібний фрагмент у результат (`hit`)?
- чи правильна відповідь (`correct`)?
- до якої категорії належить прогін?

```python
"""Вимірювання RAG-агента: три описи інструмента пошуку, по кілька повторів.

Запуск:
    python measure_rag.py              усі описи (A, B, C), по 3 повтори
    python measure_rag.py B 1          один опис, один повтор
"""
import csv
import json
import os
import re
import statistics
import sys

from langfuse import get_client, propagate_attributes

import agent
import config
import rag
import schemas
from utils.lab_logger import custom_logger

CONFIGS = ["A", "B", "C"]                      # ключі зі schemas.RAG_DESCRIPTIONS
names = [sys.argv[1]] if len(sys.argv) > 1 else CONFIGS
repeats = int(sys.argv[2]) if len(sys.argv) > 2 else 3

with open("rag_cases.json", encoding="utf-8") as f:
    cases = json.load(f)

UNKNOWN = ("не знайш", "не знайд", "немає інформац", "немає даних", "відсутн", "не вказан",
           "не містить", "не маю інформац", "не можу знайти", "нічого схожого", "не зазначен")


def norm(text):
    return re.sub(r"\s+", " ", text).strip()


def contains_value(answer, expected):
    """Чи є очікуване значення у відповіді як окреме число або слово. Неправильні відповіді перевіряйте вручну."""
    if not answer:
        return False
    text = re.sub(r"(?<=\d)[  ](?=\d{3}\b)", "", answer)     # "1 000" -> "1000"
    text = re.sub(r"(?<=\d),(?=\d)", ".", text)                   # "13,5" -> "13.5"
    if re.fullmatch(r"\d+(\.\d+)?", expected):
        return re.search(rf"(?<![\d.]){re.escape(expected)}(?!\d|\.\d)", text) is not None
    return expected.lower() in text.lower()


def admits_unknown(answer):
    """Чи визнає відповідь, що інформації немає. Автоматична перевірка груба: перегляньте ці відповіді вручну."""
    return bool(answer) and any(word in answer.lower() for word in UNKNOWN)


def classify(case, searches, hit, correct):
    if case["kind"] == "none":
        return "refused" if correct else "invented"
    if correct:
        return "ok"
    if searches == 0:
        return "no_search"
    return "miss" if not hit else "ignored"


os.makedirs("results", exist_ok=True)               # папку logs/ створює custom_logger
rows = []

for repeat in range(1, repeats + 1):               # повтори - зовнішній цикл: описи чергуються
    for name in names:
        schemas.set_description("search_docs", schemas.RAG_DESCRIPTIONS[name])
        # окремий лог на кожну пару опис+повтор: logs/rag_<опис>-r<повтор>.log
        log_name = f"rag_{name}-r{repeat}"
        logger = custom_logger(log_name, overwrite=True)     # очищаємо файл один раз на початку серії

        for case in cases:
            rag.TRACE.clear()
            run_id = f"{name}-r{repeat}-{case['id']}"
            logger.info(f"\n##### {run_id}")
            with propagate_attributes(trace_name=f"rag-{run_id}", tags=[f"rag-{name}"]):
                # log_overwrite=False: агент дописує в той самий файл, а не стирає попередні питання
                answer = agent.run_agent(case["question"], logfile_name=log_name,
                                         task_id=run_id, log_overwrite=False)
            searches = len(rag.TRACE)
            hit = case["kind"] != "none" and any(norm(case["must_contain"]) in norm(r["text"])
                                                  for t in rag.TRACE for r in t["results"])
            if case["kind"] == "none":
                correct = admits_unknown(answer)
            else:
                correct = contains_value(answer, case["expected"])
            rows.append({"config": name, "repeat": repeat, "id": case["id"], "kind": case["kind"],
                         "searches": searches, "hit": int(hit), "correct": int(correct),
                         "category": classify(case, searches, hit, correct),
                         "top_score": round(rag.TRACE[0]["top_score"], 3) if searches else "",
                         "answer": (answer or "").replace("\n", " ")[:300],
                         **{k: agent.LAST_RUN[k] for k in ("status", "steps", "prompt_tokens",
                                                            "completion_tokens", "seconds")}})

get_client().flush()

# файл результатів: рядки цих описів замінюються новими, рядки інших лишаються
path = "results/rag.csv"
old = []
if os.path.exists(path):
    with open(path, encoding="utf-8", newline="") as f:
        old = [r for r in csv.DictReader(f) if r["config"] not in names]
with open(path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(old + rows)

print("\n=== Підсумок ===")
for name in names:
    part = [r for r in rows if r["config"] == name]
    answerable = [r for r in part if r["kind"] !="none"]
    print(f"{name}: правильно {sum(r['correct'] for r in answerable)}/{len(answerable)} | "
          f"викликали пошук у {sum(1 for r in answerable if r['searches'] > 0)}/{len(answerable)} | "
          f"кроків (медіана) {statistics.median(r['steps'] for r in part)}")
print("Детальні таблиці: python rag_report.py")
```

Перевірка правильності автоматична й груба: для питань з відповіддю шукається число з `expected` у відповіді, для питань без відповіді - слова на кшталт «не знайшов», «немає інформації». Тому **відповіді з `correct = 0` і всі відповіді на питання `none` перегляньте вручну** (колонка `answer` у `results/rag.csv`). Якщо автоматична оцінка помилкова (модель записала число словами, написала в іншому форматі), виправте `correct` і `category` у файлі й скажіть про це у звіті.

Спершу один прогін, щоб переконатися, що все працює:

```
python measure_rag.py B 1
``` 

Потім повне вимірювання: три описи, по три повтори, разом 90 запусків агента:

```
python measure_rag.py
```

Це займе деякий час (кожен запуск - кілька кроків моделі), тому запускайте, коли комп'ютер можна залишити. Зверніть увагу: тепер Ollama працює з двома моделями (чату й ембедингів). Якщо оперативної пам'яті мало, вона може вивантажувати одну, щоб завантажити іншу, і кожне таке перемикання додає секунди до кроку. Подивитися, що завантажено, можна командою `ollama ps`. Якщо прогін надто повільний, дозвольте Ollama тримати дві моделі одночасно: перед запуском сервера задайте змінну `set OLLAMA_MAX_LOADED_MODELS=2` (за умови, що пам'яті вистачає для обох; ембединг-модель займає близько 1,2 ГБ). Скрипт замінює в `results/rag.csv` рядки тих описів, які щойно запускалися, тож пробний прогін не заважає. 
Таблиці будує другий скрипт `rag_report.py`:

```python
"""Таблиці за results/rag.csv: підсумок і розподіл поламок за описами інструмента."""
import csv
import statistics

with open("results/rag.csv", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
configs = sorted({r["config"] for r in rows})
CATEGORIES = [("ok", "Правильно (питання з відповіддю)"),
              ("no_search", "Не шукав і відповів неправильно"),
              ("miss", "Шукав, але потрібного фрагмента в результаті немає"),
              ("ignored", "Фрагмент у результаті був, відповідь неправильна"),
              ("refused", "Питання без відповіді: визнав, що не знає"),
              ("invented", "Питання без відповіді: вигадав відповідь")]


def med(part, field):
    return statistics.median(float(r[field]) for r in part)


print("Підсумок за описами (по всіх повторах)")
print(f"{'опис':5} {'правильно':>10} {'шукав':>8} {'кроків':>7} {'токенів входу':>14} {'час, с':>7}")
for name in configs:
    part = [r for r in rows if r["config"] == name]
    answerable = [r for r in part if r["kind"] != "none"]
    right = sum(int(r["correct"]) for r in answerable)
    searched = sum(1 for r in answerable if int(r["searches"]) > 0)
    print(f"{name:5} {right:>4}/{len(answerable):<5} {searched:>3}/{len(answerable):<4} {med(part, 'steps'):7.1f} "
          f"{med(part, 'prompt_tokens'):14.0f} {med(part, 'seconds'):7.1f}")

print("\nПоламки (кількість прогонів)")
print(f"{'':58}" + "".join(f"{c:>6}" for c in configs))
for key, title in CATEGORIES:
    counts = [sum(1 for r in rows if r["config"] == c and r["category"] == key) for c in configs]
    print(f"{title:58}" + "".join(f"{n:6}" for n in counts))
```

```
python rag_report.py
```

Заповніть табл. 5 і 6 за його виводом.

Таблиця 5 - Агент з трьома описами інструмента (дані за всіма повторами; питань з відповіддю 8, у трьох повторах 24 прогони)

| Опис | Правильно (з 24) | Викликав пошук (з 24) | Кроків, медіана | Токенів входу, медіана | Час, с, медіана |
|------|------------------|-----------------------|-----------------|------------------------|-----------------|
| `A`  |                  |                       |                 |                        |                 |
| `B`  |                  |                       |                 |                        |                 |
| `C`  |                  |                       |                 |                        |                 |

Таблиця 6 - Куди ламається відповідь (кількість прогонів; питань з відповіддю 24 на опис, без відповіді 6)

| Категорія                                          | `A` | `B` | `C` |
|----------------------------------------------------|-----|-----|-----|
| Правильно                                          |     |     |     |
| Не шукав і відповів неправильно                    |     |     |     |
| Шукав, але потрібного фрагмента в результаті немає |     |     |     |
| Фрагмент був у результаті, відповідь неправильна   |     |     |     |
| Питання без відповіді: визнав, що не знає          |     |     |     |
| Питання без відповіді: вигадав відповідь           |     |     |     |

Три рядки з помилками відповідають трьом різним причинам, і лікуються вони по-різному: «не шукав» лікує опис інструмента, «шукав, але немає» - нарізання, поріг або сам запит, «фрагмент був, відповідь неправильна» - підказка моделі, довжина результату або сама модель.

### Крок 8. Розбір у логах і трасах Langfuse

Таблиці показують скільки, а не чому. Знайдіть у `logs/rag_*.log` (кожен прогін позначено рядком `##### <опис>-r<повтор>-<id питання>`) і розберіть конкретні прогони:

1. **Агент не шукав.** Знайдіть прогін з категорією `no_search` (найімовірніше, в описі `C`). Що саме відповіла модель? Чи вигадала вона значення? Наведіть фрагмент логу.
2. **Який запит написала модель.** Для кількох прогонів з пошуком порівняйте текст питання користувача з полем `query` у виклику `search_docs`. Чи переписала модель питання, чи скопіювала? Як це пов'язано зі схожістю першого результату (колонка `top_score` у `results/rag.csv`)?
3. **Шукав, але не знайшов** (категорія `miss`). Подивіться результат пошуку в лозі. Чому потрібного чанка там немає: вигляд запиту, нарізання, поріг, перефразування?
4. **Знайшов, але не використав** (категорія `ignored`). Знайдіть у результаті пошуку потрібну фразу й порівняйте з відповіддю моделі. Що вона взяла замість неї?
5. **Питання без відповіді.** Що зробив агент у кожному описі: визнав, що відповіді немає, чи вигадав? Чи допоміг поріг схожості?

У Langfuse відфільтруйте траси за міткою `rag-B` і `rag-C` (назва траси - `rag-<опис>-r<повтор>-<id>`). Для одного питання з кожного опису:

1. Відкрийте дерево траси й зробіть скріншот. Знайдіть вузол `call_tool` для `search_docs`: що в його вході (запит) і виході (чанки)?
2. Відкрийте вхід першого виклику моделі й знайдіть опис інструмента `search_docs`. Чим він відрізняється між `B` і `C`?
3. Поясніть, що в трасі видно одразу, а в текстовому лозі довелося б шукати вручну.

### Крок 9. Звичайні задачі після зміни пошуку

Агент змінився: старий пошук підрядком замінено новим. Переконайтеся, що п'ять звичайних задач з `tasks.json` не зламалися. Встановіть `DOCS_DESCRIPTION = "B"`, запустіть:

```
python agent_runner.py
```

Перейменуйте `logs/lab5.log` на `logs/run_rag.log` і порівняйте з `logs/run_lab4.log`. Лог дописується, тому перед запуском видаліть старий `logs/lab5.log` (там прогони `ask.py`), щоб у `run_rag.log` були лише ці п'ять задач. Заповніть табл. 7 (або, якщо ваш `tasks.json` має іншу кількість рядків, додайте їх).

Таблиця 7 - П'ять задач до і після заміни пошуку

| Задача | Відповідь у лабораторній № 4 | Відповідь тепер | Чи викликав `search_docs` | Що змінилося |
|--------|------------------------------|-----------------|---------------------------|--------------|
| 1      |                              |                 |                           |              |
| 2      |                              |                 |                           |              |
| 3      |                              |                 |                           |              |
| 4      |                              |                 |                           |              |
| 5      |                              |                 |                           |              |

Якщо якась задача стала гіршою, знайдіть причину в лозі: нове нарізання повернуло не той чанк, агент не звернувся до пошуку, чи змінилося щось інше.

## Додаткове завдання: той самий індекс на Chroma

Виконується за бажанням, на підвищену оцінку.

Лекція 9 попереджає про пастки бібліотек, які не дають помилки. Перевірте одну з них.

Спочатку інсталюйте додаткову бібліотеку

```bash
pip install chromadb
```

**Chroma** - векторна база даних, яка (на відміну від FAISS) зберігає разом з векторами тексти й метадані. Створіть файл `chroma_index.py`:

```python
"""Додаткове завдання: той самий індекс на Chroma."""
import chromadb
import numpy as np

import embedder


class ChromaIndex:
    def __init__(self, chunks, vectors, path="chroma_db", space="cosine"):
        client = chromadb.PersistentClient(path=path)
        try:
            client.delete_collection("docs")                    # щоразу будуємо з нуля
        except Exception:
            pass
        settings = {"configuration": {"hnsw": {"space": space}}} if space else {}   # space=None: значення за замовчуванням
        self.collection = client.create_collection("docs", **settings)
        matrix = np.array(vectors, dtype="float32")
        matrix = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)             # нормалізуємо самі
        self.collection.add(ids=[f"c{i}" for i in range(len(chunks))],
                            documents=[c["text"] for c in chunks],
                            embeddings=matrix.tolist(),
                            metadatas=[{"source": c["source"], "chunk": c["chunk"]} for c in chunks])

    def search(self, query, k=3):
        q = np.array(embedder.embed([query])[0], dtype="float32")
        q = q / np.linalg.norm(q)
        result = self.collection.query(query_embeddings=[q.tolist()], n_results=k)
        return [{"distance": float(dist), "source": meta["source"], "chunk": meta["chunk"], "text": text}
                for text, meta, dist in zip(result["documents"][0], result["metadatas"][0], result["distances"][0])]
```

Інтерфейс `search` такий самий, як у `rag.Index`, але повертає **відстань** (`distance`: менше - ближче), а не схожість. 
Побудуйте три індекси у `chroma_test` на одних і тих самих чанках і векторах і порівняйте перший результат для питання D1:

```python
import chunking
import config
import embedder
import rag
from chroma_index import ChromaIndex

docs = chunking.load_documents(config.DOC_DIRS)
chunks = chunking.make_chunks(docs, config.CHUNK_METHOD, config.CHUNK_SIZE,
                              config.CHUNK_OVERLAP, config.WITH_TITLE)
vectors = embedder.embed([c["text"] for c in chunks])
question = "..."                                        # вставте текст питання D1

faiss_top = rag.Index(chunks, vectors).search(question, 1)[0]
cosine_top = ChromaIndex(chunks, vectors, "chroma_cos", "cosine").search(question, 1)[0]
default_top = ChromaIndex(chunks, vectors, "chroma_default", None).search(question, 1)[0]

print("FAISS, схожість           :", round(faiss_top["score"], 4))
print("Chroma cosine, відстань   :", round(cosine_top["distance"], 4))
print("Chroma за замовчуванням   :", round(default_top["distance"], 4))
```

Поясніть у звіті: 
1. Як пов'язані числа в трьох рядках (підказка: косинусна відстань дорівнює 1 мінус схожість, а квадрат евклідової відстані для нормалізованих векторів дорівнює 2 мінус подвоєна схожість; лекція 9, п. 9.6)? 
2. Чи збігаються чанки, які повернули три індекси?
3. Що сталося б з вашим порогом `MIN_SCORE`, якби ви перенесли його на Chroma зі стандартними налаштуваннями й не помітили, що там відстань?

## Документи за варіантами

Номер варіанта й предметна область - ті самі, що в лабораторній роботі № 2. Табл. 8 задає теми п'яти документів (крок 2). Вигадану організацію, в якій діють ці правила, оберіть самі.

Таблиця 8 - Теми документів за варіантами

| №  | Область             | П'ять документів                                                                                                                                                    |
|----|---------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1  | Бібліотека          | Правила користування бібліотекою; читальна зала й електронні ресурси; міжбібліотечний абонемент; формування й списання фонду; гуртки та заходи при бібліотеці       |
| 2  | Кулінарія           | Техніки приготування; зберігання продуктів і терміни придатності; заміна інгредієнтів; кухонне обладнання й догляд за ним; безпека на кухні й алергени              |
| 3  | Доставка посилок    | Пакування відправлень; заборонені й обмежені до пересилання речі; страхування й компенсації; повернення та недоставлені відправлення; строки доставки й відстеження |
| 4  | Тренування          | Техніка безпеки в залі; програма для початківців; відновлення й харчування; правила абонементів і заморожування; користування обладнанням                           |
| 5  | Догляд за рослинами | Полив; ґрунт і пересадка; освітлення й температура; хвороби та шкідники; сезонний догляд                                                                            |
| 6  | Ремонт квартири     | Підготовка поверхонь; електропроводка й безпека; укладання плитки; штукатурка й шпаклівка; гарантії та приймання робіт                                              |
| 7  | Подорожі            | Правила багажу; безпека в поході; спорядження; документи й страхування; правила проживання в таборах і хостелах                                                     |
| 8  | Обслуговування авто | Регламент технічного обслуговування; шини й колеса; експлуатаційні рідини; діагностика несправностей; гарантійні умови сервісу                                      |
| 9  | Вибір ноутбука      | Процесори й продуктивність; пам'ять і накопичувачі; акумулятор і зарядка; гарантія й сервіс; екрани й порти                                                         |
| 10 | Догляд за котом     | Годування; щеплення й паразити; поведінка й навчання; перевезення й подорожі; стерилізація й догляд після операції                                                  |

## Відповіді на питання

По два-три речення, з посиланням на таблиці й фрагменти логів:

1. Табл. 1: на скільки відрізнялося нарізання за кількістю символів від нарізання за абзацами? Наведіть приклад чанка, у якому факт розрізано, і поясніть, чим це загрожує агентові.
2. Табл. 2: яка конфігурація виявилася найкращою за `hit@3` і чому? Як змінилися результати при збільшенні розміру чанка з 200 до 1500 символів, при додаванні перекриття, при додаванні назви документа? Яка ціна більшого чанка?
3. Чи відрізняється `hit@3` для прямих і перефразованих питань? Що це говорить про пошук за змістом порівняно з пошуком підрядком (для якого перефразовані питання майже безнадійні)?
4. Табл. 3: чи розділяє поріг `MIN_SCORE` питання з відповіддю й без неї? Що буде, якщо поріг поставити надто високим? Надто низьким?
5. Табл. 5 і 6: який з трьох описів дав найбільше правильних відповідей? Як часто агент не звертався до пошуку в кожному описі? Що в тексті опису `B` змінило поведінку порівняно з `A` і `C`?
6. Табл. 6: яка категорія помилок найчастіша в найкращому описі? Чи можна її виправити зміною опису, чи потрібно змінювати пошук (нарізання, `TOP_K`, поріг) або модель? Чому це розрізнення важливе?
7. Питання без відповіді: у скількох прогонах агент вигадав відповідь? Які два захисти є в системі (поріг у `search_docs` і текст опису) і який із них спрацював у ваших прогонах?
8. Оцініть із логу, скільки токенів додає один виклик `search_docs` (різниця `prompt_tokens` між кроками). Порівняйте з оцінкою з табл. 2. Скільки викликів моделі вміщується у вікно 4096 при вашому `TOP_K` і розмірі чанка (формула з лекції 7, п. 7.5)?
9. Табл. 7: чи зламав новий пошук якісь із п'яти звичайних задач? Чому так або чому ні?
10. Яку з поламок цієї роботи не вилікує жодна зміна опису інструмента? Що б ви змінили в системі, щоб її виправити?

## Звіт

Оформлюється у форматі Markdown. Структура:

1. Титульна сторінка.
2. Мета роботи, номер варіанта, предметна область, модель чату, розмір вікна, модель ембедингів.
3. Дані: теми п'яти документів, обсяг (символів, оцінка в токенах), список десяти питань з `must_contain` і `expected`, результат перевірки «чи вгадує модель без документів».
4. Результат перевірки моделі ембедингів (`embed_check.py`): довжина вектора, норма, два числа близькості.
5. Табл. 1 (нарізання одного документа) з прикладом розрізаного факту.
6. Табл. 2 (нарізання і hit rate) з вибором конфігурації та обґрунтуванням; табл. 3 (схожість) і вибраний `MIN_SCORE`.
7. Результат перевірки інструмента без моделі (`try_tool.py D1`, `try_tool.py N1`).
8. Табл. 5 і 6: агент із трьома описами.
9. Розбір прогонів у логах і трасах Langfuse (крок 8): фрагменти логів, скріншоти.
10. Табл. 7: п'ять звичайних задач до і після.
11. Відповіді на питання.
12. Додаткове завдання (якщо виконували).
13. Висновок: що найбільше вплинуло на якість відповідей агента (нарізання, поріг, опис інструмента), яка частина помилок лежить у пошуку, а яка в агенті, і що ще варто змінити.

## Що здається

Архів або репозиторій із такою структурою:

```
lab5/
├── report.md
├── data/
│   ├── corpus/
│   └── docs/                   п'ять довгих документів
├── logs/
│   ├── run_lab4.log
│   ├── run_rag.log
│   └── rag_*-r*.log            логи вимірювання (дев'ять файлів)
├── results/
│   └── rag.csv
├── index/                      індекс і параметри (без embeddings_cache.json)
│   ├── docs.faiss
│   ├── chunks.json
│   └── meta.json
├── agent.py
├── agent_runner.py
├── arguments.py
├── ask.py
├── build_index.py
├── check_cases.py
├── check_retrieval.py
├── checks.py
├── chunking.py
├── config.py
├── dispatcher.py
├── embed_check.py
├── embedder.py
├── measure_rag.py
├── rag.py
├── rag_cases.json
├── rag_report.py
├── schemas.py
├── show_chunks.py
├── tasks.json
├── tools.py
└── try_tool.py
```

Каталоги `venv/`, `cache/`, `chroma_db/` і файл `.env` до архіву не включаються. Файл `index/embeddings_cache.json` великий і не потрібен: його можна відновити, запустивши `build_index.py`.

## Питання для захисту

1. Чому модель сама не знає вмісту ваших документів? Чому не можна просто покласти їх усі в контекст? Покажіть це на цифрах свого корпусу.
2. Що таке ембединг? Чому для документів і для запитів використовують одну й ту саму модель?
3. Що таке косинусна схожість? Навіщо вектори нормалізують і що змінюється, якщо цього не зробити?
4. Що таке чанк і від чого залежить його розмір? Що втрачається, якщо чанки надто малі, і що, якщо надто великі?
5. Чому пошук завжди повертає k результатів? Що станеться, якщо питання не має відповіді в документах, і як цього уникнути?
6. Що таке hit rate і чому пошук перевіряють окремо від агента? Яку помилку агента ця перевірка допомагає відрізнити?
7. Чому в `rag.py` відкидається номер `-1` і зберігаються параметри індексу в `meta.json`?
8. Чим кеш ембедингів у `embedder.py` відрізняється від кешу викликів моделі з лабораторної № 4? Чи можна цей кеш вмикати під час вимірювань?
9. Чому опис інструмента впливає на те, чи звернеться агент до пошуку? Що саме в описі `B` це змінило?
10. Яку з трьох причин помилки RAG-агента (не шукав, не знайшов, не використав знайдене) ви спостерігали найчастіше? Що б ви робили для її усунення?
