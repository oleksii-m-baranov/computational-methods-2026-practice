"""Короткий звіт лише за реальними файлами logs/extra1500_*.log."""
from pathlib import Path
import re
import sys
from statistics import median

series=sys.argv[1] if len(sys.argv)>1 else 'extra1500'
logs=Path('logs')
data={}
for mode in ('trim','summary'):
    rows=[]
    for path in sorted(logs.glob(f'{series}_{mode}_r*.log')):
        content=path.read_text(encoding='utf-8',errors='replace')
        pt=[int(v) for v in re.findall(r'prompt_tokens=(\d+)',content)]
        costs=[int(v) for v in re.findall(r'підсумовування коштувало (\d+) токенів',content)]
        compress_events=re.findall(r'СТИСНЕННЯ: вхід був \d+',content)
        rows.append((path.name, sum(pt),sum(costs),len(compress_events)))
    data[mode]=rows
    print(f'\n=== {mode.upper()} ===')
    if not rows:
        print('Логів немає')
    for name,prompt,extra,events in rows:
        print(f'{name}: вхідних токенів={prompt}; на підсумовування={extra}; стиснень={events}')
    if rows:
        print(f'Медіана: вхід={median(r[1] for r in rows)}; підсумовування={median(r[2] for r in rows)}; стиснень={median(r[3] for r in rows)}')

if data['trim'] and data['summary']:
    m_trim=median(row[1] for row in data['trim'])
    m_summary=median(row[1] for row in data['summary'])
    print(f'\nЗміна медіани вхідних токенів (trim - summary): {m_trim-m_summary:+g}')
    print('Додаткові токени summary рахуйте окремо від основних вхідних токенів.')

paths=sorted(logs.glob(f'{series}_summary_r*.log'))
if paths:
    s=paths[0].read_text(encoding='utf-8',errors='replace')
    # Знаходимо перший підсумок та сусідні записи для РУЧНОЇ перевірки чисел.
    marker='ПІДСУМОК ІСТОРІЇ:'
    pos=s.find(marker)
    if pos>=0:
        extract=s[pos+len(marker):]
        stop=re.search(r'(?m)^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\s+-\s+(?:INFO|WARNING|ERROR)',extract)
        text=extract[:stop.start()] if stop else extract[:1500]
        print(f'\nПерший підсумок моделі з {paths[0].name} (фрагмент):\n{text[:1000].strip()}')
        prefix=s[:pos]
        source_results=re.findall(r'(?m)^.*?результат:\s*(.+)$',prefix)
        print('\nРезультати інструментів ДО підсумку (для перевірки точності):')
        for result in source_results[-12:]:
            print(' -',result[:160])
        print('\nУ звіті порівняйте кожне число з реального результату і тексту підсумку; не вважайте точність підтвердженою автоматично.')
    else:
        print('\nПІДСУМОК ІСТОРІЇ не знайдено: модельне підсумовування не активувалося.')
