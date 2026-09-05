# -*- coding: utf-8 -*-
"""Ep 05 — Transformer Block & the Full GPT (EN deck + narration)."""
import os

import slides_kit as kit

kit.FOOTER = "minGPT Learning Book · Ep 05 · Block & Full GPT"
kit.TOTAL = 10

SLUG = "ep05-block-and-gpt"
PNG_SUBDIR = "ep05-en"
VOICE = "en-US-AndrewNeural"

NARR = [
    "Episode five. Last time on the theory side, we built attention — the information mixer. But a mixer alone can't think. A real GPT interleaves it with a small per-word network, wraps both in two safety rails, and stacks the result many times deep. Today we open the box: one Transformer block, then the whole model — and we verify every claim with real numbers from the code.",
    "Here is one block, left to right. Input comes in. LayerNorm first — a small normalizer that keeps numbers in a stable range. Then attention: positions talk to each other. Then the first safety rail: the attention output is added straight back to the input — the residual connection. Then the same pattern again: LayerNorm, then the MLP — a tiny two-layer network each position applies to itself, alone. Mixer, thinker. That rhythm is the entire Transformer.",
    "And here are the actual two lines from mingpt's model dot py: x equals x plus attention of layer-norm of x; x equals x plus m l p of layer-norm of x. The plus is the residual — an escape hatch that lets gradients flow through untouched, which is what makes hundred-layer stacks trainable. And notice the order: normalize BEFORE each sub-layer. That's Pre-LN, and it's why GPT-style models train stably where the original twenty-seventeen design needed careful warm-up.",
    "Now assemble the full model. The entrance: every token ID is looked up twice — what it is, in the token-embedding table, and where it is, in the position-embedding table. The two vectors simply add. The body: N blocks stacked. The exit: one final LayerNorm, then the LM head — a linear layer that scores every word in the vocabulary, at every position.",
    "How big are these models, really? From the actual config table in the code: gpt-nano — three layers, three heads, forty-eight dimensions. Micro: four. Mini: six. Then real GPT-2: twelve layers, seven hundred sixty-eight dimensions, one hundred twenty-four million parameters — all the way to extra-large: forty-eight layers, one and a half billion parameters. The recipe never changes. Only the numbers do.",
    "Now the parameter census, and it's embarrassing. gpt-nano: two and a half million parameters in the transformer body — plus two point four million in the output head. Almost half the model is dictionary! The token-embedding table alone outweighs all three thinking blocks combined. Keep that in mind whenever you hear how many parameters a model has: a lot of them are just the word list.",
    "Watch one invariant as data flows through. Tokens go in as batch by sequence. After embedding: batch, sequence, channel — and that shape does not move through every single block. Channels get richer in meaning, but the shape holds. Only at the very end does the LM head fan it out to batch, sequence, fifty-thousand-two-hundred-fifty-seven. If you remember one thing today, remember that shape line.",
    "Last piece, and it surprises people: minGPT's model file contains its own optimizer factory, and it splits parameters into two groups. Matrices — anything with two or more dimensions — get weight decay: gentle pressure keeping them small. Biases and LayerNorm scales decay by zero. Why? Matrices are where capacity lives; regularize capacity. Calibration knobs shouldn't be shrunk for sport. This exact split is copied across modern training code.",
    "Your homework: switch the notebook to gpt-mini. Predict first: how many blocks, and does the embedding still dominate? Then run. Next episode: the two small functions that give a network its nonlinearity — GELU and softmax.",
]


