# Lab 4 — варіант 12 (кулінарія)

Запуск (з каталогу lab4, з активованим середовищем; `.env` з ключами Langfuse поклади поруч):

    pip install openai pydantic python-dotenv "langfuse>=4"
    pip install -e .            # у корені репозиторію (utils.lab_logger)
    ollama create qwen3-1792 -f Modelfile
    python make_task.py         # -> long_task.json (expected = 2320.6)
    python measure.py none 1 probe
    python analyze.py logs\probe_none_r1.log steps
    python measure.py all 3 main

Параметри (config.py): модель qwen3-1792 (з qwen3:4b-instruct), NUM_CTX=1792, COMPRESS_AT=1600.
Вікно 1792 підібране за пробним прогоном (вхід першого кроку 1199, приріст ~61 токен/виклик).
Якщо в пробному прогоні `none` вхід не доходить до ~95% вікна (випадок C) —
зменшіть num_ctx у Modelfile й NUM_CTX/COMPRESS_AT у config.py (COMPRESS_AT ≈ 0.9 * NUM_CTX).