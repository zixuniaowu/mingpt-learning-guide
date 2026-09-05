# Ep 01 — Welcome & How to Use This Book

Source: `docs/learning_guide.html` → #overview, #glossary, #preface, #structure, #workflow
Notebook: `learning_guide.ipynb` Step 1
Target: ~10 min · Status: FULL SCRIPT

---

## Cold open (0:00–0:40)

**[SAY]**
"Every AI course shows you slides. This one hands you a live model.
By the end of this series you will have *run* — not watched, *run* — a real GPT: you'll create it, break it, train it, and make it write text.
And we'll do it with minGPT: Andrej Karpathy's three-hundred-line implementation. Small enough to read on a weekend, real enough to match what powers ChatGPT."

**[SHOW: README hero image or the HTML overview section]**

---

## Segment 1 — What this book actually is (0:40–2:30)

**[SHOW: #overview — the "HTML 书页 → Notebook 实验台 → minGPT 源码" flow diagram]**

**[SAY]**
"This project is built as three layers that say the same thing three ways.
First, the HTML book: diagrams and intuition — this is where you *understand*.
Second, the notebook: every idea becomes code you can execute — this is where you *verify*.
Third, the source: `mingpt/model.py`, `trainer.py`, and the adder project — this is where you *confirm nothing was hidden from you*.
If a diagram ever feels hand-wavy, the code is one click away. That's the whole design."

**[SAY]**
"One warning before we start: this is a *learning* fork of minGPT, and the guide itself is written in Chinese. If you're watching this in English — the diagrams are language-independent, and I'll translate everything that matters. The code comments are trilingual anyway."

---

## Segment 2 — The reading loop: guess, run, explain, tweak (2:30–4:30)

**[SHOW: #labs — the circular "先猜 → 执行 → 解释 → 改参数" diagram]**

**[SAY]**
"Here is the rule that makes this course work. Every single code cell goes through a four-step loop.
Step one: *guess*. Before you run anything, predict the output. What shape? What number?
Step two: *run* the cell.
Step three: *explain* every line of the output to yourself.
Step four: *tweak* one parameter and watch what changes.
If you skip the guessing step, a notebook is just a script you execute. With the guessing step, it's a conversation with the model. This loop is the book — everything else is content."

---

## Segment 3 — Set up your environment, live (4:30–7:00)

**[SAY]**
"Let's get you running. You need Python 3.10 or newer. Two install commands — that's it."

**[RUN: terminal]**
```
pip install torch numpy
pip install -e .
```

**[SAY]**
"`torch` is the deep-learning framework, `numpy` is numeric Python, and the editable install wires the `mingpt` package into your environment so the notebooks can import it.
If you want to follow the GPT-2 generation episode later, add `pip install transformers` — but you don't need it today."

**[RUN: Step 1 · cell 1 (environment check)]**

**[SAY]**
"Now open `learning_guide.ipynb` and run the very first cell. It diagnoses your setup: torch version, whether CUDA is available — don't worry if it says CPU, every model in this course is tiny — and whether all imports resolve.
Green checkmarks across the board? You're in business."

**[PAUSE]**

---

## Segment 4 — How to read the jargon (7:00–8:30)

**[SHOW: #glossary — the main-line pipeline figure: Text → Token → Embedding → Transformer → Logits → Softmax → {Training loop, Generation loop}]**

**[SAY]**
"Before episode two, one study skill. This field drowns you in jargon — logits, embeddings, causal masks. The glossary chapter has a trick: for every term ask three questions.
What does it take as *input*? What does it *output*? And where does it sit on *this line* — the main pipeline of GPT?
Look at this figure. Text becomes tokens, tokens become vectors, the Transformer scores every possible next word, softmax turns scores into probabilities. Training closes the loop by measuring error and updating weights; generation closes the loop by sampling and appending.
Every term you'll ever hear in this series lives in one of those boxes. If you can place it, you understand it."

---

## Segment 5 — Course map (8:30–9:30)

**[SHOW: sidebar / table of contents of the HTML]**

**[SAY]**
"Here's the route. Episodes 2 and 3 build first principles and tokenization. Episode 4 is the heart — attention. Episode 5 assembles the full GPT. Episode 7 is training, including the most instructive demo in the whole book: watching *exactly which positions* of a sequence get trained. Episode 8 is generation. Then scaling, evaluation, and how all of this connects to the coding agents you use every day.
Short episodes, one idea each, and we run code in every single one."

## Outro (9:30–10:00)

**[TRY]**
"Your homework: run the Step 1 environment cell, then read the glossary chapter's first table — just the first one.
Next episode: what a language model is *actually* doing when it predicts the next word. See you there."
