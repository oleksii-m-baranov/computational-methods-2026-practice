
import json


class TaskProgress:
    def __init__(self, task_data):
        self.models = {
            item["model"]: {
                "price": float(item["price"]),
                "search": False,
                "info": False,
                "installment": False
            }
            for item in task_data["expected"]["details"]
        }

        self.months = int(task_data["months"])
        self.overpay_percent = float(
            task_data["overpay_percent"]
        )

        self.successful_calls = 0

    def record(self, name, arguments, level):
        if level != "ok":
            return

        try:
            args = json.loads(arguments)
        except (TypeError, ValueError):
            return

        if not isinstance(args, dict):
            return

        if name == "search_laptops":
            model = str(args.get("query", "")).strip()

            if model in self.models:
                self.successful_calls += 1
                self.models[model]["search"] = True

        elif name == "laptop_info":
            model = str(args.get("model", "")).strip()

            if model in self.models:
                self.successful_calls += 1

                if self.models[model]["search"]:
                    self.models[model]["info"] = True

        elif name == "calc_installment":
            try:
                price = float(args.get("price"))
                months = int(args.get("months"))
                overpay = float(args.get("overpay_percent"))
            except (TypeError, ValueError):
                return

            if (
                months != self.months
                or overpay != self.overpay_percent
            ):
                return

            for model, data in self.models.items():
                if (
                    price == data["price"]
                    and data["search"]
                    and data["info"]
                ):
                    self.successful_calls += 1
                    data["installment"] = True
                    break

    def is_complete(self):
        return all(
            data["search"]
            and data["info"]
            and data["installment"]
            for data in self.models.values()
        )

    def missing(self):
        missing_items = []

        for model, data in self.models.items():
            for key in ("search", "info", "installment"):
                if not data[key]:
                    missing_items.append(
                        f"{model}: {key}"
                    )

        return missing_items

    def summary(self):
        completed = sum(
            all(
                data[key]
                for key in ("search", "info", "installment")
            )
            for data in self.models.values()
        )

        remaining = self.missing()

        return (
            f"Готово моделей: {completed}/{len(self.models)}. "
            f"Успішних викликів: {self.successful_calls}. "
            f"Невиконано: "
            + (", ".join(remaining) if remaining else "немає")
        )

