# Ep 07 — Training: Loss, Gradients, and the Loss Mask

Source: `docs/learning_guide.html` → #training
Notebook: `learning_guide.ipynb` Step 7.5 (adder loss mask), Step 8 (Trainer), Step 10 (autograd)
Target: ~13 min · Status: FULL SCRIPT

---

## Cold open (0:00–0:50)

**[SAY]**
"Here's a question that sounds trivial and isn't: when GPT trains on an addition problem — '85 plus 50 equals 135' — *which tokens does it actually learn from?*
All seven? The whole equation?
The answer is three. Just the answer digits. And by the end of this episode you'll not only know why — you'll catch the model proving it, live, with gradients."

---

## Segment 1 — What training optimizes (0:50–3:00)

**[SHOW: #training — the "next-token prediction" loss figure; cross-entropy formula]**

**[SAY]**
"Training a GPT is one objective, applied everywhere: predict the next token.
We already know the forward pass produces logits — a score for every vocabulary word at every position. Training turns those scores into a single number, the loss, with cross-entropy: informally, *negative log of the probability the model assigned to the correct next token*. Confident and right: near-zero loss. Confident and wrong: huge loss.
Two things to internalize. First, at initialization the model is random, so every word gets roughly equal probability — one over vocabulary size. Take the natural log of that and you get the *expected starting loss*: ln of vocab size. Remember this — we'll verify it in five minutes.
Second, this loss is computed at *every position in parallel*, then averaged. That's what makes GPU training so efficient — and it's exactly where today's villain and hero, the loss mask, enters."

---

## Segment 2 — The loop itself (3:00–4:30)

**[SHOW: #training — the training-loop diagram mapped to first principles]**

**[SAY]**
"The loop is five lines of intent.
Sample a batch. Forward pass — logits and loss. Backward pass — `loss.backward()` sends each parameter its share of the blame, the gradient. The optimizer — AdamW — nudges every parameter a small step downhill, scaled by the learning rate. Repeat.
Two safety details you'll see in minGPT's Trainer: gradient *clipping*, which caps how far a single bad batch can yank the weights, and gradient *accumulation*, which simulates bigger batches on small GPUs.
That's genuinely the whole algorithm. Everything else is hygiene."

---

## Segment 3 — The loss mask, caught live (4:30–8:30)

**[SHOW: #training or the adder chapter — the x/y grid figure, red -1 band vs green answer band]**

**[SAY]**
"Now the experiment. The adder dataset teaches GPT arithmetic. The problem '85 plus 50 equals 135' is encoded — with plus and equals stripped and the answer *written backwards*, which makes carry-over easier to learn — as the digit string eight-five-five-zero-five-three-one.
The dataset hands the model two sequences: x, everything except the last digit; and y, everything except the first — shifted by one, because the job is always *predict the next*. And then the trick: in y, every position over the question part is overwritten with minus one."

**[RUN: Step 7.5 · cell 1 — print the mask table]**

**[SAY]**
"Look at this table. Position by position: the question digits are labeled 'masked, gradient zero'. Only the three answer positions say 'counted in loss'.
Minus one is not a number here — it's a *sentinel*. PyTorch's cross-entropy has an `ignore_index` argument; minGPT passes minus one. Ignored positions contribute exactly zero to the loss, so during backprop, no gradient flows from the question. The model cannot learn from reading the problem. Only from producing the answer."

**[PAUSE]**

**[SAY]**
"Now the prediction from segment one. This vocabulary is tiny — ten digits. What should the *initial* loss be? ln of ten: about 2.30. Let's see."

**[RUN: continue the same cell — gpt-nano forward pass]**

**[SAY]**
"Two-point-two-five. Right next to ln ten, two-point-three-zero. A randomly initialized model is exactly as confused as theory says it should be.
And the last lines are the proof: per-position loss, printed. Question positions: *zero, exactly*. Answer positions: about 2.3 each. Average those three — you get the model's loss, to four decimal places. The mask is not a metaphor. It's arithmetic."

**[EDIT: change `split="train"` to `split="test"`, rerun — different problem, same mask shape]**

---

## Segment 4 — Watch the loss actually fall (8:30–10:30)

**[RUN: Step 8 · cell 1 — configure Trainer, small run]**

**[SAY]**
"Let's train for real — gpt-nano on the adder task, a few hundred iterations, CPU-friendly.
While this spins: the Trainer config you see sets max iterations, batch size, and learning rate. We're using five-times-ten-to-the-minus-four — aggressively fast, but this model is so small it can take it.
Watch the printed loss. It starts near ln ten… and now it's falling. Not smoothly — look, plateaus, then sudden drops. That's not broken; that's what real loss curves look like. Sudden drops are the model discovering a structure — here, usually the digit-by-digit carry algorithm."

**[PAUSE: let the loss lines accumulate on screen]**

---

## Segment 5 — Learning rate: the one knob that bites (10:30–12:00)

**[SHOW: the interactive gradient-descent toy in the HTML book (#gd-canvas)]**

**[SAY]**
"The book has a toy for the failure mode. A ball rolling down a loss valley: learning rate is step size.
Small step: slow but smooth. Big step: fast… until you overshoot and the ball ricochets — loss goes *up*. Way too big: divergence, NaN, done.
The toy adds momentum, the same slider AdamW hides inside. Feel it for thirty seconds — you'll never again be surprised by a loss curve that suddenly explodes after five thousand healthy steps."

**[EDIT: drag the learning-rate slider in the toy past the stability threshold]**

---

## Segment 6 — Where the gradient comes from (12:00–12:40)

**[SHOW: Step 10 · autograd cell — brief]**

**[SAY]**
"One honest footnote: you never write the calculus. `loss.backward()` walks the whole computation graph in reverse and fills in every gradient automatically. Step 10 of the notebook has a minimal demo — run it once, see `.grad` appear on tensors, and move on. Autograd is a rabbit hole you don't need today."

## Outro (12:40–13:10)

**[SAY]**
"Recap: training is next-token cross-entropy, averaged over positions — minus any position masked with ignore-index. The adder mask means GPT learns arithmetic *only from answers*, and we proved it: masked positions contribute exactly zero.
Next episode: the model is trained — time to make it write. Temperature, top-k, and why generation is one token at a time.
Homework: in Step 8, raise the learning rate to one-times-ten-to-the-minus-two and predict what the loss curve does before you run it."

**[TRY]**
Step 8: `train_config.learning_rate = 1e-2`; predict the loss curve, then run.
