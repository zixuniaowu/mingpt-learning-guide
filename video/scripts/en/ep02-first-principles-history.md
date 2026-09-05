# Ep 02 — First Principles of Language Modeling (OUTLINE — expand before recording)

Source: `docs/learning_guide.html` → #first-principles, #history
Notebook: none mandatory; optional Step 2 (create model)
Target: ~12 min · Status: OUTLINE

## Cold open
The game every LLM plays: "guess the next word" — nothing more. Tease: from this party trick to writing code.

## Segments

1. **The always-guess-the-next-word game** (~3 min)
   - [SHOW: #first-principles — the guessing-game figure]
   - Key points: probabilities over vocabulary; no database of sentences; generalization comes from compression.
   - [EDIT: play the "human next-word" game on screen with 3 example sentences]

2. **Why prediction forces understanding** (~3 min)
   - Key points: to predict well you must model grammar, facts, style, world state — they fall out as *compression strategies*, not hand-coded rules.
   - Connect: loss = negative log probability; lower loss = better compression (mention "language modeling is compression" intuition).

3. **A 10-minute history: RNN → LSTM → Attention** (~4 min)
   - [SHOW: #history — the evolution timeline figure]
   - Key points: RNN's vanishing memory; LSTM gates (a patch, not a cure); Seq2Seq's bottleneck; 2017 "Attention Is All You Need" removes recurrence entirely.
   - Do NOT deep-dive attention here — one sentence and defer to Ep 04.

4. **Scale changed the game** (~2 min)
   - Key points: same objective, more data + parameters + compute → qualitatively new skills (in-context learning). Sets up Ep 09 scaling laws.

## Code moment (mandatory)
- [RUN: Step 2 · cell 1 — create gpt-nano, count parameters]
- Say: "four million parameters of pure next-token machinery — everything in this episode lives in there."

## Outro + [TRY]
- Try: hand-complete 3 sentences two different plausible ways — that's the distribution a model samples from.
- Tease Ep 03: before a model can play the game, text must become numbers.
