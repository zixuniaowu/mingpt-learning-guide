# -*- coding: utf-8 -*-
"""Ep 09 — Scaling, Fine-tuning & Position Encoding (EN deck + narration)."""
import os

import slides_kit as kit

kit.FOOTER = "minGPT Learning Book · Ep 09 · Scaling & Fine-tuning"
kit.TOTAL = 9

SLUG = "ep09-scaling-finetuning-position"
PNG_SUBDIR = "ep09-en"
VOICE = "en-US-AndrewNeural"

NARR = [
    "Episode nine. A base model is a wild stallion: brilliant, no manners. Three topics today: how raw predictors become assistants — pretraining, SFT, RLHF. How to adapt one cheaply — LoRA. And a question you've never heard answered properly: how does the model know word ORDER at all? Position encoding.",
    "The pipeline everyone sells as magic. Stage one, pretraining: next-token prediction on a giant slice of the internet — ourEp-07 loss, nothing more. Stage two, supervised fine-tuning: SAME loss, better data — demonstrations of an assistant answering well. Stage three, RLHF: train on preferences — which answer is better — instead of exact text. Chat behavior is data and rewards, not a different architecture.",
    "Fine-tuning everything is expensive. LoRA — low-rank adaptation — freezes the big matrix W and trains two small ones, B and A, whose product approximates the task's update. The math for a four-thousand-ninety-six square matrix: full fine-tuning touches sixteen point eight million parameters. LoRA with rank eight: two matrices of four-thousand-ninety-six by eight — sixty-five thousand parameters. Zero point four percent. And because B starts at zero, the model begins exactly where pretraining left off.",
    "And how big should a model be? The scaling-law surprise: loss falls as a smooth power law in parameters, data, AND compute — and most models were starved on data. The Chinchilla result: parameter count and training tokens should scale together. Bigger is not automatically better per FLOP — better-fed usually wins. minGPT's own table already shows the shape: same recipe, from three layers to forty-eight.",
    "Now the question nobody asks: how does the model know word order? Attention is permutation-symmetric — a bag of tokens. Dog bites man and man bites dog would score identically. The fix: inject position information. minGPT follows GPT-2: learned absolute position embeddings — one vector per position, simply added to the token embedding. One line of code in the forward pass: token embedding plus the first T position vectors.",
    "Learned absolute positions are simple but can't generalize past the trained window. Modern models use rotary embeddings — RoPE — which encode relative position by rotating queries and keys inside attention. Same idea — position must enter somewhere — different injection point. When a model stumbles beyond its context window, position encoding is usually why.",
    "Your homework: sketch the LoRA shapes for a four-thousand-ninety-six square weight with rank eight, and count the trainable parameters — sixty-five thousand five hundred thirty-six. Feel how small that is. Next episode: the model sounds so confident. Why confidence is evidence of nothing.",
]


def deck():
    return [
        kit.title("minGPT LEARNING BOOK · EPISODE 09",
                  "Scaling, Fine-tuning & Position", "pretrain \u2192 SFT \u2192 RLHF \u00b7 LoRA \u00b7 where order lives",
                  chips=["3 stages", "LoRA rank 8", "wpe"],
                  tagline="taming the stallion", page=1),
        kit.flow("THE LLM PIPELINE", "Chat behavior is data, not magic",
                 [("Pretraining", "next-token on everything (Ep 07 loss)", "var(--mut)"),
                  ("SFT", "SAME loss, demonstration data", "var(--blue)"),
                  ("RLHF", "train on preferences, not exact text", "var(--green)")],
                 page=2,
                 note="same architecture end to end \u2014 only the data and the objective's details change"),
        kit.code("LORA, THE MATH", "Freeze W \u00b7 train the low-rank detour",
                 [("comment", "# full fine-tune of one 4096\u00d74096 matrix"),
                  ("code", "4096 \u00d7 4096            = 16,777,216 params"),
                  ("comment", "# LoRA: W' = W + B\u00b7A, B starts at ZERO"),
                  ("code", "B: 8\u00d74096 + A: 4096\u00d78 =     65,536 params   (0.39%)")],
                 page=3,
                 right=["B = 0 at start \u2192 the model begins exactly where pretraining ended.",
                        "Rank r is the capacity/cost dial (the book has a whole LoRA chapter).",
                        "Task updates are approximately low-rank \u2014 that's why this works."],
                 right_title="99.6% smaller", right_color="var(--green)"),
        kit.table("SCALING LAWS, IN ONE TABLE", "minGPT's model_type table is the shape of the law", 4,
                  ["model", "layers \u00d7 heads \u00d7 dim", "params"],
                  [["gpt-nano \u2192 mini", "3 \u2192 6 layers", "\u2192"],
                   ["gpt2", "12 \u00d7 12 \u00d7 768", "124M"],
                   ["gpt2-large", "36 \u00d7 20 \u00d7 1280", "774M"],
                   ["gpt2-xl", "48 \u00d7 25 \u00d7 1600", "1558M"]],
                  note="Chinchilla's lesson: parameters and training TOKENS must scale together \u2014 bigger alone is not better",
                  hl_col=2, widths="1fr 1.4fr 0.8fr"),
        kit.cards("POSITION ENCODING", "How the model knows word order", [
            ("THE PROBLEM", "Attention is a bag of tokens", "Permutation-symmetric: \u201cdog bites man\u201d and \u201cman bites dog\u201d score identically without help.", "var(--orange)"),
            ("minGPT / GPT-2", "Learned absolute", "One learned vector per position, added at the entrance: x = wte[idx] + wpe[:T].", "var(--blue)"),
            ("LLaMA & friends", "RoPE (rotary)", "Rotates Q/K inside attention to encode RELATIVE position; generalizes better past the window.", "var(--green)"),
        ], page=5),
        kit.code("THE ONE LINE", "minGPT's forward, entrance",
                 [("comment", "# mingpt/model.py \u00b7 GPT.forward"),
                  ("code", "tok_emb = self.wte(idx)        # what it is"),
                  ("code", "pos_emb = self.wpe(pos)        # where it is"),
                  ("out", "x = self.drop(tok_emb + pos_emb)")],
                 page=6,
                 right=["Two lookup tables, one addition.",
                        "Order enters the model HERE \u2014 nowhere else.",
                        "Beyond block_size? The wpe table simply ends."],
                 right_title="position, injected", right_color="var(--blue)"),
        kit.homework("HOMEWORK",
                     ["Sketch LoRA shapes for a 4096\u00d74096 weight, rank 8.",
                      "Count the trainable params: 2\u00d74096\u00d78 = 65,536."],
                     "Next episode", "Hallucination & Evaluation"),
        kit.end("Next episode", "Hallucination & Evaluation", "why confidence is evidence of nothing",
                read="Read along: docs/learning_guide.html · #finetuning, #scaling, #position",
                run="Run along: demo.ipynb"),
    ]


if __name__ == "__main__":
    kit.write_deck(os.path.join(os.path.dirname(__file__), "..", "build", "ep09", "html", "slides_ep09_en.html"),
                   "en", deck())
