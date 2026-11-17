"""Складає таблиці звіту ТІЛЬКИ з реальних логів локального Ollama.

Команда: python build_results.py
Вихід: results_from_logs.md. Якщо логів немає, дані лишаються прочерками.
"""
import json
import statistics
from pathlib import Path
from logparse import parse_log
from metrics import describe
import config

ROOT = Path(__file__).resolve().parent
LOGS = ROOT / 'logs'
EMPTY = '—'


def readrun(run_id):
    path = LOGS / f'{run_id}.log'
    if not path.exists():
        return None, None
    runs = parse_log(path.read_text(encoding='utf-8'))
    if not runs:
        return None, None
    return runs[0], describe(runs[0])


def details_for(series, run_id):
    path = LOGS / f'results_{series}.json'
    if not path.exists():
        return None
    try:
        return next((x for x in json.loads(path.read_text(encoding='utf-8'))
                     if x['run_id'] == run_id), None)
    except (json.JSONDecodeError, KeyError):
        return None


def md_table(headers, rows):
    def cell(x):
        return str(x if x is not None else EMPTY).replace('|', '\\|').replace('\n', ' ')
    return '\n'.join(['| ' + ' | '.join(headers) + ' |',
                      '| ' + ' | '.join('---' for _ in headers) + ' |'] +
                     ['| ' + ' | '.join(map(cell, row)) + ' |' for row in rows])


def fmt(x):
    if x is None:
        return EMPTY
    if isinstance(x, float):
        return f'{x:g}'
    return str(x)


def summarize_step(step):
    if step['server_error']:
        return 'помилка сервера'
    if step['calls']:
        names = [c.split('(', 1)[0] for c in step['calls']]
        return ', '.join(names)
    if step['answer']:
        return 'фінальна відповідь'
    return 'відхилено перевіркою / інше'


