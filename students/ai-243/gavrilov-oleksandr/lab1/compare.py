import time
from providers import make_client

# Твоє точне питання (Варіант 4)
QUESTION = "Поясни різницю між оперативною пам’яттюі жорстким диском.Коротко."

for name in ["local", "cloud"]:
    client, model = make_client(name)
    
    t0 = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": QUESTION}],
        temperature=0.7,
    )
    elapsed = time.perf_counter() - t0
    
    print(f"===== {name.upper()} ({model}) =====")
    print(response.choices[0].message.content)
    print(f"Час: {elapsed:.2f} с")
    print(response.usage)
    print()
