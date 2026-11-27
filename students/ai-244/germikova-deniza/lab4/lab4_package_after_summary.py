#!/usr/bin/env python3
"""Create a clean submission archive without keys, caches or draft backups."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import re

root=Path(__file__).resolve().parent
files=[
 'report.md','Modelfile','arguments.py','checks.py','config.py','tools.py',
 'schemas.py','dispatcher.py','agent.py','agent_runner.py','model.py',
 'context.py','compress.py','state.py','cache.py','make_task.py',
 'measure.py','logparse.py','metrics.py','analyze.py','table.py',
 'tasks.json','long_task.json','summary.py','guided_longrun.py',
 'longrun_guard.py','lab4_guided_run_v3.py','lab4_extra_run.py',
 'lab4_summary_review.py','lab4_append_summary_results.py',
 'lab4_package_after_summary.py'
]
for optional in ('Modelfile_3k','Modelfile_4k','README_SUMMARY.md'):
    if (root/optional).is_file(): files.append(optional)
missing=[x for x in files if not (root/x).is_file()]
if missing: raise SystemExit(f'ПОМИЛКА: відсутні файли {missing}')
for group in ('extra','extra1500'):
    modes=('summary',) if group=='extra' else ('trim','summary')
    for mode in modes:
        for i in (1,2,3):
            if not (root/f'logs/{group}_{mode}_r{i}.log').is_file():
                raise SystemExit(f'ПОМИЛКА: немає logs/{group}_{mode}_r{i}.log')
for f in ('langfuse_none.png','langfuse_trim_state.png','langfuse_diag_trim_state.png'):
    if not (root/'screenshots'/f).is_file():
        raise SystemExit(f'ПОМИЛКА: немає screenshots/{f}')
report=(root/'report.md').read_text(encoding='utf-8')
for needle in ('LAB4-SUMMARY-EXTRA:BEGIN','GUIDED V4','На підсумовування','1625,6'):
    if needle not in report: raise SystemExit(f'ПОМИЛКА: звіт не містить: {needle}')
for target in re.findall(r'!\[[^\]]*\]\((screenshots/[^)]+)\)',report):
    if not (root/target).is_file(): raise SystemExit(f'ПОМИЛКА: зображення відсутнє: {target}')
paths=[root/x for x in files]
for folder in ('data','logs','state','screenshots'):
    d=root/folder
    if not d.is_dir(): raise SystemExit(f'ПОМИЛКА: немає папки {folder}')
    paths.extend(p for p in d.rglob('*') if p.is_file() and not p.is_symlink()
        and not any(part.startswith('.') or part=='__pycache__' or part.startswith('backup_')
                    for part in p.relative_to(root).parts))
paths=list(dict.fromkeys(paths))
archive=Path.home()/'Downloads'/'Lab4_Germikova_AI244_SUMMARY_FINAL.zip'
archive.parent.mkdir(parents=True,exist_ok=True)
with ZipFile(archive,'w',ZIP_DEFLATED) as z:
    for path in paths:
        rel=path.relative_to(root)
        z.write(path,arcname=Path('lab4')/rel)
with ZipFile(archive) as z:
    bad=z.testzip()
    if bad: raise SystemExit(f'ПОМИЛКА ZIP: {bad}')
    if any('.env' in x or '__pycache__' in x for x in z.namelist()):
        raise SystemExit('ПОМИЛКА: у ZIP потрапили службові файли')
    print('УСПІХ: ZIP перевірено:',len(z.namelist()),'файлів')
print('Файл:',archive)
print('Розмір:',round(archive.stat().st_size/1024/1024,2),'МБ')
