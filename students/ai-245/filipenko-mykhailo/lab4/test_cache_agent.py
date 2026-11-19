import config
from agent import call_tool_cached, tool_cache
from utils.lab_logger import custom_logger

config.USE_CACHE = True

logger = custom_logger(config.LAB_LOGFILE_NAME)

tool_cache.data.clear()
tool_cache.hits = 0
tool_cache.misses = 0

name = "laptop_info"
arguments = '{"model": "StudyNova 14"}'

print("Перший виклик")
level1, result1 = call_tool_cached(name, arguments, logger)
print("Рівень:", level1)
print("Результат:", result1)
print("Кеш:", tool_cache.stats())

print()

print("Другий виклик")
level2, result2 = call_tool_cached(name, arguments, logger)
print("Рівень:", level2)
print("Результат:", result2)
print("Кеш:", tool_cache.stats())

assert level1 == "ok"
assert level2 == "ok"
assert result1 == result2
assert tool_cache.stats()["hits"] == 1
assert tool_cache.stats()["misses"] == 1

print()
print("CACHE TEST: PASS")
