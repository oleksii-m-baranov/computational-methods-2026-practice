from openai import OpenAI
# Кажемо клієнту стукати не в OpenAI, а на наш комп'ютер
client = OpenAI(
base_url="http://localhost:11434/v1",  # адреса локальної Ollama
api_key="ollama",                       
)

SYSTEM = "Відповідай лише українською, максимум двома реченнями."
USER = " Поясни різницю між процесом і потоком"

# Ollama ключ не перевіряє,
# але поле обов'язкове
response = client.chat.completions.create(
model="llama3.2:3b",
messages=[
{"role": "system", "content": SYSTEM},
{"role": "user",   "content": USER},
],
temperature=0.7,
)
print(response.choices[0].message.content)
print(response.usage)   
# скільки токенів витрачено