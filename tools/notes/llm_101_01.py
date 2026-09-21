"""LLM 101 §1: What a Language Model Actually Does, as traditional notes."""
from notelib import *

TOPIC, SECTION = 'llm-101', 1
TITLE = 'What a Language Model Actually Does'
DESCRIPTION = 'LLM 101 notes: language modelling, next-token prediction, reasoning, scaling and emergence, foundation models, and generative vs representation models.'
LEAD = ('LLM 101 · Section 1. What a language model outputs, how it is trained, why writing steps helps it reason, '
        'what scale changes, what a foundation model is, and the two kinds of model used in real systems.')

B1 = 'wjZofJX0v4M'     # 3Blue1Brown, Transformers, the tech behind LLMs
KD = '7xTGNNLPyMI'     # Karpathy, Deep Dive into LLMs like ChatGPT
KI = 'zjkBMFhNj_g'     # Karpathy, Intro to Large Language Models
CL = 'fiqo6uPCJVI'     # CampusX, LSTM Part 3: Next Word Predictor
CF = 'bTLaTvbi9vM'     # CampusX, What are Foundation Models?
CM = 'HdcLE8JuMrA'     # CampusX, LangChain Models

S = []

# ================================================================= 1
S.append(('s1', '1. What “language modeling” means', f'''
<p>A <strong>language model</strong> takes some text and returns the probability of every possible next token. That is the whole definition. Transformers, training and GPUs are all machinery for making that one output more accurate.</p>

<h3>The output is a probability table</h3>
<p>Given the text <code>"The capital of France is"</code>, the model doesn't return a sentence. It returns one probability for every token in its vocabulary:</p>
{show("""
  " Paris"       0.87
  " located"     0.04
  " a"           0.02
  " home"        0.01
  " known"       0.01
  … 100,272 more rows, each a tiny number
                 ─────
  every row adds to  1.00
""", 'output')}
<p class="small">The probabilities are illustrative; they differ per model. The shape of the output is always this.</p>

<h3>Terms</h3>
{table(['Term', 'Meaning'], [
    ['token', 'A word-piece, not a word. <code>" Paris"</code> is one token; <code>"thermodynamics"</code> is three (<code>ther</code> + <code>m</code> + <code>odynamics</code>).'],
    ['vocabulary', 'The fixed list of tokens a model knows: 100,277 for GPT-4\'s tokenizer, 50,257 for GPT-2.'],
    ['probability distribution', 'The whole table: every token with its probability. The values always add up to 1.'],
    ['logit', 'The raw score the network gives each token before it becomes a probability. Any number, even negative.'],
    ['softmax', 'The step that turns logits into probabilities: raise <em>e</em> to each score, then divide each by the total.'],
])}

<h3>How text is generated</h3>
<p>Text is produced one token at a time. At each step the model outputs a table, one token is picked from it and appended, and the longer text goes back into the model:</p>
{table(['Step', 'Text going in', 'Top of the table', 'Picked'], [
    ['1', '<code>The capital of France is</code>', '<code>" Paris"</code> 0.87', '<code>" Paris"</code>'],
    ['2', '<code>…France is Paris</code>', '<code>"."</code> 0.61', '<code>"."</code>'],
    ['3', '<code>…France is Paris.</code>', '<code>" It"</code> 0.22', '<code>" It"</code>'],
])}
{fig('llm_101_01_fig1')}
<p>The model never writes a sentence directly. It produces one table per token, and a separate step, the <strong>sampler</strong>, picks a row from each.</p>

<h3>From logits to probabilities</h3>
<p>The network first gives every token a logit, then softmax turns the logits into the table. With a three-token vocabulary:</p>
{code("""
import math

logits = {" Paris": 5.0, " located": 2.0, " a": 1.2}
total = sum(math.exp(v) for v in logits.values())
for token, v in logits.items():
    print(f"{token!r:12} {math.exp(v) / total:.3f}")
""")}

<h3>Greedy picking, sampling and temperature</h3>
<ul class="points">
  <li><strong>Greedy</strong> picking always takes the top row, as in the steps above.</li>
  <li><strong>Sampling</strong> picks at random, weighted by the table, so <code>" Paris"</code> at 0.933 wins about 93 times in 100. Chat models usually sample.</li>
  <li><strong>Temperature</strong> divides the logits before softmax. Below 1 it sharpens the table towards the top row; above 1 it flattens it and gives more variety.</li>
</ul>
{code("""
import math

logits = [5.0, 2.0, 1.2]
for t in (0.5, 1, 2):
    exps = [math.exp(v / t) for v in logits]
    print(f"temperature {t}:", " / ".join(f"{x / sum(exps):.4f}" for x in exps))
""")}
<p>This is why the same prompt can give different answers. Inference settings are covered in their own section (§5).</p>

<h3>Key points</h3>
{ul(['A language model outputs a probability for every token in its vocabulary, one step at a time.',
     'A 50-word answer is about 60 tokens, so about 60 separate tables.',
     'The model produces the probabilities; a sampler chooses the token.',
     'Temperature reshapes the probabilities before sampling.'])}
<h3>Common misconceptions</h3>
{ul(['"The model writes a whole answer at once." It produces one token per step and never plans the full sentence.',
     '"The top token is always chosen." Only with greedy decoding; sampling can pick lower-ranked tokens.'])}

{resources([
    (yt(B1, 85), '3Blue1Brown, Transformers, the tech behind LLMs — 1:25–2:57', 'prediction as a distribution, and the sample-append-repeat loop'),
    (yt(B1, 1222), '3Blue1Brown, same video — 20:22–26:03', 'logits, softmax and temperature'),
    (yt(KD, 1560), 'Karpathy, Deep Dive into LLMs — 26:00–29:40', 'inference as sampling, token by token'),
])}
{practice('llm-101/01/01_next_token_table.py',
          'prints the real probability table GPT-2 produces for <code>"The capital of France is"</code>.',
          'change the text to <code>"The capital of Japan is"</code>, then to <code>"I love eating"</code>.',
          'Japan gives <code>\' the\'</code> 0.094 then <code>\' Tokyo\'</code> 0.067; "I love eating" spreads thinly (<code>\',\'</code> 0.064, <code>\' and\'</code> 0.060), because many continuations are reasonable.')}
<p class="small">GPT-2 is a small 2019 model, which is why <code>" Paris"</code> comes fifth at 0.032 in the real output. A modern large model puts most of its probability on it.</p>
'''))

