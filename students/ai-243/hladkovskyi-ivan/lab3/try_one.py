import sys
import config
config.LAB_LOGFILE_NAME = "lab3_extra"  
from langfuse import get_client, propagate_attributes
from agent import run_agent

with propagate_attributes(trace_name="extra", tags=["extra"]):
    run_agent(sys.argv[1])
get_client().flush()