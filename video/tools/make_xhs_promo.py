# -*- coding: utf-8 -*-
"""小红书推广视频 · 终极合并版（1080x1920 竖版, 男声云健, ~90s）：
是什么 → 封皮 → 章节概览 → 为什么重要 → 有什么用 → 6 张关键图 → 私信+点赞订阅分享 CTA。"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from slides_lib import tts, ffprobe_duration

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PDF_PATH = os.path.join(ROOT, "publish", "minGPT学习书_审读版_A4.pdf")
WORK = os.path.join(ROOT, "video", "build", "xhs")
OUT = os.path.join(ROOT, "publish", "xhs_book_promo.mp4")
VOICE = "zh-CN-YunjianNeural"
PROFILE = os.path.join(os.environ.get("TEMP", "/tmp"), "opencode", "chrome-xhs")
os.makedirs(WORK, exist_ok=True)
os.makedirs(os.path.dirname(OUT), exist_ok=True)

PDF_PAGES = [1, 3, 31, 16, 53, 57, 68, 95]  # cover, toc, 6 key figures

NARR = [
    "你天天用大语言模型，写代码、写文案、查资料。但你真的知道，它是怎么工作的吗？",
    "这本《从第一性原理理解 GPT》，就是回答这个问题的。它基于 Karpathy 的 minGPT，源码全部可以亲手运行。",
    "111 页刚刚成稿，我来把它给你过一遍。",
    "五大部分、三十二章：从注意力、训练、生成，一路讲到 Scaling、幻觉，和 Coding Agent。",
    "为什么这本书重要？提示词会过时，工具会淘汰，但大模型的底层原理，八年没变。会用 AI 的人很多，懂 AI 的人稀缺。",
    "学会它能干什么？用得明白——知道幻觉从哪来；用得好——参数才会调；往上走——Agent、微调、RAG，地基全是它。",
    "而书里最值钱的，是 60 多张手绘图。挑六张，带你看看。",
    "第一张：GPT 完整数据流。从 token 到 logits，一条线贯穿全书。",
    "第二张：损失掩码。聊天训练为什么只学助手该说的部分，一张图讲透。",
    "第三张：真实损失曲线。平台期之后突然下降，这才是训练的真相。",
    "第四张：自回归生成。一次一个 token，长文就是这么写出来的。",
    "第五张：Scaling Laws。参数、数据、算力怎么配比，一张图看懂。",
    "第六张：Agent 闭环。模型加工具加反馈，就是你天天用的编程智能体。",
    "111 页 PDF 已经打包好，需要的私信我，扣个书字。点赞订阅分享，欢迎扩散！",
]


# ---------- PDF pages -> framed canvases (blurred fill) ----------
def compose_pdf_pages():
    import pypdfium2 as pdfium
    from PIL import Image, ImageDraw, ImageFilter

    pdf = pdfium.PdfDocument(PDF_PATH)
    outs = []
    for n in PDF_PAGES:
        page = pdf[n - 1].render(scale=2.6).to_pil()
        page.thumbnail((1350, 10000))
        bg = page.copy()
        ratio = max(1620 / bg.width, 2880 / bg.height)
        bg = bg.resize((int(bg.width * ratio) + 1, int(bg.height * ratio) + 1))
        bx, by = (bg.width - 1620) // 2, (bg.height - 2880) // 2
        bg = bg.crop((bx, by, bx + 1620, by + 2880)).filter(ImageFilter.GaussianBlur(28))
        bg = Image.eval(bg, lambda v: int(v * 0.38 + 8))
        x, y = (1620 - page.width) // 2, (2880 - page.height) // 2
        ImageDraw.Draw(bg).rounded_rectangle(
            [x - 8, y - 8, x + page.width + 8, y + page.height + 8], radius=20, fill=(30, 36, 54))
        bg.paste(page, (x, y))
        out = os.path.join(WORK, f"pdfpage_{n:03d}.png")
        bg.save(out)
        outs.append(out)
        print("composed page", n)
    return outs


# ---------- HTML deck (1080x1920) ----------
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{margin:0;background:#0f1420;color:#e8eaf0;font-family:"Microsoft YaHei","Segoe UI",sans-serif;width:1080px;height:1920px;overflow:hidden}
.slide{display:none;width:1080px;height:1920px;position:relative;flex-direction:column;align-items:center;justify-content:center;gap:44px;padding:90px 70px;
background:radial-gradient(900px 1300px at 50% -10%,#1c2745 0%,#141a2b 55%,#10141f 100%)}
.slide.on{display:flex}
.kicker{color:#6c9eff;font-weight:700;font-size:34px;letter-spacing:6px}
.big{font-size:84px;font-weight:800;line-height:1.35;text-align:center}
.mid{font-size:42px;font-weight:700;color:#34d399;text-align:center;line-height:1.65}
.small{font-size:31px;color:#9aa3b8;text-align:center;line-height:1.8}
.chip{display:inline-flex;align-items:center;padding:14px 32px;border-radius:999px;background:#1e3a5f;border:3px solid #6c9eff;color:#bfdbfe;font-weight:700;font-size:30px}
.chips{display:flex;gap:18px;flex-wrap:wrap;justify-content:center}
.card{width:100%;background:#1a2233;border:3px solid var(--c,#6c9eff);border-radius:22px;padding:36px 40px;text-align:center}
.card .h{font-size:36px;font-weight:800}
.card .b{font-size:28px;color:#9aa3b8;margin-top:12px;line-height:1.7}
.bookcard{width:100%;background:#1a2233;border:4px solid #6c9eff;border-radius:26px;padding:50px 46px;text-align:center}
.dm{font-size:64px;font-weight:800;color:#facc15}
.cta-box{width:100%;text-align:center;background:#1e2a41;border:4px solid #6c9eff;border-radius:28px;padding:56px 50px}
.foot{position:absolute;bottom:70px;left:0;right:0;text-align:center;color:#5b6b8c;font-size:28px}
"""
SWITCH_JS = ("addEventListener('load',()=>{const id=location.hash.slice(1)||'s01';"
             "document.querySelectorAll('.slide').forEach(el=>el.classList.toggle('on',el.id===id));});")


