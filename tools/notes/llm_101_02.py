"""LLM 101 §2: How the Machine Is Built (the transformer), as traditional notes."""
from notelib import *

TOPIC, SECTION = 'llm-101', 2
TITLE = 'How the Machine Is Built'
DESCRIPTION = 'LLM 101 notes on the transformer: why RNNs failed, attention, self-attention, multi-head attention, encoder and decoder models, positional encoding, context windows and the KV cache.'
LEAD = ('LLM 101 · Section 2. The transformer: why it replaced RNNs, how attention and self-attention work, '
        'multi-head attention, the three model families, position and context length, and the KV cache.')

CR = 'AWHSZzp96kM'   # CampusX, Problems with RNN
CA = 'rj5V6q6-XUM'   # CampusX, Attention Mechanism in 1 video
CS = '-tCKPl_8Xb8'   # CampusX, Self Attention in Transformers
CD = 'r7mAt0iVqwo'   # CampusX, Scaled Dot Product Attention
CG = '5ZgGuujZSbs'   # CampusX, Self Attention Geometric Intuition
CH = 'bX2QwpjsmuA'   # CampusX, Multi-head Attention
CK = 'm6onaKFzF94'   # CampusX, Masked Self Attention
CP = 'GeoQBNNqIbM'   # CampusX, Positional Encoding
CL = 'RG5A-W3eMHI'   # CampusX, Selecting the Right LLM
B3 = 'eMlx5fFNoYc'   # 3Blue1Brown, Attention in transformers
HF = 'https://huggingface.co/learn/llm-course/chapter1/6'

S = []

# ================================================================= 1
S.append(('s1', '1. Why RNNs failed at scale', f'''
<p>Before transformers (2017), the standard model for text was the <strong>RNN</strong> (recurrent neural network). It reads one token at a time and carries a fixed-size memory, the <strong>hidden state</strong>, from each step to the next. A transformer processes all positions of the text at once.</p>
{show("""
RNN: must go in order
  tok 1 → tok 2 → tok 3 → … → tok 1000
  1,000 steps, each waiting for the one before

Transformer: all positions at once
  tok 1  tok 2  tok 3  …  tok 1000
    ↓      ↓      ↓         ↓
  one step, every token processed together
""")}

<h3>Problem 1: information decays</h3>
<p>For a fact at token 1 to matter at token 1,000, it has to survive 999 rewrites of one fixed-size memory, and mostly it doesn't. Training makes it worse. The <strong>gradient</strong>, the signal that tells the model which numbers to adjust, is multiplied by one factor per step on its way back. Slightly below 1 and it vanishes; slightly above 1 and it explodes:</p>
{code("""
print(f"0.9 multiplied 100 times: {0.9 ** 100:.5f}")
print(f"1.1 multiplied 100 times: {1.1 ** 100:,.0f}")
""")}
<p>These are the <em>vanishing</em> and <em>exploding gradient</em> problems. LSTMs, a gated kind of RNN, fixed much of the decay.</p>

<h3>Problem 2: no parallelism</h3>
<p>Step 500 needs step 499's output, so the steps can't run at the same time. GPUs are fast only at work that can run in <strong>parallel</strong>, so training an RNN on a large corpus would have taken years of wall-clock time. LSTMs didn't fix this: they still read one token at a time.</p>
<p>This second problem is the one that decided it. What the transformer really removed was the sequential dependency during training, which made it possible to train on thousands of GPUs at once.</p>

<h3>Training is parallel, generation is not</h3>
<p>Transformers are parallel <em>during training</em>, because the whole text is already known and every position can be scored at once. Generation is still one token per pass (§1). Most of the later sections follow from this split.</p>

<h3>Key points</h3>
{ul(['RNNs process tokens in order through one fixed-size memory.',
     'Long-range information decays, and gradients vanish or explode over many steps.',
     'The decisive limit was that RNN training can\'t be parallelised; transformers removed that.'])}

{resources([
    (yt(CR, 210), 'CampusX, Problems with RNN — 3:30–7:30', 'the long-term dependency problem'),
    (yt(CR, 1020), 'CampusX, same video — 17:00–26:00', 'why gradients from far back shrink'),
    (yt(CR, 1710), 'CampusX, same video — 28:30–32:00', 'exploding gradients and the move to LSTM'),
    (yt(CP, 60), 'CampusX, Positional Encoding — 1:00–5:00', 'the parallelism side: sequential RNN vs all-at-once self-attention'),
])}
{practice('llm-101/02/01_sequential_vs_parallel.py',
          'times the same matrix work done one row after another (like an RNN) and all at once.',
          'rewrite <code>one_after_another</code> so it doesn\'t need the loop.',
          'you can\'t: each <code>h</code> needs the previous one. That dependency is what stopped RNNs using a GPU.')}
<p class="small">On a laptop CPU the gap is modest and noisy (about 4–5× here); on a GPU, which runs thousands of independent operations at once, it is far larger.</p>
'''))

