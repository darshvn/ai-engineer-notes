# Section 03: pickle keeps Python objects exactly, and loading one can run code.
# Predict first: what type comes back, and what does the second load print?
import pickle   # safe here only because this script loads nothing but bytes it just made
from pathlib import Path

out = Path(__file__).parent / "out"
out.mkdir(exist_ok=True)

class Student:
    def __init__(self, name, skills):
        self.name, self.skills = name, skills

data = {"student": Student("Asha", {"python", "sql"}), "scores": (92, 78)}
(out / "data.pkl").write_bytes(pickle.dumps(data))
back = pickle.loads((out / "data.pkl").read_bytes())
print(type(back["student"]).__name__, sorted(back["student"].skills), back["scores"])
print("first bytes:", (out / "data.pkl").read_bytes()[:12])

class Surprise:                      # a harmless stand-in for a malicious file
    def __reduce__(self):
        return (print, ("this line ran inside pickle.loads()",))

pickle.loads(pickle.dumps(Surprise()))

# Then try: json.dumps(data) and read the error.
