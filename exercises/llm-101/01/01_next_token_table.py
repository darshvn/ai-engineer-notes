# Section 01: see the table a language model actually outputs.
# Predict first: what will the top next token be after "The capital of France is"?
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

tok = AutoTokenizer.from_pretrained("gpt2", clean_up_tokenization_spaces=True)
model = AutoModelForCausalLM.from_pretrained("gpt2")

text = "The capital of France is"
ids = tok(text, return_tensors="pt").input_ids
with torch.no_grad():
    scores = model(ids).logits[0, -1]      # one score for every possible next token
table = torch.softmax(scores, dim=-1)      # scores -> probabilities that add to 1

print(f"The table has {len(table):,} rows and they add up to {table.sum():.4f}\n")
top = torch.topk(table, 8)
for p, i in zip(top.values, top.indices):
    print(f"  {tok.decode(i)!r:14} {p:.3f}")

# Then try: change `text` to "The capital of Japan is", then to "I love eating".
