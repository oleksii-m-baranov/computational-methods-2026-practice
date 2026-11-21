"""Перегляд згенерованої схеми інструмента."""
import json
from schemas import SCHEMAS

for s in SCHEMAS:
    print(json.dumps(s, ensure_ascii=False, indent=2))