# ================================================================= 2
S.append(('s2', '2. Attention', f'''
<p><strong>Attention</strong> lets every token look at every other token, decide how relevant each one is, and mix them into itself accordingly. The relevance numbers are called <strong>attention weights</strong>; for each token they add up to 1.</p>

<h3>Why it is needed</h3>
{show("""
"The animal didn't cross the street because it was too tired."   → it = the animal
"The animal didn't cross the street because it was too wide."    → it = the street
""")}
<p>Changing one word at the end flips what <code>it</code> refers to. Whatever processes <code>it</code> has to reach back and pull in the right earlier word. An RNN can only hope the right word is still in its memory. Attention looks at every token directly.</p>

<h3>Distance stops mattering</h3>
<p>With attention, token 900 reaching token 3 is one operation, the same as reaching token 899. In an RNN, that information had to survive 897 rewrites of a fixed-size memory.</p>

<h3>Where attention came from</h3>
<p>Attention was introduced in 2014 for translation, added on top of RNNs. The RNN compressed the whole input sentence into one summary vector before producing the output, and past about 25–30 words that summary couldn't hold enough. Attention let each output word take a fresh weighted mix of all the input words: to write "लाइट" for "Turn off the lights", look mostly at <code>lights</code>. Transformers kept the attention and dropped the RNN.</p>

<h3>Key points</h3>
{ul(['Attention = a weighted mix of all tokens, with weights decided by content, not position.',
     'Any token can use any other token in one step.',
     'It began as a fix for translation RNNs; the transformer is built entirely around it.'])}

{resources([
    (yt(CA, 210), 'CampusX, Attention Mechanism in 1 video — 3:30–11:00', 'why attention exists (the 2014 translation version)'),
    (yt(CA, 1230), 'CampusX, same video — 20:30–25:30', 'the context as a weighted sum of input states'),
    (yt(CA, 2160), 'CampusX, same video — 36:00–40:00', 'translation quality on long sentences, and a weight heatmap'),
    (yt(B3, 115), '3Blue1Brown, Attention in transformers — 1:55–4:29', 'how attention moves a word towards the right meaning'),
])}
{practice('llm-101/02/02_what_it_attends_to.py',
          'prints what GPT-2 attends to from the word "it" in both sentences.',
          'set <code>look_from = len(words) - 1</code> to measure from the last word instead.',
          'now the sentences differ, but attention mostly goes to nearby words (too 0.20, tired 0.18, was 0.12).')}
<p class="small">The two sentences give identical weights from "it" (because 0.31, it 0.19, animal 0.10): GPT-2 is a decoder, so at "it" it hasn't seen "tired" or "wide" yet (section 5). Averaged attention weights are also not a readable "this refers to that" arrow; meaning is built up across all 12 layers.</p>
'''))

