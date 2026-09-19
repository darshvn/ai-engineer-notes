# Section 03: the three steps from the note, in ten lines.
# Predict first: what will "bank"'s water and money numbers be afterwards?
import numpy as np

words = ["the", "river", "bank"]
E = np.array([[0.3, 0.3, 2.5, 0.0],        # water, money, generic, unused
              [2.6, 0.0, 0.5, 0.0],
              [1.6, 1.6, 0.8, 0.0]])

scores = E @ E[2]                          # 1. score every word against "bank"
shares = np.exp(scores / np.sqrt(4))       # 2. divide by sqrt(4), then softmax
shares /= shares.sum()
new_bank = shares @ E                      # 3. mix the words by those shares

for w, s, sh in zip(words, scores, shares):
    print(f"  {w:<6} score {s:.2f}   share {sh:.3f}")
print(f"\nbank before: water {E[2, 0]:.2f}  money {E[2, 1]:.2f}")
print(f"bank after : water {new_bank[0]:.2f}  money {new_bank[1]:.2f}")

# Then try: replace river with savings = [0.0, 2.6, 0.5, 0.0].
# Then try: delete "/ np.sqrt(4)" and watch the shares.
