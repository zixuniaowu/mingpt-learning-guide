# -*- coding: utf-8 -*-
"""Ep 08 — Generation: one token at a time (EN deck + narration)."""
import os
import math

import slides_kit as kit

kit.FOOTER = "minGPT Learning Book · Ep 08 · Generation"
kit.TOTAL = 9

SLUG = "ep08-generation"
PNG_SUBDIR = "ep08-en"
VOICE = "en-US-AndrewNeural"

LOGITS = [2.8, 1.9, 0.7, -0.4]
WORDS = ["the", "a", "cat", "xyz"]


def softmax_t(logits, t):
    m = max(l / t for l in logits)
    e = [math.exp(l / t - m) for l in logits]
    s = sum(e)
    return [x / s for x in e]


def row(words, probs):
    return "   ".join(f"{w}: {p * 100:5.1f}%" for w, p in zip(words, probs))


NARR = [
    "Episode eight. When ChatGPT answers a long question, it is not handing you a completed thought. It is playing a slot machine — thousands of times. Predict one token. Append it. Predict again. Today: why that works, what temperature and top-k do to the slot machine, and the one engineering trick production systems add. Everything you've learned so far drives this episode.",
    "Here is generate, the whole thing. Take your prompt — a list of token IDs. Forward pass. Take the logits from the LAST position only — the model's guess for what comes next. Pick one token from that distribution. Append it to the sequence. Feed the whole thing back in. Repeat until a length limit or an end-of-text token. Twenty lines of code in minGPT. And it explains, for free, why chat answers unroll token by token: you are watching the loop run.",
    "The sampling core, in four lines. Divide the last-position logits by the temperature. Optionally keep only the top k and ban the rest with minus infinity. Softmax. Multinomial sample. That's it — and those are the same lines inside every production LLM API you have ever called.",
    "Temperature, with real numbers. Our four candidates — the, a, cat, xyz — with fixed logits. At temperature one: sixty-four, twenty-six, eight, three percent — the model's honest opinion. At temperature zero-point-five: eighty-five, fourteen, one, zero — sharp, safe, repetitive. At temperature two: forty-six, twenty-nine, sixteen, nine — flattened; even the junk token xyz now wins sometimes. Temperature doesn't change what the model knows. It changes how adventurous the pick is.",
    "Top-k is the safety net, not a flavor knob. Whatever temperature did, top-k says: only the k most likely candidates may survive; the tail is banned with minus infinity before softmax. Why? A flattened distribution gives every token — including junk — a non-zero chance. Top-k draws a hard floor. Low temperature plus top-k is the standard recipe for code generation: safe and sane.",
    "One honest engineering note. Our generate recomputes the ENTIRE forward pass for the ENTIRE sequence, every step. A hundred generated tokens means a hundred full passes, mostly recomputing attention over tokens already seen. Production engines fix this with the KV cache: remember each token's keys and values from the moment you compute them, and each step processes only ONE new token. Identical output, dramatically faster. minGPT skips the cache on purpose — caching would double this chapter's code for zero extra insight. But now you can name what every inference library sells.",
    "And the payoff moment of the whole course: same minGPT class, same generate loop — but the weights come from OpenAI's pretrained GPT-2, one hundred twenty-four million parameters. One call to from-pretrained, and gibberish becomes fluent English. Same code. The only difference is training. Fluency, remember, is not truth — that's episode ten.",
    "Your homework: open the sampler playground in the book's generation chapter and find the temperature where the junk token wins about one time in ten. Then justify that value using the softmax curve. Next episode: scaling laws, fine-tuning, and how the model knows word order at all.",
]


