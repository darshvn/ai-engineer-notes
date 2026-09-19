# Section 02: look inside a real model and see which words "it" pulls from.
# Predict first: will "it" attend differently in the two sentences?
# (They differ only in the last word: "tired" versus "wide".)
import torch
from transformers import AutoModel, AutoTokenizer

tok = AutoTokenizer.from_pretrained("gpt2", clean_up_tokenization_spaces=True)
model = AutoModel.from_pretrained("gpt2", output_attentions=True, attn_implementation="eager")

for text in ["The animal didn't cross the street because it was too tired",
             "The animal didn't cross the street because it was too wide"]:
    ids = tok(text, return_tensors="pt").input_ids
    words = [tok.decode(i).strip() for i in ids[0]]
    look_from = words.index("it")
    with torch.no_grad():
        attn = torch.stack(model(ids).attentions)    # [layer, batch, head, from, to]
    w = attn[:, 0, :, look_from, :].mean(dim=(0, 1))  # average over 12 layers x 12 heads
    w[0] = 0                                           # drop the first token (see the gotcha)
    w = w / w.sum()
    print(text)
    for i in torch.argsort(w, descending=True)[:4]:
        print(f"   {words[i]:<8} {w[i]:.2f}")
    print()

# Then try: set look_from = len(words) - 1, so you measure from the last word instead.
