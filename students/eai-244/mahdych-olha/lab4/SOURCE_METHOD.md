# Лабораторна робота № 4. Контекст, стан і кеш агента

## Мета

Побачити, що відбувається з агентом, коли історія не вміщується в контекстне вікно моделі; навчитися скорочувати історію, зберігати результати інструментів поза текстом діалогу та кешувати виклики моделі; виміряти, скільки це коштує.

## Що потрібно мати перед початком

- Виконану лабораторну роботу № 3 з усіма файлами (`arguments.py`, `checks.py`, `config.py`, `tools.py`, `schemas.py`, `dispatcher.py`, `agent.py`, `agent_runner.py`, каталог `data/`).
- Запущений Ollama і акаунт Langfuse з лабораторної роботи № 3, ту саму локальну модель.

**Хід роботи.** Кроки 1-2: готуємо вузьке вікно і довгу задачу. Кроки 3-4: запускаємо агента без захисту й дивимось, як він ламається. Кроки 5-7: додаємо три способи захисту (обрізання, стан, кеш). Крок 8: вимірюємо, що з цього дало користь.

## Хід роботи

### Крок 1. Проєкт і вузьке вікно

**Що робимо і навіщо.** Копіюємо агента з лабораторної роботи № 3 і створюємо копію моделі з вікном 4096 токенів. **Контекстне вікно** - максимальна кількість токенів, яку модель читає за один виклик: у нього мають вміститися інструкція, уся історія повідомлень і результати інструментів. У вашої моделі вікно в десятки або сотні тисяч токенів, і довга задача вмістилася б повністю - нічого цікавого ми б не побачили. 4096 - це розмір, який Ollama виділяє за замовчуванням на комп'ютері з невеликою відеопам'яттю, тож у такому вікні локальні агенти працюють щодня.

1. **Створіть** папку `lab4`

2. **Перейдіть** у каталог, де лежить `lab3`, і **скопіюйте** всі файли в новостворену директорію.
3. **(Опціонально)** Створіть нове середовище та інсталюйте потрібні бібліотеки

   ```
   python -m venv venv
   venv\Scripts\activate
   pip install openai pydantic python-dotenv "langfuse>=4"
   ```

4. **Створіть** у каталозі `lab4` текстовий файл `Modelfile` (без розширення). Це «рецепт» нової моделі для Ollama: перший рядок - на основі якої моделі, другий - що змінити. `num_ctx` задає розмір вікна в токенах:

   ```
   FROM llama3.2:3b
   PARAMETER num_ctx 4096
   ```

   Замість `llama3.2:3b` напишіть модель, на якій ви виконували лабораторну роботу № 3.

5. **Виконайте** створення моделі й перегляд параметрів обох моделей (підставте назву своєї вихідної):

   ```
   ollama create llama32-4k -f Modelfile
   ollama show llama32-4k
   ollama show llama3.2:3b
   ```

6. **Запишіть у звіт** три числа: `context length` вихідної моделі, `num_ctx` нової моделі (розділ `Parameters`) і у скільки разів вікно звузили.

7. **Внесіть** у `config.py` чотири правки: новий номер для лабораторної роботи, нова модель, мітка прогонів у Langfuse, розмір вікна (за цим числом скрипти аналізу рахуватимуть, яку частину вікна займає вхід) і ліміт кроків для довгої задачі (звичайних 8 кроків для неї замало):

   У `config.py` замініть рядок, що починається з `LAB_LOGFILE_NAME =`, на:

   ```python
   LAB_LOGFILE_NAME = "lab4"   # ім'я лога для agent.py і agent_runner.py
   ```
   
   У `config.py` замініть рядок, що починається з `MODEL =`, на:

   ```python
   MODEL = "llama32-4k"      # нова модель з малим вікном
   ```

   У `config.py` замініть рядок, що починається з `RUN_TAG =`, на:

   ```python
   RUN_TAG = "ctx-control"   # мітка прогонів у Langfuse
   ```

   Додайте в кінець `config.py`:

   ```python
   NUM_CTX = 4096          # розмір вікна, який ви задасте в кроці 1
   MAX_STEPS_LONG = 25     # ліміт кроків для довгої задачі (MAX_STEPS не змінюємо)
   ```
   
8. **Внесіть** у `agent.py` одну правку — перенесіть ініціалізацію логера всередину `run_agent()` . Рядок 11 треба перенести на 18 рядок.
   
   Із
   ```python
   ...
   logger = custom_logger(config.LAB_LOGFILE_NAME)


   @observe()
   def run_agent(task):
       """task – питання користувача
       Повертає текст відповіді або None, якщо вичерпано ліміт."""
   ...
   ```
   
   Повинно стати
   
   ```python
   ...
   


   @observe()
   def run_agent(task):
       """task – питання користувача
       Повертає текст відповіді або None, якщо вичерпано ліміт."""
       logger = custom_logger(config.LAB_LOGFILE_NAME)
   ...
   ```

### Крок 2. Довга задача

**Що робимо і навіщо.** Звичайні задачі короткі, і історія майже не росте. Потрібна задача з довгим ланцюжком: шість позицій, для кожної пошук по корпусу, звернення до довідника й обчислення (6 × 3 = 18 викликів). Правильну відповідь скрипт **рахує сам**, прямими викликами ваших функцій, без моделі: так ми зможемо автоматично перевіряти відповідь агента. `min_calls` (18) - мінімум викликів для повного розв'язання; якщо агент відповів, зробивши менше, він відповів «з пам'яті».

1. **Створіть** файл `make_task.py`. Нижче приклад для варіанта 3 (доставка). **Замініть** у ньому імпорти, `ITEMS`, `QUESTION` і `cost_of_one()` за даними зі свого рядка таблиці 6. Питання будуйте за шаблоном: *«Для кожної з шести позицій: [перелік]. Для кожної: (а) знайди в корпусі [що саме] і наведи одним реченням; (б) знайди в довіднику [поле]; (в) порахуй [величина]. У кінці назви [підсумок] одним числом»*.

   ```python
   """Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.

   Запуск:  python make_task.py

   Приклад нижче - для варіанта 3 (доставка). Для свого варіанта замініть:
   імпорти, список ITEMS, текст QUESTION і функцію compute().
   """
   import json

   # Беремо власні функції-інструменти з tools.py. ЗАМІНІТЬ на свої.
   from tools import calculate, get_tariff

   # Шість позицій. У варіанті 3 кожна позиція - пара (місто, вага посилки в кг).
   ITEMS = [("Київ", 2.0), ("Львів", 1.5), ("Харків", 3.0),
            ("Одеса", 1.0), ("Дніпро", 2.5), ("Запоріжжя", 4.0)]

   # Питання для агента. У ньому має бути перелік усіх шести позицій.
   QUESTION = (
       "Для кожної з шести посилок: Київ 2.0 кг, Львів 1.5 кг, Харків 3.0 кг, Одеса 1.0 кг, "
       "Дніпро 2.5 кг, Запоріжжя 4.0 кг. Для кожної: (а) знайди в правилах доставки, що сказано "
       "про місто, і наведи одним реченням; (б) знайди в довіднику тариф міста; "
       "(в) порахуй вартість доставки як вагу, помножену на тариф. "
       "У кінці назви загальну вартість усіх шести посилок одним числом."
   )

   # Мінімум викликів інструментів для повного розв'язання: шість позицій по три інструменти.
   MIN_CALLS = 18


   def cost_of_one(city, weight):
       """Вартість доставки однієї посилки: вага, помножена на тариф міста."""
       tariff = get_tariff(city)                       # тариф з довідника
       return float(calculate(f"{weight} * {tariff}"))  # множення через калькулятор


   def compute():
       """Правильна відповідь: сума по всіх шести позиціях. Рахуємо самі, без моделі."""
       total = 0.0
       for city, weight in ITEMS:
           total = total + cost_of_one(city, weight)
       return total


   def save_task(total):
       """Записує питання, правильну відповідь і MIN_CALLS у файл long_task.json."""
       task = {
           "id": "L1",
           "question": QUESTION,
           "expected": format(round(total, 2), "g"),   # число як текст, без зайвих нулів: 142.5
           "min_calls": MIN_CALLS,
       }
       with open("long_task.json", "w", encoding="utf-8") as f:
           json.dump(task, f, ensure_ascii=False, indent=2)
       return task


   task = save_task(compute())
   print("Правильна відповідь:", task["expected"])
   print("Файл long_task.json записано")
   ```

   Вимоги: кожна позиція вимагає всіх трьох інструментів; якщо потрібного поля в довіднику немає, візьміть інше числове; результат пошуку по корпусу **не скорочуйте** в `tools.py`.

