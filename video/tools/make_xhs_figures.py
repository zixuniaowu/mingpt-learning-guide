# -*- coding: utf-8 -*-
"""小红书「图解特辑」v2：先讲为什么学大模型基础（铺垫），再引出书，用 6 张关键图作证。
1080x1920 竖版, 男声(云健), ~70s。"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from slides_lib import tts, ffprobe_duration

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PDF_PATH = os.path.join(ROOT, "publish", "minGPT学习书_审读版_A4.pdf")
WORK = os.path.join(ROOT, "video", "build", "xhs_fig")
OUT = os.path.join(ROOT, "publish", "xhs_figures.mp4")
VOICE = "zh-CN-YunjianNeural"
PROFILE = os.path.join(os.environ.get("TEMP", "/tmp"), "opencode", "chrome-xhs")
os.makedirs(WORK, exist_ok=True)
os.makedirs(os.path.dirname(OUT), exist_ok=True)

FIGURES = [
    (31, "第一张图：GPT 的完整数据流。从 token 到 logits，一条线贯穿全书。"),
    (16, "第二张：损失掩码。聊天训练为什么只学「助手该说的部分」，一张图讲透。"),
    (53, "第三张：真实的损失曲线。平台期之后突然下降，这才是训练的真相。"),
    (57, "第四张：自回归生成。一次只出一个 token，长文就是这么写出来的。"),
    (68, "第五张：Scaling Laws。参数、数据、算力怎么配比，一张图看懂。"),
    (95, "第六张：Agent 闭环。模型加工具加反馈，就是你天天用的编程智能体。"),
]
NARR = [
    "你天天用 GPT，但如果现在让你讲清楚：它是怎么工作的，你能说出口吗？",
    "这就是为什么要学基础。提示词会过时，工具会淘汰，但大模型的底层原理，从 2017 年到现在，一寸都没变过。",
    "会调接口的人满大街都是，能把原理讲明白的人才是稀缺的。面试、转行、做 Agent、做微调，地基全是这套东西。",
    "所以我把 Karpathy 的 minGPT——三百行源码，做成了一本可以运行的书，专门打这个地基。",
    FIGURES[0][1],
    FIGURES[1][1],
    FIGURES[2][1],
    FIGURES[3][1],
    FIGURES[4][1],
    FIGURES[5][1],
    "六张图，只是冰山一角。全书 PDF 已经打包好，需要的私信我，扣个书字。顺手点赞订阅分享，欢迎扩散！",
]


def compose_pages():
    import pypdfium2 as pdfium
    from PIL import Image, ImageDraw, ImageFilter

    pdf = pdfium.PdfDocument(PDF_PATH)
    outs = []
    for n, _ in FIGURES:
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
        out = os.path.join(WORK, f"fig_{n:03d}.png")
        bg.save(out)
        outs.append(out)
        print("composed page", n)
    return outs


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{margin:0;background:#0f1420;color:#e8eaf0;font-family:"Microsoft YaHei","Segoe UI",sans-serif;width:1080px;height:1920px;overflow:hidden}
.slide{display:none;width:1080px;height:1920px;position:relative;flex-direction:column;align-items:center;justify-content:center;gap:46px;padding:90px 70px;
background:radial-gradient(900px 1300px at 50% -10%,#1c2745 0%,#141a2b 55%,#10141f 100%)}
.slide.on{display:flex}
.kicker{color:#6c9eff;font-weight:700;font-size:34px;letter-spacing:6px}
.big{font-size:88px;font-weight:800;line-height:1.35;text-align:center}
.mid{font-size:42px;font-weight:700;color:#34d399;text-align:center;line-height:1.6}
.small{font-size:32px;color:#9aa3b8;text-align:center;line-height:1.8}
.chip{display:inline-flex;align-items:center;padding:14px 34px;border-radius:999px;background:#1e3a5f;border:3px solid #6c9eff;color:#bfdbfe;font-weight:700;font-size:32px}
.chips{display:flex;gap:20px;flex-wrap:wrap;justify-content:center}
.card{width:100%;background:#1a2233;border:3px solid var(--c,#6c9eff);border-radius:22px;padding:40px 42px;text-align:center}
.card .h{font-size:38px;font-weight:800}
.card .b{font-size:29px;color:#9aa3b8;margin-top:14px;line-height:1.7}
.dm{font-size:64px;font-weight:800;color:#facc15}
.cta-box{width:100%;text-align:center;background:#1e2a41;border:4px solid #6c9eff;border-radius:28px;padding:56px 50px}
.foot{position:absolute;bottom:70px;left:0;right:0;text-align:center;color:#5b6b8c;font-size:28px}
"""
SWITCH_JS = ("addEventListener('load',()=>{const id=location.hash.slice(1)||'s01';"
             "document.querySelectorAll('.slide').forEach(el=>el.classList.toggle('on',el.id===id));});")