# ================================================================= 2
S.append(('s2', '2. Next-token prediction', f'''
<p>A language model learns by predicting the next token of real text, over and over. Take a sentence, hide the next token, let the model guess, and score how much probability it gave to the true token. Then adjust the model so that probability goes up.</p>

<h3>The loss</h3>
<p>The score is the <strong>loss</strong>: <code>-log(probability given to the true token)</code>. Lower is better, and zero means the model was certain and correct. For the sentence <code>"The cat sat on the mat"</code> with the last token hidden:</p>
{code("""
import math

for p in (0.95, 0.60, 0.01):
    print(f"model gave ' mat' {p:.2f}  ->  loss {-math.log(p):.2f}")
""")}
<p>The penalty isn't linear. Going from 0.95 to 0.60 costs 0.46, but going from 0.60 to 0.01 costs 4.10. Training punishes being <em>confident and wrong</em> far more than being unsure.</p>

<h3>Terms</h3>
{table(['Term', 'Meaning'], [
    ['loss (cross-entropy)', 'How wrong one guess was: <code>-log p</code> of the true token. Called <code>categorical_crossentropy</code> in Keras.'],
    ['training', 'Repeating the guess-and-score step and nudging the model\'s parameters so the true tokens get more probability. Real training updates once per <em>batch</em> (about a million tokens in Karpathy\'s run) and reports the average loss.'],
    ['self-supervised', 'Supervised learning where the labels come from the text itself: the next token is already in the sentence, so no human labelling is needed.'],
])}

<h3>One sentence gives many training examples</h3>
<p>Every position in a sentence is used, so a sentence of <em>n</em> tokens gives <em>n</em> &minus; 1 examples. CampusX's example, split by word for readability:</p>
{show("""
"Hi my name is Nitish"  →  4 training examples

Hi               →  my
Hi my            →  name
Hi my name       →  is
Hi my name is    →  Nitish
""")}

<h3>Why the output is a table</h3>
<p>Token IDs are labels, not quantities: token 4 isn't "bigger" than token 2, and a predicted 2.7 would mean nothing. So next-token prediction is a <strong>classification</strong> problem over the whole vocabulary, with one probability per token.</p>

<h3>Where hallucinations come from</h3>
<p>The probabilities always add up to 1, so something always gets the probability, even when the model has no reliable knowledge. There is no "I don't know" row. A made-up answer is the same mechanism working normally on a question it has nothing solid for.</p>

<h3>Key points</h3>
{ul(['Training = hide the next token, predict it, score with <code>-log p</code>, adjust. At every position, over trillions of tokens (FineWeb, used by Karpathy, is 15 trillion).',
     'No hand labelling: the text supplies its own answers.',
     'The loss rewards justified confidence, so a model\'s probabilities are a meaningful signal of how sure it is.'])}
<h3>Common misconceptions</h3>
{ul(['"The model is updated after every single guess." Updates happen per batch of many guesses.',
     '"Hallucination is a bug." It follows directly from always producing a full probability table.'])}

{resources([
    (yt(CL, 330), 'CampusX, LSTM Part 3: Next Word Predictor — 5:30–11:45', 'turning text into prefix → next-word training pairs'),
    (yt(CL, 1680), 'CampusX, same video — 28:00–32:00', 'why it is classification over the vocabulary'),
    (yt(KD, 900), 'Karpathy, Deep Dive into LLMs — 15:00–19:55', 'a window of tokens, 100,277 probabilities out, nudging the true token up'),
    (yt(KD, 2080), 'Karpathy, same video — 34:40–38:05', 'a real training run with the loss falling'),
])}
<p class="small">The CampusX video calls this "supervised learning" and splits text by whole words; LLMs split it into tokens. The idea is the same.</p>
{practice('llm-101/01/02_loss.py',
          'prints the loss GPT-2 assigns to every token of two sentences.',
          'replace the two sentences with <code>"Paris is the capital of France."</code>',
          'the total is 16.56; the cheapest token is <code>\' of\'</code> after "capital" (p = 0.72, loss 0.32).')}
<p class="small">The two sentences cost the same until the last word: 27.02 in total for "mat" against 46.99 for "thermodynamics", which GPT-2 splits into two unexpected tokens (11.47 + 10.82).</p>
'''))

