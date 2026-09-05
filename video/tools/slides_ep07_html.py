# -*- coding: utf-8 -*-
"""Ep 07 — Training & the Loss Mask (EN deck + narration)."""
import os

import slides_kit as kit

kit.FOOTER = "minGPT Learning Book · Ep 07 · Training"
kit.TOTAL = 10

SLUG = "ep07-training"
PNG_SUBDIR = "ep07-en"
VOICE = "en-US-AndrewNeural"

LOSS_CURVE = """
<svg width="1300" height="470" viewBox="0 0 1300 470">
  <rect x="0" y="0" width="1300" height="470" fill="#171e30" stroke="#2e3345" stroke-width="2" rx="14"/>
  <line x1="90" y1="40" x2="90" y2="400" stroke="#2e3345" stroke-width="2"/>
  <line x1="90" y1="400" x2="1240" y2="400" stroke="#2e3345" stroke-width="2"/>
  <text x="46" y="52" fill="#9aa3b8" font-size="22" font-family="Segoe UI">loss</text>
  <text x="1180" y="436" fill="#9aa3b8" font-size="22" font-family="Segoe UI">iterations</text>
  <text x="34" y="72" fill="#6c9eff" font-size="20" font-family="Consolas">2.30</text>
  <line x1="90" y1="66" x2="1240" y2="66" stroke="#2e3345" stroke-width="1" stroke-dasharray="5 5"/>
  <text x="950" y="56" fill="#9aa3b8" font-size="20" font-family="Segoe UI">ln(10) = 2.30 \u2014 random guessing</text>
  <path d="M 90 70 L 140 96 L 190 88 L 250 130 L 310 118 L 380 168 L 450 158 L 520 196 L 590 190 L 660 206 L 730 200 L 800 262 L 860 250 L 930 320 L 1000 310 L 1080 344 L 1240 352"
        fill="none" stroke="#fb923c" stroke-width="4" stroke-linejoin="round"/>
  <circle cx="830" cy="255" r="8" fill="#34d399"/>
  <text x="700" y="296" fill="#34d399" font-size="22" font-family="Segoe UI">a sudden drop = the model found a structure</text>
  <text x="120" y="120" fill="#9aa3b8" font-size="20" font-family="Segoe UI">starts at ln(10)\u2026</text>
</svg>
"""

NARR = [
    "Episode seven — training. And a question that sounds trivial but isn't: when GPT trains on an addition problem, eighty-five plus fifty equals one-thirty-five — which tokens does it actually learn from? All of them? The answer is three. Just the answer digits. By the end of this episode you'll have seen the model prove it, with gradients.",
    "The loop itself is five lines of intent. Sample a batch. Forward pass: logits and loss. Backward pass: loss-dot-backward sends every parameter its share of the blame. The optimizer — AdamW — nudges each parameter a small step downhill, scaled by the learning rate. Repeat. Gradient clipping and gradient accumulation are the two hygiene details minGPT adds. That is genuinely the whole algorithm.",
    "The loss is cross-entropy. Informally: minus the log of the probability the model put on the correct next token. Confident and right: near zero. Confident and wrong: enormous. And a prediction you can now make yourself: at initialization the model is random, every word gets one-over-vocabulary, so the loss should sit near the natural log of the vocabulary size. For adder's ten-digit vocabulary: ln of ten — about two point three. Hold that thought.",
    "Now the adder dataset, from the projects folder. The problem eighty-five plus fifty equals one-thirty-five is encoded — plus and equals stripped, and the answer written BACKWARDS, which makes carry-over easier to learn — as eight-five-five-zero-five-three-one. x is everything except the last digit; y is everything except the first, shifted left: always predict the next. Then the trick: every y position over the question part is overwritten with minus one.",
    "Minus one is not a number here. It's a sentinel. Cross-entropy takes an ignore-index argument; minGPT passes minus one. Ignored positions contribute exactly zero to the loss — and zero gradient. The model cannot learn from reading the question. Only from producing the answer.",
    "And the notebook proves it with real numbers, from a real gpt-nano. Per-position loss: zero, zero, zero for the question — exactly zero, not approximately — then two-point-one-eight, two-point-two-zero, two-point-three-seven for the three answer digits. Their mean: two-point-two-five. Right next to our predicted ln of ten, two-point-three-zero. The mask is not a metaphor. It's arithmetic.",
    "Three safety rails worth naming. Gradient clipping: cap how far one bad batch can yank the weights. The two-group weight decay from episode five: decay the matrices, spare the knobs. And the learning rate — the one knob that bites. Too small crawls; too big explodes. AdamW packages most of this with momentum and per-parameter scaling.",
    "And this is what a real loss curve looks like. Starts at ln of ten. Wobbles down. Plateaus — and then a sudden drop. That drop is not magic: it's the model discovering a structure — here, usually the digit-by-digit carry algorithm. Plateaus followed by cliffs are normal. Don't panic at the plateau; wait for the cliff.",
    "Your homework: in Step eight of the notebook, raise the learning rate to one-times-ten-to-the-minus-two. Predict what the loss curve does before you run it. Next episode: the model is trained — time to make it talk. Temperature, top-k, and why generation is one token at a time.",
]


