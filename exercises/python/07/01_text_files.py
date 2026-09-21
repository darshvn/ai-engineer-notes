# Section 01: write a text file, add to it, read it back.
# Predict first: how many lines will the file have, and what does the last read() return?
from pathlib import Path

out = Path(__file__).parent / "out"
out.mkdir(exist_ok=True)
notes = out / "notes.txt"

with open(notes, "w", encoding="utf-8") as f:      # "w" empties the file first
    f.write("tokens\n")
    f.write("embeddings\n")

with open(notes, "a", encoding="utf-8") as f:      # "a" adds to the end
    f.write("attention\n")

with open(notes, encoding="utf-8") as f:           # "r" is the default
    for n, line in enumerate(f, start=1):
        print(n, repr(line))
    print("read() at the end gives", repr(f.read()))

# Then try: change "a" to "w" on the second open and run it again.
