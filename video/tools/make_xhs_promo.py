# -*- coding: utf-8 -*-
"""小红书推广视频 v2（1080x1920 竖版, 男声, ~45s）：
PDF 真实页面（模糊背景填充+缓推）+ 真实终端输出 + 云健男声 + 强钩子 + 私信 CTA。"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # video/tools -> video -> repo root
sys.path.insert(0, HERE)
from slides_lib import tts, ffprobe_duration

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PDF_PATH = os.path.join(ROOT, "publish", "minGPT学习书_审读版_A4.pdf")
WORK = os.path.join(ROOT, "video", "build", "xhs")
OUT = os.path.join(ROOT, "publish", "xhs_book_promo.mp4")
VOICE = "zh-CN-YunjianNeural"  # 男声
PROFILE = os.path.join(os.environ.get("TEMP", "/tmp"), "opencode", "chrome-xhs")
os.makedirs(WORK, exist_ok=True)
os.makedirs(os.path.dirname(OUT), exist_ok=True)

PDF_PAGES = [1, 3, 24, 16]  # cover, toc, RNN->TF evolution, loss-mask figure

NARR = [
    "你天天用 GPT，但你知道它是怎么学会说话的吗？我用三百行源码，亲手跑给你看。",
    "就是这本书——《从第一性原理理解 GPT》，一百一十一页，刚刚成稿。",
    "五大部分，三十二章，从注意力一路讲到 Coding Agent，一章都不水。",
    "六十多张手绘图解，从 RNN 到 Transformer，一眼看穿演进路线。",
    "损失掩码这种硬概念，直接一张图，给你讲透。",
    "两条命令装好环境，GPT 当场开训——你看这个损失，二点三一路砸到一点五。",
    "全书PDF已经打包好了。需要这本书的，私信我，扣个书字，看到秒回！顺手点个赞，订阅一下，再分享给身边想搞懂GPT的朋友——欢迎扩散，感谢支持！",
]


# ---------- 1. PDF pages -> framed canvases (blurred fill, no dead bars) ----------
def compose_pdf_pages():
    import pypdfium2 as pdfium
    from PIL import Image, ImageDraw, ImageFilter

    pdf = pdfium.PdfDocument(PDF_PATH)
    outs = []
    for n in PDF_PAGES:
        page = pdf[n - 1].render(scale=2.6).to_pil()
        page.thumbnail((1350, 10000))

        # background: page scaled to FILL 1620x2880, blurred + darkened
        bg = page.copy()
        ratio = max(1620 / bg.width, 2880 / bg.height)
        bg = bg.resize((int(bg.width * ratio) + 1, int(bg.height * ratio) + 1))
        bx = (bg.width - 1620) // 2
        by = (bg.height - 2880) // 2
        bg = bg.crop((bx, by, bx + 1620, by + 2880)).filter(ImageFilter.GaussianBlur(28))
        bg = Image.eval(bg, lambda v: int(v * 0.38 + 8))

        fg = page.copy()
        x = (1620 - fg.width) // 2
        y = (2880 - fg.height) // 2
        d = ImageDraw.Draw(bg)
        d.rounded_rectangle([x - 8, y - 8, x + fg.width + 8, y + fg.height + 8],
                            radius=20, fill=(30, 36, 54))
        bg.paste(fg, (x, y))
        out = os.path.join(WORK, f"pdfpage_{n:03d}.png")
        bg.save(out)
        outs.append(out)
        print("composed page", n)
    return outs


# ---------- 2. HTML deck (1080x1920) ----------
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{margin:0;background:#0f1420;color:#e8eaf0;font-family:"Microsoft YaHei","Segoe UI",sans-serif;width:1080px;height:1920px;overflow:hidden}
.slide{display:none;width:1080px;height:1920px;position:relative;flex-direction:column;align-items:center;justify-content:center;gap:46px;padding:90px 70px;
background:radial-gradient(900px 1300px at 50% -10%,#1c2745 0%,#141a2b 55%,#10141f 100%)}
.slide.on{display:flex}
.kicker{color:#6c9eff;font-weight:700;font-size:34px;letter-spacing:6px}
.big{font-size:96px;font-weight:800;line-height:1.3;text-align:center}
.mid{font-size:44px;font-weight:700;color:#34d399;text-align:center}
.chip{display:inline-flex;align-items:center;padding:14px 34px;border-radius:999px;background:#1e3a5f;border:3px solid #6c9eff;color:#bfdbfe;font-weight:700;font-size:32px}
.chips{display:flex;gap:20px;flex-wrap:wrap;justify-content:center}
.term{width:100%;background:#0c101c;border:3px solid #26304a;border-radius:24px;padding:44px 48px}
.term .bar{display:flex;gap:12px;margin-bottom:30px}
.term .dot{width:22px;height:22px;border-radius:50%}
.term .line{font-family:Consolas,monospace;font-size:32px;line-height:2.0;color:#e8eaf0;word-break:break-all}
.term .c{color:#5b6b8c}
.term .hl{color:#34d399;font-weight:700}
.cta-box{width:100%;text-align:center;background:#1e2a41;border:4px solid #6c9eff;border-radius:28px;padding:60px 50px}
.dm{font-size:64px;font-weight:800;color:#facc15}
.foot{position:absolute;bottom:70px;left:0;right:0;text-align:center;color:#5b6b8c;font-size:28px}
"""
SWITCH_JS = ("addEventListener('load',()=>{const id=location.hash.slice(1)||'s01';"
             "document.querySelectorAll('.slide').forEach(el=>el.classList.toggle('on',el.id===id));});")