# ================================================================= 3
S.append(('s3', '3. Self-attention', f'''
<p><strong>Self-attention</strong> is attention within one sentence: each word is rebuilt as a weighted mix of all the words around it. It turns a <em>static</em> embedding (one vector per word, whatever the context) into a <em>contextual</em> one. It works in three steps: <strong>score</strong>, <strong>convert to weights</strong>, <strong>mix</strong>.</p>

<h3>A worked example: "the river bank"</h3>
<p>Each word is a list of numbers (its embedding). The numbers here are picked by hand to be readable; a trained model learns its own. Each word also has a fourth number, 0 for all three, which is left out.</p>
{show("""
          water  money  generic
the     [  0.3    0.3     2.5  ]   filler word
river   [  2.6    0.0     0.5  ]   very water
bank    [  1.6    1.6     0.8  ]   equally both
""")}
<p><code>bank</code> starts as equally "water" and "money". Self-attention should push it towards "water" because of <code>river</code>.</p>

<h3>Step 1: score with dot products</h3>
<p>A <strong>dot product</strong> multiplies two lists position by position and adds the results. Large numbers in the same positions give a large score.</p>
{show("""
bank·the    =  1.6×0.3 + 1.6×0.3 + 0.8×2.5  =  2.96
bank·river  =  1.6×2.6 + 1.6×0.0 + 0.8×0.5  =  4.56   ← shared "water"
bank·bank   =  1.6×1.6 + 1.6×1.6 + 0.8×0.8  =  5.76
""")}

<h3>Step 2: turn scores into weights</h3>
<p>Divide each score by √<em>d</em>, where <em>d</em> is the number of values per vector (√4 = 2 here), then apply softmax so the weights are positive and add up to 1:</p>
{show("""
         score   ÷ 2     e^x     weight
the       2.96   1.48    4.39    0.137
river     4.56   2.28    9.78    0.306
bank      5.76   2.88   17.81    0.557
                        ─────    ─────
                        31.98    1.000
""")}

<h3>Step 3: mix</h3>
<p>The new <code>bank</code> is the weighted average of the three words, one position at a time:</p>
{show("""
water  =  0.137×0.3 + 0.306×2.6 + 0.557×1.6  =  1.73
money  =  0.137×0.3 + 0.306×0.0 + 0.557×1.6  =  0.93
""")}
{table(['', 'water', 'money', ''], [
    ['<code>bank</code> on its own', '1.60', '1.60', 'ambiguous'],
    ['"the river bank"', '<strong>1.73</strong>', '0.93', 'leans water'],
    ['"the savings bank"', '0.93', '<strong>1.73</strong>', 'leans money'],
])}
<p>Same word, same three steps; only the neighbour changed (<code>savings</code> is <code>river</code> with its water and money values swapped). The whole calculation in NumPy:</p>
{code("""
import numpy as np

E = np.array([[0.3, 0.3, 2.5, 0.0],    # the
              [2.6, 0.0, 0.5, 0.0],    # river
              [1.6, 1.6, 0.8, 0.0]])   # bank
scores = E @ E[2]                       # step 1: bank against every word
w = np.exp(scores / np.sqrt(4))
w = w / w.sum()                         # step 2: softmax
new_bank = w @ E                        # step 3: weighted mix
print("weights:", np.round(w, 3))
print("bank before:", E[2][:2], " after:", np.round(new_bank[:2], 2))
""")}

<h3>Why divide by √d</h3>
<p>Softmax exaggerates differences between scores. Without the division, <code>bank</code>'s weights become 0.045 / 0.221 / 0.734: less mixing, more copying itself. The bigger reason is size: the dot product of two random vectors of length <em>d</em> has a variance of about <em>d</em>.</p>
{code("""
import numpy as np

rng = np.random.default_rng(0)
for d in (4, 64, 512):
    q, k = rng.standard_normal((2, 100_000, d))
    s = (q * k).sum(axis=1)
    print(f"d = {d:3}: variance {s.var():6.1f}   after dividing by sqrt(d): {(s / np.sqrt(d)).var():.2f}")
""")}
<p>With 512 values, typical scores are about 23 away from zero, softmax gives nearly 1.0 and 0.0, and the small weights stop learning because their gradients vanish. Dividing by √<em>d</em> brings the variance back to about 1 for any size. Strictly, <em>d</em> is the length of the key vector (below).</p>

<h3>Query, key and value</h3>
<p>In the example, each word used its own embedding for everything. That version has nothing to learn. A real model multiplies each embedding by three learned matrices, <strong>W<sub>Q</sub></strong>, <strong>W<sub>K</sub></strong> and <strong>W<sub>V</sub></strong>, shared by all words:</p>
{table(['Vector', 'Role', 'Used in'], [
    ['query (Q)', 'what this word is looking for', 'step 1, as the word doing the scoring'],
    ['key (K)', 'what this word offers to be matched on', 'step 1, as the word being scored'],
    ['value (V)', 'what this word hands over if chosen', 'step 3, the mix'],
])}
<p>The names come from a dictionary lookup: <code>d[query]</code> finds the matching key and returns its value. In matrix form the whole thing is <code>softmax(Q·Kᵀ / √d_k)·V</code>, which is why the paper calls it <em>scaled dot-product attention</em>.</p>
<p>One difference from the example: real transformers <em>add</em> the mixed result to the original embedding (a residual connection) instead of replacing it.</p>

<h3>Key points</h3>
{ul(['Score with dot products, turn scores into weights with softmax, mix by those weights.',
     'Divide scores by √d_k so softmax doesn\'t saturate as vectors get longer.',
     'Q, K and V are learned projections of each embedding; they make attention trainable.'])}

{resources([
    (yt(CS, 990), 'CampusX, Self Attention in Transformers — 16:30–24:30', 'score, softmax, weighted sum on "money bank grows" (this video doesn\'t scale by √d)'),
    (yt(CS, 4230), 'CampusX, same video — 70:30–78:30', 'where Q, K and V come from (43:30–51:30 explains why three roles)'),
    (yt(CD, 1350), 'CampusX, Scaled Dot Product Attention — 22:30–30:30', 'why scale at all; 43:30–47:30 for why the square root'),
    (yt(CG, 690), 'CampusX, Self Attention Geometric Intuition — 11:30–19:30', 'the same steps drawn as vectors in 2-D'),
    (yt(B3, 269), '3Blue1Brown, Attention in transformers — 4:29–10:55', 'queries, keys and the attention pattern; 13:00–15:35 for values'),
])}
{practice('llm-101/02/03_self_attention.py',
          'computes the "river bank" example step by step.',
          'replace <code>river</code> with <code>savings = [0.0, 2.6, 0.5, 0.0]</code>; then, separately, delete <code>/ np.sqrt(4)</code>.',
          'with savings, water and money flip (0.93 / 1.73); without the division the weights become 0.045 / 0.221 / 0.734 and bank blends less.')}
'''))

