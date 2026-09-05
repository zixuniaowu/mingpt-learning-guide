# Ep 04 — Self-Attention: The Core of the Transformer

Source: `docs/learning_guide.html` → #attention
Notebook: `learning_guide.ipynb` Step 4.5 (attention hand-calculation)
Target: ~13 min · Status: FULL SCRIPT

---

## Cold open (0:00–0:45)

**[SAY]**
"Read this sentence: 'The animal didn't cross the street because *it* was too tired.'
What does 'it' refer to? You resolved that instantly — but for a neural network, that's the hardest problem in language. Every word needs to know which *other* words matter to it.
Attention is the mechanism that makes that possible, and it is *the* core idea of the Transformer. This is the most important episode in the series. Give me thirteen minutes and you'll be able to compute attention by hand."

---

## Segment 1 — Why attention at all (0:45–2:30)

**[SHOW: #attention — the RNN vs Attention comparison figure]**

**[SAY]**
"Before Transformers, language models were RNNs. An RNN reads a sentence one word at a time, squeezing everything it has seen into a single hidden state — a running summary.
Think about what that means for a hundred-word sentence. Word number one has been compressed, and recompressed, ninety-nine times. Details die in that pipeline. And because it's sequential, you can't parallelize it — GPUs sit idle.
Attention throws away the running summary. Instead, *every word looks at every other word directly, in one step*. The path length between any two words is one. That's the whole revolution of the 2017 'Attention Is All You Need' paper."

---

## Segment 2 — Q, K, V: the library analogy (2:30–4:30)

**[SHOW: #attention — the Q/K/V three-roles diagram]**

**[SAY]**
"Attention gives every position three vectors, and the names are actually intuitive if you picture a library.
**Query** — what am I looking for? The word 'it' might ask: *I need a noun, singular, an animal or object.*
**Key** — what do I advertise? Every other word carries a label: *I'm a noun*, *I'm a verb*, *I'm recent*.
**Value** — what do I actually hand over if someone attends to me? My content, my meaning.
Matching is just a dot product: query dots key, big score means 'we're relevant'. Then every position takes a weighted average of the Values, using those scores as weights.
That's it. Attention is a *soft, differentiable dictionary lookup*. Keep that phrase — it's the honest one-line definition."

---

## Segment 3 — The five steps, as real numbers (4:30–8:00)

**[SHOW: #attention — the Q@K^T → causal mask → softmax → weighted V step figure]**

**[SAY]**
"Here is the entire computation in five steps.
One: multiply queries by keys transposed — a T-by-T score matrix.
Two: scale by one over root d-k, so dot products don't blow up softmax.
Three: apply the *causal mask* — more on that in a second.
Four: softmax each row, so scores become weights that sum to one.
Five: multiply the weights by V. Output: each position now holds a blend of the information it was allowed to see.
Don't take my word for it. Let's compute it — live."

**[RUN: Step 4.5 · cell 1 — attention hand-calculation]**

**[SAY]**
"Four positions, three dimensions — deliberately tiny, same as the interactive toy in the HTML book.
First output: S equals Q times K transposed. A four-by-four score table. Entry i-j is how much position i wants position j.
Now — before I run the next part, *you* guess: after the causal mask and softmax, what will row zero look like?"

**[PAUSE]**

**[RUN: continue the same cell — mask + softmax]**

**[SAY]**
"Row zero is one-zero-zero-zero. Why? The causal mask. Position zero isn't *allowed* to look right, so its only visible option is itself. Every row of A sums to exactly one — softmax guarantees it.
And notice the last cell of the notebook: when we zero out the query projection, every position treats all visible positions *equally* — a uniform distribution. The queries are what break the tie. No query preference, no attention pattern."

**[EDIT: in the notebook, change `Wq = torch.eye(d_k)` to a matrix with a big second-column value, rerun, observe row shifts]**

---

## Segment 4 — The causal mask: no peeking (8:00–9:30)

**[SHOW: the masked score matrix in Step 4.5 output, upper triangle = -inf]**

**[SAY]**
"Why the mask? A language model is trained to predict the *next* token. If position three could see position four while being trained to predict it, that's cheating — like training on the answer key.
So every position gets to look at itself and everything to the *left*, and nothing else. We enforce it brutally: future positions get minus infinity before the softmax, which becomes *exactly zero* after.
One subtlety worth knowing: the full Q-times-K is still computed for those positions — the work isn't skipped, the *result* is discarded. Optimization tricks like FlashAttention exist precisely to avoid wasting that work."

---

## Segment 5 — Multi-head in one minute (9:30–10:30)

**[SHOW: #attention — multi-head "experts" section]**

**[SAY]**
"One attention pattern per layer is one *opinion*. Real GPTs run many in parallel — multi-head attention. Each head gets a slice of the embedding dimension and learns its own notion of relevance: one head might track grammar, another coreference — that's our 'it'-refers-to-'the animal' head — another just tracks recency.
In minGPT's gpt-nano: four heads, each watching a twelve-dimensional slice. Small specialists, concatenated back together at the end."

---

## Segment 6 — See it move (10:30–12:30)

**[SHOW: the interactive attention toy in the HTML book (#attn-toy)]**

**[SAY]**
"The book has a live toy for this — the same four tokens, real computation, nothing pre-recorded. Click 'next step' to walk through scores, mask, softmax, and the weighted values.
Now the fun part: *every number in Q, K and V is editable*. Let's make 'cats' pay more attention to 'love' — I'll bump the second entry of cats' query row… see the scores change? The softmax row re-normalized, and the output vector for 'cats' shifted toward love's value vector.
This is the experiment loop from episode one: guess, change, observe. Do it a few times until 'softmax re-normalizes' stops being a formula and becomes a reflex."

**[EDIT: live — modify Q/K/V values in the toy, predict which arrows get stronger]**

---

## Outro (12:30–13:00)

**[SAY]**
"Recap: attention is a soft dictionary lookup — query dots key gives relevance, softmax makes it a distribution, weighting values gives each position its new representation. The causal mask keeps the future invisible. Heads give you parallel experts.
Next episode we wrap attention in residuals, LayerNorm and an MLP — the Transformer *block* — and stack it into a complete GPT.
Your homework: in the notebook's Step 4.5, replace the identity value-projection with a random matrix and explain, in one sentence, what changed in the output and why."

**[TRY]**
Step 4.5: swap `Wv` for `torch.randn(d_k, d_k)`; explain the effect in one sentence.
