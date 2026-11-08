"""Перевірка описів, згенерованих з класів Pydantic (крок 3)."""
import json

from schemas import SCHEMAS

for schema in SCHEMAS:
    print(json.dumps(schema, ensure_ascii=False, indent=2))
