"""Provocative recovery test (provoke-X1) for error recovery demo. Variant 11 (Library)."""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import config
from agent import run_agent
from langfuse import get_client, propagate_attributes
from lab_logger import custom_logger

logger = custom_logger(config.LAB_LOGFILE_NAME)

task = "Які правила видачі книги 'Основи програмування'? Подивись у довіднику книжок book_info."
logger.info("\n" + "=" * 60)
logger.info(f"=== provoke-X1 | очікується: помилка meaning (немає в CSV), виправлення на 'Основи алгоритмів'")
with propagate_attributes(trace_name="provoke-X1", tags=["provoke"]):
    run_agent(task)

get_client().flush()
print("\nRecovery demo completed.")
