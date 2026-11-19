"""Ask the local chat model three fixed questions without tools or documents."""

import json
from pathlib import Path

from openai import OpenAI

import config


def main():
    client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
    cases = json.loads(Path("rag_cases.json").read_text(encoding="utf-8"))
    sample = []
    for case in cases:
        if case["id"] not in {"D1", "P2", "P4"}:
            continue
        response = client.chat.completions.create(
            model=config.MODEL,
            temperature=config.TEMPERATURE,
            max_completion_tokens=100,
            messages=[{"role": "system", "content": config.SYSTEM},
                      {"role": "user", "content": case["question"]}],
        )
        sample.append({**case, "answer": response.choices[0].message.content})
    print(json.dumps(sample, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
