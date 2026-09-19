# Section 06: turn sentences into numbers and compare them by meaning.
# Predict first: which sentence is closest to "How do I reset my password?"
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2", tokenizer_kwargs={"clean_up_tokenization_spaces": True})
sentences = ["How do I reset my password?", "I forgot my login", "What time do you close?"]
vectors = model.encode(sentences, normalize_embeddings=True)

print(f"Each sentence becomes {vectors.shape[1]} numbers.")
print("First five for sentence one:", np.round(vectors[0][:5], 3), "\n")
for sentence, v in zip(sentences, vectors):
    print(f"  {vectors[0] @ v:.3f}  {sentence}")    # 1.0 means identical meaning

# Then try: add "Can you help me get back into my account?". Where does it rank?