def deck():
    return [
        kit.title("minGPT LEARNING BOOK · EPISODE 08",
                  "Generation", "One token at a time",
                  chips=["last-position logits", "temperature", "top-k"],
                  tagline="a slot machine, played thousands of times", page=1),
        kit.flow("THE AUTO-REGRESSIVE LOOP", "Predict, append, repeat",
                 [("Prompt", "token IDs", "var(--mut)"),
                  ("Forward", "all positions", "var(--blue)"),
                  ("Last logits", "next-word scores", "var(--orange)"),
                  ("Sample", "pick one", "var(--green)"),
                  ("Append", "feed it back", "var(--purple)"),
                  ("Repeat", "\u2026", "var(--red)")],
                 page=2, gap=10,
                 note="no planner, no memory of the paragraph — just next-token prediction, recursively eating its own output"),
        kit.code("THE SAMPLING CORE", "Four lines power every LLM API",
                 [("code", "logits = model(idx)[:, -1] / temperature"),
                  ("code", "topk: ban everything outside the k best"),
                  ("code", "probs  = softmax(logits)"),
                  ("code", "next   = multinomial(probs) \u2192 append")],
                 page=3,
                 right=["Same three lines inside GPT-4-class APIs (behind nicer names).",
                        "greedy = temperature \u2192 0: always the argmax, prone to repetition loops.",
                        "minGPT's generate(): ~20 lines total."],
                 right_title="read it once, recognize it forever", right_color="var(--green)"),
        kit.code("TEMPERATURE — REAL NUMBERS", "logits: the 2.8, a 1.9, cat 0.7, xyz \u22120.4",
                 [("code", f"T = 1.0  \u2192  {row(WORDS, softmax_t(LOGITS, 1.0))}"),
                  ("code", f"T = 0.5  \u2192  {row(WORDS, softmax_t(LOGITS, 0.5))}"),
                  ("code", f"T = 2.0  \u2192  {row(WORDS, softmax_t(LOGITS, 2.0))}"),
                  ("out", "the model didn't change \u2014 the pick did")],
                 page=4,
                 right=["Low T: sharp, safe, repetitive.",
                        "High T: flat, creative \u2014 junk tokens start winning.",
                        "Computed from the actual softmax \u2014 verify in the book's sampler toy."],
                 right_title="how adventurous is the pick?", right_color="var(--orange)"),
        kit.two_panel("TWO DIALS, TWO JOBS", "temperature flavors \u00b7 top-k protects",
                      "<div style='font-size:28px;line-height:1.9;color:var(--mut)'>"
                      "<b style='color:var(--ink)'>T &lt; 1</b> sharpens: boring, safe, deterministic-feeling.<br>"
                      "<b style='color:var(--ink)'>T &gt; 1</b> flattens: creative, drunk, surprising.<br>"
                      "<b style='color:var(--ink)'>T \u2192 0</b> is greedy decoding: argmax every time.</div>",
                      "<div style='font-size:28px;line-height:1.9;color:var(--mut)'>"
                      "Keep only the <b style='color:var(--ink)'>k</b> most likely tokens; ban the tail with \u2212\u221e before softmax.<br><br>"
                      "A hard floor, so flattened distributions can't hand the win to junk.<br>"
                      "Code generation standard: <b style='color:var(--ink)'>low T + top-k</b>.</div>",
                      page=5, left_color="var(--orange)", right_color="var(--blue)",
                      left_head="TEMPERATURE \u2014 flavor", right_head="TOP-K \u2014 safety net"),
        kit.code("THE MISSING PIECE", "Why production inference is fast: the KV cache",
                 [("comment", "# minGPT generate(): recompute EVERYTHING, every step"),
                  ("code", "step 1: forward(prompt)               \u2192 1 pass"),
                  ("code", "step 2: forward(prompt + t1)           \u2192 2 passes worth"),
                  ("code", "step n: forward(all tokens so far)     \u2192 n passes worth"),
                  ("out", "KV cache: remember past K/V \u2192 each step processes ONE new token")],
                 page=6,
                 right=["Identical output, dramatically less compute.",
                        "minGPT skips it on purpose: caching doubles this chapter's code for zero extra insight.",
                        "Now you can name what every inference library sells."],
                 right_title="prompt caching \u2192 cheaper tokens", right_color="var(--purple)"),
        kit.statement('Same code, pretrained weights: <span style="color:var(--green)">GPT-2 speaks English</span>.',
                      "model = GPT.from_pretrained('gpt2') \u2014 124M params, one line.<br>"
                      "Gibberish \u2192 fluent text. <b>The only difference is training.</b> (Fluency \u2260 truth \u2014 Ep 10.)", page=7),
        kit.homework("HOMEWORK",
                     ["Open the sampler playground in the book's generation chapter.",
                      "Find the temperature where junk wins ~1 in 10 \u2014 justify it via the softmax curve."],
                     "Next episode", "Scaling, Fine-tuning & Position"),
        kit.end("Next episode", "Scaling, Fine-tuning & Position", "pretrain \u2192 SFT \u2192 RLHF \u00b7 LoRA \u00b7 RoPE",
                read="Read along: docs/learning_guide.html · #generation, #finetuning, #scaling",
                run="Run along: generate.ipynb"),
    ]


if __name__ == "__main__":
    kit.write_deck(os.path.join(os.path.dirname(__file__), "..", "build", "ep08", "html", "slides_ep08_en.html"),
                   "en", deck())
