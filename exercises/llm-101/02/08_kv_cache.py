# Section 08: generate tokens with and without a KV cache, and time both.
# Predict first: roughly how much faster is the cached version at 400 tokens?
import time
import numpy as np

rng = np.random.default_rng(0)
d, n = 64, 400
W = rng.standard_normal((d, d)) / 8
tokens = rng.standard_normal((n, d))

start = time.perf_counter()                        # no cache: redo every token each step
for t in range(1, n + 1):
    keys = tokens[:t] @ W
    _ = keys @ tokens[t - 1]
no_cache = time.perf_counter() - start

start = time.perf_counter()                        # cache: compute each token's key once
cache = np.empty((n, d))
for t in range(1, n + 1):
    cache[t - 1] = tokens[t - 1] @ W
    _ = cache[:t] @ tokens[t - 1]
with_cache = time.perf_counter() - start

print(f"key rows computed, no cache : {n * (n + 1) // 2:,}")
print(f"key rows computed, cache    : {n:,}")
print(f"time, no cache : {no_cache * 1000:6.1f} ms")
print(f"time, cache    : {with_cache * 1000:6.1f} ms   ({no_cache / with_cache:.0f}x faster)")
per_token = 2 * 32 * 1024 * 2                      # keys and values, 32 layers, 1024 wide, 2 bytes
print(f"\ncache memory for an 8B-class model: {per_token // 1024} KiB per token, "
      f"{per_token * 8192 / 1024**3:.2f} GiB at 8,192 tokens")

# Then try: set n = 800. Does the gap double, or more?
