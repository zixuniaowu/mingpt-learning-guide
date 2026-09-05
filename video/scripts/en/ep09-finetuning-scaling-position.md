# Ep 09 — Fine-tuning, Scaling Laws & Position Encoding (OUTLINE — expand before recording)

Source: `docs/learning_guide.html` → #finetuning, #comparisons, #scaling, #position
Notebook: demo.ipynb (optional compare), no mandatory live run
Target: ~14 min · Status: OUTLINE

## Cold open
A base model is a wild stallion: brilliant, no manners. This episode: how you tame it (fine-tuning), how big "big enough" is (scaling laws), and how the model knows word order at all (position encoding).

## Segments

1. **Pretraining vs fine-tuning vs RLHF — the pipeline** (~3.5 min)
   - [SHOW: #finetuning — the three-stage pipeline figure]
   - Key points: pretraining = next-token on everything; SFT = next-token on demonstrations (same loss, better data!); RLHF = optimize preferences, not likelihood. "Chat behavior is data, not magic."

2. **LoRA and parameter-efficient fine-tuning** (~3 min)
   - [SHOW: #finetuning — LoRA side-matrix diagram]
   - Key points: freeze W, train low-rank BA; rank as capacity/cost dial; why it works (task deltas are approximately low-rank); connect: minGPT's configure_optimizers two-group split (Ep 05) as the conceptual ancestor.

3. **Scaling laws** (~3 min)
   - [SHOW: #scaling — loss vs compute/params/data log-log figure]
   - Key points: loss falls as a smooth power law; the Chinchilla lesson — most models were underfed on data; why the biggest model is not automatically the best per-FLOP.

4. **Position encoding: where am I?** (~3 min)
   - [SHOW: #position — position embedding figure; architecture comparison table (#comparisons)]
   - Key points: attention is permutation-symmetric — without position info "dog bites man" == "man bites dog"; learned absolute embeddings (minGPT/GPT-2) vs rotary (LLaMA); extrapolation beyond the training window as the key trade-off.

## Code moment (mandatory)
- [RUN: scratch cell — gpt-nano `wpe` weight matrix plotted as a heatmap; point out structured row patterns]
- [EDIT: slice rows 0, 1, 2 vs rows 1000+; comment on similarity]

## Outro + [TRY]
- Try: sketch the LoRA shapes for a 4096×4096 weight with rank 8 — how many trainable parameters?
- Tease Ep 10: the model sounds confident. Confidence is not correctness.
