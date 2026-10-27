import json
from urllib.request import Request, urlopen

def ask_model(prompt, model="llama3.2:3b"):
    url = "http://localhost:11434/api/generate"

    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    request = Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    with urlopen(request, timeout=180) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["response"]


if __name__ == "__main__":
    question = "Поясни різницю між функцією і методом. Коротко."

    print("Запитання:", question)
    print("Відповідь моделі:")
    print(ask_model(question))