def deck():
    return [
        kit.title("minGPT LEARNING BOOK · EPISODE 07",
                  "Training & the Loss Mask", "cross-entropy · AdamW · which positions get taught",
                  chips=["loss = \u2212log p", "ignore_index", "ln(vocab)"],
                  tagline="featuring the most instructive experiment in the book", page=1),
        kit.flow("THE LOOP", "Five lines of intent",
                 [("Batch", "sample (x, y)", "var(--mut)"),
                  ("Forward", "logits + loss", "var(--blue)"),
                  ("Backward", "gradients", "var(--orange)"),
                  ("AdamW", "step downhill", "var(--green)"),
                  ("Repeat", "\u00d7 max_iters", "var(--purple)")],
                 page=2,
                 note="+ two hygiene details: gradient clipping \u00b7 gradient accumulation"),
        kit.code("CROSS-ENTROPY, INFORMALLY", "loss = \u2212 log p(correct token)",
                 [("code", "confident & right   \u2192 loss \u2248 0"),
                  ("code", "confident & wrong    \u2192 loss \u2192 \u221e"),
                  ("comment", "# at init, every token is equally likely: p = 1/vocab"),
                  ("out", "expected initial loss = ln(vocab_size)  \u2192  ln(10) = 2.30")],
                 page=3,
                 right=["A testable prediction, before touching a GPU.",
                        "Adder's vocabulary is just the 10 digits.",
                        "We check this live in a minute — watch."],
                 right_title="guess before you run", right_color="var(--blue)"),
        kit.code("THE ADDER DATASET", "\u201c85+50=135\u201d, the GPT way",
                 [("comment", "# + and = stripped \u00b7 answer REVERSED (carry becomes left-to-right)"),
                  ("code", "digits: 8 5 5 0 5 3 1"),
                  ("code", "x: [8, 5, 5, 0, 5, 3]"),
                  ("code", "y: [-1, -1, -1, 5, 3, 1]   \u2190 -1 = sentinel, not a number"),
                  ("out", "cross_entropy(..., ignore_index=-1)")],
                 page=4,
                 right=["y is x shifted left: always predict the NEXT token.",
                        "Every question position is overwritten with \u22121.",
                        "Ignored positions: zero loss, zero gradient.",
                        "The model learns arithmetic only from answers."],
                 right_title="the mask", right_color="var(--orange)"),
        kit.table("THE PROOF — REAL GPT-NANO NUMBERS", "Per-position loss", 5,
                  ["position", "0", "1", "2", "3", "4", "5"],
                  [["loss", "0.000", "0.000", "0.000", "2.175", "2.196", "2.370"],
                   ["mean over answers", "\u2192 2.2466", "", "vs ln(10) =", "2.3026", "", ""]],
                  note="masked positions are EXACTLY zero \u00b7 the mask is arithmetic, not a metaphor",
                  widths="1.2fr 0.6fr 0.6fr 0.6fr 0.6fr 0.6fr 0.6fr"),
        kit.cards("SAFETY RAILS", "What keeps training alive", [
            ("RAIL 1", "Gradient clipping", "Caps how far one bad batch can yank the weights. One line, saves runs.", "var(--orange)"),
            ("RAIL 2", "Two-group decay", "Decay the matrices, spare biases & norms (Ep 05's optimizer factory).", "var(--blue)"),
            ("RAIL 3", "Learning rate", "The knob that bites: small crawls, big explodes. Feel it in the book's GD toy.", "var(--green)"),
        ], page=6),
        kit.svg_panel("WHAT A REAL RUN LOOKS LIKE", "Plateaus, then cliffs", LOSS_CURVE, page=7,
                      note="the sudden drop = the model discovering a structure (here: the carry algorithm)"),
        kit.homework("HOMEWORK",
                     ["Notebook Step 8: set learning_rate = 1e-2.",
                      "Predict the loss curve BEFORE you run. Then run."],
                     "Next episode", "Generation: one token at a time"),
        kit.end("Next episode", "Generation", "The autoregressive loop \u00b7 temperature \u00b7 top-k",
                read="Read along: docs/learning_guide.html · #training",
                run="Run along: learning_guide.ipynb · Step 8, Step 10"),
    ]


if __name__ == "__main__":
    kit.write_deck(os.path.join(os.path.dirname(__file__), "..", "build", "ep07", "html", "slides_ep07_en.html"),
                   "en", deck())
