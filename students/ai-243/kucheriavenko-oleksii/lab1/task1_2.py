import json
import urllib.request
import statistics
from providers import make_client

def ollama_generate(model, prompt):
    data = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    req = urllib.request.Request("http://localhost:11434/api/generate", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

print("=== ЗАВДАННЯ 1: Фактичне питання ===")
for m in ["qwen3:4b", "llama3.2:3b"]:
    ollama_generate(m, "Привіт") # прогрів
    r = ollama_generate(m, "Столиця України? Відповідай одним словом.")
    total_s = r["total_duration"] / 1e9
    tok_s = r["eval_count"] / (r["eval_duration"] / 1e9)
    print(f"{m}: response='{r['response'].strip()}' | eval_count={r['eval_count']} | Час={total_s:.2f} с | Токенів/с={tok_s:.2f}")

print("\n=== ЗАВДАННЯ 1: Задача на міркування (5 запусків) ===")
logic_prompt = "Ручка і зошит разом коштують 110 грн. Ручка на 100 грн дешевша за зошит. Скільки коштує ручка?"
for m in ["qwen3:4b", "llama3.2:3b"]:
    runs = [ollama_generate(m, logic_prompt) for _ in range(5)]
    for i, r in enumerate(runs, 1):
        print(f"  [{m} #{i}] відповідь: {r['response'].strip().splitlines()[-1]}")
    avg_eval = statistics.mean(r["eval_count"] for r in runs)
    avg_time = statistics.mean(r["total_duration"] / 1e9 for r in runs)
    print(f"--> {m} СЕРЕДНЄ: eval_count={avg_eval:.1f} | Час={avg_time:.2f} с")

print("\n=== ЗАВДАННЯ 2 (Варіант 5): Роль system-повідомлення ===")
USER_Q = "Поясни різницю між масивом і зв'язним списком."
SYSTEMS = [
    ("лаконічний асистент", "Ти лаконічний технічний асистент."),
    ("українською, 2 речення", "Відповідай лише українською, максимум двома реченнями.")
]
for prov in ["local", "local_reason"]:
    client, model = make_client(prov)
    for label, sys_msg in SYSTEMS:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": USER_Q}],
            temperature=0.7,
        )
        ans = resp.choices[0].message.content.strip()
        u = resp.usage
        print(f"\n[{model} | {label}] довжина={len(ans)} симв. | prompt={u.prompt_tokens}, completion={u.completion_tokens}, total={u.total_tokens}")
        print(ans)
