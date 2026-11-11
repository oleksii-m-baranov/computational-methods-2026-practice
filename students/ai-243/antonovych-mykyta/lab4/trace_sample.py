"""Record one separately labelled Lab 4 replay in the configured Langfuse project."""

import argparse

from langfuse import get_client, propagate_attributes

import agent
import config
from measure import CONFIGS, load_task


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("none", "trim+state"))
    args = parser.parse_args()
    client = get_client()
    if not client.auth_check():
        raise SystemExit("Set the keys for the separate Lab 4 Langfuse project in this lab's .env.")

    for name, value in CONFIGS[args.mode].items():
        setattr(config, name, value)
    task = load_task()
    name = f"lab4-capture-{args.mode}"
    with client.start_as_current_observation(name=name, as_type="span", input=task["question"]) as span:
        with propagate_attributes(trace_name=name, tags=["lab4", args.mode, "capture"]):
            answer = agent.run_agent(task["question"], max_steps=config.MAX_STEPS_LONG,
                                     logfile_name=name, task_id=name, log_overwrite=True)
        span.update(output=answer)
        print(client.get_trace_url())
    client.flush()


if __name__ == "__main__":
    main()