# ================================================================= 4
S.append(('s4', '4. Multi-head attention', f'''
<p>One attention calculation produces one set of weights, so it can capture one kind of relationship. A token usually needs several at once:</p>
{show("""
"The keys to the cabinet were on the table."
To get "were" right you need:
  which noun is the subject   →  "keys" (not "cabinet")
  what tense this is          →  the wider sentence
  what it connects to         →  "on the table"
""")}
<p><strong>Multi-head attention</strong> runs several attention calculations (<strong>heads</strong>) in parallel, each with its own W<sub>Q</sub>, W<sub>K</sub> and W<sub>V</sub>, so each can learn a different notion of relevance.</p>

<h3>How it works</h3>
<ol>
  <li>Each head multiplies the <em>full</em> token vector by its own learned matrices, projecting it down to a smaller size.</li>
  <li>Each head runs score → weights → mix in that smaller space.</li>
  <li>The heads' outputs are joined back together (concatenated), and one more learned matrix, <strong>W<sub>O</sub></strong>, mixes them into the final result.</li>
</ol>
{table(['Model', 'Values per token', 'Heads × size per head'], [
    ['Original transformer (2017)', '512', '8 × 64'],
    ['A 4,096-wide model', '4,096', '32 × 128'],
    ['GPT-3', '12,288', '96 × 128'],
])}
<p>Splitting the width this way costs about the same as one full-width head: 32 heads of 128 is the same total width as one head of 4,096. You get several kinds of relationship for roughly the price of one.</p>

<h3>What heads learn</h3>
<p>Researchers inspecting trained models find heads that track grammatical subjects, heads that match quotes to speakers, and heads that mostly look at the previous token. But this is a useful story, not a guarantee: heads are found by training, not assigned, many do things no one can name, and removing a supposedly critical head often changes little.</p>

<h3>Key points</h3>
{ul(['One head = one set of weights = one kind of relationship.',
     'Multi-head attention = many heads in parallel, each with its own learned projections, joined by W<sub>O</sub>.',
     'Splitting the width across heads keeps the cost about the same as one wide head.'])}

{resources([
    (yt(CH, 390), 'CampusX, Multi-head Attention — 6:30–11:20', '"The man saw the astronomer with a telescope": why one head isn\'t enough'),
    (yt(CH, 1680), 'CampusX, same video — 28:00–34:30', 'the paper\'s version: 8 heads of 64, concatenation, W_O, and the cost'),
    (yt(CH, 2100), 'CampusX, same video — 35:00–37:45', 'visualising what two heads attend to'),
    (yt(B3, 1159), '3Blue1Brown, Attention in transformers — 19:19–21:55', 'why different kinds of context need different heads'),
])}
{practice('llm-101/02/04_two_heads.py',
          'runs two heads over "the river bank" and shows they weight the words differently.',
          'change <code>the</code> to <code>[0.3, 2.5, 2.5, 0.0]</code>, giving it a large money value.',
          'head A\'s weight for "the" jumps from 0.03 to 0.30; head B is unchanged because it never sees the money value.')}
<p class="small">The script gives each head a fixed slice of the numbers so the effect is easy to see. Real heads see the whole vector through learned projections.</p>
'''))

