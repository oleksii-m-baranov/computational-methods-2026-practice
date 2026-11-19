from pathlib import Path
import sys
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
for parent in ROOT.parents:
    if (parent / "utils" / "lab_logger.py").is_file():
        sys.path.insert(0, str(parent))
        break
else:
    raise RuntimeError("Shared utils not found above lab4. Extract the complete ZIP.")
load_dotenv(ROOT / ".env")

BASE_URL = "http://127.0.0.1:11434/v1"
API_KEY = "ollama"
MODEL = 'qwen25-lab4-final-3k'
MAX_STEPS = 6
TEMPERATURE = 0
SYSTEM = """Ти кухонний помічник. Допомагаєш підібрати страву
та розрахувати інгредієнти.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

MAX_RETRIES = 2
ALLOWED = ["search_recipes", "product_info", "scale_amount"]
RUN_TAG = "ctx-control"
LAB_LOGFILE_NAME = "lab4"

NUM_CTX = 3072
MAX_STEPS_LONG = 25
COMPRESS = "none"
COMPRESS_AT = 2150
KEEP_LAST = 6
USE_STATE = False
STATE_RESULT_CHARS = 200
USE_CACHE = False
# HTTP timeout per request; a separate worker deadline prevents an endless wait.
REQUEST_TIMEOUT = 240.0
RUN_TIMEOUT = 900
CACHE_NAMESPACE = 'lab4-final-qwen25-3k-v1'