# ================================================================= 3
S.append(('s3', '3. Why next-token prediction leads to reasoning-like behavior', f'''
<p>Producing one token takes one <strong>forward pass</strong> through the network, and a forward pass does a fixed amount of computation, because the network has a fixed number of layers (about a hundred in a modern model). The model can't "think harder" inside one pass. The only way it gets more computation is to produce more tokens.</p>

<h3>The same question, answered two ways</h3>
{show("""
A.  "17 × 24 = "
    → one token, one pass. Often wrong.

B.  "17 × 24 = ? Work step by step."
    → "17 × 20 = 340"        ← a pass
      "17 × 4  = 68"         ← a pass
      "340 + 68 = 408"       ← a pass
      "The answer is 408"    ← a pass
""")}
<p>In B, every written token is fed back in as input, so <code>"17 × 20 = 340"</code> becomes text the model can read while computing the next token. It stores partial results on the page and builds on them.</p>
{fig('llm_101_01_fig2')}

<h3>Order matters</h3>
<p>If the model writes <code>"The answer is 408, because 17 × 20 = 340…"</code>, the <code>408</code> was produced in one pass before any working existed. The explanation after it can't have helped. Karpathy calls this <strong>post-hoc justification</strong>. Working must come before the answer.</p>

<h3>Steps give computation, not correctness</h3>
<p>Each written step is itself one pass and can be wrong. When exactness matters, the better route is a tool: Karpathy has the model write and run code instead. Asked to count a row of dots, the model guessed 161; Python's <code>.count()</code> gave the true 177.</p>

<h3>Key points</h3>
{ul(['One pass = a fixed amount of computation; more tokens = more passes.',
     '"Think step by step" works because it gives the model more passes, not because the phrase is special.',
     'Put the working before the answer.',
     'For exact arithmetic or counting, use tools (code) rather than written steps.'])}

{resources([
    (yt(KD, 6505), 'Karpathy, Deep Dive into LLMs — 1:48:25–1:53:10', 'fixed compute per token, and why answer-first is post-hoc justification'),
    (yt(KD, 6840), 'Karpathy, same video — 1:54:00–1:55:30', 'forcing a one-token answer with harder numbers'),
    (yt(KD, 6930), 'Karpathy, same video — 1:55:30–2:00:55', 'using tools for arithmetic and counting'),
])}
{practice('llm-101/01/03_passes.py',
          'counts how many passes each answer style gives the model.',
          'write your own step-by-step working for 23 × 47 and count its passes.',
          '<code>23 × 40 = 920. 23 × 7 = 161. 920 + 161 = 1081. The answer is 1081.</code> is 34 tokens, so 34 passes.')}
'''))

