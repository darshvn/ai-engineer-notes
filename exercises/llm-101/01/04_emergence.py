# Section 04: smooth improvement underneath, a cliff in the score on top.
# Each digit is right with probability p, and p rises smoothly with model size.
# A 5-digit answer only counts if all five digits are right, so the score is p**5.
# Predict first: at p = 0.85, how often is the whole answer right?
sizes = ["1B", "3B", "7B", "30B", "70B", "150B", "400B"]
per_digit = [0.30, 0.45, 0.60, 0.75, 0.85, 0.93, 0.98]   # illustrative, rising smoothly

digits = 5
print(f"{'size':<6}{'each digit':>11}{'whole answer':>14}")
for size, p in zip(sizes, per_digit):
    print(f"{size:<6}{p:>11.2f}{p ** digits:>14.1%}")

# Then try: set digits = 10. Where does the jump move?
