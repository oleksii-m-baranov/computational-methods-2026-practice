import os
import json
import urllib.request
from pathlib import Path

env_path = Path(__file__).parent / ".env"

for line in env_path.read_text(encoding="utf-8-sig").splitlines():
    if line.strip().startswith("GEMINI_API_KEY="):
        os.environ["GEMINI_API_KEY"] = (
            line.split("=", 1)[1].strip().strip('"').strip("'")
        )

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise SystemExit("API-ключ не знайдено у .env")

url = "https://generativelanguage.googleapis.com/v1beta/models"

request = urllib.request.Request(
    url,
    headers={"x-goog-api-key": api_key}
)

try:
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))

    print("Доступні моделі для generateContent:")

    for model in data.get("models", []):
        methods = model.get("supportedGenerationMethods", [])

        if "generateContent" in methods:
            print(model["name"])

except urllib.error.HTTPError as error:
    print("HTTP помилка:", error.code)
except Exception as error:
    print("Помилка:", type(error).__name__)