# ================================================================= 4
S.append(('s4', '4. Emergence and scaling laws', f'''
<p>Bigger models trained on more data get better, and part of that improvement is very predictable while part of it looks sudden.</p>

<h3>Terms</h3>
{table(['Term', 'Meaning'], [
    ['parameters', 'The internal numbers adjusted during training. "7 billion" means seven billion of them.'],
    ['scaling law', 'The observed fact that loss falls smoothly and predictably as two things grow: parameters (<em>N</em>) and training data (<em>D</em>). Predictable enough to forecast a model before building it.'],
    ['emergence', 'An ability that seems absent in smaller models and present in larger ones, appearing as a jump rather than gradually.'],
])}

<h3>Smooth loss, jumpy tasks</h3>
<p>Train the same design at four sizes and measure the average loss and 5-digit addition accuracy:</p>
{show("""
size        average loss      5-digit addition
──────────────────────────────────────────────
1 billion       3.2                  0%
7 billion       2.9                  0%
30 billion      2.6                  0%
150 billion     2.3                 61%
""", 'output')}
<p class="small">Illustrative numbers with the real shape.</p>
<p>The loss column improves steadily, but addition jumps. One reason: 5-digit addition is scored right or wrong. Four correct digits out of five still scores zero. If each digit is right with probability <em>p</em>, the whole answer is right with probability <em>p</em><sup>5</sup>, which stays near zero for a long time and then rises quickly. Much of the "cliff" is in the way the test is scored, not in the model.</p>
<p>This is the argument of Schaeffer et al. (2023): with a score that gives partial credit, or more test questions, many claimed emergent abilities become smooth curves. It's a strong case but not settled; the paper itself says emergence "may not be" a fundamental property of scale.</p>

<h3>What it means in practice</h3>
{ul(['Loss can be forecast, and averages over many benchmarks tend to improve with it (Karpathy: every exam improved from GPT-3.5 to GPT-4).',
     'A single pass-or-fail task can\'t be forecast: it can sit at 0% and then jump.',
     'So test each new model on your own task instead of assuming it will be "the same, but a bit better".'])}

<h3>Key points</h3>
{ul(['Scaling laws: loss is a smooth function of parameters and data.',
     'Apparent emergence is often a property of all-or-nothing metrics.',
     'A benchmark at 0% may be improving steadily underneath.'])}

{resources([
    (yt(KI, 1535), 'Karpathy, Intro to Large Language Models — 25:35–27:35', 'scaling laws: accuracy as a smooth function of N and D'),
    ('https://arxiv.org/abs/2304.15004', 'Schaeffer, Miranda & Koyejo — Are Emergent Abilities of LLMs a Mirage? (abstract)', 'the metric argument, with evidence'),
])}
{practice('llm-101/01/04_emergence.py',
          'shows smooth per-digit accuracy turning into a sudden jump in whole-answer accuracy.',
          'set <code>digits = 10</code>.',
          'at 0.85 per digit the whole answer is right only 19.7% of the time, and the jump moves to larger sizes (48.4% at 150B, 81.7% at 400B).')}
<p class="small">The sizes and per-digit accuracies are made up to show the shape; the arithmetic (<em>p</em> to the power of the number of digits) is exact.</p>
'''))

