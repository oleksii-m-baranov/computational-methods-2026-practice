"""Коротка перевірка доступу до Langfuse; ключі не друкуються."""
import config
from langfuse import get_client
if __name__=="__main__":
    ok=get_client().auth_check()
    print("LANGFUSE AUTH:",ok)
    raise SystemExit(0 if ok else 1)