def deck_html():
    rows = [l for l in open(r"C:\Users\zixun\AppData\Local\Temp\opencode\train_out.txt",
                            encoding="utf-8").read().splitlines() if l.strip()]
    pick = rows[0:1] + rows[3::4]
    train_lines = ""
    for l in pick:
        it = l.split("iter ")[1].split(":")[0]
        lo = l.split("loss ")[1]
        cls = "hl" if l is pick[-1] else ""
        train_lines += f'<div class="line {cls}">iter {it:>4}   loss {lo}</div>'

    s1 = f"""<div class="slide" id="s01">
  <div class="kicker">300 行源码 · 亲手跑给你看</div>
  <div class="big">GPT 是怎么<br>「学会说话」的？</div>
  <div class="mid">把它的底裤，翻给你看</div>
  <div class="chips"><span class="chip">111 页</span><span class="chip">60+ 图解</span><span class="chip">代码全可跑</span></div>
  <div class="foot">从第一性原理 · 到 Coding Agent</div>
</div>"""
    s2 = f"""<div class="slide" id="s02">
  <div class="kicker">真实训练 · gpt-nano · CPU</div>
  <div class="mid" style="color:#e8eaf0;font-size:56px">loss 2.32 <span style="color:#34d399">↓ 1.55</span></div>
  <div class="term"><div class="bar">
    <div class="dot" style="background:#f87171"></div><div class="dot" style="background:#facc15"></div><div class="dot" style="background:#34d399"></div>
  </div><div class="line c">加法任务 · 200 iters · 你电脑就能跑</div>{train_lines}</div>
  <div class="foot">GPT 真的在你电脑上学会了加法</div>
</div>"""
    s3 = f"""<div class="slide" id="s03">
  <div class="kicker">PDF 已打包</div>
  <div class="big">想要这本书的</div>
  <div class="cta-box">
    <div style="font-size:44px;color:#e8eaf0;font-weight:700">私信我 · 扣个</div>
    <div class="dm" style="margin-top:22px">「 书 」</div>
    <div style="font-size:34px;color:#9aa3b8;margin-top:22px">看到秒回</div>
  </div>
  <div class="chips">
    <span class="chip" style="border-color:#34d399;color:#a7f3d0">👍 点赞</span>
    <span class="chip" style="border-color:#facc15;color:#fef08a">⭐ 订阅</span>
    <span class="chip" style="border-color:#fb923c;color:#fed7aa">↗ 分享</span>
  </div>
  <div style="font-size:32px;color:#9aa3b8">欢迎扩散 · 分享给每个想搞懂 GPT 的朋友</div>
  <div class="chips"><span class="chip">审读版 PDF</span><span class="chip">111 页</span><span class="chip">60+ 图解</span></div>
</div>"""
    return ('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">'
            f"<style>{CSS}</style></head><body>" + s1 + s2 + s3
            + "<script>" + SWITCH_JS + "</script></body></html>")