# ================================================================= 5
S.append(('s5', '5. Encoder-only, decoder-only and encoder-decoder models', f'''
<p>The three transformer families differ in one thing: <strong>which tokens each token is allowed to look at</strong>. Everything else is the same.</p>
{table(['Family', 'Each token sees', 'Trained to', 'Good at', 'Examples'], [
    ['Encoder-only', 'everything, both directions', 'fill in hidden words', 'classifying, embeddings', 'BERT, e5'],
    ['Decoder-only', 'itself and earlier tokens only', 'predict the next token', 'generating text', 'GPT, Claude, Llama'],
    ['Encoder-decoder', 'encoder: everything; decoder: left only', 'rebuild hidden spans', 'fixed input → output (translation, summaries)', 'T5, BART'],
])}

<h3>The causal mask</h3>
<p>A decoder is enforced by a <strong>causal mask</strong>: a matrix of 0s and minus infinity added to the scores after dividing by √d and before softmax. Softmax turns minus infinity into exactly 0, so later tokens get zero weight and each row still adds up to 1. Setting weights to 0 <em>after</em> softmax would break that. The same three words as section 3, every row:</p>
{code("""
import numpy as np

E = np.array([[0.3, 0.3, 2.5, 0.0], [2.6, 0.0, 0.5, 0.0], [1.6, 1.6, 0.8, 0.0]])
scores = E @ E.T / np.sqrt(4)

def softmax_rows(x):
    x = np.exp(x - x.max(axis=1, keepdims=True))
    return x / x.sum(axis=1, keepdims=True)

mask = np.triu(np.full((3, 3), -np.inf), k=1)      # minus infinity above the diagonal
print("encoder (sees everything):")
print(np.round(softmax_rows(scores), 2))
print("decoder (looks left only):")
print(np.round(softmax_rows(scores + mask), 2))
""")}
<p>In the decoder, the first word can only see itself (1.00, 0, 0). The last row is the same in both, because the last word already sees everything to its left. The mask only removes information from earlier words.</p>

<h3>Why a generative model must be a decoder</h3>
<p>During training, a model predicting token 5 that can see token 5 is just copying the answer, which teaches nothing usable at generation time, when nothing to the right exists yet. CampusX calls this <strong>data leakage</strong>.</p>

<h3>Cross-attention</h3>
<p>The decoder in an encoder-decoder model has one extra attention step, <strong>cross-attention</strong>: its queries come from the output being written, and its keys and values from the encoder's reading of the input. This is the translation setup from section 2.</p>
<p>The split mirrors §1: representation models are encoders, generative models are decoders.</p>

<h3>Key points</h3>
{ul(['The families differ only in which positions attention may reach.',
     'The causal mask adds minus infinity before softmax so future tokens get exactly zero weight.',
     'Encoders understand text; decoders generate it; encoder-decoders map one sequence to another.'])}

{resources([
    (yt(B3, 660), '3Blue1Brown, Attention in transformers — 11:00–12:40', 'why the mask exists and why it uses minus infinity'),
    (yt(CK, 3300), 'CampusX, Masked Self Attention — 55:00–59:00', 'a 3×3 mask worked by hand'),
    (HF + '#encoder-models', 'Hugging Face LLM Course — Transformer architectures', 'the three families, their training objectives, and which suits which task'),
])}
{practice('llm-101/02/05_masks.py',
          'prints the full attention weights for an encoder and a decoder.',
          'add a fourth word, <code>"flooded" = [2.4, 0.0, 0.6, 0.0]</code>, and change the 3 in <code>triu_indices</code> to 4.',
          'now only the <code>flooded</code> row matches between the two; <code>bank</code>\'s row changes because the encoder can see <code>flooded</code> and the decoder can\'t.')}
'''))

