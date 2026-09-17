# -*- coding: utf-8 -*-
"""Build the A4 review PDF of the learning guide for publisher submission.

Pipeline: learning_guide.html
  -> inject print.css + front matter (cover / meta / TOC from the sidebar nav)
  -> headless Chrome print-to-pdf (keeps SVG diagrams, draws JS canvas charts)
  -> pypdf stamps page numbers
  -> publish/minGPT学习书_审读版_A4.pdf
"""
import io
import os
import re
import subprocess
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORK = os.path.join(HERE, "_print")
OUT_DIR = os.path.join(ROOT, "publish")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

SRC = os.path.join(HERE, "learning_guide.html")
PRINT_CSS = os.path.join(HERE, "print.css")
PRINT_HTML = os.path.join(WORK, "learning_guide_print.html")
RAW_PDF = os.path.join(WORK, "raw.pdf")
FINAL_PDF = os.path.join(OUT_DIR, "minGPT学习书_审读版_A4.pdf")


REPO_URL = "https://github.com/zixuniaowu/mingpt-learning-guide"


def build_toc(html):
    nav = re.search(r"<nav>(.*?)</nav>", html, re.S).group(1)
    items = []
    for m in re.finditer(r'<div class="nav-group">([^<]+)</div>|<a href="#([^"]+)">([^<]+)</a>', nav):
        group, anchor, label = m.group(1), m.group(2), m.group(3)
        if group:
            items.append(f'<li class="grp">{group}</li>')
        else:
            items.append(f'<li><a href="#{anchor}">{label}</a></li>')
    return ("<section class='front-toc'><h2 style='border:none'>目录</h2><ol>"
            + "".join(items) + "</ol></section>")


def make_qr(path):
    import qrcode
    img = qrcode.make(REPO_URL, box_size=8, border=2)
    img.save(path)
    return path


def front_matter(html):
    today = date.today().strftime("%Y 年 %m 月")
    qr = make_qr(os.path.join(WORK, "qr.png"))
    toc = build_toc(html)
    cover = f"""
<section class="front-cover">
  <div class="t">从第一性原理理解 GPT</div>
  <div class="s">minGPT 中文可执行学习书</div>
  <div class="based">基于 Andrej Karpathy 的 minGPT（MIT License）<br>
      图解 · 可执行代码 · 训练与生成 · Scaling · AI Agent</div>
  <div class="meta" style="margin-top:64px">作者：Jacky Wang<br>版本：审读版 v1.0<br>日期：{today}</div>
  <div class="gh-box">
    <a href="{REPO_URL}" style="text-decoration:none;color:inherit;display:flex;align-items:center;gap:24px;width:100%">
      <img src="{os.path.basename(qr)}" alt="GitHub 二维码">
      <div class="txt">
        <div class="h">本书配套可执行代码 · 开源（点击访问）</div>
        <div class="u">github.com/zixuniaowu/<br>mingpt-learning-guide</div>
        <div class="s">扫码或访问仓库，clone 后 <b>pip install -e .</b><br>即可运行书中全部 Notebook 实验与交互版</div>
      </div>
    </a>
  </div>
</section>"""
    meta = f"""
<section class="front-cover" style="padding-top:90px">
  <div class="t" style="font-size:20pt">本书说明</div>
  <div class="based" style="margin-top:40px; text-align:left; max-width:430px; margin-left:auto; margin-right:auto">
    · 本书是一本可执行的学习书：所有结论都可以在配套 Notebook（learning_guide.ipynb）中运行验证。<br><br>
    · 源码基于 Andrej Karpathy 的开源项目 minGPT（MIT License），
      本书在其基础上添加了大量教学图解与中文讲解，源码注释为英/中/日三语。<br><br>
    · 书中插图均为自绘 SVG，代码示例遵循原项目 MIT 许可并保留归属。<br><br>
    · 交互版（在线 HTML）含可操作的注意力演示与采样玩具；
      本 PDF 为纸面审读版，交互元素已省略。
  </div>
  <div style="margin:36px auto 0; max-width:540px; background:#eff6ff; border:2px solid #2563eb; border-radius:14px; padding:24px 30px; text-align:center; break-inside: avoid">
    <div style="font-weight:700; color:#1d4ed8; font-size:12pt">本书配套可执行代码 · 开源</div>
    <div style="margin-top:12px; font-size:12.5pt; font-weight:700">
      <a href="{REPO_URL}" style="color:#2563eb; text-decoration:none">github.com/zixuniaowu/mingpt-learning-guide</a>
    </div>
    <div style="margin:12px auto 0; width:110px"><img src="qr.png" style="width:110px;height:110px" alt="GitHub 二维码"></div>
    <div style="margin-top:10px; font-size:10pt; color:#5a6578; line-height:1.8">
      扫码或访问仓库，clone 后执行 <b>pip install -e .</b><br>
      即可运行书中全部 Notebook 实验与项目（含学习书 HTML 交互版）
    </div>
  </div>
  <div class="based" style="margin-top:28px; text-align:center">
    联系方式：＿＿＿＿＿＿＿＿
  </div>
</section>"""
    return cover + meta + toc


