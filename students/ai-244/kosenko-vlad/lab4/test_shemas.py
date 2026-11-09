from tools import TOOLS
from schemas import SCHEMAS

print(len(SCHEMAS))
print({s["function"]["name"] for s in SCHEMAS} == set(TOOLS))