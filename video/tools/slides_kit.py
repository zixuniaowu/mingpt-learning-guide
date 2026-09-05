# -*- coding: utf-8 -*-
"""Shared slide layout kit for the minGPT video series (HTML decks -> headless Chrome)."""
import os

from make_slides_html import CSS, JS  # shared theme + hash-switch JS

FOOTER = "minGPT Learning Book"
TOTAL = 10


def _footer(page):
    return f'<div class="footer"><span>{FOOTER}</span><span>{page} / {TOTAL}</span></div>'


def _head(kicker, title, page):
    return (f'<div class="kicker">{kicker}</div><h1>{title}</h1><div class="rule"></div>' + _footer(page))


def _open(sid):
    return f'<section class="slide" id="s{sid:02d}">'


# ---------------- slides ----------------

def title(brand, big, sub, chips=None, tagline="", page=1):
    chips_html = ('<div style="display:flex;gap:22px">' +
                  "".join(f'<span class="chip">{c}</span>' for c in chips) + '</div>') if chips else ""
    return f"""{_open(1)}
<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:34px;text-align:center">
  <div class="kicker" style="letter-spacing:6px">{brand}</div>
  <div style="font-size:92px;font-weight:700">{big}</div>
  <div style="font-size:44px;color:var(--blue)">{sub}</div>
  {chips_html}
  <div style="font-size:27px;color:var(--mut);margin-top:12px">{tagline}</div>
</div>{_footer(page)}</section>"""


def statement(big, sub="", page=2):
    subh = f'<div style="font-size:31px;color:var(--mut);max-width:1300px;line-height:1.7">{sub}</div>' if sub else ""
    return f"""{_open(page)}
<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:44px;text-align:center">
  <div style="font-size:60px;font-weight:700;line-height:1.4;max-width:1560px">{big}</div>
  <div style="width:520px;height:2px;background:var(--edge)"></div>{subh}
</div>{_footer(page)}</section>"""


def cards(kicker, title, items, page, gap=32, vertical=False, note=None):
    """items: list of (tag, title, body, color). Vertical stack or horizontal row."""
    def one(t, tt, b, c):
        return f"""<div class="card" style="{('width:100%' if vertical else 'flex:1')};padding:36px;border-color:{c}">
      <div style="font-size:24px;font-weight:700;color:{c};letter-spacing:2px">{t}</div>
      <div style="font-size:33px;font-weight:700;margin-top:10px">{tt}</div>
      <div style="font-size:26px;color:var(--mut);margin-top:14px;line-height:1.6">{b}</div></div>"""
    arrow = '<div style="align-self:center;color:var(--mut);font-size:40px">&rarr;</div>'
    row = arrow.join(one(*it) for it in items)
    lay = f"flex-direction:column;gap:{gap}px" if vertical else f"gap:{gap}px;align-items:stretch"
    note_h = f'<div style="font-size:27px;color:var(--mut);text-align:center">{note}</div>' if note else ""
    return f"""{_open(page)}{_head(kicker, title, page)}
<div class="content" style="{lay};padding-top:40px">{row}</div>{note_h}</section>"""


def bullets(kicker, title, items, page, note=None):
    lis = "".join(f'<li style="margin:20px 0;font-size:32px;line-height:1.6">{it}</li>' for it in items)
    note_h = f'<div style="font-size:27px;color:var(--mut);text-align:center;margin-top:10px">{note}</div>' if note else ""
    return f"""{_open(page)}{_head(kicker, title, page)}
<div class="content" style="flex-direction:column;justify-content:center">
  <ul style="list-style:none;padding:0">{lis}</ul>{note_h}
</div></section>"""


def flow(kicker, title, boxes, page, note=None, branches=None, gap=16):
    """boxes: list of (name, sub, color). branches: list of (head, mono, color)."""
    line = f'<div style="position:absolute;left:30px;right:30px;top:50%;height:2px;background:var(--edge)"></div>'
    row = '<div style="color:var(--mut);font-size:30px;align-self:center">&rarr;</div>'.join(
        f"""<div class="card" style="flex:1;padding:26px 12px;text-align:center;border-color:{c};position:relative;z-index:1">
        <div style="font-size:28px;font-weight:700;color:{c}">{t}</div>
        <div style="font-size:21px;color:var(--mut);margin-top:8px">{s}</div></div>""" for t, s, c in boxes)
    br = ""
    if branches:
        br = '<div style="display:flex;gap:44px">' + "".join(
            f"""<div class="card" style="flex:1;padding:30px 40px;border-color:{c}">
            <div style="font-size:28px;font-weight:700;color:{c}">{h}</div>
            <div style="font-size:25px;color:var(--mut);margin-top:10px;font-family:Consolas,monospace">{m}</div></div>"""
            for h, m, c in branches) + "</div>"
    note_h = f'<div style="font-size:27px;color:var(--mut);text-align:center">{note}</div>' if note else ""
    return f"""{_open(page)}{_head(kicker, title, page)}
<div class="content" style="flex-direction:column;justify-content:center;gap:48px">
  <div style="display:flex;{('gap:' + str(gap) + 'px;') if gap else ''}position:relative">{line}{row}</div>{br}{note_h}
</div></section>"""


