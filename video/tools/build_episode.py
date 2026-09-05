# -*- coding: utf-8 -*-
"""Generic video builder driven by an episode content module.

Module must define: SLUG, PNG_SUBDIR, NARR, and optionally VOICE (default en-US-AndrewNeural).
Usage: python build_episode.py slides_ep02_html
"""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slides_lib import build_video

HERE = os.path.dirname(os.path.abspath(__file__))
PNG_ROOT = os.path.abspath(os.path.join(HERE, "..", "build", "ep04", "png"))
OUTPUT = os.path.abspath(os.path.join(HERE, "..", "..", "video", "output"))


def main():
    mod = importlib.import_module(sys.argv[1])
    voice = getattr(mod, "VOICE", "en-US-AndrewNeural")
    png_dir = os.path.join(PNG_ROOT, mod.PNG_SUBDIR)
    build_dir = os.path.abspath(os.path.join(HERE, "..", "build", mod.SLUG, "en"))
    out = os.path.join(OUTPUT, "en", f"{mod.SLUG}-en.mp4")

    slides = []
    for i, text in enumerate(mod.NARR, 1):
        png = os.path.join(png_dir, f"s{i:02d}.png")
        assert os.path.exists(png), f"missing {png} — render first"
        slides.append((png, text))

    total = build_video(slides, build_dir, out, voice=voice)
    print(f"{mod.SLUG} done: ~{total / 60:.1f} min -> {out}")


if __name__ == "__main__":
    main()