# ================================================================= 5
S.append(('s5', '5. Foundation models vs task-specific models', f'''
<p>A <strong>foundation model</strong> is a large model pre-trained on huge, varied data with a general task (for text, next-token prediction), whose learning transfers to many other jobs. A <strong>task-specific model</strong> is trained for one job only.</p>

<h3>Comparison: classifying review sentiment</h3>
{table(['', 'Task-specific model', 'Foundation model'], [
    ['How you get it', 'Collect ~20,000 labelled reviews, train a model', 'Prompt a general model, or fine-tune it on a few hundred examples'],
    ['Data needed', 'A lot of labelled data', 'None (prompting) or a little (fine-tuning)'],
    ['Speed per call', '~3 ms', '~800 ms'],
    ['Cost per call', 'very low', 'hundreds of times higher'],
    ['Other jobs', 'none; a new category means starting over', 'also summarises, translates, writes code'],
])}

<h3>Terms</h3>
{table(['Term', 'Meaning'], [
    ['pre-training', 'The expensive first stage: training on a huge dataset with a general task.'],
    ['alignment', 'Adjusting the model\'s behaviour, e.g. people rank its answers and it is rewarded for the best ones.'],
    ['fine-tuning', 'Further training on a small labelled dataset for a specific job. CampusX\'s analogy: engineering college is pre-training, a company\'s induction programme is fine-tuning.'],
])}

<h3>Why foundation models took over</h3>
<p>Building a good task-specific model needs data, money and a team that can train models from scratch. CampusX's point is that most companies lacked these, so their models were mediocre. A foundation model arrives already strong because someone else paid for pre-training and alignment; you only adapt it by prompting or fine-tuning.</p>

<h3>When task-specific still wins</h3>
{ul(['No general model covers the job (CampusX\'s example: predicting a cricket innings\' final score).',
     'Very high volume, where per-call cost and latency dominate: e.g. flagging spam at 50,000 messages a second with millions of labels already available.'])}
<p>A common sequence: use a foundation model to find out whether the idea is worth building, and build a small specialised model only once it is and the volume makes cost matter.</p>

<h3>Key points</h3>
{ul(['What makes a foundation model is general pre-training whose learning transfers; in practice they are also large.',
     'Foundation models trade cost and speed for flexibility and a head start.',
     'Task-specific models are cheap and fast but only do one thing and need labelled data.'])}

{resources([
    (yt(CF, 150), 'CampusX, What are Foundation Models? — 2:30–3:30', 'the definition: huge architecture, massive data, general task'),
    (yt(CF, 705), 'CampusX, same video — 11:45–16:00', 'why next-word prediction transfers to other tasks'),
    (yt(CF, 990), 'CampusX, same video — 16:30–25:05', 'pre-training, alignment and fine-tuning'),
    (yt(CF, 1505), 'CampusX, same video — 25:05–31:45', 'before and after foundation models, and when task-specific still wins'),
])}
{practice('llm-101/01/05_task_specific.py',
          'builds a tiny task-specific sentiment model from labelled examples.',
          'add <code>("a masterpiece", "pos")</code> to the training data.',
          '"an absolute masterpiece" becomes <code>pos</code>, but "summarise this review" is still <code>no idea</code>: more labels fix gaps, not the fact that it does one job.')}
'''))

