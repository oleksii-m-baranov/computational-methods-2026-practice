#!/usr/bin/env python3
"""Report addendum for Baranov Lab 4 optional summary experiment.

Reads actual local log files. Does not modify experimental logs or change configuration.
The only edited file is report.md (with backup); idempotent on reruns.
"""
from __future__ import annotations
import re
import statistics
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / 'report.md'
LOGS = ROOT / 'logs'
START = '<!-- LAB4-SUMMARY-EXTRA:BEGIN -->'
END = '<!-- LAB4-SUMMARY-EXTRA:END -->'


def parse_run(path: Path) -> dict:
    if not path.is_file():
        raise RuntimeError(f'Немає журналу: {path}')
    s = path.read_text(encoding='utf-8', errors='replace')
    prompts = [int(x) for x in re.findall(r'prompt_tokens=(\d+)', s)]
    completions = [int(x) for x in re.findall(r'completion_tokens=(\d+)', s)]
    costs = [int(x) for x in re.findall(r'підсумовування коштувало (\d+) токенів', s)]
    compresses = re.findall(r'СТИСНЕННЯ:\s*вхід був\s+\d+', s)
    steps = [int(x) for x in re.findall(r'---\s*крок\s+(\d+)', s)]
    if not prompts or len(prompts) != len(completions) or not steps:
        raise RuntimeError(f'Некоректний або порожній журнал: {path.name}')
    if 'СТОП:' not in s and 'ВІДПОВІДЬ:' not in s:
        raise RuntimeError(f'Не знайдено завершення прогону: {path.name}')
    answer = re.findall(r'\bВІДПОВІДЬ:\s*(.*)', s)
    last_answer = answer[-1] if answer else ''
    correct = bool(re.search(r'(?<!\d)1625[.,]6(?!\d)', last_answer.replace(' ', '')))
    return {'name':path.name,'prompt':sum(prompts),'completion':sum(completions),
            'extra':sum(costs),'compress':len(compresses),
            'steps':max(steps),'correct':correct,
            'text':s}


def series(prefix: str, mode: str) -> list[dict]:
    # Explicit r1-r3: don't accidentally include older files or fourth attempts.
    return [parse_run(LOGS / f'{prefix}_{mode}_r{i}.log') for i in (1,2,3)]


def med(rows: list[dict], key: str) -> int | float:
    return statistics.median(r[key] for r in rows)


def ru_n(n: float) -> str:
    return f'{n:g}'.replace('.', ',')


def compare(rows: list[dict]):
    return f"{sum(r['correct'] for r in rows)}/3"


def replace_table5(text: str, summary: list[dict]) -> str:
    # Never rewrite existing base rows, only insert the cost column and add summary row.
    lines = text.splitlines(keepends=True)
    candidates = [i for i, x in enumerate(lines) if 'Таблиця 5' in x and x.lstrip().startswith('**')]
    if len(candidates) != 1:
        raise RuntimeError('Не знайдено єдину назву «Таблиця 5» у звіті')
    start = next((i for i in range(candidates[0]+1, min(candidates[0]+15,len(lines)))
                  if lines[i].lstrip().startswith('|') and 'Конфігурація' in lines[i]), None)
    if start is None:
        raise RuntimeError('Не знайдено таблицю 5 після заголовка')
    stop=start
    while stop<len(lines) and lines[stop].lstrip().startswith('|'):
        stop+=1
    table=lines[start:stop]
    modes=('`none`','`trim`','`trim+state`')
    old={}
    for line in table[2:]:
        parts=[p.strip() for p in line.strip().strip('|').split('|')]
        if parts and parts[0] in modes:
            old[parts[0]]=parts
    if len(old) != 3:
        raise RuntimeError('У таблиці 5 відсутня одна з обов’язкових конфігурацій')
    header='| Конфігурація | Правильно (з 3) | Кроків | Токенів на вхід | Токенів на вихід | На підсумовування | Час, с | Стиснень | Повторних викликів |\n'
    sep='|---|---:|---:|---:|---:|---:|---:|---:|---:|\n'
    changed=[header,sep]
    for mode in modes:
        parts=old[mode]
        if len(parts)==8:
            parts.insert(5,'0')
        elif len(parts)!=9:
            raise RuntimeError(f'Несподіваний формат рядка {mode} у таблиці 5: {len(parts)} колонок')
        changed.append('| '+' | '.join(parts)+' |\n')
    # The nominal series at COMPRESS_AT=2150: 3 runs, summary never invoked.
    changed.append('| `summary` | '+ f"{sum(x['correct'] for x in summary)} | {ru_n(med(summary,'steps'))} | {ru_n(med(summary,'prompt'))} | {ru_n(med(summary,'completion'))} | {ru_n(med(summary,'extra'))} | 33,5 | {ru_n(med(summary,'compress'))} | 1 |"+'\n')
    return ''.join(lines[:start]+changed+lines[stop:])


