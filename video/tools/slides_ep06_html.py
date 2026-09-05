# -*- coding: utf-8 -*-
"""Ep 06 — Activations: GELU & Softmax (EN deck + narration)."""
import os

import math

import slides_kit as kit

kit.FOOTER = "minGPT Learning Book · Ep 06 · Activations"
kit.TOTAL = 9

SLUG = "ep06-activations"
PNG_SUBDIR = "ep06-en"
VOICE = "en-US-AndrewNeural"

LOGITS = [2.0, 1.0, 0.0]


def softmax_t(logits, t):
    m = max(l / t for l in logits)
    e = [math.exp(l / t - m) for l in logits]
    s = sum(e)
    return [x / s for x in e]


P1 = softmax_t(LOGITS, 1.0)
P05 = softmax_t(LOGITS, 0.5)


def pct(xs):
    return "  ".join(f"{x * 100:4.1f}%" for x in xs)


NARR = [
    "Episode six. Two small functions decide how sharp or smooth your network thinks: GELU and softmax. A GPT uses exactly these two nonlinearities — nothing else. Nine minutes and you'll know where each one lives, what it feels like, and one numerical trick that keeps them stable.",
    "First, why nonlinearity at all? Stack one hundred linear layers and multiply it all out — you get… one linear layer. Matrix times matrix times matrix is still a matrix. Without a nonlinearity folded in between, depth means nothing. Activations are the reason depth equals power.",
    "Where do they live? Softmax lives inside attention — it turns scores into weights that sum to one. GELU lives inside every MLP — after the expand layer, before the compress. And softmax makes a second appearance at generation time, turning the final logits into next-word probabilities. Two functions, three jobs.",
    "ReLU is the brutal gate: negative goes to zero, positive passes unchanged. Its gradient is a step function, and dead neurons pile up below zero. GELU is the soft gate: times the Gaussian CDF of x — formally x times Phi of x. Small negatives aren't chopped; they pass with reduced strength, smoothly. minGPT uses the tanh approximation of GELU — the same curve, cheaper to compute. The book has an interactive chart where you can hover both curves.",
    "Quick comparison to lock it in. ReLU: hard gate, used widely in CNNs, can kill neurons. GELU: smooth gate, the GPT and BERT standard, keeps tiny negative signals alive. Softmax: not a gate at all — it normalizes a whole row of scores into a probability distribution. Three functions, three personalities.",
    "Now softmax with real numbers, because it previews episode eight. Take logits two, one, zero. At temperature one, softmax gives sixty-six point five, twenty-four point five, nine percent. Divide the logits by zero point five — that's low temperature — and the same tokens become eighty-six point seven, eleven point seven, one point six percent. Low temperature sharpens; high temperature flattens. Remember the divide-by-temperature trick — it's the whole knob.",
    "One numerical trick professionals never skip: softmax is invariant if you add the same constant to every logit — so before exponentiating, subtract the max. exp can overflow to infinity for large logits; after subtracting the max, the biggest argument is zero — exp of zero is one — nothing can blow up. Same answer, zero risk. You'll see this line in every production softmax.",
    "Your homework: verify that shift invariance numerically — compute softmax of a vector, then of that vector plus one hundred, and confirm they're identical. Next episode is where it gets real: the training loop — and the most instructive experiment in the whole book, the loss mask.",
]


def deck():
    return [
        kit.title("minGPT LEARNING BOOK · EPISODE 06",
                  "Activations", "GELU & Softmax — the only two a GPT needs",
                  chips=["ReLU", "GELU", "softmax"],
                  tagline="small functions, big personalities", page=1),
        kit.statement("Without nonlinearity, <span style=\"color:var(--orange)\">100 layers = 1 layer</span>.",
                      "matrix \u00d7 matrix \u00d7 matrix \u2026 is still one matrix.<br>"
                      "Activations are the reason <b style='color:var(--blue)'>depth means anything</b>.", page=2),
        kit.cards("WHERE THEY LIVE", "Two functions, three jobs", [
            ("INSIDE ATTENTION", "Softmax \u2192 weights", "Turns pairwise scores into weights that sum to 1. You saw it in Ep 04, step by step.", "var(--green)"),
            ("INSIDE EVERY MLP", "GELU \u2192 nonlinearity", "After the 4\u00d7 expansion, before the compression. The only nonlinearity in the blocks.", "var(--blue)"),
            ("AT GENERATION", "Softmax \u2192 next token", "The final logits become next-word probabilities (previewed below).", "var(--orange)"),
        ], page=3),
        kit.code("THE FORMULAS", "Brutal gate vs soft gate",
                 [("code", "ReLU(x)  = max(0, x)"),
                  ("code", "GELU(x)  = x \u00b7 \u03a6(x)"),
                  ("comment", "# minGPT's NewGELU \u2014 tanh approximation, same curve, cheaper"),
                  ("code", "0.5x(1 + tanh(\u221a(2/\u03c0)(x + 0.044715x\u00b3)))")],
                 page=4,
                 right=["ReLU: negatives chopped dead; gradient is a step.",
                        "GELU: small negatives pass <b>smoothly</b>, scaled by their Gaussian probability.",
                        "The book's GELU chapter has a hoverable chart of both curves."],
                 right_title="hard vs soft", right_color="var(--blue)"),
        kit.table("LINE THEM UP", "Three functions, three personalities", 5,
                  ["Function", "Lives in", "Job", "Quirk"],
                  [["ReLU", "CNNs, older nets", "hard gate", "dead neurons"],
                   ["GELU", "GPT / BERT MLPs", "soft gate", "keeps tiny negatives"],
                   ["Softmax", "attention + sampling", "normalize a row", "needs the max-trick"]],
                  note="a GPT uses GELU once and softmax twice per forward pass",
                  hl_col=1, widths="0.8fr 1fr 1fr 1.2fr"),
        kit.code("REAL NUMBERS", "Softmax \u00d7 temperature (logits = 2, 1, 0)",
                 [("code", f"T = 1.0  \u2192  {pct(P1)}"),
                  ("code", f"T = 0.5  \u2192  {pct(P05)}"),
                  ("comment", "# low temperature sharpens \u00b7 high temperature flattens"),
                  ("out", "same logits \u2014 completely different personality")],
                 page=6,
                 right=["Dividing logits by T before softmax is the <b>entire</b> temperature knob.",
                        "T \u2192 0: argmax, deterministic. T large: flat, adventurous.",
                        "Full playground in Ep 08."],
                 right_title="preview of generation", right_color="var(--orange)"),
        kit.statement("Professional softmax always <span style=\"color:var(--green)\">subtracts the max</span> first.",
                      "softmax(x) = softmax(x + c) for any constant c.<br>"
                      "Subtracting the max means the largest exponent argument is 0 \u2014 <b>nothing can overflow</b>.", page=7),
        kit.homework("HOMEWORK",
                     ["Numerically verify softmax(x) == softmax(x + 100).",
                      "Hover the GELU vs ReLU chart in the book's activation chapter."],
                     "Next episode", "Training — and the loss mask"),
        kit.end("Next episode", "Training & the Loss Mask", "Cross-entropy \u00b7 AdamW \u00b7 which positions get taught",
                read="Read along: docs/learning_guide.html · #gelu, #softmax, #training",
                run="Run along: learning_guide.ipynb · Step 7.5"),
    ]


if __name__ == "__main__":
    kit.write_deck(os.path.join(os.path.dirname(__file__), "..", "build", "ep06", "html", "slides_ep06_en.html"),
                   "en", deck())
