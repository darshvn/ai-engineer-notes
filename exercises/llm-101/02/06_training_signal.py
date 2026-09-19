# Section 06: count how much a model learns from one passage.
# Predict first: how many predictions does each design get from this text?
import tiktoken

text = ("Attention lets every token look at every other token in the sentence, "
        "decide how relevant each one is, and mix them into a new representation. "
        "Stacking this many times, with ordinary layers in between, is what a "
        "transformer is.")
n = len(tiktoken.get_encoding("cl100k_base").encode(text))

print(f"passage: {n} tokens")
print(f"decoder-only, predict every next token : {n - 1} training signals")
print(f"encoder-style, predict 15% hidden ones : {round(n * 0.15)} training signals")
print(f"ratio                                  : {(n - 1) / (n * 0.15):.1f}x")

# Then try: paste a paragraph from these notes into `text` and recount.