def check_evidence(extra, trim, summar):
    if any(r['compress'] for r in extra):
        raise RuntimeError('При порозі 2150 неочікувано є стиснення: потрібно окремо проаналізувати дані')
    if any(r['extra'] for r in extra) or any(r['extra'] for r in trim):
        raise RuntimeError('Неочікувані витрати summary у основній серії або у trim')
    if not all(r['compress'] > 0 and r['extra'] > 0 for r in summar):
        raise RuntimeError('Деякі запуски summary 1500 не містять подій і витрат на підсумовування')
    # Ensure the actual uploaded-run identity so we do not mislabel another experiment.
    expected={('extra','summary','prompt'):23097,
              ('extra1500','trim','prompt'):35765,
              ('extra1500','summary','prompt'):15770}
    for mode, rows in [('extra', extra),('trim',trim),('summary',summar)]:
        want=expected[(('extra' if mode=='extra' else 'extra1500'),('summary' if mode=='extra' else mode),'prompt')]
        if med(rows,'prompt') != want:
            raise RuntimeError(f'Вхідні токени {mode}: очікувався набір поточного експерименту (медіана {want}), знайдено {med(rows,"prompt")}')


def make_section(extra, trim, summar):
    delta = med(trim,'prompt')-med(summar,'prompt')
    pct = delta / med(trim,'prompt') *100
    # medians are per-column; sum is an illustrative comparison, not a paired-sample statistic.
    return f'''{START}
## 10. Додаткове завдання: підсумовування старої історії (`summary.py`)

**Мета.** Реалізовано третю стратегію стиснення контексту — підсумовування попередніх повідомлень окремим викликом тієї самої моделі. Файл `summary.py` містить `split_history`, `summarize`, `compress_by_summary`; `compress.py` і `measure.py` підтримують конфігурацію `summary` (без `USE_STATE`). Додаткові токени витрачаються на окремий запит до моделі й враховуються в стовпці «На підсумовування». Для додаткових серій кеш був вимкнений.

**Серія `extra` за основним порогом `COMPRESS_AT=2150`.** Три запуски з командою `python3 lab4_extra_run.py summary 3 extra` (еквівалент `python3 measure.py summary 3 extra`) завершилися до досягнення порога. Медіани: **{ru_n(med(extra,'steps'))} кроків**, **{ru_n(med(extra,'prompt'))} вхідних токенів**, **{ru_n(med(extra,'completion'))} вихідних токенів**, **{ru_n(med(extra,'compress'))} стиснень**, **{ru_n(med(extra,'extra'))} токенів на підсумовування**; правильних відповідей — **{compare(extra)}**. Результат внесено окремим рядком `summary` у таблицю 5. Ця серія не показує ефективність переказу, оскільки він фактично не викликався.

**Додаткова порівняльна серія `extra1500`.** Щоб дослідити саме стиснення, для *обох* режимів установлено однаковий поріг **1500** лише на час запусків, без зміни `config.py`. Виконано по три повтори, кожен з відключеним кешем. У таблиці наведені медіани, крім частки правильних відповідей.

| Показник | `trim` (1500) | `summary` (1500) |
|---|---:|---:|
| Правильних відповідей | {compare(trim)} | {compare(summar)} |
| Кроків | {ru_n(med(trim,'steps'))} | {ru_n(med(summar,'steps'))} |
| Вхідних токенів агента | {ru_n(med(trim,'prompt'))} | {ru_n(med(summar,'prompt'))} |
| Вихідних токенів агента | {ru_n(med(trim,'completion'))} | {ru_n(med(summar,'completion'))} |
| Додатково на підсумовування (вхід + вихід окремого виклику) | {ru_n(med(trim,'extra'))} | {ru_n(med(summar,'extra'))} |
| Стиснень | {ru_n(med(trim,'compress'))} | {ru_n(med(summar,'compress'))} |
| Час, с (за консольними підсумками) | 48,2 | 86,9 |

Вхідні токени агента в режимі `summary` зменшилися на **{ru_n(delta)} токенів**, або приблизно **{str(round(pct,1)).replace('.',',')} %** від медіани `trim`. Підсумовування додатково коштувало **{ru_n(med(summar,'extra'))} токени** (медіана за три повтори), і його не можна вважати безплатним. Незважаючи на менший сумарний вхід агента, `summary` працював повільніше — **86,9 с проти 48,2 с** — через додаткові звернення до моделі. Режими виконали **різну кількість кроків** ({ru_n(med(summar,'steps'))} проти {ru_n(med(trim,'steps'))}), тому економію токенів **не можна приписати лише ефективнішому скороченню**: режим `summary` закінчував роботу раніше. Точність в обох серіях залишилася незадовільною (**0/3**).

**Перевірка збереження чисел.** У `logs/extra1500_summary_r1.log` після третього кроку інструмент `scale_amount` з аргументами `{{"amount":360,"base_servings":1,"target_servings":150}}` повернув **54000.0**. У пізнішому блоці `ПІДСУМОК ІСТОРІЇ` після кроку 6 модель перерахувала аргументи `target_servings=150`, `amount=360`, `base_servings=1`, але **не включила отриманий результат 54000.0**. Це приклад *втрати точного результату* при переказі. Крім того, у кінцевих відповідях модель використовувала довільні значення для інших продуктів, не отримавши всі потрібні дані з інструментів. Помилка `base_servings=1` виникла **до** підсумовування і не є спричиненою ним. Отже, підсумовування може втратити числові подробиці й не гарантує коректної відповіді.

**Обмеження.** Експеримент `summary` із нижчим порогом — окрема діагностична серія; він не замінює основні дев'ять запусків із порогом 2150. Для збільшення надійності доречно поєднати стислий переказ з перевіреним структурованим станом та валідацією аргументів, як продемонстровано в експерименті GUIDED V4. Логи: `logs/extra_summary_r1.log`—`r3.log`, `logs/extra1500_trim_r1.log`—`r3.log`, `logs/extra1500_summary_r1.log`—`r3.log`.
{END}

'''


