# Section 02: score how surprised a model is by each real next token.
# Predict first: which sentence gets the higher total loss, and at which word?
import math
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

tok = AutoTokenizer.from_pretrained("gpt2", clean_up_tokenization_spaces=True)
model = AutoModelForCausalLM.from_pretrained("gpt2")

for text in ["The cat sat on the mat.", "The cat sat on the thermodynamics."]:
    ids = tok(text, return_tensors="pt").input_ids[0]
    with torch.no_grad():
        tables = torch.softmax(model(ids[None]).logits[0], dim=-1)
    print(text)
    total = 0.0
    for pos in range(1, len(ids)):
        p = tables[pos - 1, ids[pos]].item()   # probability given to the real next token
        loss = -math.log(p)
        total += loss
        print(f"   {tok.decode(ids[pos])!r:18} p = {p:.4f}   loss = {loss:.2f}")
    print(f"   total loss {total:.2f}\n")

# Then try: add a sentence that is true but unusual, e.g. "Paris is the capital of France."
