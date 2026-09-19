# Section 01: the same multiplications, done one after another or all at once.
# Predict first: how much faster is doing all 1,000 rows at once?
import time
import numpy as np

rng = np.random.default_rng(0)
n = 1000
x = rng.standard_normal((n, 256))          # n tokens, 256 numbers each
W = rng.standard_normal((256, 256)) / 16

def one_after_another():                    # RNN-style: step i needs step i-1 first
    h = np.zeros(256)
    for i in range(n):
        h = np.tanh(x[i] @ W + h)

def all_at_once():                          # transformer-style: no step waits on another
    np.tanh(x @ W)

def best_of_5(f):                           # timings on a laptop are noisy, so keep the best run
    runs = []
    for _ in range(5):
        start = time.perf_counter(); f(); runs.append(time.perf_counter() - start)
    return min(runs)

a, b = best_of_5(one_after_another), best_of_5(all_at_once)
print(f"one after another : {a * 1000:7.2f} ms")
print(f"all at once       : {b * 1000:7.2f} ms   ({a / b:.0f}x faster)")

# Then try: set n = 4000. Which time grows faster?
