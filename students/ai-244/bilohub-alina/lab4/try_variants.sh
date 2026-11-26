#!/bin/bash
# Пробує три формулювання довгого питання (вікно 2048, один виклик за крок, без захисту).
cd ~/lab4 || exit 1
source ~/lab3/venv/bin/activate
export PYTHONPATH=~/cm-utils

python set_window.py 2048

for v in 1 2 3; do
  echo
  echo "################ ФОРМУЛЮВАННЯ $v ################"
  python make_task.py $v
  python measure.py none 1 v$v > /dev/null 2>&1
  python analyze.py logs/v${v}_none_r1.log steps
done
