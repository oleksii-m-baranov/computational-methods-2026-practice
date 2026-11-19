"""Record one separately labelled Lab 5 replay in the configured Langfuse project."""

import argparse
import json
from pathlib import Path

from langfuse import get_client, propagate_attributes

import agent
import schemas


def main():
    cases = {row["id"]: row["question"] for row in json.loads(Path("rag_cases.json").read_text())}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("description", choices=("B", "C"))
    parser.add_argument("case", choices=sorted(cases))
    args = parser.parse_args()
    client = get_client()
    if not client.auth_check():
        raise SystemExit("Set the keys for the separate Lab 5 Langfuse project in this lab's .env.")

    schemas.set_description("search_docs", schemas.RAG_DESCRIPTIONS[args.description])
    name = f"rag-{args.description}-capture-{args.case}"
    with client.start_as_current_observation(name=name, as_type="span", input=cases[args.case]) as span:
        with propagate_attributes(trace_name=name, tags=["lab5", f"rag-{args.description}", "capture"]):
            answer = agent.run_agent(cases[args.case], logfile_name=name, log_overwrite=True)
        span.update(output=answer)
        print(client.get_trace_url())
    client.flush()


if __name__ == "__main__":
    main()
