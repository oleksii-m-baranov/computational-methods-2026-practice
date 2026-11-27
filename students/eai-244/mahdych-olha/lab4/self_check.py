"""Перевірки логіки без Ollama, Langfuse й мережевих запитів."""
import os
import json
from pathlib import Path
os.chdir(Path(__file__).resolve().parent)
from make_task import build_task, calories_of_one, ITEMS
from context import trim
from measure import is_correct
assert build_task()["expected"]=="1298.9"
assert json.loads(Path("long_task.json").read_text(encoding="utf-8"))==build_task()
assert [calories_of_one(p,g) for p,g in ITEMS]==[516,380,28,192.5,62.4,120]
assert is_correct("Разом 1298,9 ккал", "1298.9")
assert not is_correct("11298.9", "1298.9")
assert not is_correct("1298.95", "1298.9")
head=[{"role":"system","content":"s"},{"role":"user","content":"u"}]
turns=[{"role":"assistant","tool_calls":[{"id":"a"}]},{"role":"tool","tool_call_id":"a"},
       {"role":"assistant","tool_calls":[{"id":"b"}]},{"role":"tool","tool_call_id":"b"},
       {"role":"tool","tool_call_id":"b"}]
result=trim(head+turns,4)
assert result[:2]==head
assert len(result)==2 or result[2]["role"]!="tool"
assert trim(head+turns,1)==head
print("SELF CHECK OK: arithmetic, task, numeric check, history pairs")
