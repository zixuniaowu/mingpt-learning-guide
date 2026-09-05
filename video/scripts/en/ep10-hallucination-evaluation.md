# Ep 10 — Hallucination & How to Evaluate LLMs (OUTLINE — expand before recording)

Source: `docs/learning_guide.html` → #beyond, #hallucination, #evaluation
Notebook: none mandatory; generate.ipynb optional as a hallucination specimen generator
Target: ~12 min · Status: OUTLINE

## Cold open
Ask GPT-2 (from Ep 08) for a biography of a person who doesn't exist. It writes one, fluently. It was never lying — it was never capable of *not*.

## Segments

1. **What LLMs actually are — beyond the hype** (~2.5 min)
   - [SHOW: #beyond — "what it is / what it isn't" two-column figure]
   - Key points: a next-token distribution conditioned on context; no world model guarantee, no truth module, no memory beyond the window.

2. **Hallucination is a feature of the objective, not a bug** (~3.5 min)
   - [SHOW: #hallucination — the mechanism figure]
   - Key points: training rewards *plausible continuation*; plausibility ≠ truth; when the prompt asks about something the weights never saw, the model samples from the nearest plausible manifold — fluent fabrication; why "it sounds confident" is evidence of nothing.
   - Mitigations one-liner each: grounding/RAG, tool use, calibrated uncertainty — full treatment in Ep 11.

3. **How do you measure a language model?** (~3.5 min)
   - [SHOW: #evaluation — benchmark table + per-task-metric table]
   - Key points: perplexity (internal quality) vs task accuracy (useful quality); why benchmarks leak — training on the test set, literally; benchmark saturation and Goodhart's law; evals as the real bottleneck of agent progress — foreshadow Ep 11 "verification loop".

4. **A skeptic's checklist** (~2 min)
   - Key points: when you read "model X beats model Y" — same eval? same prompts? same parser? contamination? Encourage viewers to default to running evals themselves.

## Code moment (mandatory)
- [RUN: generate.ipynb — prompt GPT-2 with a fictional entity; show confident fluent nonsense]
- [EDIT: raise temperature to 1.3 — hallucination rate visibly explodes; connect to Ep 08 sampling]

## Outro + [TRY]
- Try: find one claim by any LLM this week, trace it to a primary source; note how often "plausible" ≠ "true".
- Tease Ep 11: if hallucination can't be eliminated, agents need *external verification* — that's loop engineering.
