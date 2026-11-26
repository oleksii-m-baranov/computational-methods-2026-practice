#!/bin/bash
# Пробні прогони без захисту для двох розмірів вікна (3072 і 2048 токенів).
cd ~/lab4 || exit 1
source ~/lab3/venv/bin/activate
export PYTHONPATH=~/cm-utils

# перший пробний лог (паралельні виклики) лишаємо для звіту під іншою назвою
if [ -f logs/probe_none_r1.log ]; then
  mv logs/probe_none_r1.log logs/probe_parallel_r1.log
fi

python make_task.py

for size in 3072 2048; do
  echo
  echo "################ ВІКНО $size ################"
  python set_window.py $size
  python measure.py none 1 probe$size
  python analyze.py logs/probe${size}_none_r1.log steps
done
