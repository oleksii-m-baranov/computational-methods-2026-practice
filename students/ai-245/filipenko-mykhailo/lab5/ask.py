import sys
from agent import run_agent

if __name__ == "__main__":
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        question = input("Введіть запитання: ").strip()

    if not question:
        print("Запитання не може бути порожнім.")
        sys.exit(1)

    result = run_agent(question)
    if result is not None:
        print(result)
