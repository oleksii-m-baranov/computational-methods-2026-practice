#!/usr/bin/env python3
"""Install real Langfuse screenshot and portable logger into the user's Lab4.

Works in lab4, makes report backup, leaves all experimental logs/config untouched.
"""
from __future__ import annotations
import ast
from pathlib import Path
import hashlib
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SCREEN = HERE / 'screenshots' / 'langfuse_guidedv4.png'
REPORT = HERE / 'report.md'
MARKER = '<!-- LAB4-GUIDED-V4-SCREENSHOT -->'


def same_bytes(a: Path, b: Path) -> bool:
    return a.read_bytes() == b.read_bytes()


def main() -> None:
    if not SCREEN.is_file() or not SCREEN.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):
        raise SystemExit('ПОМИЛКА: скриншот screenshots/langfuse_guidedv4.png не знайдено або пошкоджено. Розпакуйте ZIP у lab4.')
    if not REPORT.is_file():
        raise SystemExit('ПОМИЛКА: відсутній report.md (потрібно запускати в lab4).')

    # The parent repository has no setup.py / pyproject.toml: editable pip install cannot work.
    # Ship the exact working logger implementation, instead of inventing a replacement.
    dest = HERE / 'utils' / 'lab_logger.py'
    if not dest.is_file():
        sources = [p / 'utils' / 'lab_logger.py' for p in HERE.parents]
        source = next((p for p in sources if p.is_file()), None)
        if source is None:
            raise SystemExit('ПОМИЛКА: не знайдено utils/lab_logger.py у батьківських папках. ' 
                             'Залишаємо проєкт без змін; перевірте корінь /Users/deniza/lab3.')
        source_text = source.read_text(encoding='utf-8')
        ast.parse(source_text, filename=str(source))
        dest.parent.mkdir(exist_ok=True)
        init = dest.parent / '__init__.py'
        if not init.exists():
            init.write_text('"""Локальна копія спільного логера з навчального репозиторію."""\n',encoding='utf-8')
        shutil.copy2(source, dest)
        print('УСПІХ: utils/lab_logger.py додано з оригінального репозиторію')
    else:
        print('OK: utils/lab_logger.py уже присутній, не перезаписуємо')
        init=dest.parent/'__init__.py'
        if not init.exists():
            init.write_text('"""Локальний пакет спільного логера."""\n',encoding='utf-8')

    # Prove that import resolves inside lab4, NOT through an inherited PYTHONPATH.
    import os
    env=os.environ.copy()
    env.pop('PYTHONPATH',None)
    code='import utils.lab_logger as m; print(m.__file__)'
    check=subprocess.run([sys.executable,'-c',code], cwd=HERE,env=env,
                         text=True, capture_output=True)
    if check.returncode != 0 or Path(check.stdout.strip()).resolve() != dest.resolve():
        raise SystemExit('ПОМИЛКА: автономний імпорт utils не пройшов:\n'+check.stderr+'\n'+check.stdout)
    print('УСПІХ: автономний імпорт utils підтверджений без PYTHONPATH')

    content = REPORT.read_text(encoding='utf-8')
    if MARKER in content:
        if 'screenshots/langfuse_guidedv4.png' not in content:
            raise SystemExit('ПОМИЛКА: некоректний маркер скриншота в report.md')
        print('OK: скриншот GUIDED V4 вже є у звіті, дубль не додаємо')
        return
    if 'screenshots/langfuse_guidedv4.png' in content:
        print('OK: скриншот GUIDED V4 вже має посилання в report.md')
        return

    start = content.find('## 9. Додатковий експеримент: керований агент GUIDED V4')
    if start < 0:
        raise SystemExit('ПОМИЛКА: не знайдено розділ 9 про GUIDED V4 у report.md; змін немає')
    import re
    following = re.search(r'(?m)^##\s+\d+\.\s+', content[start+10:])
    if not following:
        raise SystemExit('ПОМИЛКА: не знайдено наступного розділу після GUIDED V4')
    end=start+10+following.start()
    add=(f'\n{MARKER}\n'
         '**Рисунок 4 — справжня траса успішного запуску GUIDED V4 у Langfuse.** '
         'На знімку видно дерево `run_agent`, послідовність `OpenAI-generation` і `call_tool`, '
         'час виконання та підсумок **1625,6 ккал**. '
         'Чотири події стиснення підтверджені текстовим журналом `logs/guidedv4_trim+state_r1.log`; '
         'вони не позначені окремими вузлами дерева.\n\n'
         '![Успішний GUIDED V4 — дерево Langfuse та фінальна відповідь]'
         '(screenshots/langfuse_guidedv4.png)\n\n')
    backup=HERE/'report_before_guidedv4_screenshot.md'
    if not backup.exists(): shutil.copy2(REPORT,backup)
    REPORT.write_text(content[:end].rstrip()+'\n\n'+add+content[end:],encoding='utf-8')
    print('УСПІХ: справжній скриншот GUIDED V4 додано до report.md')
    print('Код агента, config.py, main-логи не змінено')

if __name__ == '__main__':
    main()
