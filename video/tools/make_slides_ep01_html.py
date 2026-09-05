# -*- coding: utf-8 -*-
"""Ep 01 — How to Use This Book (EN): HTML slides for the video pipeline."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_slides_html import CSS, JS  # shared theme

OUT = os.path.join(HERE, "..", "build", "ep01", "html")
os.makedirs(OUT, exist_ok=True)

BRAND = "minGPT LEARNING BOOK · EPISODE 01"
FOOTER = "minGPT Learning Book · Ep 01 · How to Use This Book"


def open_s(sid):
    return f'<section class="slide" id="{sid}">'


def head(kicker, title, page, total=10):
    return (f'<div class="kicker">{kicker}</div><h1>{title}</h1><div class="rule"></div>'
            f'<div class="footer"><span>{FOOTER}</span><span>{page} / {total}</span></div>')


def s1_title():
    return f"""{open_s('s01')}
<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:34px;text-align:center">
  <div class="kicker" style="letter-spacing:6px">{BRAND}</div>
  <div style="font-size:96px;font-weight:700">How to Use This Book</div>
  <div style="font-size:46px;color:var(--blue)">Run the model while you read it</div>
  <div style="display:flex;gap:22px;margin-top:8px">
    <span class="chip">HTML book</span><span class="chip">Notebook</span><span class="chip">minGPT source</span>
  </div>
  <div style="font-size:28px;color:var(--mut);margin-top:14px">Episode 01 · the tour and the setup</div>
</div>
<div class="footer"><span>{FOOTER}</span><span></span></div>
</section>"""


def s2_statement():
    return f"""{open_s('s02')}
<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:44px;text-align:center">
  <div style="font-size:64px;font-weight:700;line-height:1.35;max-width:1500px">Every AI course shows you slides.<br>
    <span style="color:var(--green)">This one hands you a live model.</span></div>
  <div style="width:520px;height:2px;background:var(--edge)"></div>
  <div style="font-size:32px;color:var(--mut);max-width:1250px;line-height:1.7">
    Our vehicle is <b style="color:var(--ink)">minGPT</b> — Andrej Karpathy's famously small implementation of GPT:
    about <b style="color:var(--blue)">300 lines</b> of clean PyTorch. Small enough to read on a weekend,
    real enough that everything transfers to the big models.</div>
</div>
<div class="footer"><span>{FOOTER}</span><span>2 / 10</span></div>
</section>"""


def s3_layers():
    def card(num, title, sub, color, what):
        return f"""<div class="card" style="flex:1;padding:38px;border-color:{color}">
      <div style="font-size:24px;font-weight:700;color:{color};letter-spacing:2px">{num}</div>
      <div style="font-size:36px;font-weight:700;margin-top:10px">{title}</div>
      <div style="font-size:27px;color:{color};margin-top:14px;font-family:Consolas,monospace">{sub}</div>
      <div style="font-size:26px;color:var(--mut);margin-top:18px;line-height:1.6">{what}</div></div>"""
    arrow = '<div style="align-self:center;color:var(--mut);font-size:40px">&rarr;</div>'
    return f"""{open_s('s03')}{head('WHAT THIS BOOK IS', 'Three layers, one story', 3)}
<div class="content" style="align-items:center;gap:28px;padding-top:48px">
  {card('1', 'Understand', 'docs/learning_guide.html', 'var(--blue)', 'The HTML book: diagrams and intuition. You look at the data flow until it makes sense.')}
  {arrow}
  {card('2', 'Verify', 'learning_guide.ipynb', 'var(--green)', 'The notebook: every idea becomes code you actually execute, with real numbers.')}
  {arrow}
  {card('3', 'Confirm', 'mingpt/model.py', 'var(--purple)', 'The source: nothing hidden. If a diagram feels hand-wavy, the code is one click away.')}