# ================================================================= 6
S.append(('s6', '6. Generative vs representation models', f'''
<p>There are two kinds of model in most AI applications, and they return different things for the same input.</p>
{table(['', 'Generative model', 'Representation (embedding) model'], [
    ['Returns', 'text, one token at a time', 'a fixed-length list of numbers (an embedding)'],
    ['Example output for "How do I reset my password?"', '"Go to Settings, then click Reset Password…"', '<code>[0.04, -0.21, 0.88, …]</code>, always the same length'],
    ['Used for', 'chat, writing, answering', 'search by meaning, clustering, classification'],
    ['Size', 'large (GPT-2 small: 124 million parameters; chat models: billions)', 'small (the exercise\'s model: 22.7 million)'],
    ['LangChain name', 'language model (LLM / chat model)', 'embedding model'],
])}

<h3>Embeddings and similarity</h3>
<p>An <strong>embedding</strong> is a position in space that stands for the meaning of the input. On its own it means nothing; the point is that texts with similar meanings get similar embeddings. Closeness is measured with <strong>cosine similarity</strong>, the cosine of the angle between two vectors: 1 means same direction, 0 means unrelated.</p>
{code("""
import math

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.hypot(*a) * math.hypot(*b))

question = [0.9, 0.1, 0.3]     # made-up 3-number embeddings
login    = [0.8, 0.2, 0.4]
hours    = [0.1, 0.9, 0.2]
print(f"question vs login: {cosine(question, login):.3f}")
print(f"question vs hours: {cosine(question, hours):.3f}")
""")}
<p class="small">The vectors here are made up to show the calculation; real embeddings have hundreds of numbers. The practice script uses a real model.</p>

<h3>Why real systems use both</h3>
<p>Search that works on meaning (semantic search) embeds every document once and stores the vectors in a <strong>vector database</strong>. Each question is embedded, and the closest documents are found by cosine similarity (CampusX calls this step <em>retrieve</em>). The generative model then reads only those few documents and writes the answer. This is the basis of RAG (retrieval-augmented generation).</p>
{fig('llm_101_01_fig3')}

<h3>Key points</h3>
{ul(['Generative models return text; representation models return vectors that encode meaning.',
     'Similar meanings give nearby vectors, even with no words in common.',
     'Real question-answering systems use a cheap embedding model to find documents and an expensive generative model to answer.'])}
<h3>Common misconceptions</h3>
{ul(['"LLM means any language model." Usage varies: CampusX\'s foundation-models video counts BERT, a representation model, as an LLM, while LangChain uses "LLM" for text-in, text-out models.',
     '"The big model can just search the documents itself." It would have to read all of them for every question: too slow, too expensive, and more text than fits in its context.'])}

{resources([
    (yt(CM, 145), 'CampusX, LangChain Models — 2:25–6:30', 'language models vs embedding models'),
    (yt(CM, 5392), 'CampusX, same video — 89:52–101:00', 'document similarity with embeddings and cosine similarity in code'),
    (yt(CM, 540), 'CampusX, same video — 9:00–15:30', 'LLMs vs chat models in LangChain (optional)'),
])}
{practice('llm-101/01/06_embeddings.py',
          'embeds three sentences with a real model and compares them to a question.',
          'add <code>"Can you help me get back into my account?"</code> to the list.',
          'it scores 0.565, close to "I forgot my login" and far above the closing-time question: similar meaning, different words.')}
'''))

SUMMARY = f'''
<section class="sect" id="summary">
<h2>Summary</h2>
{table(['Idea', 'In one line'], [
    ['Language model', 'text in, a probability for every next token out'],
    ['Generation', 'one token per step; a sampler picks from each table'],
    ['Training', 'predict the next token, score with <code>-log p</code>, adjust; the text labels itself'],
    ['Reasoning', 'each token is one fixed-size pass; writing steps gives more passes'],
    ['Scaling', 'loss improves smoothly; pass-or-fail tasks can look like sudden jumps'],
    ['Foundation model', 'general pre-training that transfers; adapt by prompting or fine-tuning'],
    ['Generative vs representation', 'text out vs meaning-vectors out; real systems use both'],
])}
</section>
'''

QUESTIONS = [
    ('A model writes a 50-word answer. How many probability tables does it produce?',
     'About 60, one per token (50 words is about 60 tokens).'),
    ('Two models both predict the right token, one with probability 0.55 and one with 0.99. Which gets the higher loss?',
     'The 0.55 one (loss 0.60 against 0.01). The loss rewards justified confidence, not just correctness.'),
    ('Why can\'t a model "think harder" within a single token?',
     'Each token is one forward pass through a fixed number of layers, so the computation per token is fixed. More computation needs more tokens.'),
    ('A benchmark shows 0% today. Should you expect it to stay near 0% for a model twice the size?',
     'No. A pass-or-fail score can stay at zero while the model improves steadily underneath, then jump.'),
    ('You must flag spam at 50,000 messages a second and have millions of labelled examples. Foundation model or task-specific?',
     'Task-specific: one narrow job, labels already available, and a volume where cost and latency dominate.'),
    ('Why not let the generative model search two million documents itself?',
     'It would have to read all of them for every question: too slow, too expensive, and more than fits in its context. The embedding model narrows them to a few.'),
]


def build():
    return page(TITLE, DESCRIPTION, LEAD, S, SUMMARY + review(QUESTIONS))
