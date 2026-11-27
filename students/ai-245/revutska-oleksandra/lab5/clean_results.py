
import csv
from pathlib import Path

path = Path("results/description_comparison.csv")
backup = Path("results/description_comparison_backup.csv")

with path.open("r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    rows = list(reader)

if not backup.exists():
    backup.write_bytes(path.read_bytes())

unique = {}

for row in rows:
    key = (
        row["variant"],
        row["repeat"],
        row["case_id"],
    )
    unique[key] = row

with path.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(unique.values())

print("Було рядків:", len(rows))
print("Стало рядків:", len(unique))
print("Дублікатів прибрано:", len(rows) - len(unique))
