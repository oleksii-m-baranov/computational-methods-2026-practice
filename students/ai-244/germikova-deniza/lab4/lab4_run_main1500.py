#!/usr/bin/env python3
"""Nine supplementary long-task runs at threshold 1500, preserving main at 2150.

Three modes x three repeats, baseline agent, same threshold across all modes.
Existing completed run logs are resumed, never overwritten without a backup.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
import sys
import time

HERE=Path(__file__).resolve().parent
os.chdir(HERE)
for p in [HERE, *HERE.parents]:
    if (p/'utils'/'lab_logger.py').is_file():
        if str(p) not in sys.path: sys.path.insert(0,str(p))
        break

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv=None
if load_dotenv:
    candidates=[HERE/'.env',HERE.parent/'.env',HERE.parent/'lab3'/'.env']
    candidates += [p/'.env' for p in HERE.parents]
    for p in candidates:
        if p.is_file(): load_dotenv(p,override=False)

# Additional diagnostics must not secretly change the baseline agent behavior.
for key in ('LAB4_GUIDED_V3','LAB4_LONGRUN_GUARD'):
    os.environ.pop(key,None)

import config
if getattr(config,'NUM_CTX',None) != 3072:
    raise SystemExit(f'ПОМИЛКА: очікуємо NUM_CTX=3072, поточне {getattr(config,"NUM_CTX",None)}')
if getattr(config,'COMPRESS_AT',None) != 2150:
    raise SystemExit(f'ПОМИЛКА: базовий COMPRESS_AT має бути 2150, зараз {config.COMPRESS_AT}; не змінюємо файл')
if not all((HERE/'logs'/f'main_{mode}_r{rep}.log').is_file()
           for mode in ('none','trim','trim+state') for rep in (1,2,3)):
    raise SystemExit('ПОМИЛКА: потрібно зберегти спочатку 9 оригінальних main-логів')
if not (HERE/'utils'/'lab_logger.py').is_file():
    raise SystemExit('ПОМИЛКА: спочатку запустіть python3 lab4_upgrade_prepare.py')

config.COMPRESS_AT=1500  # process memory only, NOT config.py on disk
config.USE_CACHE=False
import measure
from langfuse import get_client

if set(('none','trim','trim+state')) - set(measure.CONFIGS):
    raise SystemExit('ПОМИЛКА: вимірювач не має обов’язкових режимів')

logs=HERE/'logs';logs.mkdir(exist_ok=True)
manifest_path=logs/'main1500_manifest.json'
if manifest_path.is_file():
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
else:
    manifest={'experiment':'main1500','threshold':1500,'baseline_threshold':2150,
              'guided':False,'cache':False,'runs':{}}
if manifest.get('threshold') != 1500 or manifest.get('experiment') != 'main1500':
    raise SystemExit('ПОМИЛКА: некоректний main1500_manifest.json')

def complete(path:Path)->bool:
    if not path.is_file(): return False
    text=path.read_text(encoding='utf-8',errors='replace')
    return ('ВІДПОВІДЬ:' in text or 'СТОП:' in text) and '--- крок ' in text

print('=== ОКРЕМА СЕРІЯ main1500 ===')
print('Поріг 1500 для ВСІХ трьох режимів; кеш та guided вимкнені')
print('Вихідні 9 logs/main_* не змінюються; config.py також')
print('Langfuse:', 'ключі знайдені' if os.getenv('LANGFUSE_PUBLIC_KEY') and os.getenv('LANGFUSE_SECRET_KEY')
      else 'ключі не знайдені — нові траси можуть бути відсутні')

for repeat in (1,2,3):
    for mode in ('none','trim','trim+state'):
        run_id=f'main1500_{mode}_r{repeat}'
        path=logs/f'{run_id}.log'
        if complete(path):
            print('ПРОПУСК: завершений журнал уже існує:',path.name)
            continue
        if path.exists():
            old=path.with_suffix('.incomplete_backup')
            if old.exists():
                old=path.with_name(path.name+'.incomplete_backup_'+str(int(time.time())))
            path.rename(old)
            print('Резервна копія незавершеного журналу:',old.name)
        print(f'\nПУСК: {run_id}')
        run_id, answer, seconds=measure.run_once(mode,repeat,'main1500',measure.load_task())
        expected=measure.load_task()['expected']
        manifest['runs'][run_id]={'time_seconds':seconds,
                                  'correct_by_expected_substring':measure.is_correct(answer,expected),
                                  'finished_at_epoch':round(time.time())}
        tmp=manifest_path.with_suffix('.tmp')
        tmp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        tmp.replace(manifest_path)
        get_client().flush()
        print(f'ПІДСУМОК {run_id}: {seconds} с; правильно: {"так" if manifest["runs"][run_id]["correct_by_expected_substring"] else "ні"}')

print('\nУСПІХ: додаткова серія main1500 завершена, 9/9 журналів')
print('Наступна команда: python3 lab4_upgrade_finalize.py')
