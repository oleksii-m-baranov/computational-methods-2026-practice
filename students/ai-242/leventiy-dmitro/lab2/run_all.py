import json

from matplotlib import text
from agent import run_agent

with open("tasks.json", encoding="utf-8") as f:
    tasks = json.load(f)
    
logfile = open("logs/run.txt", "w", encoding="utf-8")

def log(text):
    print(text)
    logfile.write(text + "\n")

for task in tasks:
    log(f"\n=== {task['id']} | очікується: {task['expected']}")
    run_agent(task["question"], log)

logfile.close()
print(f"\nОброблено задач: {len(tasks)}. Лог: logs/run.txt")