# Section 03: a model gets one pass of computation per token it writes.
# Predict first: how many passes does each answer buy the model?
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")
answers = {
    "straight to it": "408",
    "step by step": "17 × 20 = 340. 17 × 4 = 68. 340 + 68 = 408. The answer is 408.",
}
for name, answer in answers.items():
    n = len(enc.encode(answer))
    print(f"{name:<15} {n:>3} tokens -> {n} passes")

# Then try: write your own step-by-step working for 23 × 47 and count its passes.
