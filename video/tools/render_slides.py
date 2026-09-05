# -*- coding: utf-8 -*-
"""Render slide HTML decks to PNGs via headless Chrome (2x supersampling)."""
import os
import pathlib
import subprocess
import sys

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
HTML_DIR = os.path.abspath(os.path.join(HERE, "..", "build", "ep04", "html"))
PNG_DIR = os.path.abspath(os.path.join(HERE, "..", "build", "ep04", "png"))
PROFILE = os.path.join(os.environ.get("TEMP", "/tmp"), "opencode", "chrome-profile")
os.makedirs(PNG_DIR, exist_ok=True)
os.makedirs(PROFILE, exist_ok=True)

N_SLIDES = 14


def find_html(html_name):
    build_root = os.path.abspath(os.path.join(HERE, "..", "build"))
    for dirpath, _dirnames, filenames in os.walk(build_root):
        if html_name in filenames:
            return pathlib.Path(dirpath, html_name).as_uri()
    raise FileNotFoundError(html_name)


def render_generic(html_name, n_slides, out_subdir):
    html = find_html(html_name)
    outdir = os.path.join(PNG_DIR, out_subdir)
    os.makedirs(outdir, exist_ok=True)
    for i in range(1, n_slides + 1):
        out = os.path.join(outdir, f"s{i:02d}.png")
        cmd = [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            "--hide-scrollbars",
            "--force-device-scale-factor=2",
            "--window-size=1920,1080",
            "--virtual-time-budget=6000",
            "--run-all-compositor-stages-before-draw",
            f"--user-data-dir={PROFILE}",
            f"--screenshot={out}",
            f"{html}#s{i:02d}",
        ]
        subprocess.run(cmd, capture_output=True, check=True, timeout=60)
        print(f"  {out_subdir} s{i:02d}  {os.path.getsize(out) // 1024} KB")


def render(lang):
    render_generic(f"slides_ep04_{lang}.html", N_SLIDES, lang)


if __name__ == "__main__":
    if len(sys.argv) >= 4:
        render_generic(sys.argv[1], int(sys.argv[2]), sys.argv[3])
    else:
        langs = sys.argv[1:] or ["en", "zh", "ja"]
        for lang in langs:
            print(f"rendering {lang}...")
            render(lang)
    print("done ->", PNG_DIR)
