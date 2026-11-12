# Lab 1 — запуск (варіант 8)

```bash
python -m venv venv && venv\Scripts\activate      # Windows (Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt
echo CLOUD_API_KEY=ваш_ключ > .env                  # ключ Groq / Google AI Studio (.env у репозиторій не потрапляє)
ollama pull qwen3:4b && ollama pull llama3.2:3b

python task1_reasoning.py   # завдання 1 -> task1_results.json
python hello.py             # завдання 2 -> hello_results.json
python compare.py           # завдання 3
python benchmark.py         # завдання 4 -> results.csv; лише хмара: python benchmark.py cloud  (холодний старт: `ollama stop llama3.2:3b` перед запуском)
python chart.py             # -> chart.png
python quality.py           # завдання 5 -> quality.json; частинами: python quality.py cloud
python check_format.py      # json.loads-перевірка завдання 2
python sampling.py          # завдання 6 -> sampling_results.json
```

Після прогонів заповніть `report.md` і експортуйте його в `report.pdf` (вимога методички).
Журнал виконання пишеться у `lab1.log` (модуль `logsetup.py`). `.env` у репозиторій не потрапляє (він у `.gitignore`).
