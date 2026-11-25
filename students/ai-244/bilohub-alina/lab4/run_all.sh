#!/bin/bash
# Основна серія вимірювань у вікні 1920 токенів: три конфігурації по три повтори + кеш.
cd ~/lab4 || exit 1
source ~/lab3/venv/bin/activate
export PYTHONPATH=~/cm-utils

python make_task.py
python set_window.py 1920

# основна серія: none, trim, trim+state по 3 повтори (логи logs/main_<конфігурація>_r<повтор>.log)
python measure.py all 3 main

# серія з кешем (назва починається з cache): другий повтор бере відповіді з кешу
python measure.py trim+state 2 cache

# аналіз усіх логів серій у один файл
rm -f analysis_main.txt
for f in logs/main_*.log logs/cache_*.log; do
  echo "######## $f" >> analysis_main.txt
  python analyze.py "$f" >> analysis_main.txt 2>&1
done

# усе потрібне для мене - в один архів
rm -f lab4_results.zip
zip -r -q lab4_results.zip logs state analysis_main.txt long_task.json config.py
echo
echo "Готово: файл ~/lab4/lab4_results.zip"
