
import json

with open("quality.json", "r", encoding="utf-8") as file:
    data = json.load(file)

for model, tasks in data.items():
    print("\nМодель:", model)

    for run in tasks["2_json"]:
        print("Прогін:", run["run"])

        try:
            result = json.loads(run["answer"])

            year = result.get("year")
            person = str(result.get("person", ""))

            correct_year = str(year) == "1961"
            correct_person = (
                "гагарін" in person.lower()
                or "гагарин" in person.lower()
                or "gagarin" in person.lower()
            )

            correct_fields = set(result.keys()) == {
                "event", "year", "person"
            }

            print("JSON правильний: ТАК")
            print("Рік правильний:", correct_year)
            print("Людина правильна:", correct_person)
            print("Рівно 3 потрібні поля:", correct_fields)
            print("Загальний результат:",
                  "PASS" if (
                      correct_year
                      and correct_person
                      and correct_fields
                  ) else "FAIL")

        except json.JSONDecodeError:
            print("JSON правильний: НІ")
            print("Загальний результат: FAIL")
