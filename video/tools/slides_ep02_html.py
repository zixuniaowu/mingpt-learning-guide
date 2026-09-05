# -*- coding: utf-8 -*-
"""Ep 02 — What Language Modeling Really Does (EN deck + narration)."""
import os

import slides_kit as kit

kit.FOOTER = "minGPT Learning Book · Ep 02 · Language Modeling"
kit.TOTAL = 9

SLUG = "ep02-first-principles"
PNG_SUBDIR = "ep02-en"
VOICE = "en-US-AndrewNeural"

NARR = [
    "Episode two. Before we touch a single weight, we need to be precise about what a language model actually does. The answer sounds too simple: it plays one game — guess the next word — billions of times. This episode is about why that one game, played at scale, produces something that looks like understanding.",
    "Try it yourself. The capital of France is… blank. You already completed it, instantly, and you couldn't stop yourself. That completion — the probability you felt — is literally the only output a language model produces. Everything else, essays, code, jokes, is this one trick, applied over and over.",
    "But here's the subtle part. To guess the next word well, the model is forced to learn three things for free. Grammar — word order and agreement — because wrong grammar is almost never the right continuation. World knowledge — Paris follows France — because that's where the probability mass lives. And style: formal versus casual, code versus prose. Nobody programs these in. They fall out of the objective as compression strategies.",
    "So the objective in one line: for every position, output a probability for every word in the vocabulary, and during training, reward the probability that was put on the actual next token. During generation, we sample from that distribution instead. Same machine, two modes: training compares, generation samples.",
    "How did we get here? A quick history. In the nineties, recurrent networks read word by word through one hidden state — memory faded fast. LSTM, in ninety-seven, added gates that protect information — a patch, not a cure. Twenty-fourteen: sequence-to-sequence with attention, for translation. And twenty-seventeen: the Transformer throws away recurrence entirely — that's the model family GPT comes from. Attention gets its own episode next but one.",
    "Here's the deepest way to think about it: prediction is compression. To predict text well, you must compress it — find its structure, its regularities, its rules. A model that assigns high probability to real text has, in a precise sense, understood its patterns. Lower loss equals better compression equals more skill. This is why scaling the objective works at all.",
    "And scale did change everything. GPT-1, twenty-eightteen, one hundred seventeen million parameters. GPT-2, twenty-nineteen: one and a half billion — and suddenly coherent paragraphs. GPT-3, twenty-twenty: one hundred seventy-five billion — and in-context learning appears: the model does tasks from examples in the prompt, without any weight updates. Same objective, same game — but somewhere along the curve, quantity became quality.",
    "Your homework: write three sentence beginnings and complete each one two different plausible ways. Notice you sampled from a distribution — exactly what the model does. And skim the first-principles chapter in the book. Next episode: before a model can play this game, text has to become numbers. Tokenization, and the BPE algorithm.",
]


def deck():
    return [
        kit.title(
            "minGPT LEARNING BOOK · EPISODE 02",
            "What Language Modeling Really Does",
            "One game: guess the next word",
            chips=["probability", "compression", "scale"],
            tagline="first principles — before we touch the weights", page=1),
        kit.statement(
            'The capital of France is <span style="color:var(--orange)">____</span>',
            "You completed it instantly — and you couldn't stop yourself.<br>"
            "That felt <b style='color:var(--blue)'>probability</b> is the <b>only</b> thing a language model outputs. "
            "Essays, code, jokes: one trick, applied billions of times.", page=2),
        kit.cards("WHY ONE GAME TEACHES SO MUCH",
                  "Prediction forces understanding", [
                      ("FORCED", "Grammar", "Wrong word order is almost never a plausible continuation — so the model learns syntax for free.", "var(--blue)"),
                      ("FORCED", "World knowledge", "\u201cParis\u201d follows \u201cthe capital of France is\u201d — that's where the probability mass lives.", "var(--green)"),
                      ("FORCED", "Style & register", "Code continues as code, legalese as legalese. Tone is a statistical fingerprint.", "var(--purple)"),
                  ], page=3),
        kit.flow("THE OBJECTIVE", "One machine, two modes",
                 [("Text", "every position", "var(--mut)"),
                  ("Model", "per word: a score", "var(--orange)"),
                  ("Softmax", "scores \u2192 probability", "var(--yellow)"),
                  ("Training", "compare to truth", "var(--red)"),
                  ("Generation", "sample & append", "var(--green)")],
                 page=4,
                 note="training rewards the probability that landed on the real next token — generation samples from it instead"),
        kit.flow("A TEN-MINUTE HISTORY", "From recurrence to attention",
                 [("RNN", "1990s · one hidden state", "var(--mut)"),
                  ("LSTM", "1997 · gates protect memory", "var(--blue)"),
                  ("Seq2Seq", "2014 · + attention", "var(--purple)"),
                  ("Transformer", "2017 · no recurrence", "var(--green)")],
                 page=5,
                 note="\u201cAttention Is All You Need\u201d removes the running summary — every word sees every word (deep dive in Ep 04)"),
        kit.bullets("THE DEEPEST VIEW", "Prediction is compression",
                    ["To predict text well, you must compress it — find its regularities.",
                     "High probability on real text = the structure has been captured.",
                     "<b style='color:var(--blue)'>lower loss = better compression = more skill.</b>",
                     "This is why simply scaling the objective keeps paying off."],
                    page=6),
        kit.table("SCALE CHANGED THE GAME", "Same objective, new abilities", 7,
                  ["Model", "Year", "Parameters", "What appeared"],
                  [["GPT-1", "2018", "117M", "the recipe"],
                   ["GPT-2", "2019", "1.5B", "coherent paragraphs"],
                   ["GPT-3", "2020", "175B", "in-context learning"]],
                  note="in-context learning: doing tasks from examples in the prompt — zero weight updates",
                  hl_col=3, widths="0.7fr 0.6fr 0.8fr 1.6fr"),
        kit.homework("HOMEWORK",
                     ["Write 3 sentence beginnings; complete each in 2 plausible ways — that's sampling.",
                      "Skim the book's \u201cfirst principles\u201d chapter."],
                     "Next episode", "From Text to Vectors: Tokenization & BPE"),
        kit.end("Next episode", "From Text to Vectors", "Tokenization · BPE · embeddings",
                read="Read along: docs/learning_guide.html · chapters 3\u20134", run="Run along: learning_guide.ipynb · Step 2"),
    ]


if __name__ == "__main__":
    kit.write_deck(os.path.join(os.path.dirname(__file__), "..", "build", "ep02", "html", "slides_ep02_en.html"),
                   "en", deck())