</div></section>"""


def s4_loop():
    def card(n, t, d, color):
        return f"""<div class="card" style="flex:1;padding:34px 30px;border-color:{color};position:relative;z-index:1">
      <div style="font-size:54px;font-weight:700;color:{color}">{n}</div>
      <div style="font-size:33px;font-weight:700;margin-top:8px">{t}</div>
      <div style="font-size:25px;color:var(--mut);margin-top:12px;line-height:1.55">{d}</div></div>"""
    colors = ["var(--blue)", "var(--green)", "var(--purple)", "var(--orange)"]
    data = [("Guess", "predict the output before running: shape? number?", ),
            ("Run", "execute the cell for real"),
            ("Explain", "say what every line of output means"),
            ("Tweak", "change one parameter, watch what changes")]
    cards = "".join(card(i + 1, t, d, colors[i]) for i, (t, d) in enumerate(data))
    return f"""{open_s('s04')}{head('THE READING LOOP', 'The rule that makes it stick', 4)}
<div class="content" style="flex-direction:column;justify-content:center;gap:0">
  <div style="display:flex;gap:26px;position:relative">
    <div style="position:absolute;left:60px;right:60px;top:50%;height:2px;background:var(--edge)"></div>
    {cards}
  </div>
  <svg width="1740" height="110" viewBox="0 0 1740 110" style="margin-top:6px">
    <path d="M 1660 8 C 1660 54, 80 54, 86 16" fill="none" stroke="#6c9eff" stroke-width="2.5" stroke-dasharray="7 6"/>
    <polygon points="86,2 78,24 96,22" fill="#6c9eff"/>
    <text x="870" y="96" text-anchor="middle" fill="#9aa3b8" font-size="26" font-family="Segoe UI">…then guess again — skip the guessing step and a notebook is just a script</text>
  </svg>
</div></section>"""


def s5_terminal():
    return f"""{open_s('s05')}{head('SETUP · 2 COMMANDS', 'Get the environment running', 5)}
<div class="content" style="flex-direction:column;justify-content:center;gap:40px;align-items:center">
  <div class="card" style="width:1280px;padding:40px 48px;background:#0c101c;border-color:#26304a;font-family:Consolas,monospace">
    <div style="color:#5b6b8c;font-size:22px;margin-bottom:20px">Windows PowerShell · Python 3.10+ required</div>
    <div style="font-size:30px;line-height:2.1">
      <span style="color:#34d399">PS&gt;</span> pip install torch numpy<br>
      <span style="color:#34d399">PS&gt;</span> pip install -e .
    </div>
    <div style="margin-top:26px;font-size:24px;color:var(--mut);font-family:'Segoe UI'">
      <span style="color:#34d399">#</span> torch = the framework · numpy = numeric Python · <b>-e</b> = editable install,
      so notebooks can <span style="font-family:Consolas">import mingpt</span><br>
      <span style="color:#34d399">#</span> transformers only needed later, for the GPT-2 generation episode
    </div>
  </div>
  <div style="font-size:27px;color:var(--mut)">That's the whole install. No GPU required — every model in this course runs on CPU.</div>
</div></section>"""


def s6_check():
    def row(txt, ok=True, note=""):
        mark = '<span style="color:var(--green);font-size:30px">&#10003;</span>' if ok else '<span style="color:var(--orange);font-size:30px">!</span>'
        return f'<div style="display:flex;align-items:center;gap:18px;font-size:29px;padding:14px 0;border-bottom:1px solid var(--edge)">{mark}<span style="font-family:Consolas,monospace">{txt}</span><span style="color:var(--mut);font-size:24px">{note}</span></div>'
    return f"""{open_s('s06')}{head('SETUP · SMOKE TEST', 'Run the first notebook cell', 6)}
<div class="content" style="gap:52px;padding-top:44px;align-items:stretch">
  <div class="card" style="flex:1.25;padding:40px 48px">
    <div style="font-size:24px;color:var(--mut);margin-bottom:14px">learning_guide.ipynb · Step 1 · Imports and Environment Check</div>
    {row('torch 2.x · numpy 1.2x')}
    {row('CUDA available: False', True, '&larr; CPU is fine')}
    {row('from mingpt.model import GPT')}
    {row('from mingpt.trainer import Trainer')}
    {row('BPETokenizer ready')}
  </div>
  <div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:26px">
    <div style="font-size:31px;line-height:1.7">All green checkmarks?<br><b style="color:var(--green)">You're in business.</b></div>
    <div style="font-size:27px;color:var(--mut);line-height:1.7">If an import fails, the cell tells you which one — 99% of the time it's the missing <span style="font-family:Consolas">pip install -e .</span></div>
  </div>
