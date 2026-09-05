# Ep 05 — Transformer Block & the Full GPT

Source: `docs/learning_guide.html` → #architecture, #block, #gpt
Notebook: `learning_guide.ipynb` Step 3 (architecture), Step 4 (forward pass), Step 6 (hooks, optional)
Target: ~13 min · Status: FULL SCRIPT

---

## Cold open (0:00–0:40)

**[SAY]**
"Last episode we built attention — the information mixer. But a mixer alone can't think.
A real GPT interleaves that mixer with a small per-word neural network, wraps both in two safety rails, and stacks the result thirty-six times deep. Today we open the box: one Transformer block, then the whole model, top to bottom — and we'll verify every shape with a live model."

---

## Segment 1 — The block: mixer + thinker (0:40–3:00)

**[SHOW: #block — the block diagram: x → LN → attention → +x → LN → MLP → +x → out]**

**[SAY]**
"Here is one Transformer block. Read it left to right.
Input comes in. First a LayerNorm — a small normalization that keeps numbers in a stable range. Then attention: positions talk to each other. Then something crucial: the attention output is *added back* to the input, unchanged. That's a residual connection.
Then the same pattern again — LayerNorm, then the MLP: a small two-layer network that each position applies to *itself*, independently. No cross-position talking. Attention mixes information *across* positions; the MLP *processes* each position alone. Mixer, thinker. Mixer, thinker. That rhythm is the entire Transformer.
Why the residuals? They're an escape hatch: gradients can flow through the 'add' shortcut untouched, which is what makes hundred-layer stacks trainable. And note the order — normalization *before* each sub-layer. That's 'Pre-LN', and it's why GPT-style models train stably where the original 2017 post-LN architecture needed careful warm-up."

---

## Segment 2 — Assemble the full GPT (3:00–5:00)

**[SHOW: #gpt — the complete data-flow figure: tokens → wte+wpe → N blocks → LN → lm_head → logits]**

**[SAY]**
"Stack N blocks and wrap them in an entrance and an exit — that's GPT.
Entrance: every token ID is looked up twice. Once in the token-embedding table — *what* it is — and once in the position-embedding table — *where* it is. The two vectors simply add.
Exit: a final LayerNorm, then the LM head — a linear layer that scores every vocabulary word for every position.
Watch one invariant as data flows through: from the embedding all the way through the last block, the shape stays batch by sequence by channel — B, T, C. Channels grow richer, but the shape doesn't move. Only at the very end does the LM head fan it out to B, T, vocab-size. If you remember one thing from this episode, remember that shape line."

**[RUN: Step 3 · cell 1 — create a gpt-nano and print the architecture]**

**[SAY]**
"Here's our patient: gpt-nano. Look at the printout and find the rhythm we just named — for each of the three blocks: ln_1, attn, ln_2, mlp. Attention has four heads; the MLP expands to four-times-forty-eight hidden units and compresses back.
And check the parameter count line — about 2.5 million in the transformer body. Now guess where most parameters actually live…"

**[PAUSE]**

---

## Segment 3 — Where the parameters really are (5:00–6:30)

**[SHOW: Step 3 output — layer shapes; #gpt parameter table for model sizes]**

**[SAY]**
"Run the parameter census in the same cell and the answer is embarrassing: the token-embedding table. Fifty thousand two hundred fifty-seven words times forty-eight dimensions — the embedding dwarfs the three blocks combined.
Keep that in mind when you hear 'nano' models have millions of parameters: most of them are dictionary, not brain. Same logic explains why real GPT-2 at 124 million parameters feels so top-heavy."

---

## Segment 4 — Forward pass, live shapes (6:30–8:30)

**[RUN: Step 4 · cell 1 — random input through the model]**

**[SAY]**
"Two fake sentences, sixteen tokens each — the actual words are garbage, we only care about shapes.
Feed it through. Logits: two by sixteen by fifty-thousand-two-hundred-fifty-seven. Exactly the invariant we predicted — the fan-out happened only at the LM head.
Read those logits like a book: for every sentence, at every position, a score for every word in the vocabulary. During training we check *all* sixteen positions against the true next tokens. During generation we read only the last row."

**[EDIT: rerun with batch of 1 and sequence length 8; have viewers predict the logits shape first]**

---

## Segment 5 — Peeking inside with hooks (8:30–10:30)

**[RUN: Step 6 · cell 1 — register hooks, capture activations]**

**[SAY]**
"One more tool before we train: forward hooks — little taps on the pipeline that record what flows through each layer, without changing the model.
We register taps on the embeddings and every block, push one batch through, and print statistics. Look at the numbers: mean near zero, standard deviation roughly stable across depth. *That's* the Pre-LN and residuals doing their job — activations neither exploding nor vanishing as we go deep.
When your training loss goes NaN someday — and it will — this cell is your stethoscope."

---

## Segment 6 — The optimizer is part of the architecture (10:30–12:30)

**[SHOW: #gpt — configure_optimizers code block]**

**[SAY]**
"Last piece, and it surprises people: minGPT's model file contains its own optimizer factory, and it splits parameters into two groups.
Linear-layer weights — the big matrices — get weight decay: a gentle pressure keeping them small. Biases, LayerNorm scales, and embeddings decay by zero.
Why? The matrices are where capacity lives; regularize capacity. Biases and normalization scales are calibration knobs; shrinking them just fights the model. This two-group split is copied nearly verbatim by nanoGPT and most modern training code — you'll meet it again in the training episode."

## Outro (12:30–13:00)

**[SAY]**
"Recap: block equals attention plus MLP with residual rails and Pre-LN. Stack them, add embedding lookup at the door and an LM head at the exit, and you have GPT. Shapes stay B-T-C until the final fan-out.
Next episode: the training loop — and the single most instructive experiment in this book, where we catch the loss mask red-handed.
Homework: in Step 3, switch the model type to gpt-mini. Predict first: how many blocks, and does the embedding still dominate?"

**[TRY]**
Step 3: `config.model_type = 'gpt-mini'`; predict block count and parameter split before running.