def code(kicker, title, lines, page, right=None, right_title=None, right_color="var(--blue)"):
    """lines: list of (kind, text): code|comment|out|hl. right: list of paragraphs."""
    cmap = {"code": ("var(--ink)", ""), "comment": ("var(--green)", ""), "out": ("var(--mut)", ""), "hl": ("var(--blue)", "font-weight:700")}
    body = "".join(
        f'<div style="font-family:Consolas,monospace;font-size:26px;line-height:1.9;color:{cmap[k][0]};{cmap[k][1]}">{t}</div>'
        for k, t in lines)
    right_html = ""
    if right:
        paras = "".join(f'<div style="font-size:28px;line-height:1.8;margin-bottom:26px">{p}</div>' for p in right)
        right_html = f"""<div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:8px">
      {'<div style="font-size:36px;font-weight:700;color:' + right_color + ';font-family:Consolas,monospace">' + right_title + '</div>' if right_title else ''}{paras}</div>"""
    lay = "flex-direction:column;justify-content:center" if not right else "gap:56px;align-items:stretch"
    cardw = "width:100%" if not right else "flex:1.2"
    return f"""{_open(page)}{_head(kicker, title, page)}
<div class="content" style="{lay};padding-top:40px">
  <div class="card" style="{cardw};padding:40px 48px;background:#0c101c;border-color:#26304a">{body}</div>
  {right_html}
</div></section>"""


def table(kicker, title, page, headers, rows, note=None, hl_col=None, widths=None):
    cols = f"grid-template-columns:{widths}" if widths else f"grid-template-columns:{'1fr ' * len(headers)}".strip()
    head_cells = "".join(f'<div style="font-size:25px;font-weight:700;color:var(--mut);padding:10px 18px">{h}</div>' for h in headers)
    body = ""
    for r in rows:
        for j, c in enumerate(r):
            color = "var(--ink)"
            if hl_col is not None and j == hl_col:
                color = "var(--blue)"
            body += f'<div style="font-size:26px;padding:12px 18px;border-top:1px solid var(--edge);color:{color};{"font-family:Consolas,monospace" if j == 0 else ""}">{c}</div>'
    note_h = f'<div style="font-size:26px;color:var(--mut);margin-top:24px">{note}</div>' if note else ""
    return f"""{_open(page)}{_head(kicker, title, page)}
<div class="content" style="flex-direction:column;justify-content:center">
  <div class="card" style="padding:14px 10px">
    <div style="display:grid;{cols}">{head_cells}</div>
    <div style="display:grid;{cols}">{body}</div>
  </div>{note_h}
</div></section>"""


def two_panel(kicker, title, left, right, page, left_color="var(--orange)", right_color="var(--green)",
              left_head="", right_head="", left_bg="", right_bg=""):
    def panel(body, head_t, c, bg):
        style = f"flex:1;padding:40px;border-color:{c};"
        style += f"background:{bg};border-color:{c}" if bg else ""
        h = f'<div style="font-size:28px;font-weight:700;color:{c};margin-bottom:20px">{head_t}</div>' if head_t else ""
        return f'<div class="card" style="{style}">{h}{body}</div>'
    return f"""{_open(page)}{_head(kicker, title, page)}
<div class="content" style="gap:44px;padding-top:40px;align-items:stretch">
  {panel(left, left_head, left_color, left_bg)}{panel(right, right_head, right_color, right_bg)}
</div></section>"""


def svg_panel(kicker, title, svg, page, note=None):
    note_h = f'<div style="font-size:27px;color:var(--mut);text-align:center;margin-top:8px">{note}</div>' if note else ""
    return f"""{_open(page)}{_head(kicker, title, page)}
<div class="content" style="flex-direction:column;align-items:center;justify-content:center;gap:30px">
  {svg}{note_h}
</div></section>"""


def end(next_label, next_title, next_sub, read="", run=""):
    return f"""{_open(9999)}
<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:30px;text-align:center">
  <div style="font-size:32px;color:var(--mut)">{next_label}</div>
  <div style="font-size:66px;font-weight:700">{next_title}</div>
  <div style="font-size:33px;color:var(--blue)">{next_sub}</div>
  <div style="width:520px;height:2px;background:var(--edge);margin:18px 0"></div>
  <div style="font-size:26px;color:var(--mut)">{read}</div>
  <div style="font-size:26px;color:var(--mut)">{run}</div>
</div><div class="footer"><span>{FOOTER}</span><span></span></div></section>"""


def homework(card_title, lines, next_label, next_title):
    lis = "<br>".join(f"{i + 1}&nbsp;·&nbsp;{t}" for i, t in enumerate(lines))
    return f"""{_open(9998)}
<div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:48px;padding:0 40px">
  <div class="card" style="padding:44px 52px;background:#1e2a41;border-color:var(--blue)">
    <div style="font-size:28px;font-weight:700;color:var(--blue);letter-spacing:2px">{card_title}</div>
    <div style="margin-top:16px;font-size:29px;line-height:1.9">{lis}</div>
  </div>
  <div style="text-align:center">
    <div style="font-size:29px;color:var(--mut)">{next_label}</div>
     <div style="font-size:54px;font-weight:700;margin-top:10px">{next_title}</div>
  </div>
</div><div class="footer"><span>{FOOTER}</span><span></span></div></section>"""


def write_deck(path, lang, sections):
    import re

    parts = [f'<!DOCTYPE html><html lang="{lang}"><head><meta charset="utf-8">'
             f'<style>{CSS}</style></head><body>'] + sections + [f'<script>{JS}</script></body></html>']
    html = "".join(parts)
    counter = iter(range(1, 200))
    html = re.sub(r'id="s\d+"', lambda m: f'id="s{next(counter):02d}"', html)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", os.path.abspath(path))