# ================================================================= 6
S.append(('s6', '6. Why decoder-only models dominate', f'''
<p>Almost every large general-purpose language model is decoder-only. Three reasons, in order of importance.</p>
<p>Underneath all of them: next-token prediction needs <strong>no labels</strong>. The text is its own answer key (every next token is the target), so any text on the internet can be training data without anyone annotating it.</p>

<h3>1. More training signal per token</h3>
<p>From one 512-token passage, a decoder gets a prediction at every position, while an encoder-style model hides about 15% of tokens (BERT's rate) and predicts only those:</p>
{code("""
n = 512
decoder = n - 1
encoder = n * 0.15
print(f"decoder-only: {decoder} predictions")
print(f"encoder-style: {encoder:.0f} predictions")
print(f"ratio: {decoder / encoder:.1f}x")
""")}
<p>High-quality text is limited, so getting 6.7× more learning from the same text is decisive. All 511 predictions happen in <em>one</em> pass because of the causal mask (section 5) and <strong>teacher forcing</strong>: during training each position's input is the true previous token from the data, not the model's own guess, so every input is known in advance. Without it, a 300-token target would need 301 passes one after another (CampusX's count).</p>

<h3>2. One design does every job</h3>
<p>Any task can be written as text completion: classify, translate, summarise. An encoder needs a task-specific output layer added; a decoder only needs a different prompt.</p>

<h3>3. Simplicity scales</h3>
<p>One stack, one objective, one mask: fewer parts to tune when a training run costs millions. Inference stays simple too: a decoder only ever appends tokens on the right, so earlier keys and values never change and can be cached (the KV cache, section 8).</p>

<h3>Where encoders still win</h3>
<p>For search and classification, a small encoder beats a large decoder at a fraction of the cost, which is the two-model setup from §1. Decoder-only dominates <em>general-purpose</em> models, not everything.</p>

<h3>Key points</h3>
{ul(['Decoders learn from every position; encoder-style training uses about 15%.',
     'Teacher forcing plus the mask let training run all positions in parallel.',
     'Generation stays sequential: each new token depends on the previous one.'])}

{resources([
    (yt(CK, 1650), 'CampusX, Masked Self Attention — 27:30–35:00', 'teacher forcing, and why it lets training run in parallel'),
    (yt(CK, 1350), 'CampusX, same video — 22:30–25:00', 'why generation must stay sequential'),
    (yt(CK, 2610), 'CampusX, same video — 43:30–49:00', 'data leakage if training runs in parallel without a mask'),
    (HF + '#modern-large-language-models-llms', 'Hugging Face LLM Course — Modern LLMs', 'most modern LLMs are decoder-only, trained in two phases'),
])}
{practice('llm-101/02/06_training_signal.py',
          'counts the training signals each design gets from a real passage, using a real tokenizer.',
          'paste any paragraph from these notes into <code>text</code> and recount.',
          'a 57-token paragraph gives 56 against 9, still 6.5×: the ratio is built in, every position against 15% of them.')}
'''))

