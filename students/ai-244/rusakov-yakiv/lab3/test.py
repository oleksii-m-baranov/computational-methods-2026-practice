"""Крок 3: перевірка згенерованого опису для моделі."""
import json

from schemas import SCHEMAS

print(json.dumps(SCHEMAS[0], ensure_ascii=False, indent=2))
print(json.dumps(SCHEMAS[2], ensure_ascii=False, indent=2))
