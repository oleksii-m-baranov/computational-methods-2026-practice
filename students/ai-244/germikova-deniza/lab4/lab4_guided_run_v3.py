"""Запускає guidedv3, намагається завантажити наявний .env без друку ключів."""
import os
from pathlib import Path
import runpy
import sys

here = Path(__file__).resolve().parent
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None
if load_dotenv is not None:
    sources = [here / '.env', here.parent / '.env', here.parent / 'lab3' / '.env',
               here.parents[3] / '.env']
    for p in sources:
        if p.is_file():
            load_dotenv(p, override=False)
print('Langfuse: ' + ('ключі доступні' if os.getenv('LANGFUSE_PUBLIC_KEY') and os.getenv('LANGFUSE_SECRET_KEY')
                       else 'ключів у середовищі немає — нові траси можуть не зберегтися'))
os.environ['LAB4_GUIDED_V3'] = '1'
sys.argv = ['measure.py', *(sys.argv[1:] if len(sys.argv) > 1 else ['trim+state', '1', 'guidedv3'])]
runpy.run_path(str(here / 'measure.py'), run_name='__main__')