# ================================================================= 7
S.append(('s7', '7. Positional encoding and the context window', f'''
<p>Attention is a weighted sum, and addition doesn't depend on order, so attention on its own is <strong>blind to word order</strong>: "dog bites man" and "man bites dog" give "dog" exactly the same vector (the practice script shows this). Position has to be added to each token explicitly.</p>

<h3>Terms</h3>
{table(['Term', 'Meaning'], [
    ['positional encoding', 'Extra numbers added to each token\'s embedding to encode where it is in the text.'],
    ['context window', 'The maximum number of tokens a model can attend over at once. Anything outside it doesn\'t exist for the model.'],
])}

<h3>Why not just number the positions?</h3>
{ul(['Raw positions 1, 2, 3… grow without limit (a book reaches 100,000), and large values make training unstable.',
     'Dividing by the length keeps values small but makes position 2 worth 1.0 in a two-word sentence and 0.5 in a four-word one.',
     'A single sine wave stays between −1 and 1 but repeats, so two positions can get the same value.'])}

<h3>Sinusoidal positional encoding</h3>
<p>The original transformer uses pairs of sine and cosine waves, each pair slower than the last, and <strong>adds</strong> the result to the embedding (concatenating would double its size):</p>
{show("""
PE(pos, 2i)   = sin(pos / 10000^(2i/d))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d))        pos starts at 0
""")}
{code("""
import numpy as np

def positional_encoding(pos, d=8):
    i = np.arange(d // 2)
    angle = pos / 10000 ** (2 * i / d)
    return np.ravel(np.column_stack([np.sin(angle), np.cos(angle)]))

for pos in (0, 1, 2, 50):
    print(f"position {pos:3}:", np.round(positional_encoding(pos)[:4], 3))
""")}
<p>The pairs have a useful property: moving from any position to the one <em>k</em> steps later is the same fixed rotation of each sine–cosine pair, wherever you start, so "k tokens apart" looks the same everywhere. Modern models build on this with <strong>RoPE</strong> (rotary position embedding), which rotates the query and key vectors by position instead of adding numbers to the embedding.</p>

<h3>Why long context is expensive</h3>
<p>Every token attends to every token, so the attention pattern has length² entries and the work grows with the square of the length:</p>
{code("""
for ctx in (8_000, 16_000, 128_000):
    print(f"{ctx:>7,} tokens: {ctx / 8_000:4.0f}x the text, {(ctx / 8_000) ** 2:5.0f}x the attention work")
""")}
<p>That quadratic growth is why long context was hard for years, why long-context use is priced as it is, and why trimming what you send matters.</p>

<h3>Key points</h3>
{ul(['Attention ignores order; positional encodings are added to each token to supply it.',
     'Sinusoidal encodings use sine/cosine pairs at decreasing frequencies; RoPE rotates Q and K instead.',
     'Attention cost grows with the square of the context length.'])}

{resources([
    (yt(CP, 300), 'CampusX, Positional Encoding — 5:00–7:30', 'why position is needed ("Nitish killed lion" vs "Lion killed Nitish")'),
    (yt(CP, 1230), 'CampusX, same video — 20:30–34:00', 'from one sine wave to sine–cosine pairs (8:30–20:30 for the simpler ideas first)'),
    (yt(CP, 2040), 'CampusX, same video — 34:00–40:30', 'adding vs concatenating; 47:30–54:30 for the formula worked by hand'),
    (yt(CP, 3840), 'CampusX, same video — 64:00–71:00', 'the relative-position property'),
    (yt(B3, 745), '3Blue1Brown, Attention in transformers — 12:25–12:55', 'attention size grows with the square of the context'),
])}
{practice('llm-101/02/07_position.py',
          'runs attention on "dog bites man" and "man bites dog", with and without positional encoding.',
          'make the position signal tiny: <code>E = E + 0.01 * np.hstack(...)</code>.',
          'at two decimals the two sentences look identical again; a position signal that is too weak is as good as none.')}
'''))

# ================================================================= 8
S.append(('s8', '8. The KV cache', f'''
<p>Generating runs the model once per token on everything written so far (§1). Without any reuse, the work grows quadratically with the length of the answer:</p>
{code("""
n = 1000
without_cache = n * (n + 1) // 2      # step 1 processes 1 token, step 2 two tokens, ...
with_cache = n                         # each token processed once
print(f"without caching: {without_cache:,} token-steps")
print(f"with caching:    {with_cache:,} token-steps  ({without_cache // with_cache}x less work)")
""")}

<h3>How it works</h3>
<p>When token 900 attends to token 3, the key and value vectors it needs from token 3 are the same ones token 899 needed; nothing about token 3 has changed. The <strong>KV cache</strong> stores each token's keys and values once instead of recomputing them at every step, turning quadratic work into linear work at the cost of memory.</p>
{table(['Term', 'Meaning'], [
    ['prefill', 'Processing the prompt. Done in parallel, so it is fast; this is the time to the first token.'],
    ['decode', 'Generating each new token, one pass each. Serial, so it is the rest of the wait.'],
])}

<h3>Memory cost</h3>
{code("""
per_token = 2 * 32 * 1024 * 2      # keys and values, 32 layers, 1024 wide, 2 bytes each
print(f"per token: {per_token // 1024} KiB")
for tokens in (1_000, 8_192, 128_000):
    print(f"{tokens:>7,} tokens: {per_token * tokens / 1024**3:6.2f} GiB")
print(f"100 users at 8,192 tokens: {100 * per_token * 8_192 / 1024**3:.0f} GiB")
""")}
<p class="small">Computed for an 8B-class model; sizes vary, but the shape doesn't.</p>
<p>This explains several things: long conversations get more expensive, not just slower; a server handles far fewer long chats at once than short ones; and the cache, not the model weights, usually limits how many users one GPU can serve. Providers price input and output tokens separately because prefill and decode are different operations on the hardware.</p>

<h3>Prompt caching</h3>
<p>Providers also keep the cache for a prompt <em>prefix</em> that many requests share, such as a long system prompt, and charge less for reusing it. CampusX's text-to-SQL example (400 tokens in, 100 out, at the video's prices of $10 per million input and $50 per million output tokens):</p>
{code("""
full = 400 * 10 / 1e6 + 100 * 50 / 1e6
cached = 350 * 1 / 1e6 + 50 * 10 / 1e6 + 100 * 50 / 1e6   # 350 input tokens reused at $1 per million
print(f"per query: ${full:.5f} without caching, ${cached:.5f} with caching ({1 - cached / full:.0%} less)")
""")}
<p>The first write costs more ($12.50 per million), and the cache expires after 5 minutes unless it's used again. It helps little for RAG, where most of the prompt changes with every request.</p>

<h3>Key points</h3>
{ul(['The KV cache stores keys and values once per token, cutting generation work from quadratic to linear.',
     'It costs memory per token, per conversation; this usually limits how many users a GPU serves.',
     'Prompt caching reuses the cache for a shared prefix across requests.',
     'A chat slows down as history grows because each new token attends over more cached tokens: trim or summarise history.'])}

{resources([
    (yt(CL, 1560), 'CampusX, Selecting the Right LLM — 26:00–30:30', 'per-query cost from token counts and prices'),
    (yt(CL, 1920), 'CampusX, same video — 32:00–38:00', 'prompt caching; names the KV cache as the mechanism'),
    ('https://platform.claude.com/docs/en/build-with-claude/prompt-caching', 'Claude docs — Prompt caching', 'how prefixes are cached and priced'),
    (yt(B3, 450), '3Blue1Brown, Attention in transformers — 7:30–10:30', 'the key vectors that the cache stores'),
])}
{practice('llm-101/02/08_kv_cache.py',
          'generates 400 steps with and without a cache and compares the work and the time.',
          'set <code>n = 800</code>.',
          'about 320,400 key computations against 800: the work saved doubles, and the timing gap widens with it.')}
<p class="small">The speed-up is much smaller than the work saved (200× less work, but only around 5–8× faster at 400 tokens, and it varies run to run) because Python's loop overhead dominates at this tiny size. In a real model each key costs far more, so the saving tracks the work more closely.</p>
'''))

