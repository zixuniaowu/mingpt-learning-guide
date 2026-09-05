# -*- coding: utf-8 -*-
"""Ep 03 — From Text to Vectors: Tokenization & BPE (EN deck + narration)."""
import os

import slides_kit as kit

kit.FOOTER = "minGPT Learning Book · Ep 03 · Tokenization & BPE"
kit.TOTAL = 9

SLUG = "ep03-tokens-embeddings"
PNG_SUBDIR = "ep03-en"
VOICE = "en-US-AndrewNeural"

NARR = [
    "Episode three. Here's a fact that surprises everyone: a language model has never seen a letter. Not a word, not a sentence — only numbers. Everything it will ever read or write passes through a translator called the tokenizer. Today we watch that translator work, and we explain some famous AI failures along the way.",
    "Remember the strawberry question — how many r's are in strawberry? Models got this wrong for years. Not because they're dumb, but because they never see the letters r. They see token IDs — and spelling happens to be invisible at that level. Keep that in mind as we go.",
    "The pipeline has two steps. Step one: text goes through the tokenizer and comes out as a list of integer IDs — for GPT-2, numbers between zero and fifty thousand two hundred fifty-six. Step two: each ID is looked up in the embedding table — a giant matrix — and becomes a vector. From here on, the model does all its thinking with vectors.",
    "How is the vocabulary built? Byte-pair encoding — BPE. Start from single characters, then greedily merge the most frequent adjacent pair, again and again, until you reach the target vocabulary size. Frequent words fuse into single tokens; rare words splinter into pieces. It's a statistics-driven compression of the language itself.",
    "The classic example, from the original paper. Our corpus says low, low, low, lower, lowest, newest, newest. First merge: e-s, because e followed by s is the most frequent pair. Then e-s-t. Then e-s-t glued to the end-of-word marker. Then l-o, then l-o-w. Watch: low becomes one token, but lower stays low plus er. Frequency decided — not meaning.",
    "Now the real thing — actual GPT-2 token IDs, computed by the course notebook. I love cats becomes four tokens: forty, eighteen forty-two, eleven thousand eight hundred seventy-five, and zero for the exclamation mark. Strawberry — three tokens. And the year one-nine-eight-four is a single token. The tokenizer chops by frequency, not by meaning.",
    "This explains real failures. Letter counting: strawberry splits into three chunks, and no chunk knows how many r's it carries. Number arithmetic: digits fuse into single tokens, so digit-by-digit operations start from a handicap. And cost inequality: the same sentence can cost two or three times more tokens in Chinese or Japanese than in English — because the merges were learned mostly from English text.",
    "Step two, briefly: embeddings. The lookup table is just storage — one vector per ID. The geometry is learned. During training, words used in similar ways drift together: king, queen, prince cluster; the vector from king to man parallels queen to woman. The table stores the coordinates; training draws the map.",
    "Your homework: in the notebook's Step five, encode the word strawberry and the year of your birth, and look at how each splits. Next episode is the heart of the whole series: self-attention — and you're going to compute it by hand.",
]


