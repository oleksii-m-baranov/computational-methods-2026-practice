"""Перевірка структурованої відповіді моделі."""
from openai import OpenAI
import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
cls = ARGS['calc_food']
for question in [
    'Скільки корму на 30 днів коту вагою 5 кг за навчальної норми 25 г/кг/день? Сформуй аргументи для calc_food.',
    'Скільки корму на 0 днів коту вагою 5 кг? Сформуй аргументи для calc_food.',
]:
    print('ЗАПИТ:', question)
    try:
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=[{'role':'user', 'content': question}],
            temperature=config.TEMPERATURE,
            response_format={
                'type': 'json_schema',
                'json_schema': {'name': 'args', 'schema': cls.model_json_schema()},
            },
        )
        raw = response.choices[0].message.content
        print('JSON:', raw)
        print('Pydantic:', cls.model_validate_json(raw))
    except Exception as error:
        print('Не вдалося завершити перевірку (підтримка моделі/API або валідація):', error)
        print('У звіті зазнач, чи вдалося відтворити structured output у твоїй Ollama.')
    print()
