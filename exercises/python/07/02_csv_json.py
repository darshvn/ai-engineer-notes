# Section 02: save the same records as CSV and as JSON, then read both back.
# Predict first: what type is "score" after each round trip?
import csv, json
from pathlib import Path

out = Path(__file__).parent / "out"
out.mkdir(exist_ok=True)
rows = [{"name": "Asha", "score": 92, "tags": ("python", "sql")},
        {"name": "Ravi", "score": 78, "tags": ("maths",)}]

with open(out / "scores.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "score", "tags"])
    writer.writeheader()
    writer.writerows(rows)
with open(out / "scores.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2)

from_csv = list(csv.DictReader(open(out / "scores.csv", newline="", encoding="utf-8")))
from_json = json.load(open(out / "scores.json", encoding="utf-8"))
print("CSV :", repr(from_csv[0]["score"]), repr(from_csv[0]["tags"]))
print("JSON:", repr(from_json[0]["score"]), repr(from_json[0]["tags"]))

# Then try: add "joined": {2024, 2025} (a set) to Asha's record.
