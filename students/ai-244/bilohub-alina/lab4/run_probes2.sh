#!/bin/bash
# Пробні прогони без захисту з виконанням одного виклику за крок (вікна 3072 і 2048).
cd ~/lab4 || exit 1
source ~/lab3/venv/bin/activate
export PYTHONPATH=~/cm-utils

# вмикаємо ONE_CALL_PER_STEP у config.py, якщо його там ще немає
if ! grep -q "^ONE_CALL_PER_STEP" config.py; then
  printf '\nONE_CALL_PER_STEP = True   # виконувати лише перший із викликів, запрошених моделлю за один крок\n' >> config.py
fi

for size in 3072 2048; do
  echo
  echo "################ ВІКНО $size, ОДИН ВИКЛИК ЗА КРОК ################"
  python set_window.py $size
  python measure.py none 1 seq$size
  python analyze.py logs/seq${size}_none_r1.log steps
done
