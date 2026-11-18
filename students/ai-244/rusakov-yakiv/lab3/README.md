# Lab 3 — запуск (варіант 8)

Потрібен `lab2.log` з лабораторної №2 — скопіюйте його сюди (`cp ../lab2/lab2.log .`).

```bash
python -m venv venv && venv\Scripts\activate
pip install openai pydantic python-dotenv "langfuse>=4"
# створіть .env з рядками LANGFUSE_PUBLIC_KEY=..., LANGFUSE_SECRET_KEY=..., LANGFUSE_HOST=https://cloud.langfuse.com (.env не комітити)

# Linux/macOS:  export PYTHONPATH=../../../..
python test_checks.py       # табл. 2, без моделі
python test.py              # перевірка схем

# 1) базовий прогін: у config.py RUN_TAG = "baseline"
python agent_runner.py
mv lab3.log lab3_baseline.log

# 2) прогін з перевірками: у config.py RUN_TAG = "checks"
python agent_runner.py
mv lab3.log lab3_checks.log

python structured_demo.py   # додаткове завдання (за бажанням)
```

`agent_baseline.py` + `dispatcher_baseline.py` + `schemas_baseline.py` — агент лабораторної №2
з трасуванням (для базового прогону). `agent.py` + `dispatcher.py` + `schemas.py` — версія з перевірками.
Файл `.env` містить ключі Langfuse — **не додавайте його в git** (кореневий `.gitignore` репозиторію його ігнорує). Логи (`*.log`) лежать у каталозі лаби й комітяться як є (кореневий `.gitignore` їх не ігнорує).

Додаткові задачі: у `tasks.json` є Z4 і Z5g (провокаційне питання для події «помилка → виправлення»).
Логи: `lab3_checks_new.log` (повторний прогін з Z4), `lab3_Z5g.log` (Z5g), `z5_attempts/` — усі спроби підібрати питання (Z5–Z5i).
Скриншоти Langfuse з підписаними етапами — `screenshots/`.
