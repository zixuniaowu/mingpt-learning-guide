# -*- coding: utf-8 -*-
"""Generate HTML slide decks (en/zh/ja, 14 slides each) for Ep 04 — Self-Attention.
Slides use flex/grid layout (no manual coordinates -> no overlapping text).
Matrix numbers are really computed from the guide's toy-default Q/K/V."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "build", "ep04", "html")
os.makedirs(OUT, exist_ok=True)

TOKENS = ["I", "love", "cats", "!"]
Q = np.array([[1, 0, 0], [0, 1, 0], [1, 1, 0], [0, 0, 1]], dtype=float)
K = np.array([[1, 0, 0], [0, 1, 0], [1, 1, 0], [0, 0, 1]], dtype=float)
V = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [0.5, 0.5, 0]], dtype=float)
S = Q @ K.T
NEG = float("-inf")
M = np.where(np.triu(np.ones((4, 4)), 1) == 1, NEG, S)


def smax(row):
    fin = row[row != NEG]
    e = np.where(row == NEG, 0.0, np.exp(row - fin.max()))
    return e / e.sum()

A = np.array([smax(r) for r in M])
O = A @ V
A0 = np.array([smax(r) for r in np.where(np.triu(np.ones((4, 4)), 1) == 1, NEG, np.zeros((4, 3)) @ K.T)])


def fs(v):
    if v == NEG:
        return "\u2212\u221e"
    s = f"{v:+.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("+0", "-0", "+", "-") else s


def fu(v):
    if v == NEG:
        return "\u2212\u221e"
    return f"{v:.2f}".rstrip("0").rstrip(".")


def cell(v, cls, signed):
    return f'<div class="cell {cls}">{fs(v) if signed else fu(v)}</div>'


def grid(m, signed=True, hi_weights=False, rowhl=None, cols=None, col_labels=None):
    cols = cols or len(m[0])
    if col_labels is None:
        col_labels = TOKENS[:cols] if cols == 4 else [f"d{j}" for j in range(cols)]
    head = '<div class="corner"></div>' + "".join(f'<div class="cl">{t}</div>' for t in col_labels)
    rows = [head]
    for i in range(4):
        rows.append(f'<div class="rl">{TOKENS[i]}</div>')
        for j in range(cols):
            v = m[i][j]
            cls = ""
            if v == NEG:
                cls = "neg"
            elif hi_weights and v > 0.3:
                cls = "hi"
            if rowhl == i:
                cls += " rowhl"
            rows.append(cell(v, cls.strip(), signed))
    tpl = f"110px repeat({cols}, 96px)"
    return f'<div class="mtx" style="grid-template-columns:{tpl}">{"".join(rows)}</div>'


CSS = """
:root{--panel:#1a2233;--panel2:#171e30;--edge:#2e3345;--ink:#e8eaf0;--mut:#9aa3b8;
--blue:#6c9eff;--green:#34d399;--orange:#fb923c;--purple:#a78bfa;--red:#f87171;--yellow:#facc15}
*{box-sizing:border-box;margin:0;padding:0}
body{margin:0;background:#0d1120;color:var(--ink);
font-family:"Segoe UI","Meiryo UI","Yu Gothic UI",system-ui,sans-serif}
.slide{display:none;width:1920px;height:1080px;overflow:hidden;position:relative;
flex-direction:column;padding:60px 90px;
background:radial-gradient(1400px 900px at 75% -20%,#1c2745 0%,#141a2b 55%,#10141f 100%)}
.slide.on{display:flex}
.kicker{color:var(--blue);font-weight:700;font-size:26px;letter-spacing:3px}
h1{font-size:52px;margin-top:8px;font-weight:700}
.rule{height:2px;background:var(--edge);margin-top:18px}
.content{flex:1;min-height:0;display:flex}
.footer{position:absolute;left:90px;right:90px;bottom:28px;display:flex;
justify-content:space-between;color:var(--mut);font-size:22px}
.card{background:var(--panel);border:1px solid var(--edge);border-radius:16px}
.mtx{display:grid;gap:6px}
.cell{width:96px;height:96px;background:var(--panel2);border:1px solid var(--edge);border-radius:10px;
display:flex;align-items:center;justify-content:center;font-family:Consolas,monospace;font-size:29px;font-weight:700}
.cell.neg{background:#3a2a1f;color:var(--orange)}
.cell.hi{background:#14352a;color:var(--green)}
.cell.dim{background:#232c46;color:#bcc8e8}
.cell.rowhl{outline:3px solid var(--yellow);outline-offset:-3px}
.rl{height:96px;display:flex;align-items:center;justify-content:flex-end;padding-right:14px;color:var(--mut);font-size:24px}
.cl{width:96px;display:flex;align-items:flex-end;justify-content:center;padding-bottom:8px;color:var(--mut);font-size:24px}
.corner{width:110px}
.chip{display:inline-flex;align-items:center;padding:8px 24px;border-radius:999px;background:#1e3a5f;
border:2px solid var(--blue);color:#bfdbfe;font-weight:700;font-size:26px}
.tok{display:inline-flex;align-items:center;padding:6px 20px;border-radius:999px;background:#1e3a5f;
border:2px solid var(--blue);color:#bfdbfe;font-weight:700;font-size:24px}
"""

JS = """addEventListener('load',()=>{const id=location.hash.slice(1)||'s01';
document.querySelectorAll('.slide').forEach(el=>el.classList.toggle('on',el.id===id));});"""


def head(kicker, title, footer, page, total=14):
    f = f'<div class="footer"><span>{footer}</span><span>{page} / {total}</span></div>'
    if title is None:
        return f  # bare slide (title/end), no header
    return (f'<div class="kicker">{kicker}</div><h1>{title}</h1>'
            f'<div class="rule"></div>{f}')


def slide_open(sid):
    return f'<section class="slide" id="{sid}">'


# ---------------- per-slide builders ----------------

def b_title(L):
    return f"""{slide_open('s01')}
<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:34px;text-align:center">
  <div class="kicker" style="letter-spacing:6px">{L['brand']}</div>
  <div style="font-size:100px;font-weight:700">{L['big']}</div>
  <div style="font-size:48px;color:var(--blue)">{L['sub']}</div>
  <div style="display:flex;gap:22px;margin-top:8px">{''.join(f'<span class="chip">{c}</span>' for c in L['chips'])}</div>
  <div style="font-size:28px;color:var(--mut);margin-top:16px">{L['tagline']}</div>
</div>
<div class="footer"><span>{L['brand']}</span><span></span></div>
</section>"""


def b_problem(L):
    q = L['quote']
    return f"""{slide_open('s02')}{head(L['k2'], L['t2'], L['footer'], 2)}
<div class="content" style="flex-direction:column;align-items:center;justify-content:center;gap:48px;text-align:center">
  <div style="font-size:58px;line-height:1.5">{q[0]}<span style="color:var(--orange);font-weight:700">{q[1]}</span>{q[2]}</div>
  <div style="font-size:44px;font-weight:700;color:var(--orange)">{L['q']}</div>
  <div style="font-size:30px;color:var(--mut);max-width:1200px;line-height:1.6">{L['note']}</div>
</div></section>"""


def b_rnn(L):
    toks = "".join(f'<div style="padding:14px 30px;background:#2b241a;border:2px solid var(--orange);border-radius:12px;font-weight:700;font-size:26px;color:var(--orange)">{t}</div>'
                   + ('<div style="color:var(--mut);font-size:30px">&rarr;</div>' if t != TOKENS[-1] else '') for t in TOKENS)
    pts = [(90, 130), (280, 95), (470, 130), (660, 95)]
    n0 = L['a_nodes'][0]
    svg_lines = "".join(
        f'<line x1="{pts[i][0]}" y1="{pts[i][1]}" x2="{pts[j][0]}" y2="{pts[j][1]}" stroke="#34d399" stroke-width="1.6" stroke-opacity="0.55"/>'
        for i in range(4) for j in range(4) if i != j)
    dots = "".join(
        f'<circle cx="{p[0]}" cy="{p[1]}" r="34" fill="#14352a" stroke="#34d399" stroke-width="2"/>'
        f'<text x="{p[0]}" y="{p[1] + 9}" text-anchor="middle" fill="#e8eaf0" font-size="24" font-weight="700">{TOKENS[i]}</text>'
        for i, p in enumerate(pts))
    return f"""{slide_open('s03')}{head(L['k3'], L['t3'], L['footer'], 3)}
<div class="content" style="gap:44px;padding-top:44px">
  <div class="card" style="flex:1;padding:40px">
    <div style="font-size:28px;font-weight:700;color:var(--mut);margin-bottom:34px">{L['l3']}</div>
    <div style="display:flex;align-items:center;gap:16px;justify-content:center">{toks}</div>
    <div style="margin-top:40px;height:16px;border-radius:8px;background:linear-gradient(90deg,#3a2a1f,#241c12);border:1px solid var(--edge)"></div>
    <div style="margin-top:14px;font-size:24px;color:var(--mut)">{L['rnn1']}</div>
    <div style="margin-top:44px;font-size:27px;line-height:1.9;color:var(--mut)">{L['rnn2']}</div>
  </div>
  <div class="card" style="flex:1;padding:40px;background:#18211d;border-color:#1f4636">
    <div style="font-size:28px;font-weight:700;color:var(--green);margin-bottom:10px">{L['l3r']}</div>
    <svg width="750" height="260" viewBox="0 0 750 260">{svg_lines}{dots}</svg>
    <div style="font-size:27px;line-height:1.9;color:var(--mut)">{n0}</div>
    <div style="margin-top:12px;font-size:27px;color:var(--green)">{L['attn2']}</div>
  </div>
</div></section>"""


def b_qkv(L):
    cards = ""
    for (name, role, color, bg) in [("Q", L['qkv'][0], "var(--blue)", "#1e3a5f"),
                                    ("K", L['qkv'][1], "var(--purple)", "#2e225f"),
                                    ("V", L['qkv'][2], "var(--green)", "#14352a")]:
        cards += f"""<div class="card" style="flex:1;padding:38px">
      <span style="display:inline-block;padding:8px 26px;border-radius:12px;background:{bg};font-size:34px;font-weight:700;color:{color}">{name}</span>
      <div style="margin-top:26px;font-size:32px;line-height:1.55">{role}</div></div>"""
    return f"""{slide_open('s04')}{head(L['k4'], L['t4'], L['footer'], 4)}
<div class="content" style="flex-direction:column;gap:44px;padding-top:44px">
  <div style="display:flex;gap:40px">{cards}</div>
  <div class="card" style="padding:44px;background:#18211d;border-color:#1f4636;text-align:center">
    <div style="font-size:40px;font-weight:700;color:var(--green)">{L['takeaway']}</div>
    <div style="margin-top:14px;font-size:27px;color:var(--mut)">{L['takeaway2']}</div>
  </div>
</div></section>"""


def b_steps(L):
    colors = ["var(--blue)", "var(--purple)", "var(--orange)", "var(--green)", "var(--red)"]
    cards = "".join(
        f"""<div class="card" style="flex:1;padding:30px 28px;position:relative;z-index:1">
        <div style="font-size:52px;font-weight:700;color:{colors[i]}">{i + 1}</div>
        <div style="font-size:32px;font-weight:700;margin-top:6px">{s[0]}</div>
        <div style="font-size:29px;font-weight:700;color:{colors[i]};margin-top:10px;font-family:Consolas,monospace">{s[1]}</div>
        <div style="font-size:23px;color:var(--mut);margin-top:12px;line-height:1.5">{s[2]}</div></div>"""
        for i, s in enumerate(L['steps']))
    return f"""{slide_open('s05')}{head(L['k5'], L['t5'], L['footer'], 5)}
<div class="content" style="flex-direction:column;justify-content:center;gap:60px">
  <div style="display:flex;gap:26px;position:relative">
    <div style="position:absolute;left:0;right:0;top:50%;height:2px;background:var(--edge)"></div>
    {cards}
  </div>
  <div style="font-size:29px;color:var(--mut);text-align:center">{L['note5']}</div>
</div></section>"""


def b_playground(L):
    toks = "".join(f'<span class="tok">{i}: {t}</span>' for i, t in enumerate(TOKENS))
    subs = [L['qkv'][0], L['qkv'][1], L['qkv'][2]]
    mats = ""
    for (name, m, color) in [("Q", Q, "var(--blue)"), ("K", K, "var(--purple)"), ("V", V, "var(--green)")]:
        mats += f"""<div class="card" style="flex:1;padding:30px;display:flex;flex-direction:column;align-items:center;gap:22px">
      <div style="display:flex;align-items:baseline;gap:16px;align-self:flex-start">
        <span style="font-size:38px;font-weight:700;color:{color}">{name}</span>
        <span style="font-size:22px;color:var(--mut)">{subs[['Q', 'K', 'V'].index(name)]}</span></div>
      {grid(m.tolist(), signed=True, cols=3, col_labels=["d0", "d1", "d2"])}</div>"""
    return f"""{slide_open('s06')}{head(L['k6'], L['t6'], L['footer'], 6)}
<div class="content" style="flex-direction:column;gap:36px;padding-top:36px">
  <div style="display:flex;gap:18px;align-items:center">{toks}<span style="color:var(--mut);font-size:25px">&larr; {L['toy_note']}</span></div>
  <div style="display:flex;gap:38px">{mats}</div>
  <div style="font-size:26px;color:var(--mut)">{L['note6']}</div>
</div></section>"""


def b_matrix_slide(sid, page, L, key, m, signed, hi, rowhl, right_title_color, caption):
    return f"""{slide_open(sid)}{head(L[f'k{page}'], L[f't{page}'], L['footer'], page)}
<div class="content" style="gap:56px;padding-top:44px;align-items:stretch">
  <div class="card" style="width:960px;padding:44px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px">
    {grid(m, signed=signed, hi_weights=hi, rowhl=rowhl)}
    <div style="font-size:23px;color:var(--mut)">{caption}</div>
  </div>
  <div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:34px">
    <div style="font-size:40px;font-weight:700;color:{right_title_color};font-family:Consolas,monospace">{L[key + '_f']}</div>
    <div style="font-size:29px;line-height:1.75">{L[key + '_n']}</div>
  </div>
</div></section>"""


def b_zero(L):
    return f"""{slide_open('s11')}{head(L['k11'], L['t11'], L['footer'], 11)}
<div class="content" style="flex-direction:column;gap:40px;padding-top:40px;align-items:center">
  <div style="display:flex;gap:56px">
    <div class="card" style="padding:34px 44px;display:flex;flex-direction:column;align-items:center;gap:20px;border-color:#1f4636">
      <div style="font-size:27px;font-weight:700;color:var(--green)">{L['with_q']}</div>
      {grid(A, signed=False, hi_weights=True)}
    </div>
    <div class="card" style="padding:34px 44px;display:flex;flex-direction:column;align-items:center;gap:20px">
      <div style="font-size:27px;font-weight:700;color:var(--mut)">Q = 0</div>
      {grid_dim(A0)}
    </div>
  </div>
  <div style="font-size:29px;color:var(--mut);max-width:1500px;text-align:center;line-height:1.7">{L['note11']}</div>
</div></section>"""


def grid_dim(m):
    head = '<div class="corner"></div>' + "".join(f'<div class="cl">{t}</div>' for t in TOKENS)
    rows = [head]
    for i in range(4):
        rows.append(f'<div class="rl">{TOKENS[i]}</div>')
        for j in range(4):
            rows.append(f'<div class="cell dim">{fu(m[i][j])}</div>')
    return f'<div class="mtx" style="grid-template-columns:110px repeat(4, 96px)">{"".join(rows)}</div>'


def b_heads(L):
    colors = ["var(--blue)", "var(--purple)", "var(--green)", "var(--orange)"]
    heads = "".join(
        f"""<div class="card" style="width:540px;padding:22px 30px;display:flex;align-items:center;gap:24px;border-color:{colors[i]}">
        <span style="font-size:28px;font-weight:700;color:{colors[i]}">{L['heads'][i][0]}</span>
        <span style="font-size:25px;color:var(--mut)">{L['heads'][i][1]}</span></div>"""
        for i in range(4))
    ys = [70, 190, 310, 430]
    lines = "".join(f'<line x1="0" y1="{y}" x2="220" y2="250" stroke="#9aa3b8" stroke-width="2" stroke-opacity="0.7"/>' for y in ys)
    return f"""{slide_open('s12')}{head(L['k12'], L['t12'], L['footer'], 12)}
<div class="content" style="gap:0;padding-top:40px;align-items:center">
  <div style="display:flex;flex-direction:column;gap:44px">{heads}</div>
  <svg width="220" height="500" viewBox="0 0 220 500" style="margin:0 8px">{lines}</svg>
  <div style="display:flex;align-items:center;gap:34px">
    <div class="card" style="padding:40px 46px;font-size:33px;font-weight:700">concat</div>
    <div style="color:var(--mut);font-size:36px">&rarr;</div>
    <div class="card" style="padding:40px 46px;font-size:33px;font-weight:700">linear</div>
  </div>
</div>
<div style="position:absolute;left:90px;bottom:90px;font-size:27px;color:var(--mut)">{L['note12']}</div>
</section>"""


def b_recap(L):
    items = "".join(f'<li style="margin:18px 0;font-size:33px;line-height:1.55">{it}</li>' for it in L['recap'])
    return f"""{slide_open('s13')}{head(L['k13'], L['t13'], L['footer'], 13)}
<div class="content" style="flex-direction:column;gap:48px;padding-top:40px">
  <ul style="list-style:none;padding:0">{items}</ul>
  <div class="card" style="padding:40px 48px;background:#1e2a41;border-color:var(--blue)">
    <div style="font-size:28px;font-weight:700;color:var(--blue);letter-spacing:2px">{L['hw_t']}</div>
    <div style="margin-top:14px;font-size:29px;line-height:1.65">{L['hw_n']}</div>
  </div>
</div></section>"""


def b_end(L):
    return f"""{slide_open('s14')}
<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:30px;text-align:center">
  <div style="font-size:34px;color:var(--mut)">{L['next']}</div>
  <div style="font-size:72px;font-weight:700">{L['next_t']}</div>
  <div style="font-size:34px;color:var(--blue)">{L['next_s']}</div>
  <div style="width:520px;height:2px;background:var(--edge);margin:20px 0"></div>
  <div style="font-size:26px;color:var(--mut)">{L['read']}</div>
  <div style="font-size:26px;color:var(--mut)">{L['run']}</div>
</div>
<div class="footer"><span>minGPT Learning Book · github.com/zixuniaowu/mingpt-learning-guide</span><span></span></div>
</section>"""


# ---------------- localized content ----------------
EN = {
    "voice": "en-US-AndrewNeural",
    "lang": "en",
    "brand": "minGPT LEARNING BOOK · EPISODE 04",
    "footer": "minGPT Learning Book · Ep 04 · Self-Attention",
    "big": "Self-Attention", "sub": "The Core of the Transformer",
    "chips": ["Q·K\u1d40", "mask", "softmax", "× V"],
    "tagline": "computed for real — the same numbers as the book's interactive toy",
    "k2": "THE PROBLEM", "t2": "Every word needs to know which words matter",
    "quote": ["\u201cThe animal didn\u2019t cross the street because ", "it", " was too tired.\u201d"],
    "q": "what does \u201cit\u201d refer to?",
    "note": "You resolved that instantly. A model needs a mechanism that lets every position look at every other position and decide what matters. That mechanism is attention.",
    "k3": "WHY ATTENTION AT ALL", "t3": "From a running summary to direct access",
    "l3": "RNN: squeeze everything into one state", "l3r": "Attention: everyone sees everyone",
    "rnn1": "one compressed hidden state \u2014 details die along the way",
    "rnn2": "word 1 reaches word 4 through 3 sequential compressions.<br>GPUs wait; long-range signals vanish.",
    "a_nodes": ["path length between any two words: 1 step"],
    "attn2": "\u201cAttention Is All You Need\u201d \u00b7 2017",
    "k4": "THE THREE ROLES", "t4": "Q asks, K advertises, V delivers",
    "qkv": ["What am I looking for?", "What do I advertise about myself?", "What do I hand over if you attend to me?"],
    "takeaway": "Attention = a soft, differentiable dictionary lookup",
    "takeaway2": "relevance = dot product of Q and K · result = weighted average of V",
    "k5": "THE WHOLE COMPUTATION", "t5": "Five steps \u2014 all of them real math",
    "steps": [["Scores", "S = Q·K\u1d40", "relevance per pair"], ["Scale", "\u00f7 \u221ad\u2096", "keep softmax stable"],
              ["Mask", "future = \u2212\u221e", "no peeking right"], ["Softmax", "rows \u2192 weights", "each row sums to 1"],
              ["Blend", "out = A·V", "mix what you may see"]],
    "note5": "Let's run all five with real numbers \u2014 the same defaults as the book's interactive toy.",
    "k6": "THE PLAYGROUND", "t6": "4 tokens \u00b7 3 dims \u00b7 the book's toy defaults",
    "toy_note": "exactly the interactive toy in the guide",
    "note6": "Every matrix in the guide's toy is editable \u2014 change a number and all five steps recompute.",
    "k7": "STEP 1 · SCORES", "t7": "S = Q·K\u1d40 \u2014 relevance of every pair",
    "s7_f": "S[i][j] = dot(Q\u1d62, K\u2c7c)",
    "s7_n": "Row 2 (cats) scores highest against itself (2) \u2014 and scores 1 against both \u201cI\u201d and \u201clove\u201d. Bigger dot product = more relevant. That's all a score is.",
    "cap74": "rows: query · cols: key",
    "k8": "STEP 2 · CAUSAL MASK", "t8": "No peeking at the future",
    "s8_f": "future positions \u2192 \u2212\u221e",
    "s8_n": "A GPT is trained to predict the NEXT token \u2014 looking right would be copying the answer key.\n\nThe math still runs for those cells; the result is discarded before softmax (FlashAttention exists to skip exactly this waste).",
    "k9": "STEP 3 · SOFTMAX", "t9": "Scores \u2192 attention weights (rows sum to 1)",
    "s9_f": "row 0 = [1, 0, 0, 0]",
    "s9_n": "Position 0 may not look right \u2014 so it attends 100% to itself.\n\nEach row becomes a probability distribution: \u2212\u221e entries become exactly 0, the rest normalize to sum 1.",
    "k10": "STEP 4 · WEIGHTED BLEND", "t10": "output = A·V \u2014 mix what you may see",
    "s10_f": "output[i] = \u03a3\u2c7c A[i][j] · V[j]",
    "s10_n": "\u201ccats\u201d attends most to itself, plus \u201cI\u201d and \u201clove\u201d \u2014 its new vector is literally that mixture.\n\nAttention doesn't change the tokens. It changes what each position CONTAINS.",
    "k11": "EXPERIMENT", "t11": "Zero out the queries \u2192 attention goes uniform",
    "with_q": "with real queries",
    "note11": "All scores become 0 \u2192 every row is uniform over visible positions. The query is what breaks the tie: no query preference, no attention pattern.",
    "k12": "MULTI-HEAD", "t12": "One pattern is one opinion \u2014 run several",
    "heads": [["head 1", "grammar"], ["head 2", "\u201cit\u201d \u2192 \u201canimal\u201d"], ["head 3", "recency"], ["head 4", "\u2026"]],
    "note12": "gpt-nano: 4 heads \u00d7 12-dim slices of the 48-dim embedding \u2014 small parallel experts.",
    "k13": "RECAP", "t13": "Attention in one breath",
    "recap": ["Query dots Key \u2192 relevance score for every pair.",
              "Softmax turns each row into a distribution that sums to 1.",
              "Weighted sum of Values = each position's new representation.",
              "Causal mask keeps the future invisible (\u2212\u221e before softmax).",
              "Multi-head = parallel specialists, concatenated back together."],
    "hw_t": "HOMEWORK",
    "hw_n": "In learning_guide.ipynb \u2192 Step 4.5: replace the identity value-projection Wv with a random matrix. Run it. Explain in one sentence what changed in the output, and why.",
    "next": "Next episode", "next_t": "The Transformer Block",
    "next_s": "residuals \u00b7 LayerNorm \u00b7 the MLP \u00b7 a complete GPT",
    "read": "Read along: docs/learning_guide.html \u00b7 chapter \u201cattention\u201d",
    "run": "Run along: learning_guide.ipynb \u00b7 Step 4.5",
    "narr": [
        "Welcome to episode four of the minGPT learning book — the most important one in the series. Today we open the engine of every modern language model: self-attention. By the end, you will compute it by hand, with real numbers — the same numbers you'll find in the book's interactive toy and in the course notebook.",
        "Here is the problem attention solves. Read this sentence: the animal didn't cross the street, because it was too tired. What does it refer to? You resolved that instantly. A model needs a mechanism that lets every word look at every other word, and decide which ones matter. That mechanism is attention.",
        "Before twenty seventeen, models read through a running summary: recurrent networks squeezed everything seen so far into one hidden state, and details died along the way. Attention throws the running summary away. Every word sees every other word directly — the path between any two words is exactly one step. That is the revolution of: attention is all you need.",
        "Attention gives every position three vectors. Query: what am I looking for? Key: what do I advertise about myself? Value: what do I actually hand over if someone attends to me? Relevance is a dot product between queries and keys — a big score means we match. Then each position takes a weighted average of the values. In one phrase: attention is a soft, differentiable dictionary lookup.",
        "Here is the whole computation in five steps. Multiply queries by keys transposed: a relevance score for every pair. Scale the scores down, so softmax stays stable. Apply the causal mask, so nobody sees the future. Softmax each row into weights that sum to one. Finally, blend the values with those weights. Don't take my word for it — let's run all five, with real numbers.",
        "Our playground: four tokens — I, love, cats, and an exclamation mark. The exact sequence used by the book's interactive toy. Each token gets a three-dimensional query, key and value vector. These are the toy's default matrices. Every number you are about to see is computed from them.",
        "Step one: scores. S equals Q times K transpose — a four by four table. Row i is what token i is looking for; column j is the label token j offers. Their dot product says how relevant j is to i. Look at row two: cats scores two against itself, and one against both I and love. Bigger is more relevant. That is all a score is.",
        "Step two: the causal mask. A language model is trained to predict the next token, so looking right would be copying the answer key. We forbid it brutally: every position above the diagonal becomes minus infinity. And note — the computation still happens there. The result is simply thrown away before softmax.",
        "Step three: softmax, row by row. Every row becomes a probability distribution that sums to exactly one. Minus infinities become exactly zero. Now look at row zero: one, zero, zero, zero. Position zero isn't allowed to look right — so it attends one hundred percent to itself. No freedom at all.",
        "Step four: the payoff. Each position's new representation is the weighted blend of the value vectors it is allowed to see. Cats attends mostly to itself — plus I and love — and its output vector is literally that mixture. Attention doesn't change the tokens. It changes what each position contains.",
        "One experiment worth ten formulas: what if the queries were all zero? Every score becomes zero, and every position treats all visible tokens equally — uniform. This is the reflex I want you to build: the query is what breaks the tie. No query preference — no attention pattern. Try it yourself in the notebook, step four point five.",
        "One attention pattern is one opinion. Real models run many in parallel — multi-head attention. Each head gets a small slice of the dimensions and specializes: one head tracks grammar, another tracks what it refers to, another just tracks recency. gpt nano runs four heads of twelve dimensions each. Small experts, concatenated back together.",
        "Let's recap attention in one breath. Query dots key gives relevance. Softmax turns relevance into a distribution. Weighting values gives every position its new representation. The causal mask keeps the future invisible. Your homework: in the notebook, step four point five, replace the identity value projection with a random matrix, run it, and explain in one sentence what changed — and why.",
        "Next episode we wrap attention in residuals, layer norm and an M L P — the Transformer block — and stack it into a complete GPT. Everything from today is in the book's attention chapter, with a toy you can edit right now. See you in episode five.",
    ],
}

ZH = {
    "voice": "zh-CN-YunxiNeural",
    "lang": "zh-CN",
    "brand": "minGPT 学习书 · 第 4 集",
    "footer": "minGPT 学习书 · 第 4 集 · 自注意力",
    "big": "自注意力", "sub": "Transformer 的核心",
    "chips": ["Q·K\u1d40", "掩码", "softmax", "× V"],
    "tagline": "全部真实计算 —— 与书中交互玩具的数字完全一致",
    "k2": "问题所在", "t2": "每个词都需要知道：哪些词与自己有关",
    "quote": ["\u201cThe animal didn\u2019t cross the street because ", "it", " was too tired.\u201d"],
    "q": "\u201cit\u201d 指的是什么？",
    "note": "你瞬间就完成了判断。而模型需要一种机制，让每个位置都能环顾其他位置、判断谁才重要。这个机制就是注意力。",
    "k3": "为什么需要注意力", "t3": "从\u201c滚动摘要\u201d到\u201c直接查看\u201d",
    "l3": "RNN：把一切压进一个状态", "l3r": "Attention：人人都能看到所有人",
    "rnn1": "只有一个压缩的隐藏状态 —— 细节在路上不断丢失",
    "rnn2": "第 1 个词要经过 3 次顺序压缩才能影响到第 4 个词。<br>GPU 在等待，远距离信号在消失。",
    "a_nodes": ["任意两词之间的路径长度：1 步"],
    "attn2": "《Attention Is All You Need》· 2017",
    "k4": "三个角色", "t4": "Q 提问，K 挂标签，V 交货",
    "qkv": ["我在找什么？", "我对外贴的标签是什么？", "如果别人关注我，我真正交出去的是什么？"],
    "takeaway": "注意力 = 一次软性的、可求导的字典查询",
    "takeaway2": "相关度 = Q 和 K 的点积 · 结果 = V 的加权平均",
    "k5": "完整计算", "t5": "五步 —— 全是真实数学",
    "steps": [["打分", "S = Q·K\u1d40", "每一对的相关度"], ["缩放", "\u00f7 \u221ad\u2096", "让 softmax 保持稳定"],
              ["掩码", "未来 = \u2212\u221e", "不许偷看右边"], ["Softmax", "每行 \u2192 权重", "每行加和为 1"],
              ["加权混合", "out = A·V", "混合被允许看到的信息"]],
    "note5": "接下来用真实数字跑完全部五步 —— 和书中交互玩具的默认值完全相同。",
    "k6": "实验台", "t6": "4 个 token · 3 维 · 书中玩具的默认值",
    "toy_note": "与书中交互玩具完全相同",
    "note6": "书里玩具的每个矩阵都可以编辑 —— 改任何一个数字，五步全部实时重算。",
    "k7": "第 1 步 · 打分", "t7": "S = Q·K\u1d40 —— 每一对的相关度",
    "s7_f": "S[i][j] = dot(Q\u1d62, K\u2c7c)",
    "s7_n": "第 2 行（cats）对自己打分最高（2），对 \u201cI\u201d 和 \u201clove\u201d 各打 1 分。点积越大 = 越相关。分数就是这么朴素。",
    "cap74": "行：query · 列：key",
    "k8": "第 2 步 · 因果掩码", "t8": "不许偷看未来",
    "s8_f": "未来位置 \u2192 \u2212\u221e",
    "s8_n": "GPT 的训练目标是预测下一个 token —— 往右看等于抄答案。\n\n那些位置的计算照常进行，只是结果在 softmax 之前被丢弃（FlashAttention 就是为省掉这种浪费而生的）。",
    "k9": "第 3 步 · Softmax", "t9": "分数 \u2192 注意力权重（每行加和为 1）",
    "s9_f": "第 0 行 = [1, 0, 0, 0]",
    "s9_n": "位置 0 不许往右看 —— 所以它 100% 关注自己，毫无自由。\n\n每行变成一个概率分布：\u2212\u221e 的位置精确等于 0，其余归一化到和为 1。",
    "k10": "第 4 步 · 加权混合", "t10": "output = A·V —— 混合被允许看到的",
    "s10_f": "output[i] = \u03a3\u2c7c A[i][j] · V[j]",
    "s10_n": "cats 最关注自己，其次是 \u201cI\u201d 和 \u201clove\u201d —— 它的输出向量就是这个混合物。\n\n注意力没有改变 token，改变的是每个位置\u201c装着什么\u201d。",
    "k11": "实验", "t11": "把 Query 清零 \u2192 注意力变成均匀分布",
    "with_q": "真实 Query",
    "note11": "所有分数变成 0 \u2192 每行在可见位置上均匀分布。Query 是打破平局的那只手：没有偏好，就没有注意力模式。",
    "k12": "多头", "t12": "一种模式就是一种观点 —— 多跑几份",
    "heads": [["头 1", "语法"], ["头 2", "\u201cit\u201d \u2192 \u201canimal\u201d"], ["头 3", "近因"], ["头 4", "\u2026"]],
    "note12": "gpt-nano：4 个头 × 48 维中的 12 维切片 —— 并行的小专家。",
    "k13": "复述", "t13": "一口气说完注意力",
    "recap": ["Query 点 Key \u2192 每一对的相关度。",
              "Softmax 把每行变成加和为 1 的分布。",
              "对 Value 加权求和 = 每个位置的新表示。",
              "因果掩码把未来挡在门外（softmax 前置 \u2212\u221e）。",
              "多头 = 并行的小专家，最后拼接回一起。"],
    "hw_t": "作业",
    "hw_n": "在 learning_guide.ipynb \u2192 Step 4.5：把单位矩阵 Wv 换成随机矩阵，运行，然后用一句话解释输出变了什么、为什么。",
    "next": "下一集", "next_t": "Transformer Block 与完整的 GPT",
    "next_s": "残差 · LayerNorm · MLP · 完整 GPT",
    "read": "配合阅读：docs/learning_guide.html · attention 章节",
    "run": "配合运行：learning_guide.ipynb · Step 4.5",
    "narr": [
        "欢迎来到 minGPT 学习书第四集，整个系列最重要的一集。今天我们打开所有现代语言模型的引擎：自注意力。学完这一集，你能用真实数字亲手算一遍注意力，和书里交互玩具、练习 Notebook 里的数字完全一致。",
        "先看注意力解决的问题。读这句话：The animal didn't cross the street because it was too tired。it 指的是谁？你瞬间就完成了判断。而模型需要一种机制，让每个词都能环顾其他词，判断谁才重要。这个机制就是注意力。",
        "2017 年之前，模型靠滚动摘要读句子：循环网络把读过的所有内容压进一个隐藏状态，细节在途中不断丢失。注意力直接扔掉摘要：每个词都能直接看到其他所有词，任意两个词之间的路径长度是一步。这就是 Attention Is All You Need 带来的革命。",
        "注意力给每个位置三个向量。Query，我在找什么？Key，我对外贴的标签是什么？Value，如果别人关注我，我真正交出去的是什么？相关度就是 Query 和 Key 的点积，分数越大越匹配。然后每个位置对 Value 做加权平均。一句话：注意力就是一次软性的、可求导的字典查询。",
        "整个计算就五步。Query 乘 Key 的转置，得到每一对的分数；除以根号 dk 缩放，让 softmax 保持稳定；打上因果掩码，谁都不许看未来；对每一行做 softmax，变成和为一的权重；最后用权重混合 Value。别光听我说，我们用真实数字把五步全跑一遍。",
        "我们的实验台：四个 token，I、love、cats 和感叹号。和书里交互玩具完全相同的序列。每个 token 都有一组三维的 Q、K、V 向量，就是眼前这三张矩阵，玩具的默认值。接下来你看到的每个数字都由它们算出。",
        "第一步，打分。S 等于 Q 乘 K 的转置，一张四乘四的表。第 i 行是 token i 在找什么，第 j 列是 token j 提供的标签，点积说 j 对 i 有多相关。看第二行，cats 对自己是二，对 I 和 love 各是一。分数越大越相关，分数就是这么朴素。",
        "第二步，因果掩码。语言模型的训练目标是预测下一个 token，往右看等于抄答案。所以我们下狠手：对角线以上的位置全部变成负无穷。注意，那些位置的计算照常进行，只是结果在 softmax 之前被丢弃。FlashAttention 就是为省掉这种浪费而生的。",
        "第三步，softmax，逐行进行。每一行变成一个恰好加和为一的概率分布，负无穷的位置精确等于零。看第零行，一、零、零、零。位置零不许往右看，所以它百分之百关注自己，毫无自由可言。",
        "第四步，收获。每个位置的新表示，是它被允许看到的 Value 向量的加权混合。cats 最关注自己，其次是 I 和 love，它的输出向量就是这个混合物。注意力没有改变 token，它改变的是每个位置装着什么。",
        "一个实验胜过十个公式：如果 Query 全是零会怎样？所有分数变成零，每个位置对所有可见 token 一视同仁，均匀分布。我想让你建立的反射是：Query 是打破平局的那只手。没有偏好，就没有注意力模式。去 Notebook 的 Step 4.5 里亲手试试。",
        "一种注意力模式就是一种观点。真实模型会并行跑很多份，这就是多头注意力。每个头分到一小片维度，各自专精：有的头盯语法，有的头负责 it 指谁，有的头只看距离。gpt-nano 有四个头，每个头十二维。小专家们最后拼接回一起。",
        "一口气复述注意力：Query 点 Key 得到相关度；softmax 把相关度变成分布；对 Value 加权求和得到每个位置的新表示；因果掩码把未来挡在门外。作业：在 Notebook 的 Step 4.5 里，把单位矩阵 Wv 换成随机矩阵，跑一遍，用一句话解释输出变了什么、为什么。",
        "下一集，我们给注意力套上残差、LayerNorm 和 MLP，也就是 Transformer Block，并堆叠成完整的 GPT。今天的内容都在书的 attention 章节，玩具现在就能改。第五集见。",
    ],
}

JA = {
    "voice": "ja-JP-KeitaNeural",
    "lang": "ja",
    "brand": "minGPT 学習ブック · 第4話",
    "footer": "minGPT 学習ブック · 第4話 · セルフアテンション",
    "big": "セルフアテンション", "sub": "Transformer の核心",
    "chips": ["Q·K\u1d40", "マスク", "softmax", "× V"],
    "tagline": "すべて実計算 —— ブックのインタラクティブおもちゃと同じ数字",
    "k2": "問題", "t2": "すべての単語は「どの単語が自分に関係するか」を知る必要がある",
    "quote": ["\u201cThe animal didn\u2019t cross the street because ", "it", " was too tired.\u201d"],
    "q": "「it」は何を指すでしょう？",
    "note": "あなたは一瞬で答えました。モデルには、各位置が他のすべての位置を見て、どれが重要かを判断する仕組みが必要です。それがアテンションです。",
    "k3": "なぜアテンションか", "t3": "「要約しながら読む」から「直接見る」へ",
    "l3": "RNN：すべてを1つの状態に圧縮", "l3r": "Attention：全員が全員を見られる",
    "rnn1": "隠れ状態は1つだけ —— 詳細は途中で失われる",
    "rnn2": "単語1が単語4に届くまでに3回の圧縮。<br>GPUは待たされ、遠い信号は消える。",
    "a_nodes": ["任意の2語の間の経路長：1ステップ"],
    "attn2": "「Attention Is All You Need」· 2017",
    "k4": "3つの役割", "t4": "Q が問い、K が名乗り、V が渡す",
    "qkv": ["自分は何を探している？", "自分はどんなラベルを名乗る？", "注目されたら実際に何を渡す？"],
    "takeaway": "アテンション = 柔らかくて微分可能な辞書引き",
    "takeaway2": "関連度 = Q と K のドット積 · 結果 = V の重み付き平均",
    "k5": "計算の全体像", "t5": "5ステップ —— すべて本物の数学",
    "steps": [["スコア", "S = Q·K\u1d40", "ペアごとの関連度"], ["スケール", "\u00f7 \u221ad\u2096", "softmax を安定させる"],
              ["マスク", "未来 = \u2212\u221e", "右を覗き見禁止"], ["Softmax", "行 \u2192 重み", "各行の和は1"],
              ["ブレンド", "out = A·V", "見てよい情報を混ぜる"]],
    "note5": "この5ステップを実際の数字で全部走らせましょう —— ブックのおもちゃと同じ既定値です。",
    "k6": "実験台", "t6": "4トークン · 3次元 · ブックのおもちゃの既定値",
    "toy_note": "ブックのおもちゃと完全に同じ",
    "note6": "おもちゃの行列はすべて編集できます —— 数値を1つ変えると5ステップ全部が即再計算されます。",
    "k7": "ステップ1 · スコア", "t7": "S = Q·K\u1d40 —— すべてのペアの関連度",
    "s7_f": "S[i][j] = dot(Q\u1d62, K\u2c7c)",
    "s7_n": "第2行（cats）は自分自身に最高スコア（2）、\u201cI\u201d と \u201clove\u201d にはそれぞれ1。ドット積が大きいほど関連が強い。スコアとはそういうものです。",
    "cap74": "行：query · 列：key",
    "k8": "ステップ2 · 因果マスク", "t8": "未来は覗き見禁止",
    "s8_f": "未来の位置 \u2192 \u2212\u221e",
    "s8_n": "GPT は次のトークンを予測して訓練されます —— 右を見るのは答えのカンニングです。\n\nそこでも計算は実行され、結果は softmax の前に捨てられます（FlashAttention はまさにこの無駄を省くためのもの）。",
    "k9": "ステップ3 · Softmax", "t9": "スコア \u2192 注意重み（行和 = 1）",
    "s9_f": "行0 = [1, 0, 0, 0]",
    "s9_n": "位置0は右を見られない —— だから自分に100%注目します。\n\n各行は確率分布になります：\u2212\u221e は正確に0、残りは和が1に正規化。",
    "k10": "ステップ4 · 重み付きブレンド", "t10": "output = A·V —— 見てよいものを混ぜる",
    "s10_f": "output[i] = \u03a3\u2c7c A[i][j] · V[j]",
    "s10_n": "cats は自分自身に最も注目し、次に \u201cI\u201d と \u201clove\u201d —— 出力ベクトルは文字通りその混合物です。\n\nアテンションはトークンを変えません。各位置が「何を含むか」を変えます。",
    "k11": "実験", "t11": "Query をゼロに \u2192 アテンションは一様分布に",
    "with_q": "本物の Query",
    "note11": "スコアはすべて0になり、各行は見える位置の上で一様に分布します。Query は引き分けを破る手です：好みがなければ、アテンションのパターンも生まれません。",
    "k12": "マルチヘッド", "t12": "1つのパターンは1つの意見 —— 複数走らせる",
    "heads": [["ヘッド1", "文法"], ["ヘッド2", "\u201cit\u201d \u2192 \u201canimal\u201d"], ["ヘッド3", "近さ"], ["ヘッド4", "\u2026"]],
    "note12": "gpt-nano：4ヘッド × 48次元のうちの12次元 —— 並列の小さな専門家。",
    "k13": "復習", "t13": "アテンションを一言で",
    "recap": ["Query と Key のドット積 \u2192 すべてのペアの関連度。",
              "Softmax が各行を和が1の分布に変えます。",
              "Value の重み付き和 = 各位置の新しい表現。",
              "因果マスクが未来を遮る（softmax 前に \u2212\u221e）。",
              "マルチヘッド = 並列の専門家、最後に連結。"],
    "hw_t": "宿題",
    "hw_n": "learning_guide.ipynb \u2192 Step 4.5：単位行列 Wv をランダム行列に替えて実行し、出力がどう変わったかを一文で説明してください。",
    "next": "次のエピソード", "next_t": "Transformer ブロックと完全な GPT",
    "next_s": "残差 · LayerNorm · MLP · 完全な GPT",
    "read": "読む：docs/learning_guide.html · attention 章",
    "run": "走る：learning_guide.ipynb · Step 4.5",
    "narr": [
        "minGPT学習ブックの第4エピソードへようこそ。シリーズ全体で最も重要な回です。今日はすべての現代言語モデルのエンジン、セルフアテンションを開けます。この回を終えるころには、実際の数字でアテンションを手計算できるようになります。ブックのおもちゃやノートブックと、まったく同じ数字です。",
        "アテンションが解決する問題を見ましょう。この文を読んでください。The animal didn't cross the street because it was too tired.「it」は何を指すでしょう？あなたは一瞬で答えました。モデルには、各単語が他のすべての単語を見て、どれが重要かを判断する仕組みが必要です。それがアテンションです。",
        "2017年以前、モデルは要約しながら読む方式でした。リカレントネットワークは読んだ内容をすべて1つの隠れ状態に圧縮し、詳細は途中で失われます。アテンションはその要約を捨てました。すべての単語が他のすべての単語を直接見られる。任意の2語の間の経路長は、ちょうど1ステップです。これが Attention Is All You Need の革命です。",
        "アテンションは各位置に3つのベクトルを与えます。Query、何を探している？Key、自分はどんなラベルを名乗る？Value、注目されたら実際に何を渡す？関連度はQueryとKeyのドット積で、大きいほど一致です。そして各位置はValueの重み付き平均を取ります。一言でいえば、アテンションは柔らかくて微分可能な辞書引きです。",
        "計算全体は5ステップです。QueryにKeyの転置を掛けて、全ペアのスコアを出す。ルートdkで割って、softmaxを安定させる。因果マスクで、未来を見えなくする。各行をsoftmaxして、和が1の重みにする。最後に、その重みでValueを混ぜる。信じないでください。実際の数字で5ステップ全部走らせましょう。",
        "実験台は4つのトークン。I、love、cats、感嘆符。ブックのおもちゃと完全に同じ系列です。各トークンには3次元のQ、K、Vベクトルがあり、それが目の前の3つの行列、おもちゃの既定値です。これから見るすべての数字はここから計算されます。",
        "ステップ1、スコア。SはQにKの転置を掛けたもの、4×4の表です。行iはトークンiが探しているもの、列jはトークンjが提供するラベル。ドット積が「jはiにどれだけ関連するか」を示します。2行目を見てください。catsは自分自身に2、Iとloveにそれぞれ1。大きいほど関連が強い。スコアとはそういうものです。",
        "ステップ2、因果マスク。言語モデルは次のトークンを予測して訓練されます。右を見ることは、答えのカンニングです。だから徹底します。対角線より上を、すべてマイナス無限大に。注意してください。そこでも計算は実行されており、結果がsoftmaxの前に捨てられているだけです。FlashAttentionはまさにこの無駄を省くために存在します。",
        "ステップ3、softmax。行ごとに処理します。各行は合計がちょうど1の確率分布になり、マイナス無限大の場所は正確に0になります。0行目を見てください。1、0、0、0。位置0は右を見ることが許されないので、自分に100パーセント注目します。自由はまったくありません。",
        "ステップ4、収穫です。各位置の新しい表現は、見ることが許されたValueベクトルの重み付きブレンド。catsは自分自身に最も注目し、次にIとloveです。出力ベクトルは文字通りその混合物です。アテンションはトークンを変えません。各位置が何を含むかを変えるのです。",
        "10の公式に値する実験をひとつ。Queryをすべてゼロにしたらどうなるでしょう？スコアはすべてゼロになり、各位置は見えるトークンを平等に扱います。一様分布です。身につけてほしい反射神経はこれです。Queryは引き分けを破る手。好みがなければ、アテンションのパターンも生まれません。ノートブックのステップ4.5で、自分で試してみてください。",
        "1つのアテンションパターンは1つの意見です。本物のモデルは並列にたくさん走らせます。マルチヘッドアテンションです。各ヘッドは次元の小さな切片を受け取り、専門を持ちます。文法を追うヘッド、itの指す先を追うヘッド、近さだけを見るヘッド。gpt-nanoは12次元のヘッドが4つ。小さな専門家たちを最後に連結します。",
        "アテンションを一言で復習しましょう。QueryとKeyのドット積が関連度。softmaxが関連度を分布にします。Valueの重み付き和が、各位置の新しい表現です。因果マスクが未来を遮ります。宿題です。ノートブックのステップ4.5で、単位行列Wvをランダム行列に替えて実行し、出力がどう変わったかを一文で説明してください。",
        "次のエピソードでは、アテンションに残差接続とLayerNormとMLPをまとわせます。Transformerブロックです。そしてそれを積んで、完全なGPTを作ります。今日の内容はブックのattention章にあります。おもちゃは今すぐ編集できます。第5エピソードでお会いしましょう。",
    ],
}


def build_html(L):
    parts = [f'<!DOCTYPE html><html lang="{L["lang"]}"><head><meta charset="utf-8">'
             f'<style>{CSS}</style></head><body>']
    parts.append(b_title(L))
    parts.append(b_problem(L))
    parts.append(b_rnn(L))
    parts.append(b_qkv(L))
    parts.append(b_steps(L))
    parts.append(b_playground(L))
    parts.append(b_matrix_slide("s07", 7, L, "s7", S.tolist(), signed=True, hi=False, rowhl=None,
                                right_title_color="var(--blue)", caption=L["cap74"]))
    parts.append(b_matrix_slide("s08", 8, L, "s8", M.tolist(), signed=True, hi=False, rowhl=None,
                                right_title_color="var(--orange)", caption=L["cap74"]))
    parts.append(b_matrix_slide("s09", 9, L, "s9", A.tolist(), signed=False, hi=True, rowhl=0,
                                right_title_color="var(--green)", caption=L["cap74"]))
    parts.append(b_matrix_slide("s10", 10, L, "s10", O.tolist(), signed=False, hi=False, rowhl=None,
                                right_title_color="var(--purple)", caption="out = A\u00b7V"))

    parts.append(b_zero(L))
    parts.append(b_heads(L))
    parts.append(b_recap(L))
    parts.append(b_end(L))
    parts.append(f'<script>{JS}</script></body></html>')
    return "".join(parts)


if __name__ == "__main__":
    for L in (EN, ZH, JA):
        path = os.path.join(OUT, f"slides_ep04_{L['lang'].split('-')[0]}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(build_html(L))
        print("wrote", os.path.abspath(path))
