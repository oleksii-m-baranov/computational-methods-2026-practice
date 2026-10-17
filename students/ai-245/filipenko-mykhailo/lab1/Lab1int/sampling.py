import json
from urllib.request import Request, urlopen

MODEL = "llama3.2:3b"
PROMPT = "У якому році випустили перший iPhone? Відповідай коротко."

def generate(prompt, temperature, top_p):
    data = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": top_p
        }
    }

    request = Request(
        "http://localhost:11434/api/generate",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    with urlopen(request, timeout=180) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["response"]


temperature = 0.7
top_p = 0.3
results = []

for i in range(3):
    print(f"\nЗапуск {i + 1}")

    answer = generate(PROMPT, temperature, top_p)

    print("Відповідь:", answer)

    results.append({
        "model": MODEL,
        "temperature": temperature,
        "top_p": top_p,
        "run": i + 1,
        "answer": answer
    })

with open("sampling_top_p_03.json", "w", encoding="utf-8") as file:
    json.dump(results, file, ensure_ascii=False, indent=4)

print("\nРезультати збережено у sampling_top_p_03.json")