import time
import statistics
import csv
from providers import make_client

def measure(client, model, prompt):
    """Один вимір: повертає TTFT, загальний час і довжину відповіді."""
    t_start = time.perf_counter()
    first_token_at = None
    parts = []
    
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    
    for chunk in stream:
        piece = chunk.choices[0].delta.content
        if piece:
            if first_token_at is None:
                first_token_at = time.perf_counter()
            parts.append(piece)
            
    t_end = time.perf_counter()
    text = "".join(parts)
    
    if first_token_at is None:
        first_token_at = t_end
        
    return {
        "ttft_s": round(first_token_at - t_start, 3),
        "total_s": round(t_end - t_start, 3),
        "chars": len(text),
        "chars_per_s": round(len(text) / (t_end - t_start), 1) if (t_end - t_start) > 0 else 0,
    }

PROMPTS = {
    "short":  "Столиця Норвегії?",
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long":   "Напиши інструкцію з 10 пунктів, як провести кодрев’ю.",
}

if __name__ == "__main__":
    rows = []
    
    for provider in ["local", "cloud"]:
        print(f"\n--- Вимірювання для {provider.upper()} ---")
        client, model = make_client(provider)
        
        # Прогрів
        print("Прогрів моделі...")
        measure(client, model, "розігрів")
        if provider == "cloud":
            time.sleep(13)  # Пауза після прогріву для cloud
        
        for name, prompt in PROMPTS.items():
            print(f"Тестування промпту: {name}...")
            runs = []
            for i in range(3):
                res_single = measure(client, model, prompt)
                runs.append(res_single)
                if provider == "cloud":
                    print(f"  [Спроба {i+1}/3] Зачекайте 13s для дотримання Rate Limit...")
                    time.sleep(13)
            
            res = {
                "provider": provider,
                "model": model,
                "prompt": name,
                "ttft_s": statistics.median(r["ttft_s"] for r in runs),
                "total_s": statistics.median(r["total_s"] for r in runs),
                "chars_per_s": statistics.median(r["chars_per_s"] for r in runs),
            }
            rows.append(res)
            print(f"  Result ({name}): TTFT={res['ttft_s']}s, Total={res['total_s']}s, Speed={res['chars_per_s']} char/s")

    # Збереження у CSV
    with open("results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        
    print("\nВимірювання завершено успішно. Результати збережено в results.csv")