</div></section>"""


def s7_jargon():
    qs = [("1", "Input?", "What does it take in?", "var(--blue)"),
          ("2", "Output?", "What does it produce?", "var(--green)"),
          ("3", "Where?", "Which step of the pipeline?", "var(--purple)")]
    cards = "".join(f"""<div class="card" style="flex:1;padding:40px;border-color:{c}">
      <div style="font-size:50px;font-weight:700;color:{c}">{n}</div>
      <div style="font-size:36px;font-weight:700;margin-top:8px">{q}</div>
      <div style="font-size:26px;color:var(--mut);margin-top:12px">{d}</div></div>""" for n, q, d, c in qs)
    return f"""{open_s('s07')}{head('STUDY SKILL', 'How to read the jargon', 7)}
<div class="content" style="flex-direction:column;justify-content:center;gap:44px">
  <div style="display:flex;gap:32px">{cards}</div>
  <div style="font-size:28px;color:var(--mut);text-align:center">Can you place a term? Then you understand it. &nbsp;·&nbsp; The glossary chapter has every term of this course.</div>
</div></section>"""


def s8_pipeline():
    def box(t, s, color):
        return f"""<div class="card" style="flex:1;padding:24px 10px;text-align:center;border-color:{color};position:relative;z-index:1">
      <div style="font-size:29px;font-weight:700;color:{color}">{t}</div>
      <div style="font-size:21px;color:var(--mut);margin-top:8px">{s}</div></div>"""
    names = [("Text", '"I like cats"', "var(--mut)"), ("Token", "integer IDs", "var(--purple)"),
             ("Embed", "vectors", "var(--green)"), ("Transformer", "attention+MLP", "var(--orange)"),
             ("Logits", "vocab scores", "var(--red)"), ("Softmax", "probabilities", "var(--yellow)")]
    flow = '<div style="color:var(--mut);font-size:30px;align-self:center">&rarr;</div>'.join(
        box(t, s, c) for t, s, c in names)
    return f"""{open_s('s08')}{head('THE MAIN LINE', 'Where every term lives', 8)}
<div class="content" style="flex-direction:column;justify-content:center;gap:52px">
  <div style="display:flex;gap:16px;position:relative">
    <div style="position:absolute;left:30px;right:30px;top:50%;height:2px;background:var(--edge)"></div>
    {flow}
  </div>
  <div style="display:flex;gap:44px">
    <div class="card" style="flex:1;padding:32px 40px;border-color:var(--red)">
      <div style="font-size:29px;font-weight:700;color:var(--red)">Training loop</div>
      <div style="font-size:26px;color:var(--mut);margin-top:10px;font-family:Consolas,monospace">loss \u2192 gradient \u2192 optimizer \u2192 repeat</div>
    </div>
    <div class="card" style="flex:1;padding:32px 40px;border-color:var(--green)">
      <div style="font-size:29px;font-weight:700;color:var(--green)">Generation loop</div>
      <div style="font-size:26px;color:var(--mut);margin-top:10px;font-family:Consolas,monospace">sample \u2192 append \u2192 repeat</div>
    </div>
  </div>
</div></section>"""


def s9_map():
    rows = [("02", "First principles & history"), ("03", "Tokens, embeddings & BPE"),
            ("04", "Self-attention \u2014 computed by hand", True), ("05", "Transformer block & the full GPT"),
            ("06", "Activations: GELU & softmax"), ("07", "Training & the loss mask", True),
            ("08", "Generation: temperature & top-k"), ("09+", "Scaling, evaluation, coding agents")]
    items = "".join(
        f"""<div style="display:flex;align-items:center;gap:20px;padding:13px 26px;border:1px solid var(--edge);border-radius:12px;background:var(--panel){';border-color:var(--blue)' if star else ''}">
        <span style="font-family:Consolas,monospace;font-size:26px;font-weight:700;color:{'var(--blue)' if star else 'var(--mut)'}">Ep {n}</span>
        <span style="font-size:26px">{t}</span></div>""" for n, t, star in [(r[0], r[1], len(r) > 2) for r in rows])
    return f"""{open_s('s09')}{head('COURSE MAP', 'The route ahead', 9)}
<div class="content" style="align-items:center">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;width:100%">{items}</div>
</div></section>"""


def s10_homework():
    return f"""{open_s('s10')}
