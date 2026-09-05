# -*- coding: utf-8 -*-
"""Build Ep 01 — How to Use This Book (EN) video."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_slides_ep01_html import NARR
from slides_lib import build_video

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.abspath(os.path.join(HERE, "..", "build", "ep04", "png", "ep01-en"))
BUILD = os.path.abspath(os.path.join(HERE, "..", "build", "ep01", "en"))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "video", "output", "en", "ep01-welcome-en.mp4"))
VOICE = "en-US-AndrewNeural"


def main():
    slides = [(os.path.join(PNG, f"s{i:02d}.png"), text) for i, text in enumerate(NARR, 1)]
    for png, _ in slides:
        assert os.path.exists(png), png
    total = build_video(slides, BUILD, OUT, voice=VOICE)
    print(f"Ep01 EN done: ~{total / 60:.1f} min -> {OUT}")


if __name__ == "__main__":
    main()
