# Section 04: split the numbers into two heads and let each attend on its own.
# Head A sees the first two numbers (water, money); head B sees the other two.
# Predict first: will both heads give "river" the same share?
import numpy as np

words = ["the", "river", "bank"]
E = np.array([[0.3, 0.3, 2.5, 0.0],
              [2.6, 0.0, 0.5, 0.0],
              [1.6, 1.6, 0.8, 0.0]])

def shares_for_bank(part):
    scores = part @ part[2] / np.sqrt(part.shape[1])
    s = np.exp(scores - scores.max())
    return s / s.sum()

for name, cols in [("one big head", slice(0, 4)), ("head A (meaning)", slice(0, 2)),
                   ("head B (generic)", slice(2, 4))]:
    s = shares_for_bank(E[:, cols])
    print(f"{name:<17} " + "  ".join(f"{w} {v:.2f}" for w, v in zip(words, s)))

# Then try: change "the" to [0.3, 2.5, 2.5, 0.0], giving it a large money number.
# Which head notices?