def deck_html():
    s1 = f"""<div class="slide" id="s01">
  <div class="kicker">先问你一个问题</div>
  <div class="big">你天天用大语言模型<br>但它<br><span style="color:#6c9eff">是怎么工作的？</span></div>
  <div class="small">写代码、写文案、查资料都靠它——<br>可大部分人，从没搞懂过它。</div>
</div>"""
    s2 = f"""<div class="slide" id="s02">
  <div class="kicker">这本书，就是回答这个问题的</div>
  <div class="bookcard">
    <div style="font-size:52px;font-weight:800;line-height:1.4">从第一性原理<br>理解 GPT</div>
    <div style="font-size:30px;color:#6c9eff;margin-top:18px;font-weight:700">minGPT 中文可执行学习书</div>
    <div style="font-size:26px;color:#9aa3b8;margin-top:16px">基于 Andrej Karpathy 的 minGPT</div>
  </div>
  <div class="chips">
    <span class="chip">111 页</span><span class="chip">5 部分 32 章</span>
    <span class="chip">60+ 图解</span><span class="chip">源码全可跑</span>
  </div>
</div>"""
    s3 = f"""<div class="slide" id="s03">
  <div class="kicker">为什么它重要</div>
  <div class="big" style="font-size:72px">提示词会过时<br>工具会淘汰<br><span style="color:#34d399">原理八年没变</span></div>
  <div class="mid">会用 AI 的人很多，懂 AI 的人稀缺</div>
</div>"""
    s4 = f"""<div class="slide" id="s04">
  <div class="kicker">对「用大模型」的你，有什么用</div>
  <div style="display:flex;flex-direction:column;gap:28px;width:100%">
    <div class="card" style="--c:#6c9eff"><div class="h">用得明白</div>
      <div class="b">知道幻觉从哪来，才知道 AI 的回答什么能信</div></div>
    <div class="card" style="--c:#34d399"><div class="h">用得好</div>
      <div class="b">懂了采样、温度、top-k，参数才知道怎么调</div></div>
    <div class="card" style="--c:#fb923c"><div class="h">往上走</div>
      <div class="b">Agent、微调、RAG——上层玩法全是这套地基</div></div>
  </div>
</div>"""
    s5 = f"""<div class="slide" id="s05">
  <div class="kicker">而书里最值钱的</div>
  <div class="big">是 60+ 张<br>手绘插图</div>
  <div class="mid">我挑 6 张，带你看看</div>
  <div class="foot">每张图，都对应一章的硬概念</div>
</div>"""
    s6 = f"""<div class="slide" id="s06">
  <div class="kicker">111 页 PDF 已打包</div>
  <div class="big">需要的</div>
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
</div>"""
    return ('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">'
            f"<style>{CSS}</style></head><body>" + s1 + s2 + s3 + s4 + s5 + s6
            + "<script>" + SWITCH_JS + "</script></body></html>")


def render_deck():
    import pathlib
    html_path = os.path.join(WORK, "deck.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(deck_html())
    uri = pathlib.Path(html_path).as_uri()
    outs = []
    for i in range(1, 7):
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


def segment(img, mp3, out, zoom=False):
    dur = ffprobe_duration(mp3) + 1.0
    if zoom:
        frames = int(dur * 24) + 1
        vf = (f"zoompan=z='min(1+0.0012*on,1.12)':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'"
              f":d={frames}:s=1080x1920:fps=24,setsar=1")
        cmd = ["ffmpeg", "-y", "-i", img, "-i", mp3, "-vf", vf,
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
    import hashlib

    pdf_imgs = compose_pdf_pages()          # pages 1,3,31,16,53,57,68,95
    deck = render_deck()                    # s01 hook, s02 bookcard, s03 why, s04 use, s05 transition, s06 cta
    visuals = [
        deck[0],                            # 1 hook
        deck[1],                            # 2 book intro card
        pdf_imgs[0],                        # 3 PDF cover
        pdf_imgs[1],                        # 4 PDF toc
        deck[2],                            # 5 why important
        deck[3],                            # 6 what use
        deck[4],                            # 7 transition to figures
        pdf_imgs[2], pdf_imgs[3],           # 8-9 p31, p16
        pdf_imgs[4], pdf_imgs[5],           # 10-11 p53, p57
        pdf_imgs[6], pdf_imgs[7],           # 12-13 p68, p95
        deck[5],                            # 14 CTA
    ]
    assert len(visuals) == len(NARR) == 14

    seg_dir = os.path.join(WORK, "seg")
    os.makedirs(seg_dir, exist_ok=True)
    segs, total = [], 0.0
    for i, (img, text) in enumerate(zip(visuals, NARR), 1):
        key = hashlib.md5((VOICE + text).encode("utf-8")).hexdigest()[:8]
        mp3 = os.path.join(WORK, f"n{i:02d}_{key}.mp3")
        if not (os.path.exists(mp3) and os.path.getsize(mp3) > 0):
            tts(text, mp3, voice=VOICE)
        seg = os.path.join(seg_dir, f"s{i:02d}.mp4")
        d = segment(img, mp3, seg, zoom=(3 <= i <= 4 or 8 <= i <= 13))
        segs.append(seg)
        total += d
        print(f"  seg {i:02d}/14  tts {d - 1.0:5.1f}s")

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