SUMMARY = f'''
<section class="sect" id="summary">
<h2>Summary</h2>
{table(['Topic', 'In one line'], [
    ['RNNs', 'sequential, so they couldn\'t be trained in parallel at scale'],
    ['Attention', 'every token takes a weighted mix of every other token'],
    ['Self-attention', 'score (dot product) → weights (softmax, scaled by √d) → mix; Q, K, V are learned'],
    ['Multi-head', 'several heads in parallel, each learning a different relationship'],
    ['Model families', 'encoder sees everything, decoder looks left only (causal mask)'],
    ['Decoder-only', 'most training signal per token, one interface for every task'],
    ['Position', 'added explicitly; attention cost grows with context length squared'],
    ['KV cache', 'reuse keys and values: linear instead of quadratic work, paid for in memory'],
])}
</section>
'''

QUESTIONS = [
    ('Generation is one token at a time. Doesn\'t that make transformers sequential too?',
     'At generation time, yes. The parallelism is in training, where the whole text is known and every position can be scored at once.'),
    ('In the "river bank" example, why did bank take 0.306 of river but only 0.137 of the?',
     'River scored higher in step 1 (4.56 against 2.96) because it shares bank\'s large "water" value; softmax then widened the gap.'),
    ('Why divide attention scores by √d?',
     'Dot-product variance grows with d, which pushes softmax to near 0 and 1 and stops the small weights learning. Dividing by √d keeps the variance around 1.'),
    ('Why use 32 heads of 128 instead of 32 full-width heads?',
     'Cost: 32 × 128 is the same total width as one 4,096-wide head. Full-width heads would cost 32 times as much.'),
    ('Why can\'t a generative model be trained as an encoder that sees everything?',
     'It would see the token it is supposed to predict (data leakage), which teaches nothing usable at generation time.'),
    ('Going from 8k to 128k context is 16× the tokens. Roughly what happens to attention cost?',
     'About 256×, since the cost grows with the square of the length.'),
    ('A chat app slows down as a conversation gets longer, even though replies stay short. Why?',
     'Each new token attends over the whole history, which keeps growing, and so does the KV cache. Trimming or summarising history helps.'),
]


def build():
    return page(TITLE, DESCRIPTION, LEAD, S, SUMMARY + review(QUESTIONS))
