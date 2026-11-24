"""Запуск додаткового завдання з контрольованим порогом без змін config.py.

python3 lab4_extra_run.py summary 3 extra [2150]
python3 lab4_extra_run.py trim 3 extra1500 1500
python3 lab4_extra_run.py summary 3 extra1500 1500
"""
import os
from pathlib import Path
import sys

here=Path(__file__).resolve().parent
repo=here.parents[3]  # /Users/deniza/lab3
if str(repo) not in sys.path:
    sys.path.insert(0,str(repo))

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv=None
if load_dotenv is not None:
    for p in (here/'.env', here.parent/'.env', here.parent/'lab3'/'.env', repo/'.env'):
        if p.is_file():
            load_dotenv(p, override=False)

# Не змішуємо експеримент з автоматизованим GUIDED V4.
os.environ.pop('LAB4_GUIDED_V3',None)
os.environ.pop('LAB4_LONGRUN_GUARD',None)

if len(sys.argv) not in (4,5):
    raise SystemExit('Виклик: python3 lab4_extra_run.py <summary|trim> <повтори> <серія> [поріг]')
kind, reps, series = sys.argv[1:4]
if kind not in ('summary','trim'):
    raise SystemExit('Для додаткового експерименту допускаються summary та trim')
try:
    repeat=int(reps)
    threshold=int(sys.argv[4]) if len(sys.argv)==5 else None
except ValueError:
    raise SystemExit('Повтори і поріг мають бути цілими числами')
if repeat<1 or (threshold is not None and threshold<250):
    raise SystemExit('Некоректні повтори або поріг')

os.chdir(here)
import config
if threshold is not None:
    config.COMPRESS_AT=threshold
print(f'Додатковий експеримент: {kind}; повторів={repeat}; '
      f'поріг={config.COMPRESS_AT}; серія={series}; '
      f'кеш={"вимкнений" if not series.startswith("cache") else "ввімкнений"}')

import measure
sys.argv=['measure.py',kind,str(repeat),series]
measure.main()