def deck_html():
    s1 = f"""<div class="slide" id="s01">
  <div class="kicker">扎心一问</div>
  <div class="big">你天天用 GPT<br>但它怎么工作的<br>你能讲清楚吗？</div>
  <div class="mid" style="color:#fb923c">90% 的人，卡在这一句</div>
</div>"""
    s2 = f"""<div class="slide" id="s02">
  <div class="kicker">为什么要学基础</div>
  <div class="big" style="font-size:76px">提示词会过时<br>工具会淘汰<br><span style="color:#34d399">原理不会</span></div>
  <div class="small">Transformer 2017 年提出<br>至今仍是所有大模型共同的地基</div>
</div>"""
    s3 = f"""<div class="slide" id="s03">
  <div class="kicker">学基础，换来什么</div>
  <div style="display:flex;flex-direction:column;gap:30px;width:100%">
    <div class="card" style="--c:#6c9eff"><div class="h">面试 &amp; 转行</div>
      <div class="b">AI 岗位第一问就是：Transformer 为什么有效</div></div>
    <div class="card" style="--c:#34d399"><div class="h">做 Agent / 微调 / RAG</div>
      <div class="b">所有上层玩法，全是这套地基的延伸</div></div>
    <div class="card" style="--c:#fb923c"><div class="h">用得明白</div>
      <div class="b">知道幻觉从哪来，才知道什么能信</div></div>
  </div>
</div>"""
    s4 = f"""<div class="slide" id="s04">
  <div class="kicker">所以，地基这样打</div>
  <div class="big">我把 minGPT<br>做成了一本书</div>
  <div class="mid">300 行源码 · 可以运行 · 图解讲透</div>
  <div class="chips"><span class="chip">111 页</span><span class="chip">60+ 图解</span><span class="chip">代码全可跑</span></div>
  <div class="foot">下面这 6 张图，就是它的地基内容</div>
</div>"""
    s5 = f"""<div class="slide" id="s05">
  <div class="kicker">这只是冰山一角</div>
  <div class="big">111 页 PDF<br>已打包</div>
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
            f"<style>{CSS}</style></head><body>" + s1 + s2 + s3 + s4 + s5
            + "<script>" + SWITCH_JS + "</script></body></html>")


def render_deck():
    import pathlib
    html_path = os.path.join(WORK, "deck.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(deck_html())
    uri = pathlib.Path(html_path).as_uri()
    outs = []
    for i in range(1, 6):
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
    fig_imgs = compose_pages()
    deck = render_deck()
    visuals = deck[0:4] + fig_imgs + [deck[4]]
    assert len(visuals) == len(NARR) == 11

    seg_dir = os.path.join(WORK, "seg")
    os.makedirs(seg_dir, exist_ok=True)
    segs, total = [], 0.0
    for i, (img, text) in enumerate(zip(visuals, NARR), 1):
        mp3 = os.path.join(WORK, f"n{i}_{VOICE}.mp3")
        if not (os.path.exists(mp3) and os.path.getsize(mp3) > 0):
            tts(text, mp3, voice=VOICE)
        seg = os.path.join(seg_dir, f"s{i}.mp4")
        d = segment(img, mp3, seg, zoom=(5 <= i <= 10))
        segs.append(seg)
        total += d
        print(f"  seg {i}/11  tts {d - 1.0:5.1f}s")

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