def deck():
    return [
        kit.title("minGPT LEARNING BOOK · EPISODE 03",
                  "From Text to Vectors", "Tokenization · BPE · embeddings",
                  chips=["text \u2192 IDs", "IDs \u2192 vectors", "vocab = 50,257"],
                  tagline="the translator every model speaks through first", page=1),
        kit.statement('A language model has <span style="color:var(--orange)">never seen a letter</span>.',
                      "Only integer IDs. How many r's are in \u201cstrawberry\u201d?<br>"
                      "The model can't check — <b style='color:var(--blue)'>spelling is invisible at token level.</b>", page=2),
        kit.flow("THE PIPELINE", "Two steps into the model",
                 [("Text", "\u201cI like cats\u201d", "var(--mut)"),
                  ("Tokenizer", "BPE splits & numbers", "var(--orange)"),
                  ("IDs", "[40, 588, \u2026]", "var(--purple)"),
                  ("Embedding", "lookup table", "var(--green)"),
                  ("Vectors", "the model's diet", "var(--blue)")],
                 page=3,
                 note="GPT-2 vocabulary: 50,257 tokens \u00b7 from here on, everything is vector math"),
        kit.cards("THE TWO STEPS", "Split, then look up", [
            ("STEP 1", "text \u2192 IDs", "BPE chops text into subword chunks and numbers them. Frequent sequences fuse; rare ones splinter.", "var(--orange)"),
            ("STEP 2", "IDs \u2192 vectors", "The embedding table stores one learned vector per ID — row 1842 IS the word \u201clove\u201d, as far as the model knows.", "var(--green)"),
        ], page=4),
        kit.code("BITE-PAIR ENCODING", "BPE: greedily merge the most frequent pair",
                 [("comment", "# corpus: low low low lower lowest newest newest"),
                  ("code", "merge 1: (e, s)  -&gt; es"),
                  ("code", "merge 2: (es, t) -&gt; est"),
                  ("code", "merge 3: (est, &lt;/w&gt;) -&gt; est&lt;/w&gt;"),
                  ("code", "merge 4: (l, o)  -&gt; lo"),
                  ("code", "merge 5: (lo, w) -&gt; low"),
                  ("out", "result: low | low | low | low\u00b7er | low\u00b7est | new\u00b7est")],
                 page=5,
                 right=["Frequency decides — not meaning.",
                        "\u201clow\u201d earns its own token; \u201clower\u201d stays as low\u00b7er.",
                        "Same rule, applied to billions of characters, builds the whole 50,257 vocabulary.",
                        "The classic example from the original BPE paper."],
                 right_title="merges by statistics", right_color="var(--orange)"),
        kit.code("REAL GPT-2 OUTPUT", "The tokenizer, live",
                 [("comment", "# BPETokenizer() from mingpt.bpe"),
                  ("code", "\u201cI love cats!\u201d  \u2192 [40, 1842, 11875, 0]"),
                  ("code", "\u201cstrawberry\u201d    \u2192 [301, 1831, 8396]"),
                  ("code", "\u201c1984\u201d           \u2192 [28296]"),
                  ("out", "# one year = one token \u00b7 one word = three")],
                 page=6,
                 right=["Real IDs, from the course notebook.",
                        "\u201cstrawberry\u201d is three chunks \u2014 st\u00b7raw\u00b7berry style.",
                        "No chunk carries letter-level information.",
                        "Keep this slide in mind whenever a model fumbles spelling."],
                 right_title="token IDs", right_color="var(--green)"),
        kit.cards("SO THAT'S WHY", "Famous failures, explained", [
            ("FAILURE", "Letter counting", "strawberry = 3 opaque chunks. Counting r's means spelling — which was never visible.", "var(--orange)"),
            ("FAILURE", "Digit arithmetic", "Numbers fuse into single tokens; digit-by-digit logic starts from a handicap.", "var(--purple)"),
            ("FAILURE", "Unequal cost", "The same sentence can cost 2\u20133\u00d7 more tokens in zh/ja — merges were learned mostly from English.", "var(--red)"),
        ], page=7),
        kit.statement("Embeddings are <span style=\"color:var(--green)\">learned geometry</span>.",
                      "The table is storage; training draws the map.<br>"
                      "king \u2192 man runs parallel to queen \u2192 woman. Similar use \u2192 nearby vectors.", page=8),
        kit.homework("HOMEWORK",
                     ["Notebook Step 5: encode \u201cstrawberry\u201d and your birth year; inspect the splits.",
                      "Skim the tokenization & BPE chapters in the book."],
                     "Next episode", "Self-Attention — computed by hand"),
        kit.end("Next episode", "Self-Attention", "The core of the Transformer — real numbers, by hand",
                read="Read along: docs/learning_guide.html · chapter \u201ctokenization\u201d, \u201cbpe\u201d",
                run="Run along: learning_guide.ipynb · Step 5"),
    ]


if __name__ == "__main__":
    kit.write_deck(os.path.join(os.path.dirname(__file__), "..", "build", "ep03", "html", "slides_ep03_en.html"),
                   "en", deck())
