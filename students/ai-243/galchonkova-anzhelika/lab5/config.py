"""Налаштування агента для лабораторної роботи № 5."""
from dotenv import load_dotenv

import os
load_dotenv()
for _k in ('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy'): os.environ.pop(_k, None)
os.environ['NO_PROXY'] = '127.0.0.1,localhost'

BASE_URL = "http://127.0.0.1:11434/v1"
API_KEY = "ollama"

LAB_LOGFILE_NAME = "lab5"
MODEL = "qwen25-4k:latest"
MAX_STEPS = 6
MAX_STEPS_LONG = 25
MAX_RETRIES = 2
TEMPERATURE = 0.2
NUM_CTX = 4096
RUN_TAG = "rag"

ALLOWED = ["search_docs", "fertilizer_info", "calc_dose"]

SYSTEM = """Ти консультант з догляду за кімнатними рослинами.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""

# Параметри керування контекстом (вимкнені в лаб. 5)
COMPRESS = "none"
COMPRESS_AT = 2800
KEEP_LAST = 6
USE_STATE = False
STATE_RESULT_CHARS = 200
USE_CACHE = False

# Параметри RAG
EMBED_MODEL = "bge-m3"
DOC_DIRS = ["data/corpus", "data/docs"]
INDEX_DIR = "index"
CHUNK_METHOD = "fixed"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 0
WITH_TITLE = False
TOP_K = 3
MIN_SCORE = 0.56
DOCS_DESCRIPTION = "B"