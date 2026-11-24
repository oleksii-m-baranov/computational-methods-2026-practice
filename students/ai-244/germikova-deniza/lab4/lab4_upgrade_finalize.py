#!/usr/bin/env python3
"""Audit real main1500 logs, document diagnostic comparison, package submission.

Does not fabricate results, edit original main logs or change config.py.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime
from pathlib import Path
from statistics import median
from zipfile import ZipFile, ZIP_DEFLATED
import json
import re
import shutil

HERE=Path(__file__).resolve().parent
LOGS=HERE/'logs'
REPORT=HERE/'report.md'
SCREEN=HERE/'screenshots'/'langfuse_guidedv4.png'
BEGIN='<!-- LAB4-MAIN1500:BEGIN -->'
END='<!-- LAB4-MAIN1500:END -->'


def parse(path: Path) -> dict:
    if not path.is_file():raise RuntimeError(f'Немає журналу {path.name}')
    text=path.read_text(encoding='utf-8',errors='replace')
    hits=re.findall(r'(?m)^.*?--- крок (\d+)\s*\|.*?prompt_tokens=(\d+).*?completion_tokens=(\d+)',text)
    if not hits:raise RuntimeError(f'Немає кроків у журналі {path.name}')
    indices=[int(x[0]) for x in hits]
    if indices!=list(range(1,len(indices)+1)):
        raise RuntimeError(f'Порушена послідовність кроків: {path.name}')
    if 'ВІДПОВІДЬ:' not in text and 'СТОП:' not in text:
        raise RuntimeError(f'Немає завершення у {path.name}')
    if 'GUIDED_V' in text or 'ЕКСПЕРИМЕНТАЛЬНИЙ КОНТРОЛЬ ПОВНОТИ: увімкнено' in text:
        raise RuntimeError(f'Не можна використовувати guided/guard-логи в базовій серії: {path.name}')
    calls=[]
    for line in text.splitlines():
        m=re.search(r'виклик\s*:\s*(\w+)\((\{.*\})\)',line)
        if m:
            try:args=json.loads(m.group(2))
            except json.JSONDecodeError:args=m.group(2)
            calls.append((m.group(1),json.dumps(args,sort_keys=True,ensure_ascii=False) if isinstance(args,dict) else args))
    comp=[int(x) for x in re.findall(r'(?m)^.*?СТИСНЕННЯ: вхід був (\d+)',text)]
    # Associate compression events with their preceding step. Logs show the event after each step.
    compression_steps=[]
    step=0
    for line in text.splitlines():
        m=re.search(r'--- крок (\d+)\s*\|',line)
        if m:step=int(m.group(1))
        if re.search(r'СТИСНЕННЯ: вхід був \d+',line):
            compression_steps.append(step)
    answer=re.findall(r'ВІДПОВІДЬ:\s*(.*)',text)
    last=answer[-1] if answer else ''
    return {'name':path.name,'steps':len(hits),'p':sum(int(x[1]) for x in hits),
            'c':sum(int(x[2]) for x in hits),'per_step':{int(n):int(p) for n,p,_ in hits},
            'compressions':len(comp),'compression_steps':compression_steps,
            'calls':len(calls),'repeats':sum(cnt-1 for cnt in Counter(calls).values()),
            'correct':bool(re.search(r'(?<!\d)1625[.,]6(?!\d)', last.replace(' ',''))),
            'last_answer':last}


def med(rows:list[dict],key:str)->str:
    return f'{median(x[key] for x in rows):g}'.replace('.',',')


def make_table(rows:dict[str,list[dict]],manifest:dict)->str:
    out=['| Конфігурація | Правильно | Кроків | Токенів на вхід | На вихід | Стиснень | Повторних викликів | Час, с |',
         '|---|---:|---:|---:|---:|---:|---:|---:|']
    for mode in ('none','trim','trim+state'):
        part=rows[mode]
        times=[manifest.get('runs',{}).get(x['name'].removesuffix('.log'),{}).get('time_seconds') for x in part]
        tm=f'{median(times):g}'.replace('.',',') if all(isinstance(x,(int,float)) for x in times) else '—'
        out.append(f'| `{mode}` | {sum(x["correct"] for x in part)}/3 | {med(part,"steps")} | {med(part,"p")} | {med(part,"c")} | {med(part,"compressions")} | {med(part,"repeats")} | {tm} |')
    return '\n'.join(out)


def section(rows:dict[str,list[dict]],manifest:dict)->str:
    baseline=rows['none'][0]
    trim_state=rows['trim+state'][0]
    event=trim_state['compression_steps'][0] if trim_state['compression_steps'] else None
    compare=''
    if event is not None and event+1 in trim_state['per_step'] and event+1 in baseline['per_step']:
        step=event+1
        a=trim_state['per_step'][step];b=baseline['per_step'][step]
        compare=(f'У прогоні `main1500_trim+state_r1` перше стиснення відбулося **після кроку {event}**; '
                 f'на **кроці {step}** вхід містив **{a} токенів** проти **{b} токенів** '
                 f'на тому самому кроці `main1500_none_r1` (різниця `none − trim+state = {b-a}` токенів). '
                 'Ці значення взято з реальних рядків `prompt_tokens` відповідних журналів.\n\n')
    elif event is not None:
        compare=('Стиснення у `trim+state` було, але відповідного наступного кроку в обох '
                 'порівнюваних запусках немає; пряме порівняння токенів для `r1` неможливе.\n\n')
    else:
        compare=('У `trim+state_r1` стиснень немає, тому безпосередню пару кроків '
                 'для цього повтору не знайдено. Інші повтори наведено в таблиці.\n\n')
    premature={mode:sum(x['steps']<19 for x in part) for mode,part in rows.items()}
    return f'''{BEGIN}
## 11. Додаткова серія `main1500`: порівняння до й після стиснення

**Мета.** Додаткова діагностика для пункту про Langfuse у кроці 8 методички. Первинну серію `main` за порога **2150** збережено без змін: вона завершувалася до першого стиснення. Щоб без підміни історичних даних отримати парні кроки після стиснення, додатково виконано **9 нових запусків** (`3 конфігурації × 3 повтори`) з порогом **1500 для всіх режимів**, тим самим завданням, моделлю та лімітом 25 кроків. Параметр `COMPRESS_AT` змінювався **лише в пам'яті процесу**; у `config.py` лишилося **2150**. Кеш і експериментальний механізм GUIDED V4 були вимкнені.

{make_table(rows,manifest)}

{compare}За журналами видно повторне звернення до інструментів і втрату частини старої історії після обрізання. Кількість дострокових завершень (менше 19 кроків) у `main1500`: `none` — **{premature['none']}/3**, `trim` — **{premature['trim']}/3**, `trim+state` — **{premature['trim+state']}/3**. Статистика за три повтора є лише оцінкою на одному завданні, а не загальною гарантією правильності агента.

**Обмеження порівняння.** Це **нова діагностична серія `main1500`**, а не вихідна серія `main` при 2150 і не її заміна. Значення першого кроку після стиснення отримані з локальних текстових логів; для демонстрації в Langfuse використовуйте траси `long-main1500_trim+state_r1` та `long-main1500_none_r1`. На раніше наданих скриншотах Langfuse підтверджено наявність дерев для основних та діагностичних трас, а **нові скриншоти `main1500` автоматично не створювалися**. Текстовий журнал не дозволяє побачити всю вкладену послідовність викликів так швидко, як дерево Langfuse.
{END}

'''


def update_report(rows:dict[str,list[dict]],manifest:dict)->None:
    if not REPORT.is_file():raise RuntimeError('Немає report.md')
    txt=REPORT.read_text(encoding='utf-8')
    if 'screenshots/langfuse_guidedv4.png' not in txt:
        raise RuntimeError('Спочатку запустіть lab4_upgrade_prepare.py')
    section_text=section(rows,manifest)
    if BEGIN in txt:
        if END not in txt:raise RuntimeError('У report.md є тільки один маркер main1500')
        txt=re.sub(re.escape(BEGIN)+r'.*?'+re.escape(END)+r'\s*',section_text,txt,flags=re.S,count=1)
    else:
        anchor='## 11. Висновок'
        if anchor not in txt:
            raise RuntimeError('Не знайдено заголовок ## 11. Висновок — звіт не змінюємо')
        txt=txt.replace(anchor,section_text+'## 12. Висновок',1)
    backup=HERE/'report_before_main1500.md'
    if not backup.exists():shutil.copy2(REPORT,backup)
    REPORT.write_text(txt,encoding='utf-8')
    print('УСПІХ: розділ 11 main1500, таблиця і порівняння токенів додано до звіту')


def build_zip()->Path:
    from collections import OrderedDict
    files=[
        'report.md','Modelfile','arguments.py','checks.py','config.py','tools.py',
        'schemas.py','dispatcher.py','agent.py','agent_runner.py','model.py',
        'context.py','compress.py','state.py','cache.py','make_task.py',
        'measure.py','logparse.py','metrics.py','analyze.py','table.py',
        'tasks.json','long_task.json','summary.py','guided_longrun.py',
        'longrun_guard.py','lab4_guided_run_v3.py','lab4_extra_run.py',
        'lab4_summary_review.py','lab4_append_summary_results.py',
        'lab4_package_after_summary.py','lab4_upgrade_prepare.py',
        'lab4_run_main1500.py','lab4_upgrade_finalize.py','README_LAB4_UPGRADE.md'
    ]
    for optional in ('Modelfile_3k','Modelfile_4k','README_SUMMARY.md'):
        if (HERE/optional).is_file():files.append(optional)
    missing=[f for f in files if not (HERE/f).is_file()]
    if missing:raise RuntimeError('Відсутні основні файли: '+repr(missing))
    for folder in ('data','logs','state','screenshots','utils'):
        if not (HERE/folder).is_dir():raise RuntimeError(f'Немає каталогу {folder}')
    for required in ('screenshots/langfuse_none.png','screenshots/langfuse_trim_state.png',
                     'screenshots/langfuse_diag_trim_state.png','screenshots/langfuse_guidedv4.png',
                     'utils/lab_logger.py','utils/__init__.py'):
        if not (HERE/required).is_file():raise RuntimeError(f'Немає {required}')
    result=[HERE/f for f in files]
    for folder in ('data','logs','state','screenshots','utils'):
        d=HERE/folder
        result.extend(p for p in d.rglob('*') if p.is_file() and not p.is_symlink()
                      and not any(part.startswith('.') or part=='__pycache__' or part.startswith('backup_')
                                  or '.incomplete_backup' in part for part in p.relative_to(HERE).parts)
                      and p.suffix not in ('.pyc','.pyo'))
    result=list(dict.fromkeys(result))
    for p in result:
        n=p.name.lower()
        if '.env' in n or 'secret' in n or n in ('credentials.json','token.json'):
            raise RuntimeError(f'Небезпечна назва файла в архіві: {p.relative_to(HERE)}')
    out=Path.home()/'Downloads'/'Lab4_Germikova_AI244_ENHANCED_FINAL.zip'
    out.parent.mkdir(exist_ok=True)
    with ZipFile(out,'w',compression=ZIP_DEFLATED) as z:
        for p in result:z.write(p,arcname=str(Path('lab4')/p.relative_to(HERE)))
    with ZipFile(out) as z:
        damaged=z.testzip()
        if damaged:raise RuntimeError('ZIP має пошкоджений файл '+damaged)
        names=set(z.namelist())
        for r in ('lab4/report.md','lab4/utils/lab_logger.py',
                  'lab4/screenshots/langfuse_guidedv4.png'):
            if r not in names:raise RuntimeError('Відсутній в ZIP: '+r)
        for mode in ('none','trim','trim+state'):
            for i in (1,2,3):
                for series in ('main','main1500'):
                    path=f'lab4/logs/{series}_{mode}_r{i}.log'
                    if path not in names:raise RuntimeError('Відсутній в ZIP: '+path)
        for mode,series in [('summary','extra'),('summary','extra1500'),('trim','extra1500')]:
            for i in (1,2,3):
                path=f'lab4/logs/{series}_{mode}_r{i}.log'
                if path not in names:raise RuntimeError('Відсутній в ZIP: '+path)
        report=z.read('lab4/report.md').decode('utf-8')
        for key in ('LAB4-SUMMARY-EXTRA:BEGIN','LAB4-MAIN1500:BEGIN',
                    'screenshots/langfuse_guidedv4.png','1625,6'):
            if key not in report:raise RuntimeError(f'Відсутній пункт у звіті: {key}')
        print('ZIP перевірено:',len(names),'файлів, оригінальні main та нові main1500, скриншот і utils на місці')
    print('НОВИЙ ПІДСУМКОВИЙ АРХІВ:',out)
    print('Розмір:',round(out.stat().st_size/1024/1024,2),'МБ')
    return out


def main():
    if not SCREEN.is_file():raise SystemExit('ПОМИЛКА: немає скриншота, спочатку prepare')
    modes=('none','trim','trim+state')
    rows={mode:[parse(LOGS/f'main1500_{mode}_r{i}.log') for i in (1,2,3)]
          for mode in modes}
    manifestfile=LOGS/'main1500_manifest.json'
    manifest=json.loads(manifestfile.read_text(encoding='utf-8')) if manifestfile.is_file() else {}
    for mode in modes:
        print(f'{mode}: правильно {sum(x["correct"] for x in rows[mode])}/3, '
              f'медіана входу {med(rows[mode],"p")}, '
              f'медіана стиснень {med(rows[mode],"compressions")}')
    update_report(rows,manifest)
    build_zip()

if __name__=='__main__':
    main()