def main():
    lines = [
        '# Автоматично витягнуті результати лабораторної №4',
        '',
        '**Джерело:** лише файли `logs/*.log` і `logs/results_*.json`, створені фактичними запусками `measure.py`.',
        '**Важливо:** цей файл не є заміною трас Langfuse; правильність, повноту відповіді та вигадані числа слід перевірити вручну.',
        '',
        '## Таблиця 2. Вхід без захисту',
    ]
    run, d = readrun('probe_none_r1')
    if run:
        rows, prev = [], None
        for s in run['steps']:
            inc = s['tokens'] - prev if prev is not None and s['tokens'] is not None else EMPTY
            rows.append((s['n'], s['tokens'], inc, summarize_step(s)))
            if s['tokens'] is not None:
                prev = s['tokens']
        lines.append(md_table(['Крок', 'prompt_tokens', 'Приріст', 'Дія'], rows))
        lines += ['', f'- Статус: **{d["status"]}**; кроків: **{d["steps"]}**',
                  f'- (а) Постійна частина: **{d["first_tokens"]}** токенів',
                  f'- (б) Типовий приріст: **{fmt(d["typical_growth"])}** токенів',
                  f'- (в) Сума prompt_tokens: **{d["prompt_tokens"]}**; за формулою: **{fmt(d["formula"])}**',
                  f'- (г) Зупинка зростання входу: **{fmt(d["stall"])}**',
                  f'- (д) Три наступні кроки: **{", ".join(f"{s[chr(110)]}: {summarize_step(s)}" for s in run["steps"] if d["stall"] and d["stall"] < s["n"] <= d["stall"]+3) if d["stall"] else "не встановлено"}**']
        if d['status'] == 'server_error':
            case = 'A — серверна помилка (див. повний лог)'
        elif d['stall']:
            case = 'B — спостерігалось уповільнення зростання входу'
        elif d['status'] == 'final' and d['max_tokens'] < .95 * config.NUM_CTX:
            case = 'C — задача не заповнила 95% вікна; згідно з методичкою зменшити його до 3072'
        else:
            case = 'D / інше — необхідна ручна діагностика'
        lines += [f'- Попередня класифікація: **{case}**', '']
    else:
        lines += ['**Реального пробного лога поки немає.** Запустіть `python measure.py none 1 probe`.', '']

    lines += ['## Таблиця 3. Скорочення історії', '']
    t3 = []
    for name in ('trim', 'trim+state'):
        _, dd = readrun(f'probe_{name}_r1')
        if not dd:
            t3.append([name, EMPTY, EMPTY, EMPTY, EMPTY])
        elif dd['squeezes']:
            for s in dd['squeezes']:
                before, msgbefore, msgafter = s['squeeze']
                t3.append([name, s['n'], before, f'{msgbefore} → {msgafter}', dd['repeats']])
        else:
            t3.append([name, 'не було', EMPTY, EMPTY, dd['repeats']])
    lines += [md_table(['Режим','Крок стиснення','Вхід до стиснення','Повідомлень було → стало','Повторних викликів'],t3), '']
    lines += ['## Таблиця 4. Кеш', '']
    t4=[]
    for series in ('cache1','cache2'):
        name=f'{series}_none_r1'
        _,dd=readrun(name); dat=details_for(series,name)
        t4.append([series, dd['steps'] if dd else EMPTY, dd['cache_hits'] if dd else EMPTY,
                   dd['steps']-dd['cache_hits'] if dd else EMPTY,
                   dat.get('seconds') if dat else EMPTY,
                   'так*' if dat and dat.get('right_number_detected') else ('ні*' if dat else EMPTY)])
    lines += [md_table(['Запуск','Кроків','Влучань у кеш','Викликів сервера','Час, с','Число знайдено'], t4),
              '* Автоматична перевірка лише наявності числа 8890, не повноти відповіді.', '']

    lines += ['## Таблиця 5. Медіани по трьох прогонах', '']
    t5=[]
    for name in ('none','trim','trim+state','summary'):
        series='extra' if name=='summary' else 'main'
        parts=[]
        for j in range(1,4):
            rid=f'{series}_{name}_r{j}'
            _,dd=readrun(rid); dat=details_for(series,rid)
            if dd and dat:
                parts.append((dd,dat))
        if len(parts)==3:
            med=lambda func: fmt(statistics.median(func(d,t) for d,t in parts))
            t5.append([name, f'{sum(bool(t.get("right_number_detected")) for _,t in parts)}/3*',
                       med(lambda d,t:d['steps']), med(lambda d,t:d['prompt_tokens']),
                       med(lambda d,t:d['completion_tokens']),
                       med(lambda d,t:t['seconds']), med(lambda d,t:len(d['squeezes'])),
                       med(lambda d,t:d['repeats']),
                       med(lambda d,t:d['extra_tokens']) if name=='summary' else '—'])
        else:
            t5.append([name, f'{len(parts)}/3 логів', *([EMPTY]*8)])
    lines += [md_table(['Режим','Число знайдено','Кроків','Вхід','Вихід','Час, с','Стиснень','Повторів','Дод. токени'], t5),
              '* Необхідно перевірити шість описів маршрутів, ціни та 18 викликів вручну.',
              '', '## Траси Langfuse та ручна перевірка',
              '', '- [ ] Траса `long-main_none_r1` — зробити скриншот у Langfuse',
              '- [ ] Траса `long-main_trim+state_r1` — зробити скриншот у Langfuse',
              '- [ ] Порівняти `prompt_tokens` на першому кроці після стиснення та тому самому кроці без стиснення',
              '- [ ] Перевірити вміст усіх шести описів, ціни та підсумок; шукати вигадані числа',
              '- [ ] Записати точний розмір вікна з `ollama show` та обраний випадок A–D',
              '']
    out=ROOT/'results_from_logs.md'
    out.write_text('\n'.join(lines),encoding='utf-8')
    print('Звіт з логів:',out)
    if not run:
        print('Увага: реальні логи Ollama ще відсутні, дані вимірювань не заповнено.')

if __name__=='__main__':
    main()
