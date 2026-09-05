# -*- coding: utf-8 -*-
"""Slide framework + video assembly helpers for the minGPT video series."""
import asyncio
import math
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
BG = (18, 22, 34)         # page background
PANEL = (28, 34, 51)      # card background
PANEL2 = (23, 29, 44)
EDGE = (46, 51, 69)       # #2e3345
INK = (232, 234, 240)     # #e8eaf0
MUT = (154, 163, 184)     # #9aa3b8
BLUE = (108, 158, 255)    # #6c9eff
GREEN = (52, 211, 153)    # #34d399
ORANGE = (251, 146, 60)   # #fb923c
PURPLE = (167, 139, 250)  # #a78bfa
RED = (248, 113, 113)     # #f87171
YELLOW = (250, 204, 21)

FONT_DIR = "C:/Windows/Fonts"


def F(size, bold=False):
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except OSError:
        return ImageFont.truetype(os.path.join(FONT_DIR, "arial.ttf"), size)


def new_slide(kicker=None, title=None, page=None, total=None, footer="minGPT Learning Book · Ep 04 · Self-Attention"):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    if kicker:
        d.text((90, 64), kicker.upper(), font=F(30, bold=True), fill=BLUE)
    if title:
        d.text((90, 112), title, font=F(58, bold=True), fill=INK)
    if footer:
        d.text((90, H - 54), footer, font=F(24), fill=MUT)
    if page is not None and total is not None:
        s = f"{page} / {total}"
        w = d.textlength(s, font=F(24))
        d.text((W - 90 - w, H - 54), s, font=F(24), fill=MUT)
    if title:
        d.line([(90, 190), (W - 90, 190)], fill=EDGE, width=2)
    return img, d


def bullets(d, items, x, y, width=1000, size=34, gap=18, color=INK, bullet=BLUE):
    yy = y
    f = F(size)
    for it in items:
        d.ellipse([x, yy + size * 0.42, x + 12, yy + size * 0.42 + 12], fill=bullet)
        for line in _wrap(it, f, width - 34):
            d.text((x + 34, yy), line, font=f, fill=color)
            yy += size + 10
        yy += gap
    return yy


def _wrap(text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if font.getlength(t) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(d, text, x, y, width, size=34, color=INK, font=None, line_gap=10):
    f = font or F(size)
    yy = y
    for line in _wrap(text, f, width):
        d.text((x, yy), line, font=f, fill=color)
        yy += size + line_gap
    return yy


def card(d, x, y, w, h, fill=PANEL, edge=EDGE, radius=14):
    d.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill, outline=edge, width=2)


def arrow(d, p1, p2, color=BLUE, width=5, head=16):
    d.line([p1, p2], fill=color, width=width)
    ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    a1 = (p2[0] - head * math.cos(ang - 0.42), p2[1] - head * math.sin(ang - 0.42))
    a2 = (p2[0] - head * math.cos(ang + 0.42), p2[1] - head * math.sin(ang + 0.42))
    d.polygon([p2, a1, a2], fill=color)


def fmt_v(v):
    if v == float("-inf"):
        return "-\u221e"
    s = f"{v:+.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("+0", "-0", "+", "-") else s


def matrix(d, x, y, data, row_labels=None, col_labels=None, cell=62, label_font=None,
           hi_row=None, hi_col=None, cell_colors=None, value_font=None, label_color=MUT):
    """Draw a matrix; data cells may be floats or '-inf'. cell_colors(i,j) -> (bg, fg) override."""
    lf = label_font or F(22)
    vf = value_font or F(24, bold=True)
    n_r, n_c = len(data), len(data[0])
    ox = x + (56 if row_labels else 8)
    oy = y + (44 if col_labels else 8)
    if col_labels:
        for j, cl in enumerate(col_labels):
            d.text((ox + j * cell + cell / 2 - lf.getlength(cl) / 2, y), str(cl), font=lf, fill=label_color)
    if row_labels:
        for i, rl in enumerate(row_labels):
            d.text((x, oy + i * cell + cell / 2 - 14), str(rl), font=lf, fill=label_color)
    for i in range(n_r):
        for j in range(n_c):
            v = data[i][j]
            if cell_colors:
                bg, fg = cell_colors(i, j, v)
            else:
                bg, fg = PANEL2, INK
            rx, ry = ox + j * cell, oy + i * cell
            d.rectangle([rx + 2, ry + 2, rx + cell - 2, ry + cell - 2], fill=bg)
            if hi_row == i:
                d.rectangle([rx + 2, ry + 2, rx + cell - 2, ry + cell - 2], outline=YELLOW, width=2)
            s = v if isinstance(v, str) else fmt_v(v)
            d.text((rx + cell / 2 - vf.getlength(s) / 2, ry + cell / 2 - 16), s, font=vf, fill=fg)
    return ox + n_c * cell, oy + n_r * cell


def chip(d, x, y, text, fill=(30, 58, 95), edge=BLUE, fg=(191, 219, 254), size=26, pad=18):
    f = F(size, bold=True)
    w = f.getlength(text) + pad * 2
    d.rounded_rectangle([x, y, x + w, y + size + 16], radius=(size + 16) / 2, fill=fill, outline=edge, width=2)
    d.text((x + pad, y + 6), text, font=f, fill=fg)
    return x + w + 14


# ---------------- video assembly ----------------

VOICE = "en-US-AndrewNeural"
RATE = "-5%"


def tts(text, out_mp3, voice=None, rate=None):
    import edge_tts

    async def run():
        await edge_tts.Communicate(text, voice or VOICE, rate=rate or RATE).save(out_mp3)

    asyncio.run(run())


def ffprobe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def build_video(slides, build_dir, out_path, progress=print, voice=None):
    """slides: list of (png_path, narration_text). Produces final mp4 at out_path."""
    seg_dir = os.path.join(build_dir, "seg")
    aud_dir = os.path.join(build_dir, "audio")
    os.makedirs(seg_dir, exist_ok=True)
    os.makedirs(aud_dir, exist_ok=True)

    segs = []
    total_dur = 0.0
    for i, (png, text) in enumerate(slides, 1):
        mp3 = os.path.join(aud_dir, f"n{i:02d}.mp3")
        if not (os.path.exists(mp3) and os.path.getsize(mp3) > 0):
            tts(text, mp3, voice=voice)
        dur = ffprobe_duration(mp3)
        seg = os.path.join(seg_dir, f"s{i:02d}.mp4")
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-framerate", "30", "-i", png, "-i", mp3,
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
            "-vf", "scale=1920:1080:flags=lanczos",
            "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
            "-af", "adelay=500:all=1,apad=pad_dur=1.0",
            "-t", f"{dur + 1.5:.2f}", seg,
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        segs.append(seg)
        total_dur += dur + 1.5
        progress(f"  seg {i:02d}/{len(slides)}  tts {dur:5.1f}s")

    lst = os.path.join(build_dir, "list.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for s in segs:
            f.write(f"file '{os.path.abspath(s)}'\n")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out_path],
        capture_output=True, check=True,
    )
    return total_dur
