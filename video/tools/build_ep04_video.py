# -*- coding: utf-8 -*-
"""Build Ep 04 videos in en/zh/ja from rendered HTML-slide PNGs + per-language TTS."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_slides_html import EN, ZH, JA  # narration lists + voices live here
from slides_lib import build_video

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.abspath(os.path.join(HERE, "..", "build", "ep04"))
PNG = os.path.join(BUILD, "png")
OUTPUT = os.path.abspath(os.path.join(HERE, "..", "..", "video", "output"))

LANGS = {
    "en": (EN, os.path.join(BUILD, "en")),        # reuses cached EN audio from the first build
    "zh": (ZH, os.path.join(BUILD, "zh")),
    "ja": (JA, os.path.join(BUILD, "ja")),
}


def main(only=None):
    for lang, (L, bdir) in LANGS.items():
        if only and lang != only:
            continue
        slides = [(os.path.join(PNG, lang, f"s{i:02d}.png"), text) for i, text in enumerate(L["narr"], 1)]
        for png, _ in slides:
            assert os.path.exists(png), png
        out = os.path.join(OUTPUT, lang, f"ep04-attention-{lang}.mp4")
        print(f"== building {lang} -> {out}")
        total = build_video(slides, bdir, out, voice=L["voice"])
        print(f"== {lang} done: ~{total / 60:.1f} min")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
