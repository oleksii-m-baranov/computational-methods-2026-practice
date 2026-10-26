#import tools 

#print(tools.search_routes("Яремче"))
#print(tools.transport_info("Приморські Скелі — Очаків"))
#print(tools.calc_budget(1000, 2, 50))

from tools import TOOLS
from schemas import SCHEMAS

print(len(SCHEMAS))
print({s["function"]["name"] for s in SCHEMAS} == set(TOOLS))
