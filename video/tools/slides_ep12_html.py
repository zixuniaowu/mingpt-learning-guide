# -*- coding: utf-8 -*-
"""Ep 12 — Projects, Labs & Wrap-Up (EN deck + narration)."""
import os

import slides_kit as kit

kit.FOOTER = "minGPT Learning Book · Ep 12 · Wrap-Up"
kit.TOTAL = 9

SLUG = "ep12-projects-labs-wrapup"
PNG_SUBDIR = "ep12-en"
VOICE = "en-US-AndrewNeural"

NARR = [
    "The finale. You've seen every concept — now we walk the actual code top to bottom, then hand you the keys: the projects you can extend tonight. Three hundred lines of PyTorch are about to feel like an old friend.",
    "The reading map of mingpt's model dot py, top to bottom: NewGELU — episode six's soft gate. CausalSelfAttention — episode four's entire computation, with the mask. Block — episode five's mixer-thinker rhythm in two lines. And GPT — the assembler: embeddings in, blocks stacked, LM head out. That's the whole file. You can now read every line of it — try it tonight.",
    "Three projects, one skeleton. Adder — GPT learns addition, and the loss mask from episode seven is the star of the show. Chargpt — a character-level language model: same pipeline, a sixty-five-word vocabulary of characters. Demo notebook — a sorting task, identical skeleton again. Notice the pattern: change the dataset, keep everything else. That's the whole trick.",
    "Your own project takes three pieces. A dataset class that emits x-y pairs — token tensors, with minus one marking what not to train. A config — model type, learning rate, iterations, via the get-default-config pattern. And trainer dot run. Twenty lines that aren't about deep learning — they're about clarity.",
    "And keep using the method from episode one. The labs chapter in the book maps every experiment to a notebook step, built on the loop: guess, run, explain, tweak. It's the gym. The series gave you the concepts; the loop turns them into reflexes.",
    "Where to go next. NanoGPT — the same DNA with modern tricks; you'll recognize all of it now. Karpathy's zero-to-hero videos — the author of minGPT teaching it in person. And this book is open source — translations, diagrams, and new chapters are welcome contributions.",
    "The whole series in one breath: text becomes tokens; tokens become vectors; attention mixes information under a causal mask; blocks stack into GPT; training is next-token cross-entropy with masked positions; generation samples and appends; scale and data made it powerful; evaluation keeps it honest; and the same loop, given tools, became your coding agent.",
    "Final homework, and it's a good one: extend adder to three-digit addition — set n-digit to three. Predict what breaks first: the block size, the training time, or the model's patience? Then find out. Thank you for reading — and running — the book.",
]


def deck():
    return [
        kit.title("minGPT LEARNING BOOK · EPISODE 12",
                  "Projects, Labs & Wrap-Up", "read the code · extend the projects",
                  chips=["model.py", "adder", "your turn"],
                  tagline="the finale — from reader to owner", page=1),
        kit.code("THE 300-LINE READING MAP", "mingpt/model.py, top to bottom",
                 [("code", "NewGELU              \u2190 Ep 06 soft gate"),
                  ("code", "CausalSelfAttention  \u2190 Ep 04, mask included"),
                  ("code", "Block                \u2190 Ep 05, two lines + rails"),
                  ("code", "GPT                  \u2190 Ep 05 assembler"),
                  ("out", "you can now read every line \u2014 try it tonight")],
                 page=2,
                 right=["Each class maps to an episode you've watched.",
                        "trainer.py: the Ep-07 loop with clipping.",
                        "bpe.py: the Ep-03 translator.",
                        "utils.py: CfgNode configs + seeding."],
                 right_title="nothing left hidden", right_color="var(--green)"),
        kit.cards("THREE PROJECTS, ONE SKELETON", "Change the dataset, keep everything else", [
            ("PROJECT", "adder", "GPT learns addition. The loss mask (Ep 07) is the star: train only on answers.", "var(--orange)"),
            ("PROJECT", "chargpt", "Character-level LM: same pipeline, 65-character vocabulary.", "var(--green)"),
            ("NOTEBOOK", "demo.ipynb", "A sorting task \u2014 identical skeleton, tiny and quick to run.", "var(--blue)"),
        ], page=3),
        kit.flow("YOUR OWN PROJECT", "Three pieces, twenty lines",
                 [("Dataset", "(x, y) tensors \u00b7 -1 = don't train", "var(--blue)"),
                  ("Config", "model_type \u00b7 lr \u00b7 max_iters", "var(--purple)"),
                  ("Trainer.run()", "the Ep-07 loop does the rest", "var(--green)")],
                 page=4,
                 note="get_default_config() \u2192 tweak \u2192 run \u2014 the pattern every project here shares"),
        kit.bullets("THE LABS CHAPTER IS YOUR GYM", "Keep the loop running",
                    ["Every lab maps to a notebook step in learning_guide.ipynb.",
                     "<b style='color:var(--blue)'>Guess \u2192 run \u2192 explain \u2192 tweak</b> \u2014 the method from Ep 01.",
                     "Concepts from a video fade; reflexes from the loop stick."],
                    page=5),
        kit.bullets("WHERE NEXT", "The road after the book",
                    ["<b>nanoGPT</b> \u2014 same DNA, modern tricks; you'll recognize all of it.",
                     "<b>Karpathy's Zero-to-Hero</b> \u2014 the author teaching minGPT in person.",
                     "<b>This book is open source</b> \u2014 translations, diagrams, new chapters: welcome."],
                    page=6),
        kit.statement("The series in one breath",
                      "tokens \u2192 attention under a causal mask \u2192 blocks \u2192 masked next-token training \u2192<br>"
                      "sample &amp; append \u2192 scale &amp; evaluate \u2192 <b style='color:var(--blue)'>the loop, given tools, became your agent.</b>", page=7),
        kit.homework("FINAL HOMEWORK",
                     ["Extend adder to ndigit = 3.",
                      "Predict what breaks first: block size, time, or patience? Then find out."],
                     "Thank you", "Now go run something"),
        kit.end("The end", "You ran the model", "minGPT Learning Book \u00b7 thanks for reading \u2014 and running",
                read="docs/learning_guide.html \u00b7 learning_guide.ipynb \u00b7 projects/adder",
                run="github.com/zixuniaowu/mingpt-learning-guide \u00b7 contributions welcome"),
    ]


if __name__ == "__main__":
    kit.write_deck(os.path.join(os.path.dirname(__file__), "..", "build", "ep12", "html", "slides_ep12_en.html"),
                   "en", deck())