2. **Виконайте** скрипт і перевірте, що в `long_task.json` є `question`, `expected` і `min_calls`:

   ```
   python make_task.py
   ```

3. **Запишіть** у звіт питання і правильну відповідь. Після першого прогону `expected` не змінюйте.

### Крок 3. Запуск без захисту

**Що робимо і навіщо.** Запускаємо довгу задачу на агентові без жодного захисту: це точка відліку для всього наступного. Для цього виклик моделі виноситься з `agent.py` в окремий `model.py` (далі там з'явиться кеш), а ліміт кроків стає параметром. У `model.py` також ловимо **помилку сервера**: коли вхід не влазить у вікно, сервер може відмовити. Без цього програма впала б, а лог не зберіг би, що сталося.

1. **Створіть** файл `model.py`. **Клієнт** - об'єкт бібліотеки `openai`, через який програма звертається до сервера (адреса й ключ - з `config.py`). `call_model` робить один виклик і повертає пару: відповідь і позначку «взято з кешу» (поки завжди `False`):

   ```python
   """Виклик моделі. Тут же створюється клієнт, через який агент звертається до сервера."""
   from langfuse.openai import OpenAI

   import config
   from schemas import SCHEMAS

   # Клієнт: адреса сервера й ключ беруться з config.py.
   # Версія OpenAI з langfuse автоматично записує кожен виклик у трасу.
   client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)


   def call_model(messages, step, logger):
       """Один виклик моделі. Повертає пару (відповідь, чи_взято_з_кешу).

       Якщо сервер повернув помилку (наприклад, вхід задовгий), пишемо її в лог
       і повертаємо (None, False): програма не падає, а агент завершує прогін.
       """
       try:
           response = client.chat.completions.create(
               model=config.MODEL,
               messages=messages,
               tools=SCHEMAS,
               temperature=config.TEMPERATURE,
           )
           # другий елемент пари - «відповідь узято з кешу». Кешу ще немає, тому False
           return response, False
       except Exception as error:                  # будь-яка помилка під час виклику
           logger.error(f"\n--- крок {step} | ПОМИЛКА СЕРВЕРА: {error}")
           return None, False
   ```

2. **Внесіть** у `agent.py` шість правок. Імпорти (клієнт і схеми тепер потрібні `model.py`, а не агентові):

   Видаліть із `agent.py` рядок:

   ```python
   from langfuse.openai import OpenAI
   ```

   У `agent.py` замініть:

   ```python
   from schemas import SCHEMAS
   ```

   на:

   ```python
   from model import call_model
   ```

   Видаліть із `agent.py` рядок:

   ```python
   client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
   ```

   Ліміт кроків стає параметром (якщо не задано, береться `MAX_STEPS`, тож `agent_runner.py` працює як раніше):

   У `agent.py` замініть:

   ```python
   def run_agent(task):
       """task – питання користувача
       Повертає текст відповіді або None, якщо вичерпано ліміт."""
       logger = custom_logger(config.LAB_LOGFILE_NAME)
   ```

   на:

   ```python
   def run_agent(task, max_steps=None, logfile_name=config.LAB_LOGFILE_NAME, log_overwrite=False):
       """task – питання користувача
       Повертає текст відповіді або None, якщо вичерпано ліміт."""
       max_steps = max_steps or config.MAX_STEPS
       logger = custom_logger(logfile_name, overwrite=log_overwrite)
   ```

   Виклик моделі через `call_model`; якщо сервер повернув помилку, її вже записано в лог, і агент завершується:

   У `agent.py` замініть:

   ```python
       for step in range(1, config.MAX_STEPS + 1):
           response = client.chat.completions.create(
               model=config.MODEL,
               messages=messages,
               tools=SCHEMAS,
               temperature=config.TEMPERATURE,
           )
   ```

   на:

   ```python
       for step in range(1, max_steps + 1):
           response, from_cache = call_model(messages, step, logger)
           if response is None:                  # сервер повернув помилку (вона вже записана в лог)
               return None
   ```

   Заголовок кроку в лозі. `completion_tokens` - скільки токенів згенерувала сама модель; позначка «з кешу» знадобиться в кроці 7:

   У `agent.py` замініть:

   ```python
               f"| prompt_tokens={response.usage.prompt_tokens}")
   ```

   на:

   ```python
               f"| prompt_tokens={response.usage.prompt_tokens} "
               f"| completion_tokens={response.usage.completion_tokens}"
               + (" | з кешу" if from_cache else ""))
   ```

3. **Виконайте** перевірку, агент має відповісти без помилок:

   ```
   python agent.py
   ```

4. **Створіть** файл `measure.py`. Він запускає довгу задачу, перевіряє відповідь за `expected` і пише окремий лог кожного прогону: `logs\<серія>_<конфігурація>_r<повтор>.log`. **Конфігурація** - набір налаштувань `config.py`, які скрипт виставляє перед прогоном (зараз лише `none` - «нічого не скорочувати»). **Серія** - назва групи прогонів (`probe` - пробна, `main` - основна). Параметри запуску: конфігурація (або `all`), кількість повторів, серія:

   ```python
   """Запуск довгої задачі в заданій конфігурації.

   Запуск:
       python measure.py none 1 probe
   де none - конфігурація, 1 - кількість повторів, probe - назва серії.
   Лог кожного прогону: logs/<серія>_<конфігурація>_r<повтор>.log
   """
   import json
   import os
   import sys
   import time

   from langfuse import get_client, propagate_attributes

   import agent
   import config

   # Конфігурації: які налаштування config змінюємо перед прогоном
   CONFIGS = {
       "none": {"COMPRESS": "none"},
   }


   def read_arguments():
       """Читає параметри запуску. Повертає (список конфігурацій, кількість повторів, серія)."""
       which = sys.argv[1] if len(sys.argv) > 1 else "all"
       repeats = int(sys.argv[2]) if len(sys.argv) > 2 else 3
       series = sys.argv[3] if len(sys.argv) > 3 else "main"
       names = list(CONFIGS) if which == "all" else [which]
       return names, repeats, series


   def load_task():
       """Читає довгу задачу з файла long_task.json."""
       with open("long_task.json", encoding="utf-8") as f:
           return json.load(f)


   def is_correct(answer, expected):
       """Чи є очікуване число у відповіді. Неправильні відповіді перевіряйте вручну."""
       if not answer:
           return False
       text = answer.replace(" ", "").replace(",", ".")     # прибираємо пробіли, кому міняємо на крапку
       return str(expected) in text


   def run_once(name, repeat, series, task):
       """Один прогін агента. Повертає (номер прогону, відповідь, час у секундах)."""
       for key, value in CONFIGS[name].items():             # застосовуємо налаштування конфігурації
           setattr(config, key, value)
       run_id = f"{series}_{name}_r{repeat}"                # наприклад: probe_none_r1

       started = time.time()
       # propagate_attributes дає трасі в Langfuse назву й мітки
       with propagate_attributes(trace_name=f"long-{run_id}", tags=[series, name]):
           answer = agent.run_agent(task=task["question"],
                                    max_steps=config.MAX_STEPS_LONG,
                                    logfile_name=run_id,
                                    log_overwrite=True)
       return run_id, answer, round(time.time() - started, 1)


   def main():
       names, repeats, series = read_arguments()
       task = load_task()
       os.makedirs("logs", exist_ok=True)

       for repeat in range(1, repeats + 1):                 # повтори - зовнішній цикл,
           for name in names:                               # тож конфігурації чергуються
               run_id, answer, seconds = run_once(name, repeat, series, task)
               right = is_correct(answer, task["expected"])
               print(f"\n[{run_id}] час {seconds} с | правильно: {'так' if right else 'ні'}")
               print(f"[{run_id}] відповідь: {(answer or '').replace(chr(10), ' ')[:200]}")

       get_client().flush()                                 # дочекатися відправки трас у Langfuse


   if __name__ == "__main__":
       main()
   ```

5. **Виконайте** один прогін без захисту і **запишіть** у звіт, чи правильна відповідь і скільки секунд тривав прогін (неправильна відповідь - нормально, це те, що ми досліджуємо):

   ```
   python measure.py none 1 probe
   ```

### Крок 4. Де ламається вікно

**Що робимо і навіщо.** Дивимось на пробний прогін зсередини. На кожному кроці модель отримує **всю** історію знову, тому її вхід (`prompt_tokens`) росте з кожним викликом, а сума входів за прогін - ще швидше (приблизно як квадрат кількості кроків). Коли історія більша за вікно, можливі два сценарії: сервер повертає помилку (легко помітити) або **мовчки відкидає початок історії**, і агент «забуває» запитання та інструменти без жодної помилки. Ознака другого - вхід перестав рости, хоча агент продовжує додавати повідомлення. Скрипти цього кроку шукають саме її.

1. **Створіть** файл `logparse.py`. Лог - це текст, а нам потрібні числа з нього. Цей файл ділить лог на прогони й кроки та дістає токени, виклики інструментів і статус завершення:

   ```python
   """Читання лога прогону: розбір тексту лога на прогони та кроки.

   Лог - це звичайний текстовий файл, який пише агент. У ньому є рядки такого вигляду:
       --- крок 3 | помилок поспіль=0 | prompt_tokens=1250 | completion_tokens=30
         виклик   : search({"query": "..."})
         СТИСНЕННЯ: вхід був 2900 токенів, повідомлень 14 -> 8
       ВІДПОВІДЬ: ...
   Скрипт шукає такі рядки за зразками (регулярними виразами) і складає з них числа.
   """
   import re


   def find_status(block):
       """Як закінчився прогін. Визначаємо за рядками, які агент пише наприкінці."""
       if "ПОМИЛКА СЕРВЕРА" in block:
           return "server_error"                    # сервер повернув помилку
       if re.search(r"^ВІДПОВІДЬ:", block, flags=re.M):
           return "final"                           # модель дала відповідь без виклику інструмента
       if "СТОП: модель не змогла" in block:
           return "retry_limit"                     # забагато помилок моделі поспіль
       if "СТОП: вичерпано ліміт кроків" in block:
           return "step_limit"                      # закінчилися кроки
       return "unknown"


   def parse_step(chunk):
       """Розбирає один крок: текст від слів «--- крок» до наступного кроку."""
       first_line = chunk.split("\n", 1)[0]                          # заголовок кроку
       prompt = re.search(r"prompt_tokens=(\d+)", first_line)
       completion = re.search(r"completion_tokens=(\d+)", first_line)
       squeeze = re.search(r"^  СТИСНЕННЯ: вхід був (\d+) токенів, повідомлень (\d+) -> (\d+)",
                           chunk, flags=re.M)
       extra = re.findall(r"підсумовування коштувало (\d+) токенів", chunk)   # для додаткового завдання
       return {
           "n": int(re.match(r"\d+", chunk).group()),                # номер кроку
           "tokens": int(prompt.group(1)) if prompt else None,       # токенів на вході моделі
           "completion": int(completion.group(1)) if completion else 0,
           "from_cache": "з кешу" in first_line,                     # відповідь узято з кешу
           "calls": re.findall(r"^  виклик   : (.*)$", chunk, flags=re.M),   # виклики інструментів
           "answer": bool(re.search(r"^ВІДПОВІДЬ:", chunk, flags=re.M)),
           "server_error": "ПОМИЛКА СЕРВЕРА" in first_line,
           "squeeze": tuple(int(x) for x in squeeze.groups()) if squeeze else None,
           "extra": sum(int(x) for x in extra),
       }


   def parse_run(block):
       """Розбирає один прогін: текст від слова «ЗАДАЧА:» до наступного прогону."""
       chunks = re.split(r"^--- крок ", block, flags=re.M)[1:]       # по одному шматку на крок
       return {
           "task": block.split("\n", 1)[0],                          # текст задачі
           "status": find_status(block),
           "steps": [parse_step(chunk) for chunk in chunks],
       }


   def parse_log(text):
       """Ділить лог на прогони. У логу agent_runner.py їх п'ять, у логу measure.py - один."""
       # логер додає на початок рядка «2026-10-20 11:26:38 - INFO - », прибираємо його
       text = re.sub(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - [A-Z]+ - ", "", text, flags=re.M)
       blocks = re.split(r"^ЗАДАЧА: ", text, flags=re.M)[1:]
       return [parse_run(block) for block in blocks]
   ```

2. **Створіть** файл `metrics.py`. Він рахує показники прогону: вхід першого кроку, типовий приріст, крок, на якому вхід застиг, повторні виклики (той самий інструмент з тими самими аргументами), суму токенів і значення за формулою з лекції:

   ```python
   """Показники прогону, які рахуються з розібраного лога (див. logparse.py)."""
   import statistics

   import config


   def count_repeats(steps):
       """Рахує повторні виклики: той самий інструмент з тими самими аргументами, що вже були."""
       seen = set()                                  # виклики, які вже траплялися
       repeats = 0
       for step in steps:
           for call in step["calls"]:
               if call in seen:
                   repeats += 1
               seen.add(call)
       return repeats


   def typical_growth(tokens):
       """Типовий приріст входу за крок: медіана всіх додатних збільшень.

       tokens - список пар (номер кроку, prompt_tokens).
       """
       growth = [after - before
                 for (_, before), (_, after) in zip(tokens, tokens[1:])
                 if after > before]
       return statistics.median(growth) if growth else 0


   def find_stall(tokens, typical):
       """Шукає крок, на якому вхід підійшов до межі вікна і майже не росте.

       Це ознака того, що сервер мовчки обрізає вхід.
       """
       for (_, before), (number, after) in zip(tokens, tokens[1:]):
           near_window = after >= 0.8 * config.NUM_CTX      # вхід уже займає понад 80% вікна
           stopped = after - before <= 0.2 * typical        # а росте менш ніж на п'яту частину норми
           if near_window and stopped:
               return number
       return None


   def describe(run):
       """Збирає всі показники одного прогону в один словник."""
       steps = run["steps"]
       tokens = [(s["n"], s["tokens"]) for s in steps if s["tokens"] is not None]
       typical = typical_growth(tokens)
       n = len(tokens)
       first = tokens[0][1] if tokens else 0
       return {
           "status": run["status"],
           "steps": n,                                              # скільки разів викликали модель
           "repeats": count_repeats(steps),
           "first_tokens": first,                                   # вхід першого кроку
           "typical_growth": typical,
           "max_tokens": max((t for _, t in tokens), default=0),
           "prompt_tokens": sum(t for _, t in tokens),              # сума входів за прогін
           "completion_tokens": sum(s["completion"] for s in steps),
           "extra_tokens": sum(s["extra"] for s in steps),          # знадобиться в додатковому завданні
           "formula": n * first + typical * n * (n - 1) / 2,        # формула з лекції 7
           "stall": find_stall(tokens, typical),
           "cache_hits": sum(1 for s in steps if s["from_cache"]),
           "squeezes": [s for s in steps if s["squeeze"]],          # кроки, після яких історію скорочували
       }
   ```

3. **Створіть** файл `analyze.py`. Він друкує показники прогону і, за ключем `steps`, таблицю «що відбувалося на кожному кроці»:

   ```python
   r"""Розбір логів прогонів: що відбувалося з входом моделі.

   Запуск:
       python analyze.py logs\probe_none_r1.log           підсумок прогону
       python analyze.py logs\probe_none_r1.log steps     підсумок і таблиця за кроками
   """
   import os
   import sys

   import config
   from logparse import parse_log
   from metrics import describe


   def action_lines(step):
       """Коротко: що зробила модель на цьому кроці. Кожен виклик - окремим рядком."""
       if step["server_error"]:
           return ["ПОМИЛКА СЕРВЕРА"]
       if step["calls"]:
           return [c if len(c) < 60 else c[:57] + "..." for c in step["calls"]]
       if step["answer"]:
           return ["відповідь без виклику"]
       return ["відхилено перевіркою (див. лог)"]


   def print_steps(run):
       """Друкує таблицю: крок, prompt_tokens, приріст, що зробила модель."""
       header = ["Крок", "prompt_tokens", "Приріст", "Що зробила модель"]
       rows = []
       previous = None
       for s in run["steps"]:
           growth = ""
           if previous is not None and s["tokens"] is not None:
               growth = s["tokens"] - previous
           actions = action_lines(s)
           rows.append([str(s["n"]), str(s["tokens"]), str(growth), actions[0]])
           rows += [["", "", "", a] for a in actions[1:]]   # решта викликів кроку
           if s["tokens"] is not None:
               previous = s["tokens"]
   
       # ширина колонки - за найдовшим значенням; числа вирівнюємо праворуч
       widths = [max(len(r[i]) for r in [header] + rows) for i in range(len(header))]
       right = [True, True, True, False]
   
       def line(cells):
           parts = [c.rjust(w) if r else c.ljust(w) for c, w, r in zip(cells, widths, right)]
           return "| " + " | ".join(parts) + " |"
   
       print()
       print(line(header))
       print("|" + "|".join("-" * (w + 1) + ":" if r else ":" + "-" * (w + 1)
                            for w, r in zip(widths, right)) + "|")
       for r in rows:
           print(line(r))


   def print_summary(run):
       """Друкує показники одного прогону."""
       d = describe(run)
       print(f"  статус завершення            : {d['status']}")
       print(f"  кроків                       : {d['steps']} (повторних викликів: {d['repeats']})")
       print(f"  вхід першого кроку           : {d['first_tokens']} токенів")
       print(f"  типовий приріст за крок      : {d['typical_growth']:.0f} токенів")
       print(f"  найбільший вхід              : {d['max_tokens']} токенів "
             f"({d['max_tokens'] / config.NUM_CTX:.0%} вікна {config.NUM_CTX})")
       print(f"  сума prompt_tokens за прогін : {d['prompt_tokens']}")
       print(f"  за формулою n*C + d*n*(n-1)/2: {d['formula']:.0f}")
       print(f"  вхід перестав рости на кроці : {d['stall'] or 'не помічено'}")
       print(f"  влучань у кеш                : {d['cache_hits']}")
       for s in d["squeezes"]:
           before, msgs_before, msgs_after = s["squeeze"]
           print(f"  стиснення на кроці {s['n']}: вхід був {before}, "
                 f"повідомлень {msgs_before} -> {msgs_after}")


   if __name__ == "__main__":
       if len(sys.argv) < 2:
           sys.exit(__doc__)
   
       # відносний шлях рахуємо від теки скрипта, щоб не залежати від робочої теки
       path_to_log = os.path.join(os.path.dirname(os.path.abspath(__file__)), sys.argv[1])
       with open(path_to_log, encoding="utf-8") as f:
           runs = parse_log(f.read())
   
       for run in runs:
           print(f"\nПрогін: {run['task'][:60]}")
           print_summary(run)
           if len(sys.argv) > 2 and sys.argv[2] == "steps":
               print_steps(run)
   ```

4. **Виконайте** розбір пробного прогону:

   ```
   python analyze.py logs\probe_none_r1.log steps
   ```

5. **Заповніть** таблицю 2: перенесіть у неї таблицю за кроками з виведення.

   Таблиця 2 - Зростання входу в прогоні без захисту

   | Крок | `prompt_tokens` | Приріст | Що зробила модель |
   |------|-----------------|---------|-------------------|
   | 1    |                 |         |                   |
   | ...  |                 |         |                   |

6. **Визначте** за виведенням `analyze.py` і **запишіть у звіт**:
   - **(а)** постійну частину входу - «вхід першого кроку»;
   - **(б)** типовий приріст за крок;
   - **(в)** суму `prompt_tokens` за прогін і значення за формулою. Якщо числа сильно відрізняються, поясніть чому;
   - **(г)** крок, на якому вхід перестав рости - «вхід перестав рости на кроці»;
   - **(д)** що робила модель на трьох кроках після кроку (г): повторює той самий виклик, викликає інший інструмент чи відповідає без виклику. **Відкрийте** `logs\probe_none_r1.log`, прочитайте ці кроки та відповідь і перевірте, чи є в відповіді числа, яких не було в результатах інструментів.

7. **Віднесіть** прогін до одного з випадків:

   | Що показав `analyze.py`                                 | Випадок                                | Що зробити                                                                   |
   |---------------------------------------------------------|----------------------------------------|------------------------------------------------------------------------------|
   | Статус `server_error`                                   | A. Сервер повернув помилку про довжину | Запишіть у звіт текст помилки з рядка `ПОМИЛКА СЕРВЕРА` та номер кроку       |
   | «вхід перестав рости на кроці N»                        | B. Сервер мовчки обрізає вхід          | Виконайте пункт (д)                                                          |
   | Найбільший вхід менший за 95% вікна, статус `final`     | C. Задача закоротка                    | Зменште вікно (нижче) і повторіть пункт 5 кроку 3 та пункти 4-6 цього кроку  |
   | Інше: статус не `final`, помилки сервера й застою немає | D. Агент зламався не через вікно       | Знайдіть причину за таблицею поламок з лабораторної роботи № 2 і запишіть її |

   Для випадку C:
   - **змініть** у `Modelfile` `num_ctx` на `3072`
   - **виконайте** `ollama create llama32-3k -f Modelfile`
   - у `config.py` **задайте** `MODEL = "llama32-3k"` і `NUM_CTX = 3072`.
   
   Далі працюйте з цими значеннями (у звіті вказуйте 3072).

### Крок 5. Обрізання історії

**Що робимо і навіщо.** Перший захист - **обрізання** (*trim*): коли вхід наближається до межі вікна, програма відкидає старі повідомлення й лишає початок історії та кілька останніх. Вхід перестає рости. Ціна: агент забуває результати відкинутих повідомлень і може викликати ті самі інструменти вдруге. Поведінка вмикається налаштуванням `COMPRESS`, тож обидва варіанти можна порівняти на одній задачі однією командою (таблиця 1).

Таблиця 1 - Конфігурації агента

| Назва        | `COMPRESS` | `USE_STATE` | Що робить агент, коли вхід перевищив `COMPRESS_AT`                             |
|--------------|------------|-------------|--------------------------------------------------------------------------------|
| `none`       | `"none"`   | `False`     | Нічого: історія росте далі                                                     |
| `trim`       | `"trim"`   | `False`     | Відкидає старі повідомлення                                                    |
| `trim+state` | `"trim"`   | `True`      | Відкидає старі повідомлення і додає до запитання список збережених результатів |

1. **Додайте** в `config.py` параметри скорочення. `COMPRESS` - режим (його перемикає `measure.py`). `COMPRESS_AT` - поріг: скорочуємо, коли вхід його перевищив; він менший за вікно, бо після скорочення агент зробить ще виклик, а відповідь моделі теж займає місце у вікні. `KEEP_LAST` - скільки останніх повідомлень лишити. Для вікна 3072 задайте `COMPRESS_AT = 2150`.

   Додайте в кінець `config.py`:

   ```python
   COMPRESS = "none"       # "none" або "trim": скорочувати історію чи ні
   COMPRESS_AT = 2800      # скорочуємо, коли prompt_tokens перевищив це число
   KEEP_LAST = 6           # скільки останніх повідомлень лишати при обрізанні
   ```

2. **Створіть** файл `context.py` - власне обрізання. Два перші повідомлення (інструкція й запитання) не чіпаємо: без них модель не знає, хто вона й про що її питали. `drop_orphan_tools` потрібна, бо результат інструмента не може стояти в історії без повідомлення моделі з відповідним викликом - сервер видасть помилку:

   ```python
   """Скорочення історії повідомлень.

   Історія - це список повідомлень messages. Кожне повідомлення - словник з ключем "role"
   (хто говорить: "system", "user", "assistant" або "tool") і текстом "content".
   """


   def drop_orphan_tools(tail):
       """Прибирає з початку списку «осиротілі» результати інструментів.

       Результат інструмента (role = "tool") має стояти одразу після повідомлення моделі
       з відповідним викликом. Якщо виклик ми відрізали, а результат лишили, сервер видасть
       помилку або модель не зрозуміє, на що це відповідь. Тому такі результати відкидаємо.
       """
       while tail and tail[0]["role"] == "tool":    # поки перше повідомлення - результат інструмента
           tail = tail[1:]                          # відкидаємо його (беремо список без першого)
       return tail


   def trim(messages, keep_last):
       """Скорочує історію: лишає початок і останні keep_last повідомлень.

       Початок - це два перші повідомлення: системна інструкція і запитання користувача.
       Без них модель не знає, хто вона і про що її питали, тому їх не чіпаємо.
       """
       head = messages[:2]                          # перші два повідомлення
       tail = messages[2:][-keep_last:]             # з решти беремо лише останні keep_last
       tail = drop_orphan_tools(tail)               # не починаємо «хвіст» з результату без виклику
       return head + tail                           # склеюємо початок і хвіст в один список
   ```

3. **Створіть** файл `compress.py`. `compress_history` вирішує, чи вже час скорочувати, і викликає потрібний спосіб. Кожне стиснення пишеться в лог рядком `СТИСНЕННЯ:`:

   ```python
   """Скорочення історії, коли вхід став завеликим."""
   import config
   from context import trim


   def compress_by_trim(messages, used, logger):
       """Обрізає історію (див. context.py) і записує в лог, що сталося."""
       before = len(messages)
       messages = trim(messages, config.KEEP_LAST)
       logger.info(f"  СТИСНЕННЯ: вхід був {used} токенів, повідомлень {before} -> {len(messages)}")
       return messages


   def compress_history(messages, used, logger):
       """Скорочує історію, якщо вхід перевищив поріг COMPRESS_AT. Повертає (нову) історію."""
       if used <= config.COMPRESS_AT:               # вхід ще малий: нічого не робимо
           return messages
       if config.COMPRESS == "trim":
           return compress_by_trim(messages, used, logger)
       return messages                              # COMPRESS = "none": історія росте далі
   ```

4. **Внесіть** у `agent.py` чотири правки: підключення `compress_history`; перетворення повідомлення моделі на словник (`trim` читає ключ `"role"`, а бібліотека повертає об'єкт); запам'ятовування розміру входу; виклик наприкінці кожного кроку:

   У `agent.py` після рядка:

   ```python
   from model import call_model
   ```

   додайте:

   ```python
   from compress import compress_history
   ```

   У `agent.py` замініть:

   ```python
           messages.append(msg)
   ```

   на:

   ```python
           # зберігаємо повідомлення моделі як словник: trim читає з нього ключ "role"
           messages.append(msg.model_dump(exclude_none=True))
   ```

   У `agent.py` після рядка:

   ```python
           msg = choice.message
   ```

   додайте:

   ```python
           used = response.usage.prompt_tokens       # скільки токенів було на вході цього виклику
   ```

   У `agent.py` після рядків:

   ```python
           else:
               retries = 0
   ```

   додайте:

   ```python
           # якщо вхід завеликий, скорочуємо історію
           messages = compress_history(messages, used, logger)
   ```

5. **Внесіть** у `measure.py` правку: конфігурація `trim`.

   У `measure.py` після рядка:

   ```python
       "none": {"COMPRESS": "none"},
   ```

   додайте:

   ```python
       "trim": {"COMPRESS": "trim"},
   ```

6. **Виконайте** прогін і розбір:

   ```
   python measure.py trim 1 probe
   python analyze.py logs\probe_trim_r1.log
   ```

7. **Заповніть** рядок `trim` таблиці 3 за рядками «стиснення на кроці …» (по рядку на стиснення). Рядок `trim+state` заповните в кроці 6. «Повторних викликів» - рядок «повторних викликів» у виведенні: це ціна обрізання.

Таблиця 3 - Стиснення історії

| Конфігурація | Крок стиснення | Вхід до стиснення, токенів | Повідомлень було -> стало | Повторних викликів за прогін |
|--------------|----------------|----------------------------|---------------------------|------------------------------|
| `trim`       |                |                            |                           |                              |
| `trim+state` |                |                            |                           |                              |

### Крок 6. Стан задачі

**Що робимо і навіщо.** Після обрізання модель не бачить результатів, які вже отримала, і викликає ті самі інструменти знову. Але програма їх бачила. **Стан задачі** - «записник» програми: вона зберігає результат кожного успішного виклику (рівень `ok`) окремо від діалогу, а після обрізання дописує його вміст до запитання користувача. Довгі результати в нагадуванні скорочуються до `STATE_RESULT_CHARS` символів, щоб сам записник не з'їв вікно. Стан також пишеться у файл `state\<прогін>.json` - щоб його можна було переглянути.

1. **Додайте** в `config.py`: `USE_STATE` (чи додавати записник після обрізання; перемикає `measure.py`) і `STATE_RESULT_CHARS`:

   Додайте в кінець `config.py`:

   ```python
   USE_STATE = False       # чи додавати в контекст збережені результати
   STATE_RESULT_CHARS = 200  # довші результати в стані скорочуються до цієї довжини
   ```

2. **Створіть** файл `state.py`. `record` запам'ятовує один успішний виклик і зберігає все у файл, `render` складає з записів текст для моделі:

   ```python
   """Стан задачі: результати успішних викликів інструментів, які зберігає програма.

   Навіщо: коли ми відкидаємо старі повідомлення, модель забуває результати інструментів,
   а програма - ні. Стан - це «записник» програми, з якого можна нагадати моделі потрібне.
   """
   import json
   import os

   import config


   def shorten(text, limit):
       """Обрізає довгий текст до limit символів і додає «...», щоб було видно: це не весь текст."""
       if len(text) > limit:
           return text[:limit] + "..."
       return text


   class TaskState:
       def __init__(self, task_id):
           self.task_id = task_id             # з нього складається ім'я файла: state/<task_id>.json
           self.results = []                  # список записів: {"tool": ..., "args": ..., "result": ...}

       def record(self, name, args_raw, result):
           """Запам'ятовує результат одного успішного виклику інструмента."""
           self.results.append({
               "tool": name,                      # назва інструмента
               "args": json.loads(args_raw),      # аргументи виклику: з тексту JSON у словник
               "result": result,                  # що інструмент повернув
           })
           self.save()

       def save(self):
           """Записує весь стан у файл, щоб його можна було відкрити й подивитися."""
           os.makedirs("state", exist_ok=True)    # створюємо каталог state, якщо його ще немає
           with open(f"state/{self.task_id}.json", "w", encoding="utf-8") as f:
               json.dump(self.results, f, ensure_ascii=False, indent=2)

       def format_item(self, item):
           """Один запис у вигляді рядка: - інструмент(аргументи) -> результат."""
           args = json.dumps(item["args"], ensure_ascii=False)
           result = shorten(item["result"], config.STATE_RESULT_CHARS)   # довгі результати скорочуємо
           return f"- {item['tool']}({args}) -> {result}"

       def render(self):
           """Текст для моделі: заголовок і по рядку на кожен збережений результат."""
           if not self.results:                   # нічого ще не збережено
               return None
           lines = ["Результати вже виконаних викликів (збережені програмою):"]
           for item in self.results:
               lines.append(self.format_item(item))
           return "\n".join(lines)                # з'єднуємо рядки через перенесення рядка
   ```

3. **Замініть** увесь вміст `compress.py` кодом нижче. Додалася `attach_state`, яка дописує записник до запитання; `compress_by_trim` викликає її, якщо `USE_STATE` увімкнено:

   ```python
   """Скорочення історії, коли вхід став завеликим."""
   import config
   from context import trim


   def attach_state(messages, task, state):
       """Дописує до запитання користувача список збережених результатів (див. state.py)."""
       note = state.render()
       if note:                                     # якщо в стані вже щось є
           # messages[1] - це запитання користувача (друге повідомлення в історії)
           messages[1] = {"role": "user", "content": task + "\n\n" + note}
       return messages


   def compress_by_trim(messages, task, used, state, logger):
       """Обрізає історію і, якщо ввімкнено стан, додає його до запитання."""
       before = len(messages)
       messages = trim(messages, config.KEEP_LAST)
       if config.USE_STATE:
           messages = attach_state(messages, task, state)
       logger.info(f"  СТИСНЕННЯ: вхід був {used} токенів, повідомлень {before} -> {len(messages)}"
           + (", стан додано" if config.USE_STATE else ""))
       if config.USE_STATE:
           logger.info("  ПЕРШЕ ПОВІДОМЛЕННЯ КОРИСТУВАЧА ПІСЛЯ СТИСНЕННЯ:\n" + messages[1]["content"])
       return messages


   def compress_history(messages, task, used, state, logger):
       """Скорочує історію, якщо вхід перевищив поріг COMPRESS_AT. Повертає (нову) історію."""
       if used <= config.COMPRESS_AT:               # вхід ще малий: нічого не робимо
           return messages
       if config.COMPRESS == "trim":
           return compress_by_trim(messages, task, used, state, logger)
       return messages                              # COMPRESS = "none": історія росте далі
   ```

4. **Внесіть** у `agent.py` п'ять правок: імпорт; параметр `task_id` (за ним називається файл стану); створення записника; запис у нього після кожного успішного виклику; передача запитання й записника у `compress_history`:

   У `agent.py` після рядка:

   ```python
   from compress import compress_history
   ```

   додайте:

   ```python
   from state import TaskState
   ```

   У `agent.py` замініть:

   ```python
   def run_agent(task, max_steps=None, logfile_name=config.LAB_LOGFILE_NAME, log_overwrite=False):
   ```

   на:

   ```python
   def run_agent(task, max_steps=None, logfile_name=config.LAB_LOGFILE_NAME, task_id="task", log_overwrite=False):
   ```

   У `agent.py` перед рядком:

   ```python
       logger.info(f"\n{'=' * 60}")
   ```

   додайте:

   ```python
       state = TaskState(task_id)                # записник результатів інструментів
   ```

   У `agent.py` після рядків:

   ```python
                   "content": result,
               })
   ```

   додайте:

   ```python
               # у стан потрапляють лише успішні виклики
               if level == "ok":
                   state.record(call.function.name, call.function.arguments, result)
   ```

   У `agent.py` замініть:

   ```python
   messages = compress_history(messages, used, logger)
   ```

   на:

   ```python
   messages = compress_history(messages, task, used, state, logger)
   ```

5. **Внесіть** у `measure.py` дві правки: конфігурація `trim+state` (із явним `USE_STATE` у кожній, щоб налаштування не «протікало» в наступний прогін) і передача номера прогону агентові:

   У `measure.py` замініть:

   ```python
       "none": {"COMPRESS": "none"},
       "trim": {"COMPRESS": "trim"},
   ```

   на:

   ```python
       "none":       {"COMPRESS": "none", "USE_STATE": False},
       "trim":       {"COMPRESS": "trim", "USE_STATE": False},
       "trim+state": {"COMPRESS": "trim", "USE_STATE": True},
   ```

   У `measure.py` замініть:

   ```python
   answer = agent.run_agent(task=task["question"], max_steps=config.MAX_STEPS_LONG, logfile_name=run_id, log_overwrite=True)
   ```

   на:

   ```python
   answer = agent.run_agent(task=task["question"],
                            max_steps=config.MAX_STEPS_LONG,
                            logfile_name=run_id,
                            task_id=run_id,
                            log_overwrite=True)
   ```

6. **Виконайте** прогін і розбір, **заповніть** рядок `trim+state` таблиці 3:

   ```
   python measure.py trim+state 1 probe
   python analyze.py logs\probe_trim+state_r1.log
   ```

7. **Відкрийте** `logs\probe_trim+state_r1.log`, знайдіть перший блок `ПЕРШЕ ПОВІДОМЛЕННЯ КОРИСТУВАЧА ПІСЛЯ СТИСНЕННЯ` і **запишіть у звіт**: скільки в ньому рядків виду `- інструмент(аргументи) -> результат` і чи завеликий цей блок (порівняйте його розмір у токенах - 2,5 символа на токен - із типовим приростом за крок з кроку 4).

### Крок 7. Кеш викликів моделі

**Що робимо і навіщо.** **Кеш** запам'ятовує відповідь моделі на запит і при такому самому запиті віддає її без звернення до сервера: повторні запуски (наприклад, під час налагодження) стають миттєвими. **Ключ кешу** - «відбиток» запиту: програма перетворює запит на текст і рахує від нього хеш `sha256`; однаковий запит дає однаковий відбиток, а кожному відбитку відповідає файл у каталозі `cache`. Змінилося хоч щось у запиті (інструкція, історія, модель) - це вже інший запит, і кеш не спрацює. Кеш вмикається лише в серіях, назва яких починається з `cache`; в основному вимірюванні він вимкнений, інакше повтори брали б відповіді з кешу і вартість була б нульовою.

1. **Додайте** в `config.py` перемикач кешу (`measure.py` вмикає його сам за назвою серії):

   Додайте в кінець `config.py`:

   ```python
   USE_CACHE = False       # чи кешувати виклики моделі
   ```

2. **Створіть** файл `cache.py`. `make_key` рахує відбиток; `read_cache` і `write_cache` читають і зберігають відповідь у файл; `ask_model` поєднує все: є файл - повертає відповідь з нього, немає - звертається до сервера й зберігає результат:

   ```python
   """Кеш викликів моделі: однаковий запит не надсилається на сервер вдруге.

   Кеш - це каталог cache/. Кожна відповідь моделі лежить в окремому файлі, ім'я якого
   залежить від запиту. Однаковий запит дає однакове ім'я файла, і відповідь береться з нього.
   """
   import hashlib
   import json
   import os

   from openai.types.chat import ChatCompletion

   import config


   def make_key(request):
       """Робить з запиту «відбиток» - довгий рядок із літер і цифр, однаковий для однакових запитів.

       Запит (модель, повідомлення, інструменти, температура) перетворюється на текст JSON,
       а з тексту hashlib.sha256 рахує відбиток. Змінилась хоч одна літера - відбиток інший.
       """
       text = json.dumps(request, sort_keys=True, ensure_ascii=False, default=str)
       return hashlib.sha256(text.encode("utf-8")).hexdigest()


   def read_cache(path):
       """Читає збережену відповідь з файла й повертає її як об'єкт відповіді сервера."""
       with open(path, encoding="utf-8") as f:
           return ChatCompletion.model_validate(json.load(f))


   def write_cache(path, response):
       """Зберігає відповідь сервера у файл."""
       os.makedirs("cache", exist_ok=True)        # створюємо каталог cache, якщо його ще немає
       with open(path, "w", encoding="utf-8") as f:
           json.dump(response.model_dump(), f, ensure_ascii=False)


   def ask_model(client, **request):
       """Викликає модель (через кеш, якщо він увімкнений).

       Повертає пару: (відповідь, True, якщо відповідь узято з кешу).
       """
       if not config.USE_CACHE:                   # кеш вимкнений: просто звертаємось до сервера
           return client.chat.completions.create(**request), False

       path = f"cache/{make_key(request)}.json"
       if os.path.exists(path):                   # такий запит уже був: беремо відповідь з файла
           return read_cache(path), True

       response = client.chat.completions.create(**request)   # такого запиту ще не було
       write_cache(path, response)                             # запам'ятовуємо відповідь на майбутнє
       return response, False
   ```

3. **Внесіть** у `model.py` дві правки: `call_model` тепер викликає `ask_model` замість сервера напряму.

   У `model.py` після рядка:

   ```python
   from schemas import SCHEMAS
   ```

   додайте:

   ```python
   from cache import ask_model
   ```

   У `model.py` замініть:

   ```python
           response = client.chat.completions.create(
               model=config.MODEL,
               messages=messages,
               tools=SCHEMAS,
               temperature=config.TEMPERATURE,
           )
           # другий елемент пари - «відповідь узято з кешу». Кешу ще немає, тому False
           return response, False
   ```

   на:

   ```python
           return ask_model(client, model=config.MODEL, messages=messages,
                            tools=SCHEMAS, temperature=config.TEMPERATURE)
   ```

4. **Внесіть** у `measure.py` правку: серії `cache*` вмикають кеш.

   У `measure.py` після рядка:

   ```python
       names, repeats, series = read_arguments()
   ```

   додайте:

   ```python
       config.USE_CACHE = series.startswith("cache")      # кеш вмикають лише серії, назва яких починається з cache
   ```

5. **Виконайте** два однакових прогони поспіль (перед першим кеш очищується). Другий має бути майже миттєвим:

   ```
   # Powershell: Remove-Item -Recurse -Force cache
   # bash: rm -rf cache
   rmdir /S /Q cache
   python measure.py none 1 cache1
   python analyze.py logs\cache1_none_r1.log
   python measure.py none 1 cache2
   python analyze.py logs\cache2_none_r1.log
   ```

   Якщо каталогу `cache` ще немає, `rmdir` виведе повідомлення про помилку: це нормально.

6. **Заповніть** таблицю 4. «Кроків» і «Влучань у кеш» - з виведення `analyze.py`; «Викликів до сервера» - кроків мінус влучань; «Час» і «Правильно» - з рядка `[cache1_none_r1] час ...` у виведенні `measure.py`.

   Таблиця 4 - Робота кешу
   
   | Запуск              | Кроків | Влучань у кеш | Викликів до сервера | Час, с | Правильно |
   |---------------------|--------|---------------|---------------------|--------|-----------|
   | 1 (кеш порожній)    |        |               |                     |        |           |
   | 2 (той самий запит) |        |               |                     |        |           |

7. **Запишіть** у звіт: у скільки разів запуск 2 швидший за запуск 1 (якщо час 0, напишіть «практично миттєво») і що б сталося, якби перед запуском 2 змінити текст `SYSTEM` у `config.py`.

### Крок 8. Вимірювання і траси

**Що робимо і навіщо.** Порівнюємо `none`, `trim` і `trim+state` на одній задачі. Один прогін нічого не доводить: модель може відповісти по-різному навіть на однакових даних, тому кожну конфігурацію запускаємо тричі й беремо **медіану** - середнє з трьох значень, яке лишається, якщо відкинути найменше й найбільше. Ці дванадцять прогонів, вони займуть деякий час. Потім дивимось ті самі прогони в Langfuse: там видно кожен виклик моделі з повною історією на вході.

1. **Створіть** файл `table.py`. `make_row` складає з лога прогону рядок результатів, `print_table` друкує медіани по конфігураціях:

   ```python
   """Підсумкова таблиця вартості: по рядку на кожен прогін і медіани по конфігураціях."""
   import statistics

   from logparse import parse_log
   from metrics import describe


   def make_row(run_id, name, right, seconds):
       """Складає рядок результатів одного прогону. Числа беруться з його лога."""
       with open(f"logs/{run_id}.log", encoding="utf-8") as f:
           d = describe(parse_log(f.read())[0])             # показники прогону (metrics.py)
       return {
           "config": name, "right": int(right), "seconds": seconds,
           "steps": d["steps"], "prompt": d["prompt_tokens"], "completion": d["completion_tokens"],
           "extra": d["extra_tokens"], "squeezes": len(d["squeezes"]), "repeats": d["repeats"],
       }


   def print_table(rows):
       """Друкує таблицю: для кожної конфігурації медіани по її прогонах.
       Стовпці вирівняні пробілами, тож таблиця читається і в терміналі, і як Markdown."""
       head = ["Конфігурація", "Правильно", "Кроків", "Токенів на вхід", "Токенів на вихід",
               "На підсумовування", "Час, с", "Стиснень", "Повторних викликів"]
       lines = []
       for name in dict.fromkeys(r["config"] for r in rows):    # назви конфігурацій без повторів
           part = [r for r in rows if r["config"] == name]

           def med(field):
               return f"{statistics.median(r[field] for r in part):g}"  # медіана значень поля

           lines.append([name, f"{sum(r['right'] for r in part)} з {len(part)}", med("steps"),
                         med("prompt"), med("completion"), med("extra"),
                         med("seconds"), med("squeezes"), med("repeats")])
       widths = [max(len(line[i]) for line in [head] + lines) for i in range(len(head))]

       def show(cells):                                          # назва ліворуч, числа праворуч
           print("| " + " | ".join(c.ljust(w) if i == 0 else c.rjust(w)
                                   for i, (c, w) in enumerate(zip(cells, widths))) + " |")

       print()
       show(head)
       print("|" + "|".join("-" * (w + 2) if i == 0 else "-" * (w + 1) + ":"
                            for i, w in enumerate(widths)) + "|")
       for line in lines:
           show(line)
   ```

2. **Внесіть** у `measure.py` чотири правки: підключення `table.py`, список рядків, додавання рядка після кожного прогону і друк таблиці в кінці:

   У `measure.py` після рядка:

   ```python
   import config
   ```

   додайте:

   ```python
   from table import make_row, print_table
   ```

   У `measure.py` після рядка:

   ```python
       os.makedirs("logs", exist_ok=True)
   ```

   додайте:

   ```python
       rows = []                                            # сюди збираємо рядки результатів
   ```

   У `measure.py` після рядка:

   ```python
               right = is_correct(answer, task["expected"])
   ```

   додайте:

   ```python
               rows.append(make_row(run_id, name, right, seconds))
   ```

   У `measure.py` після рядка:

   ```python
       get_client().flush()                                 # дочекатися відправки трас у Langfuse
   ```

   додайте:

   ```python
       print_table(rows)
   ```

3. **Виконайте** основне вимірювання (серія `main`, кеш вимкнений):

   ```
   python measure.py all 3 main
   ```

4. **Заповніть** таблицю 5 за таблицею в кінці виведення. Колонку «Правильно» перевірте вручну за рядками `відповідь:` (скрипт шукає в тексті лише очікуване число, а модель могла записати його в іншому форматі).

Таблиця 5 - Вартість циклу в трьох конфігураціях (медіани по трьох повторах)

| Конфігурація | Правильно (з 3) | Кроків | Токенів на вхід | Токенів на вихід | Час, с | Стиснень | Повторних викликів |
|--------------|-----------------|--------|-----------------|------------------|--------|----------|--------------------|
| `none`       |                 |        |                 |                  |        |          |                    |
| `trim`       |                 |        |                 |                  |        |          |                    |
| `trim+state` |                 |        |                 |                  |        |          |                    |

5. **Знайдіть** у логах `logs\main_*.log` поламки, яких таблиця не показує, і **запишіть у звіт**, у скількох із дванадцяти прогонів вони сталися: агент відповів, зробивши менше 19 кроків (18 викликів і відповідь; див. рядок «кроків» у `python analyze.py <лог>`), або назвав число, якого не було в жодному рядку `результат:` цього лога (вигадав результат).

6. У Langfuse **відфільтруйте** траси за міткою `main` (назви `long-main_<конфігурація>_r<повтор>`). **Відкрийте** трасу `long-main_none_r1` і `long-main_trim+state_r1`, **зробіть** скріншоти дерев. **Запишіть** у звіт токени входу першого виклику після стиснення в `trim+state` (номер кроку - з `python analyze.py logs\main_trim+state_r1.log`) і токени входу того самого кроку в `none`, а також одне-два речення: що в трасі видно одразу, а в текстовому лозі довелося б рахувати вручну.

## Додаткове завдання: підсумовування замість обрізання

Виконується за бажанням, на підвищену оцінку. Обрізання викидає стару частину історії, стан зберігає лише результати інструментів. Третій підхід - **підсумовування**: окремим викликом просимо модель коротко переказати стару частину історії і підставляємо переказ замість неї. Ціна: додатковий виклик моделі й ризик, що модель спотворить точні числа.

1. **Створіть** файл `summary.py`. `split_history` ділить історію на початок, «старе» й «останнє»; `summarize` просить модель переказати «старе»; `compress_by_summary` підставляє переказ у запитання й пише в лог, скільки він коштував:

   ```python
   """Скорочення історії переказом: стару частину переказує сама модель."""
   import config
   from model import client


   def split_history(messages, keep_last):
       """Ділить історію на три частини: початок, «старе» і «останнє».

       Початок - системна інструкція і запитання. «Останнє» - останні keep_last повідомлень.
       «Старе» - усе, що між ними: його будемо переказувати.
       """
       head = messages[:2]
       rest = messages[2:]
       cut = max(len(rest) - keep_last, 0)       # з якого місця починається «останнє»
       # Результат інструмента не може стояти першим в «останньому»: відправляємо його в «старе»
       while cut < len(rest) and rest[cut]["role"] == "tool":
           cut = cut + 1
       return head, rest[:cut], rest[cut:]


   def render_messages(messages):
       """Перетворює повідомлення на звичайний текст: по рядку на повідомлення."""
       lines = []
       for m in messages:
           body = m.get("content") or m.get("tool_calls")   # у повідомлень з викликом тексту може не бути
           lines.append(f"[{m['role']}] {body}")
       return "\n".join(lines)


   def summarize(old_messages):
       """Просить модель стисло переказати стару частину історії (виклик без інструментів).

       Повертає пару: (текст підсумку, скільки токенів коштував цей виклик).
       """
       request = ("Стисло перекажи, що вже зроблено в цій роботі. Збережи всі точні числа, "
                  "назви й результати інструментів без змін:\n" + render_messages(old_messages))
       response = client.chat.completions.create(
           model=config.MODEL, temperature=0,
           messages=[{"role": "user", "content": request}])
       used = response.usage.prompt_tokens + response.usage.completion_tokens
       return response.choices[0].message.content, used


   def compress_by_summary(messages, used, logger):
       """Замінює стару частину історії коротким переказом, який пише модель."""
       before = len(messages)
       head, old, tail = split_history(messages, config.KEEP_LAST)
       text, extra = summarize(old)                          # окремий виклик моделі
       # Підсумок дописуємо до запитання (воно вже може містити попередній підсумок)
       question = head[1]["content"] + "\n\nПідсумок попередніх кроків: " + text
       messages = [head[0], {"role": "user", "content": question}] + tail
       logger.info(f"  СТИСНЕННЯ: вхід був {used} токенів, повідомлень {before} -> {len(messages)}"
           f", підсумовування коштувало {extra} токенів")
       logger.info("  ПІДСУМОК ІСТОРІЇ:\n" + text)
       return messages
   ```

2. **Внесіть** у `compress.py` дві правки: імпорт і гілка для `COMPRESS = "summary"`.

   У `compress.py` після рядка:

   ```python
   from context import trim
   ```

   додайте:

   ```python
   from summary import compress_by_summary
   ```

   У `compress.py` після рядків:

   ```python
       if config.COMPRESS == "trim":
           return compress_by_trim(messages, task, used, state, logger)
   ```

   додайте:

   ```python
       if config.COMPRESS == "summary":
           return compress_by_summary(messages, used, logger)
   ```

3. **Внесіть** у `measure.py` правку: конфігурація `summary`.

   У `measure.py` після рядка:

   ```python
       "trim+state": {"COMPRESS": "trim", "USE_STATE": True},
   ```

   додайте:

   ```python
       "summary":    {"COMPRESS": "summary", "USE_STATE": False},
   ```

4. **Виконайте** три повтори окремою серією:

   ```
   python measure.py summary 3 extra
   ```

5. **Додайте** рядок `summary` у таблицю 5 і **запишіть у звіт**: скільки токенів коштувало підсумовування (колонка «На підсумовування»), скільки токенів на вході заощаджено порівняно з `trim`, чи зберіг переказ точні числа (порівняйте блок `ПІДСУМОК ІСТОРІЇ` у лозі з рядками `результат:`; наведіть приклад втраченого числа або напишіть, що перевірили).

## Довгі задачі за варіантами

Номер варіанта, предметна область, дані й інструменти - ті самі, що в лабораторній роботі № 2. Таблиця 6 задає дані для довгої задачі (крок 2). Якщо потрібного поля в довіднику немає, замініть його іншим числовим полем.

Таблиця 6 - Дані для довгої задачі за варіантами

| №  | Область             | Шість позицій                   | Знайти в довіднику        | Порахувати для кожної                             | Підсумок                           |
|----|---------------------|---------------------------------|---------------------------|---------------------------------------------------|------------------------------------|
| 1  | Бібліотека          | Шість книжок                    | Термін видачі в днях      | Штраф за три дні затримки                         | Загальний штраф                    |
| 2  | Кулінарія           | Шість продуктів з рецептів      | Калорійність на 100 г     | Калорійність порції заданої ваги                  | Сумарна калорійність               |
| 3  | Доставка посилок    | Шість посилок (місто, вага)     | Тариф міста               | Вартість доставки                                 | Загальна вартість                  |
| 4  | Тренування          | Шість занять із розкладу        | Тривалість заняття        | Витрата калорій за заняття                        | Сумарна витрата калорій            |
| 5  | Догляд за рослинами | Шість рослин                    | Періодичність підживлення | Доза добрива для горщика заданого об'єму          | Сумарна доза добрива               |
| 6  | Ремонт квартири     | Шість матеріалів                | Ціна за одиницю           | Кількість за площею і вартість                    | Загальна вартість матеріалів       |
| 7  | Подорожі            | Шість відрізків маршруту        | Вартість проїзду          | Бюджет на групу з заданої кількості осіб          | Загальний бюджет                   |
| 8  | Обслуговування авто | Шість робіт або деталей         | Ціна                      | Вартість з урахуванням кількості                  | Сумарна вартість                   |
| 9  | Вибір ноутбука      | Шість моделей                   | Ціна                      | Платіж при розстрочці на задану кількість місяців | Сума щомісячних платежів           |
| 10 | Догляд за котом     | Шість котів різного віку й ваги | Щеплення за віком         | Місячна норма корму                               | Загальні витрати на корм за місяць |

## Відповіді на питання

По два-три речення, з посиланням на таблиці й фрагменти логів:

1. На якому кроці агент без захисту дійшов до межі вікна і як ви це побачили (таблиця 2, пункти (г) і (д) кроку 4)? Що в його поведінці змінилося після цього?
2. Порівняйте суму `prompt_tokens` за прогін із формулою (пункти (а)-(в) кроку 4). Чи збігається зростання з очікуваним?
3. Що втрачає агент при обрізанні? Наведіть приклад повторного виклику після стиснення. Що змінилося в `trim+state` (таблиці 3 і 5)?
4. Яка конфігурація найдешевша за токенами, найшвидша, найточніша (таблиця 5)? Чому висновок за трьома повторами однієї задачі обережний?
5. Чому під час вимірювання вартості кеш вимкнено? Що станеться з кешем, якщо інструмент поверне інші дані або ви замініть модель під тією самою назвою?
6. Які поламки довгого прогону скорочення історії не лікує в принципі?

## Звіт

Оформлюється у форматі Markdown. Структура:

1. Титульна сторінка.
2. Мета роботи, номер варіанта, предметна область, модель і розмір вікна (три числа з кроку 1).
3. Довга задача: питання і правильна відповідь (крок 2).
4. Таблиця 2, значення (а)-(д) і випадок A-D (крок 4).
5. Таблиця 3 і результати пункту 7 кроку 6.
6. Таблиця 4 і висновок про кеш (крок 7).
7. Таблиця 5, знайдені поламки і скріншоти трас Langfuse (крок 8).
8. Відповіді на питання.
9. Додаткове завдання (якщо виконували).
10. Висновок: що з трьох способів (скорочення, стан, кеш) дало найбільший ефект і що ще варто змінити.

## Що здається

Архів або репозиторій із такою структурою:

```
lab4/
├── report.md
├── data/
├── logs/                       run_lab3.log, probe_*_r1.log, cache*_none_r1.log, main_*_r*.log
├── state/                      файли стану прогонів
├── Modelfile
├── arguments.py, checks.py                                                    # з лабораторної № 3 (змінені)
├── config.py, tools.py, schemas.py, dispatcher.py, agent.py, agent_runner.py  # з лабораторної № 3 (змінені)
├── model.py, context.py, compress.py, state.py, cache.py
├── make_task.py, measure.py, logparse.py, metrics.py, analyze.py, table.py
├── summary.py                  лише в додатковому завданні
└── tasks.json, long_task.json
```

## Питання для захисту

1. Чому вартість усього прогону агента зростає швидше, ніж вартість одного кроку? Покажіть це на цифрах свого прогону.
2. Що відбувається, коли історія не вміщується у вікно? Як ви помітили це у своєму лозі і чому агент не отримує помилки?
3. Чому `COMPRESS_AT` менший за `NUM_CTX`?
4. Навіщо цикл `while` у `trim`? Що станеться, якщо його прибрати?
5. Що втрачає агент при обрізанні і як це компенсує стан? Чого стан не компенсує? Чому стан записується тільки для викликів з рівнем `ok`?
6. З чого складається ключ кешу? Коли від кешу є користь, а коли його не можна вмикати?
7. Чому кожну конфігурацію проганяли тричі й брали медіану? Чому висновки все одно обережні?
8. Покажіть у трасі Langfuse місце, де стиснення зменшило вхід моделі.
