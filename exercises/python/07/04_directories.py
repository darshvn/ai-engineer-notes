# Section 04: build folders, list files, and rename them with pathlib.
# Predict first: which files does glob("*.csv") find, and in what order?
from pathlib import Path
import shutil

root = Path(__file__).parent / "out" / "project"
shutil.rmtree(root, ignore_errors=True)
(root / "data" / "raw").mkdir(parents=True)                   # makes every missing folder
for name in ["b.csv", "a.csv", "notes.txt", "raw/c.csv"]:
    (root / "data" / name).write_text("x", encoding="utf-8")

data = root / "data"
print("glob     :", [p.name for p in data.glob("*.csv")])
print("sorted   :", sorted(p.name for p in data.glob("*.csv")))
print("parts    :", (data / "a.csv").stem, (data / "a.csv").suffix, (data / "a.csv").parent.name)
(data / "notes.txt").rename(data / "notes.md")
print("after    :", sorted(p.name for p in data.iterdir()))
print("relative :", Path("data").resolve() == data.resolve())

# Then try: change glob("*.csv") to glob("**/*.csv").
