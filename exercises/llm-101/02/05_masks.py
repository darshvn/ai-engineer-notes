# Section 05: the only difference between an encoder and a decoder.
# Predict first: what will the first row look like in the decoder?
import numpy as np

words = ["the", "river", "bank"]
E = np.array([[0.3, 0.3, 2.5, 0.0], [2.6, 0.0, 0.5, 0.0], [1.6, 1.6, 0.8, 0.0]])
scores = E @ E.T / np.sqrt(4)

def softmax_rows(m):
    e = np.exp(m - m.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)

encoder = softmax_rows(scores)
masked = scores.copy()
masked[np.triu_indices(3, k=1)] = -np.inf   # block every word from seeing later words
decoder = softmax_rows(masked)

for name, m in [("encoder: sees everything", encoder), ("decoder: looks left only", decoder)]:
    print(name)
    for w, row in zip(words, m):
        print(f"   {w:<6}" + "".join(f"{v:7.2f}" for v in row))

# Then try: add a fourth word, "flooded" = [2.4, 0.0, 0.6, 0.0], and change the 3
# in triu_indices to 4. Which rows still match between the two, and which stop?