def render_deck():
    import pathlib
    html_path = os.path.join(WORK, "deck.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(deck_html())
    uri = pathlib.Path(html_path).as_uri()
    outs = []
    for i in range(1, 4):
        out = os.path.join(WORK, f"slide{i}.png")
        subprocess.run([
            CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars",
            "--window-size=1080,1920", "--force-device-scale-factor=1",
            "--virtual-time-budget=4000", f"--user-data-dir={PROFILE}",
            f"--screenshot={out}", f"{uri}#s{i:02d}",
        ], capture_output=True, check=True, timeout=60)
        outs.append(out)
        print("slide", i, os.path.getsize(out) // 1024, "KB")
    return outs


# ---------- 3. assemble ----------
def segment(img, mp3, out, zoom=False):
    dur = ffprobe_duration(mp3) + 1.0
    if zoom:
        frames = int(dur * 24) + 1
        vf = (f"zoompan=z='min(1+0.0012*on,1.12)':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'"
              f":d={frames}:s=1080x1920:fps=24,setsar=1")
        cmd = ["ffmpeg", "-y", "-i", img, "-i", mp3,
               "-vf", vf,
               "-c:v", "libx264", "-crf", "27", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
               "-af", "adelay=300:all=1,apad=pad_dur=0.7", "-t", f"{dur:.2f}", out]
    else:
        cmd = ["ffmpeg", "-y", "-loop", "1", "-framerate", "24", "-i", img, "-i", mp3,
               "-vf", "setsar=1",
               "-c:v", "libx264", "-crf", "27", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
               "-af", "adelay=300:all=1,apad=pad_dur=0.7", "-t", f"{dur:.2f}", out]
    subprocess.run(cmd, capture_output=True, check=True)
    return dur


def main():
    page_imgs = compose_pdf_pages()
    slide_imgs = render_deck()
    visuals = [slide_imgs[0]] + page_imgs + [slide_imgs[1], slide_imgs[2]]
    assert len(visuals) == len(NARR) == 7

    seg_dir = os.path.join(WORK, "seg")
    os.makedirs(seg_dir, exist_ok=True)
    segs, total = [], 0.0
    for i, (img, text) in enumerate(zip(visuals, NARR), 1):
        mp3 = os.path.join(WORK, f"n{i}_{VOICE}.mp3")  # cache key includes voice
        if not (os.path.exists(mp3) and os.path.getsize(mp3) > 0):
            tts(text, mp3, voice=VOICE)
        seg = os.path.join(seg_dir, f"s{i}.mp4")
        d = segment(img, mp3, seg, zoom=(2 <= i <= 5))
        segs.append(seg)
        total += d
        print(f"  seg {i}/7  tts {d - 1.0:5.1f}s")

    lst = os.path.join(WORK, "list.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for s in segs:
            f.write(f"file '{os.path.abspath(s)}'\n")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", OUT],
                   capture_output=True, check=True)
    mb = os.path.getsize(OUT) / 1024 / 1024
    print(f"DONE ~{total:.0f}s {mb:.1f} MB -> {OUT}")


if __name__ == "__main__":
    main()
