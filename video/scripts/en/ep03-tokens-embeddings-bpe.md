# Ep 03 — From Text to Vectors: Tokenization & BPE (OUTLINE — expand before recording)

Source: `docs/learning_guide.html` → #tokenization, #bpe
Notebook: learning_guide.ipynb Step 5 (tokenizer prep) — extend with a live BPE demo cell
Target: ~11 min · Status: OUTLINE

## Cold open
Why can't the model see letters? Why does it miscount the r's in "strawberry"? Because it doesn't see letters at all.

## Segments

1. **Step 1 — text to integer IDs** (~2.5 min)
   - [SHOW: #tokenization — text → IDs figure]
   - Key points: the model's entire diet is integers; vocabulary ≈ 50,257 for GPT-2.

2. **Step 2 — integers to vectors** (~2.5 min)
   - [SHOW: #tokenization — embedding lookup figure]
   - Key points: embedding = lookup table, not a magic net; one row per token; vectors acquire geometry through training (similar meanings drift together).

3. **BPE: how the vocabulary is built** (~3 min)
   - [SHOW: #bpe — merge visualization]
   - Key points: start from bytes, greedily merge frequent pairs; frequent words become single tokens, rare words splinter into pieces; explains tokenizer pathologies (arithmetic, reversal, non-English inefficiency).

4. **Why tokenizers cause famous failures** (~2 min)
   - Examples: strawberry-r counting; "9.11 vs 9.9"; token-boundary artifacts. Tokenizer + next-token training explain a lot of "stupidity".

## Code moment (mandatory)
- [RUN: Step 5 · cell 1 — BPETokenizer encode/decode round-trip]
- [EDIT: encode "strawberry", "1984", a Chinese sentence; print token counts and IDs; decode back]

## Outro + [TRY]
- Try: find an English word that BPE splits into 3+ tokens; predict its IDs, then check.
- Tease Ep 04: vectors are in the door — now let positions talk to each other.
