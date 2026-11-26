#!/bin/bash
# Пробний прогін без захисту у вікні 1920 токенів.
cd ~/lab4 || exit 1
source ~/lab3/venv/bin/activate
export PYTHONPATH=~/cm-utils

ollama create qwen25-1920 -f Modelfile_1920
python make_task.py
python set_window.py 1920
python measure.py none 1 probe1920 > /dev/null 2>&1
python analyze.py logs/probe1920_none_r1.log steps
echo
echo "---- рядки лога про сервер і стиснення ----"
grep -E "ПОМИЛКА СЕРВЕРА|СТОП|ВІДПОВІДЬ" logs/probe1920_none_r1.log | head -8
