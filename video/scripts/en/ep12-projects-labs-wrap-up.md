# Ep 12 — Projects, Labs & Wrap-Up (OUTLINE — expand before recording)

Source: `docs/learning_guide.html` → #implementation, #utils, #projects, #labs, #conclusion
Notebook: demo.ipynb; projects/adder/adder.py
Target: ~12 min · Status: OUTLINE

## Cold open
You've seen every concept. Today we walk the actual code top to bottom — then hand you the keys: three projects you can extend tonight.

## Segments

1. **The 300-line reading map** (~3 min)
   - [SHOW: #implementation — model.py structure]
   - Key points: NewGELU → CausalSelfAttention → Block → GPT; where each prior episode lives in the file; "you can now read every line — try it".

2. **The config system & Trainer** (~2 min)
   - [SHOW: #utils — CfgNode and Trainer loop snippets]
   - Key points: CfgNode = minimal yacs-style config; Trainer = 50 lines of real training hygiene (device, amp, clip, checkpointing); get_default_config pattern used everywhere.

3. **Project: adder** (~2.5 min)
   - [SHOW: #projects — adder data construction recap from Ep 07]
   - Key points: the canonical minimal project — dataset class, config, Trainer.run; the loss mask as the star; open the code and locate every element named in Ep 07.

4. **Project: chargpt + demo.ipynb** (~1.5 min)
   - Key points: char-level LM = same pipeline, vocabulary of 65; demo.ipynb = sort task, identical skeleton; "change the dataset, keep everything else" is the whole lesson.

5. **The labs chapter as your gym** (~1.5 min)
   - [SHOW: #labs — the guess/run/explain/tweak loop diagram from Ep 01, full circle]
   - Key points: every lab maps to a notebook step; keep using the four-step loop.

6. **Wrap-up: where to go next** (~1.5 min)
   - Key points: read nanoGPT (same DNA, modern tricks); Karpathy's "Zero to Hero" videos; the guide's own glossary as review; contribute back — the book is open source, translations welcome.

## Code moment (mandatory)
- [RUN: demo.ipynb — first three cells live]
- [EDIT: change the sort-task sequence length; predict effect on learning speed before running]

## Outro
- Recap the whole series in 60 seconds: tokens → attention → blocks → training with masks → generation → scale & evaluation → agents.
- Final [TRY]: extend adder to 3-digit addition (`ndigit=3`) — predict what breaks first (block size? vocabulary? training time?), then find out.