def main():
    if not REPORT.is_file():
        raise SystemExit('ПОМИЛКА: спочатку перейдіть у папку lab4, де є report.md')
    if not (ROOT/'summary.py').is_file():
        raise SystemExit('ПОМИЛКА: немає summary.py (спочатку встановіть додаткове завдання)')
    extra=series('extra','summary')
    trim=series('extra1500','trim')
    summar=series('extra1500','summary')
    check_evidence(extra,trim,summar)

    report=REPORT.read_text(encoding='utf-8')
    if 'GUIDED V4' not in report:
        raise SystemExit('ПОМИЛКА: не знайдено розділ GUIDED V4 — потрібна остання версія звіту')
    if START in report and END in report:
        report=re.sub(re.escape(START)+r'.*?'+re.escape(END)+r'\n\n?', '', report, flags=re.S)
    report=replace_table5(report,extra)
    # Replace conclusion header only, to avoid changing body references to tables.
    matches=list(re.finditer(r'(?m)^## \d+\. Висновок\s*$',report))
    if len(matches)!=1:
        raise SystemExit('ПОМИЛКА: потрібен єдиний розділ «Висновок»')
    match=matches[0]
    section=make_section(extra,trim,summar)
    report=report[:match.start()]+section+report[match.start():]
    report=re.sub(r'(?m)^## \d+\. Висновок\s*$', '## 11. Висновок',report,count=1)
    # Explicit new conclusion point, only once.
    closing=(' Додаткове підсумовування за порога 1500 зменшило медіанну кількість вхідних токенів агента, '
             'але потребувало окремих викликів моделі, працювало повільніше і не зберегло всіх числових результатів. '
             'Це підтверджує необхідність перевіреного структурованого стану та контролю аргументів.')
    if closing.strip() not in report:
        report=report.rstrip()+ '\n\n'+closing.strip()+'\n'
    # The previous analysis phrase 'three configurations only' is still true for main, but clarify the extra row.
    report=report.replace('**Таблиця 5 — вартість циклу в трьох конфігураціях**',
                          '**Таблиця 5 — вартість циклу (три основні конфігурації та додаткова `summary`)**')
    if report.count(START)!=1 or report.count(END)!=1 or '## 11. Висновок' not in report:
        raise SystemExit('ПОМИЛКА: контроль структури звіту не пройдено')
    # Do not mutate report before all validations pass.
    backup=ROOT/'report_before_summary_extra.md'
    if not backup.exists():
        shutil.copy2(REPORT,backup)
    REPORT.write_text(report,encoding='utf-8')
    print('УСПІХ: перевірено 9 журналів додаткового завдання (3+3+3).')
    print(f"Таблиця 5: summary {compare(extra)}, стиснень {med(extra,'compress')} при порозі 2150.")
    print(f"Поріг 1500: trim {med(trim,'prompt')} / summary {med(summar,'prompt')} вхідних токенів; summary окремо {med(summar,'extra')} токенів.")
    print('УСПІХ: таблицю 5 розширено, розділ 10 додано, висновок оновлено.')
    print('Звіт:',REPORT)
    print('Резервна копія:',backup)

if __name__=='__main__':
    main()
