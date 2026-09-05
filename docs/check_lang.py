# -*- coding: utf-8 -*-
"""
三语学习书一致性检查工具 / Trilingual guide consistency checker.

Checks (run from anywhere, paths are resolved relative to this script):
1. Section ID sets must match across zh / en / ja HTML files.
2. Every section in the Chinese file must start with Chinese prose
   (catches sections that are still untranslated English stubs).

Exit code 0 = all good, 1 = inconsistencies found (usable in scripts/CI).

用法 / Usage:
    python docs/check_lang.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

FILES = {
    "zh": os.path.join(HERE, "learning_guide.html"),
    "en": os.path.join(HERE, "learning_guide_en.html"),
    "ja": os.path.join(HERE, "learning_guide_ja.html"),
}

SECTION_RE = re.compile(r'<section id="([^"]+)"')


def has_chinese(text):
    return any("\u4e00" <= c <= "\u9fff" for c in text)


def section_bodies(html):
    """Return {id: first 800 chars of section content}."""
    out = {}
    for m in SECTION_RE.finditer(html):
        sid = m.group(1)
        out[sid] = html[m.start() : m.start() + 800]
    return out


def main():
    docs = {lang: open(path, encoding="utf-8").read() for lang, path in FILES.items()}
    secs = {lang: SECTION_RE.findall(html) for lang, html in docs.items()}
    problems = []

    # ---- check 1: section id sets must be identical across the three files ----
    zh_set, en_set, ja_set = set(secs["zh"]), set(secs["en"]), set(secs["ja"])
    only_zh = zh_set - en_set - ja_set
    missing_en = zh_set - en_set
    missing_ja = zh_set - ja_set
    if missing_en:
        problems.append(f"sections missing in EN: {sorted(missing_en)}")
    if missing_ja:
        problems.append(f"sections missing in JA: {sorted(missing_ja)}")
    if only_zh:
        problems.append(f"sections only in ZH: {sorted(only_zh)}")
    for lang in ("en", "ja"):
        extra = set(secs[lang]) - zh_set
        if extra:
            problems.append(f"sections in {lang.upper()} but not in ZH: {sorted(extra)}")

    # ---- check 2: every ZH section should start with Chinese prose ----
    bodies = section_bodies(docs["zh"])
    untranslated = []
    for sid, body in bodies.items():
        p = body.find("<p>")
        if p >= 0:
            snippet = body[p + 3 : p + 150]
            if not has_chinese(snippet):
                untranslated.append(sid)
    if untranslated:
        problems.append(f"ZH sections whose first paragraph has no Chinese: {untranslated}")

    # ---- report ----
    print(f"ZH sections: {len(secs['zh'])}  EN: {len(secs['en'])}  JA: {len(secs['ja'])}")
    if problems:
        print("\nFAIL")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print("\nOK: trilingual section skeleton is in sync")


if __name__ == "__main__":
    main()
