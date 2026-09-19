# Section 07: attention on its own cannot tell word order.
# Predict first: will "dog" come out the same in both sentences?
import numpy as np

V = {"dog": [2.0, 0.3, 0.5, 0.0], "bites": [0.4, 2.2, 0.3, 0.0], "man": [1.8, 0.4, 1.9, 0.0]}

def attend(words, add_position=False):
    E = np.array([V[w] for w in words], dtype=float)
    if add_position:                               # the sine/cosine pattern from the note
        pos = np.arange(len(words))[:, None]
        E = E + np.hstack([np.sin(pos), np.cos(pos), np.sin(pos / 10), np.cos(pos / 10)])
    s = E @ E.T / 2
    w = np.exp(s - s.max(axis=1, keepdims=True))
    return (w / w.sum(axis=1, keepdims=True)) @ E

for add in (False, True):
    a = attend(["dog", "bites", "man"], add)[0]    # "dog" is word 0 here...
    b = attend(["man", "bites", "dog"], add)[2]    # ...and word 2 here
    label = "with position " if add else "without position"
    print(f"{label}  dog/bites/man {np.round(a, 2)}   man/bites/dog {np.round(b, 2)}")

# Then try: make the position signal tiny by writing E = E + 0.01 * np.hstack(...).
# Can you still tell the two sentences apart?