def deck():
    return [
        kit.title("minGPT LEARNING BOOK · EPISODE 05",
                  "Block & the Full GPT", "residuals · LayerNorm · the MLP · stacking",
                  chips=["mixer + thinker", "Pre-LN", "(B, T, C) forever"],
                  tagline="from one block to a complete model — with real numbers", page=1),
        kit.flow("ONE BLOCK", "The rhythm: mixer, thinker",
                 [("x", "input", "var(--mut)"),
                  ("LayerNorm", "stabilize", "var(--blue)"),
                  ("Attention", "mix across positions", "var(--green)"),
                  ("\u2295 add", "residual rail", "var(--orange)"),
                  ("LayerNorm", "stabilize", "var(--blue)"),
                  ("MLP", "think per position", "var(--purple)"),
                  ("\u2295 add", "residual rail", "var(--orange)")],
                 page=2, gap=10,
                 note="attention talks ACROSS positions \u00b7 the MLP processes each position ALONE"),
        kit.code("INSIDE THE CODE", "The whole block, in two lines",
                 [("comment", "# mingpt/model.py \u00b7 Block.forward"),
                  ("code", "x = x + self.attn(self.ln_1(x))"),
                  ("code", "x = x + self.mlp(self.ln_2(x))")],
                 page=3,
                 right=["The <b>+</b> is the residual — a gradient highway that makes deep stacks trainable.",
                        "Normalize <b>before</b> each sub-layer: <b style='color:var(--green)'>Pre-LN</b> — the reason GPT-style models train stably.",
                        "The 2017 original normalized after, and needed careful warm-up to survive."],
                 right_title="why it trains"),
        kit.cards("ASSEMBLE", "Door, hallway, exit", [
            ("ENTRANCE", "wte + wpe", "Look up each ID twice — what it is, where it is — and add the two vectors.", "var(--blue)"),
            ("BODY", "N \u00d7 Block", "Stack identical blocks. Depth = expertise. Same weights pattern, many copies.", "var(--green)"),
            ("EXIT", "ln_f + lm_head", "Final norm, then a linear layer scores all 50,257 words at every position.", "var(--purple)"),
        ], page=4),
        kit.table("FROM THE CODE", "The model_type table (mingpt/model.py)", 5,
                  ["model_type", "layers", "heads", "dim", "params"],
                  [["gpt-nano", "3", "3", "48", "tiny"],
                   ["gpt-micro", "4", "4", "128", "\u2014"],
                   ["gpt-mini", "6", "6", "192", "\u2014"],
                   ["gpt2", "12", "12", "768", "124M"],
                   ["gpt2-medium", "24", "16", "1024", "350M"],
                   ["gpt2-large", "36", "20", "1280", "774M"],
                   ["gpt2-xl", "48", "25", "1600", "1558M"]],
                  note="the recipe never changes — only the numbers do",
                  widths="1fr 0.6fr 0.6fr 0.6fr 0.8fr"),
        kit.code("PARAMETER CENSUS", "Where gpt-nano's parameters live",
                 [("code", "transformer body   2.55M"),
                  ("code", "lm_head            2.41M"),
                  ("out", "total              4.96M   \u2190 ~half is the DICTIONARY"),
                  ("comment", "# the 3 thinking blocks are a rounding error next to the embedding table")],
                 page=6,
                 right=["50,257 words \u00d7 48 dims = a huge lookup table.",
                        "The blocks that \u201cthink\u201d are tiny in comparison.",
                        "\u201cParameter count\u201d can be misleading — ask where they live."],
                 right_title="dictionary vs brain", right_color="var(--purple)"),
        kit.flow("THE SHAPE LINE", "One invariant to remember",
                 [("tokens", "(B, T)", "var(--mut)"),
                  ("embed", "(B, T, 48)", "var(--blue)"),
                  ("N blocks", "(B, T, 48)", "var(--green)"),
                  ("lm_head", "(B, T, 50257)", "var(--orange)")],
                 page=7,
                 note="channels grow richer, but the shape never moves — until the final fan-out"),
        kit.code("OPTIMIZER FACTORY", "Two groups of parameters",
                 [("comment", "# mingpt/model.py \u00b7 configure_optimizers"),
                  ("code", "decay:    params with dim &gt;= 2   (matrices)"),
                  ("code", "no_decay: params with dim  &lt; 2   (biases, LayerNorm)"),
                  ("out", "AdamW(decay: weight_decay=0.1 | no_decay: 0.0)")],
                 page=8,
                 right=["Matrices hold the capacity — regularize capacity.",
                        "Biases & norms are calibration knobs — shrinking them just fights the model.",
                        "This exact split is copied across modern training code."],
                 right_title="regularize what matters", right_color="var(--red)"),
        kit.homework("HOMEWORK",
                     ["Switch to gpt-mini in the notebook.",
                      "Predict: how many blocks? Does the embedding still dominate? Then run."],
                     "Next episode", "Activations: GELU & Softmax"),
        kit.end("Next episode", "Activations: GELU & Softmax", "The only two nonlinearities a GPT needs",
                read="Read along: docs/learning_guide.html · #block, #gpt",
                run="Run along: learning_guide.ipynb · Step 3, Step 4"),
    ]


if __name__ == "__main__":
    kit.write_deck(os.path.join(os.path.dirname(__file__), "..", "build", "ep05", "html", "slides_ep05_en.html"),
                   "en", deck())