def inject(html):
    css = open(PRINT_CSS, encoding="utf-8").read()
    html = html.replace("</head>", f"<style>{css}</style></head>")
    fm = front_matter(html)
    html = html.replace('<main class="main">', '<main class="main">' + fm, 1)
    return html


def print_pdf(print_html_path, out_pdf):
    uri = "file:///" + os.path.abspath(print_html_path).replace("\\", "/")
    cmd = [
        CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
        "--no-pdf-header-footer", "--disable-extensions", "--hide-scrollbars",
        "--virtual-time-budget=30000", "--run-all-compositor-stages-before-draw",
        f"--user-data-dir={os.path.join(os.environ.get('TEMP', '/tmp'), 'opencode', 'chrome-pdf')}",
        f"--print-to-pdf={out_pdf}", uri,
    ]
    subprocess.run(cmd, capture_output=True, check=True, timeout=300)


def stamp_page_numbers(pdf_path):
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas as rl_canvas

    reader = PdfReader(pdf_path)
    w = float(reader.pages[0].mediabox.width)
    h = float(reader.pages[0].mediabox.height)
    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=(w, h))
    for i in range(len(reader.pages)):
        if i > 0:  # skip the cover
            c.setFont("Helvetica", 8)
            c.setFillColorRGB(0.45, 0.49, 0.55)
            c.drawString(46, 26, REPO_URL.replace("https://", ""))
            c.setFont("Helvetica", 9)
            c.drawRightString(w - 46, 26, f"— {i + 1} —")
        c.showPage()
    c.save()

    overlay = PdfReader(buf)
    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        if i > 0:
            page.merge_page(overlay.pages[i])
        writer.add_page(page)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return len(reader.pages)


def stats(html):
    text = re.sub(r"<[^>]+>", " ", html)
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    words = len(re.findall(r"[A-Za-z]+", text))
    return cjk, words


def main():
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    html = open(SRC, encoding="utf-8").read()

    with open(PRINT_HTML, "w", encoding="utf-8") as f:
        f.write(inject(html))
    print("print html ->", PRINT_HTML)

    print_pdf(PRINT_HTML, RAW_PDF)
    n_pages = stamp_page_numbers(RAW_PDF)
    os.replace(RAW_PDF, FINAL_PDF)

    cjk, words = stats(html)
    size_mb = os.path.getsize(FINAL_PDF) / 1024 / 1024
    print(f"PDF -> {FINAL_PDF}")
    print(f"pages: {n_pages}   size: {size_mb:.1f} MB")
    print(f"stats: {cjk:,} CJK chars + {words:,} latin words")


if __name__ == "__main__":
    sys.exit(main())
