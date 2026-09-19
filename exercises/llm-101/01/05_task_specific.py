# Section 05: build a task-specific model from labelled examples.
# Predict first: what will it say about "an absolute masterpiece"?
import time
from collections import Counter

train = [
    ("loved it, great acting", "pos"), ("wonderful and moving", "pos"),
    ("great fun, loved the ending", "pos"), ("brilliant, wonderful cast", "pos"),
    ("boring and far too long", "neg"), ("terrible plot, awful acting", "neg"),
    ("awful, boring, a waste", "neg"), ("terrible ending, hated it", "neg"),
]

weights = Counter()                       # training: count which words go with which label
for text, label in train:
    for word in text.replace(",", "").split():
        weights[word] += 1 if label == "pos" else -1

def classify(text):
    score = sum(weights[w] for w in text.lower().replace(",", "").split())
    return "pos" if score > 0 else "neg" if score < 0 else "no idea"

tests = ["great acting, wonderful", "boring and awful",
         "an absolute masterpiece", "summarise this review for me"]
start = time.perf_counter()
results = [classify(t) for t in tests]
took = time.perf_counter() - start
for t, r in zip(tests, results):
    print(f"  {t!r:32} -> {r}")
print(f"\n{len(tests)} predictions in {took * 1e6:.0f} microseconds")

# Then try: add ("a masterpiece", "pos") to train and run it again.
