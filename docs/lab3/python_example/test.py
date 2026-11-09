from schemas import SCHEMAS
import json

print(json.dumps(SCHEMAS[0], ensure_ascii=False, indent=2))
