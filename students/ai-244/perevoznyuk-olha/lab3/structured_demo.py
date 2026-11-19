from openai import OpenAI

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["search_routes"].model_json_schema()

response = client.chat.completions.create(
    model=config.MODEL,
    messages=[
        {
            "role": "user",
            "content": (
                "Підбери маршрути для подорожі до Нарнії. "
            ),
        }
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {"name": "args", "schema": schema},
    },
)

text = response.choices[0].message.content
print(text)
print(ARGS["search_routes"].model_validate_json(text))