"""Генератор отчёта по набору данных (вариант 7)."""
import argparse
import json
import sys


def load_data(path):
    """Читает JSON-файл со списком записей {"name": str, "value": число}."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("dataset must be a JSON list")
    return data


def build_report(records):
    """Строит сводку: количество, сумма, среднее и максимум."""
    values = []
    for rec in records:
        if not isinstance(rec, dict) or "value" not in rec:
            raise ValueError("record must contain 'value'")
        value = rec["value"]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("'value' must be a number")
        values.append(float(value))
    count = len(values)
    total = sum(values)
    average = round(total / count, 2) if count else 0.0
    maximum = max(values) if values else 0.0
    return {"count": count, "total": total, "average": average, "max": maximum}


def format_report(report):
    return (
        f"Records: {report['count']}\n"
        f"Total: {report['total']:.2f}\n"
        f"Average: {report['average']:.2f}\n"
        f"Max: {report['max']:.2f}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Create a report from a JSON dataset.")
    parser.add_argument("--input", default="data.json.example", help="path to JSON dataset")
    args = parser.parse_args(argv)
    try:
        report = build_report(load_data(args.input))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(format_report(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
