# -*- coding: utf-8 -*-
"""Build ALL English episodes: deck -> render -> video, driven by each module's NARR length."""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_slides as rs
from slides_lib import build_video

HERE = os.path.dirname(os.path.abspath(__file__))
PNG_ROOT = rs.PNG_DIR  # png root lives under build/ep04/png (legacy location, shared)

MODULES = [
    "slides_ep02_html", "slides_ep03_html", "slides_ep05_html", "slides_ep06_html",
    "slides_ep07_html", "slides_ep08_html", "slides_ep09_html", "slides_ep10_html",
    "slides_ep11_html", "slides_ep12_html",
]


def main(only=None):
    for name in MODULES:
        if only and only not in name:
            continue
        mod = importlib.import_module(name)
        n = len(mod.NARR)
        html_name = name.replace("_html", "_en") + ".html"
        print(f"== {mod.SLUG}: {n} slides")
        rs.render_generic(html_name, n, mod.PNG_SUBDIR)

        png_dir = os.path.join(PNG_ROOT, mod.PNG_SUBDIR)
        slides = [(os.path.join(png_dir, f"s{i:02d}.png"), t) for i, t in enumerate(mod.NARR, 1)]
        for p, _ in slides:
            assert os.path.exists(p), p
        build_dir = os.path.abspath(os.path.join(HERE, "..", "build", mod.SLUG, "en"))
        out = os.path.abspath(os.path.join(HERE, "..", "..", "video", "output", "en", f"{mod.SLUG}-en.mp4"))
        total = build_video(slides, build_dir, out, voice=mod.VOICE)
        print(f"== {mod.SLUG} done: ~{total / 60:.1f} min -> {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