<div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:48px;padding:0 40px">
  <div class="card" style="padding:44px 52px;background:#1e2a41;border-color:var(--blue)">
    <div style="font-size:28px;font-weight:700;color:var(--blue);letter-spacing:2px">HOMEWORK</div>
    <div style="margin-top:16px;font-size:30px;line-height:1.8">
      1&nbsp;·&nbsp;Run the Step 1 environment cell in <span style="font-family:Consolas">learning_guide.ipynb</span><br>
      2&nbsp;·&nbsp;Read the first table of the glossary chapter — that's all.
    </div>
  </div>
  <div style="text-align:center">
    <div style="font-size:30px;color:var(--mut)">Next episode</div>
    <div style="font-size:58px;font-weight:700;margin-top:10px">What language modeling <span style="color:var(--blue)">really</span> does</div>
  </div>
</div>
<div class="footer"><span>{FOOTER}</span><span>10 / 10</span></div>
</section>"""


NARR = [
    "Welcome to the minGPT learning book. This first episode is short and practical: how the course works, and how to get it running on your machine. By the end, you'll have a real GPT notebook alive on your screen — and a study method that makes it stick.",
    "Here is the idea in one sentence. Every AI course shows you slides; this one hands you a live model. Our vehicle is minGPT — Andrej Karpathy's famously small implementation of GPT. About three hundred lines of clean PyTorch. Small enough to read on a weekend, and real enough that everything you learn transfers to the big models.",
    "The book is three layers that say the same thing three ways. First, the HTML book: diagrams and intuition — where you understand. Second, the notebook: every idea becomes code you actually execute — where you verify. Third, the source: model dot py and trainer dot py — where you confirm nothing was hidden from you. If a diagram ever feels hand-wavy, the code is one click away.",
    "And here is the rule that makes it work: the reading loop. Before you run any cell — guess. Predict the shape, the number. Then run it. Then explain every line of output to yourself. Then tweak one parameter and watch what changes. Skip the guessing step, and a notebook is just a script you execute. Keep it, and the notebook becomes a conversation with the model. This loop is the whole method.",
    "Let's get you running. You need Python three point ten or newer, and two commands. Pip install torch numpy — the deep learning framework and numeric Python. Then pip install dash e dot — an editable install that wires the mingpt package into your environment so the notebooks can import it. That's the whole install. Transformers can wait until the GPT-2 generation episode, and no GPU is required.",
    "Now open learning guide dot i p y n b and run the very first cell. It checks your torch version, whether CUDA is available — don't worry if it says false; every model in this course is tiny enough for a laptop — and whether every import resolves. Green checkmarks across the board? You're in business. And if an import fails, the cell tells you which one — usually it's the editable install you missed.",
    "One study skill before we start. This field drowns you in jargon. The book's glossary chapter has a trick: for every term, ask three questions. What does it take as input? What does it output? And where does it sit in the pipeline? If you can place a term, you understand it. Memorizing definitions is optional.",
    "And here is the pipeline where every term lives. Text becomes tokens — integer IDs. Tokens become vectors — embeddings. The transformer scores every possible next word — logits. Softmax turns scores into probabilities. Then two loops close the system. Training: measure the loss, compute gradients, update weights, repeat. Generation: sample a token, append it, repeat. Every term you will ever hear in this series sits in one of these boxes.",
    "Here's the route. Episode two: first principles. Episode three: tokens and BPE. Episode four is the heart — attention, where you will compute it by hand with real numbers. Episode five assembles the full GPT. Episode six: activations. Episode seven: training — with the most instructive experiment in the book. Episode eight: generation. Then scaling, evaluation, and the bridge to coding agents.",
    "Your homework: run the Step one environment cell, and read the first table of the glossary chapter. That's all. Next episode we ask the only question that matters: what is a language model actually doing when it predicts the next word? See you there.",
]


if __name__ == "__main__":
    parts = ['<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
             f'<style>{CSS}</style></head><body>',
             s1_title(), s2_statement(), s3_layers(), s4_loop(), s5_terminal(),
             s6_check(), s7_jargon(), s8_pipeline(), s9_map(), s10_homework(),
             f'<script>{JS}</script></body></html>']
    path = os.path.join(OUT, "slides_ep01_en.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write("".join(parts))
    print("wrote", os.path.abspath(path))
