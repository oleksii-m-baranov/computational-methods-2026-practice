"""Налаштування агента."""
from dotenv import load_dotenv
load_dotenv()                      # завантажує ключі Langfuse з .env

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen25-4k"
MAX_STEPS = 6
MAX_STEPS_LONG = 25
TEMPERATURE = 0

LAB_LOGFILE_NAME = "lab5"          # лог пишеться в lab4.log

MAX_RETRIES = 2      # скільки помилок моделі поспіль допускаємо

# інструменти, які агентові дозволено викликати (варіант 2: кулінарія).
# place_order у tools.py є, але сюди свідомо НЕ входить
ALLOWED = ["search_docs", "product_info", "scale_amount"]

# мітка прогону: за нею в Langfuse відрізнятимемо прогони
RUN_TAG = "ctx-control"


SYSTEM = """
Ти кулінарний агент. Відповідай українською мовою.

Використовуй інструменти для пошуку рецептів,
отримання калорійності та масштабування значень.

ВАЖЛИВІ ПРАВИЛА:

1. Назви продуктів передавай точно так,
   як вони записані в завданні українською.
   Не перекладай їх російською.

2. Для кожного продукту спочатку виклич
   search_recipes, потім product_info,
   потім scale_amount.

3. Для scale_amount:
   amount = число калорійності з product_info;
   base_servings = 10;
   target_servings = вага продукту / 10.

4. Приклад:
   продукт має 344 ккал на 100 г,
   порція важить 150 г.

   Правильний виклик:
   scale_amount(
       amount=344,
       base_servings=10,
       target_servings=15
   )

   Результат: 516 ккал.

5. Не використовуй вигадані значення amount.
   Не передавай вагу в грамах як target_servings.

6. Якщо інструмент повернув помилку,
   виправ тільки неправильний виклик.

7. Завершуй роботу лише після обробки
   всіх шести продуктів.

8. У фінальній відповіді наведи
   калорійність кожного продукту
   та загальну суму в ккал.
"""
NUM_CTX = 4096

COMPRESS = "none"
COMPRESS_AT = 2800
KEEP_LAST = 6

USE_STATE = False
STATE_RESULT_CHARS = 200
USE_CACHE = False

EMBED_MODEL = "bge-m3"                   # модель ембедингів
DOC_DIRS = ["data/corpus", "data/docs"]  # де лежать документи
INDEX_DIR = "index"                      # куди зберігається індекс
CHUNK_METHOD = "fixed"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 0
WITH_TITLE = False

TOP_K = 3
MIN_SCORE = 0.46                     # поріг схожості: у кроці 5 ви підберете значення
DOCS_DESCRIPTION = "B"                   # який опис search_docs використовувати: "A", "B" або "C"
