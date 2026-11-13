# Lab 2 — запуск (варіант 8)

`utils/lab_logger.py` лежить у корені репозиторію, тому запускайте з каталогу `lab2`,
додавши корінь репозиторію в `PYTHONPATH`:

```bash
python -m venv venv && venv\Scripts\activate
pip install openai
ollama pull qwen2.5:3b

# Linux/macOS:  export PYTHONPATH=../../../..
# Windows (PowerShell):  $env:PYTHONPATH="..\..\..\.."
python dispatcher.py        # перевірка диспетчера без моделі
python agent_runner.py      # ОДИН прогін на 5 задачах -> lab2.log
```

Далі працюйте з `lab2.log` і заповніть таблиці в `report.md`.
Файл `*.log` у `.gitignore` репозиторію — додавайте його через `git add -f lab2/lab2.log`.
