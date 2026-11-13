"""Provocative recovery test (provoke-X1) for error recovery demo. Variant 11 (Library)."""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import config
from agent import run_agent
from langfuse import get_client, propagate_attributes
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from utils.lab_logger import custom_logger

logger = custom_logger(config.LAB_LOGFILE_NAME)

task = "Порахуй штраф через calculate з operation='mul', a=-5, b=10."
logger.info("\n" + "=" * 60)
logger.info("=== provoke-X1 | очікується: помилка schema (a=-5 < 0), виправлення на a=5")
with propagate_attributes(trace_name="provoke-X1", tags=["provoke"]):
    run_agent(task)

get_client().flush()
print("\nRecovery demo completed.")
