from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"
MODEL = "qwen25-4k"
MAX_STEPS = 6
TEMPERATURE = 0.2

MAX_RETRIES = 2
ALLOWED = ["search_docs", "fertilizer_info", "calc_dose"]
RUN_TAG = "rag-agent"
LAB_LOGFILE_NAME = "lab5"

NUM_CTX = 4096
MAX_STEPS_LONG = 25

COMPRESS = "none"
COMPRESS_AT = 2150
KEEP_LAST = 6
USE_STATE = False
STATE_RESULT_CHARS = 200
USE_CACHE = False

SYSTEM = """Ти консультант з догляду за кімнатними рослинами.
Відповідай українською мовою, точно й лаконічно, спираючись лише на дані з інструментів."""

EMBED_MODEL = "bge-m3"                 
DOC_DIRS = ["data/corpus", "data/docs"]  
INDEX_DIR = "index"                      
CHUNK_METHOD = "paragraphs"             
CHUNK_SIZE = 800                        
CHUNK_OVERLAP = 0                      
WITH_TITLE = False                      
TOP_K = 3                                
MIN_SCORE = 0.52
DOCS_DESCRIPTION = "C"            