# minGPT Learning Workspace

Chinese-language learning fork of [karpathy/minGPT](https://github.com/karpathy/minGPT): an executable learning book (HTML guide + notebooks) wrapped around the original minimal GPT code. Active development happens mostly in `docs/` and notebooks, not the core library. README and guide content are Chinese-first.

## Environment

- Windows / PowerShell. Repo-local `.venv/` (Python 3.13); README requires Python 3.10+.
- Install: `pip install torch numpy` then `pip install -e .`. `setup.py` only declares `torch`, but `mingpt/utils.py` and all notebooks import `numpy`.
- `transformers` is not a declared dependency but is required by `tests/` and `generate.ipynb`.

## Verification (no CI, no lint/typecheck config exists)

```bash
python -m json.tool learning_guide.ipynb   # also run on generate.ipynb after editing
node --check docs/learning_guide.js        # syntax check for guide's interactive JS
python docs/check_lang.py                  # trilingual section-sync check (exit 1 on drift)
python -m unittest discover tests
python run_notebook.py                     # launches Jupyter on learning_guide.ipynb
```

- The unittest suite is a single file (`test_huggingface_import.py`) that imports `transformers` and downloads GPT-2 weights from the Hugging Face Hub — needs network and time.
- `run_notebook.py` runs `python -m notebook`, which requires the `notebook` package.

## Structure

- `docs/learning_guide.html` — the main deliverable (Chinese HTML book). `learning_guide_en.html` and `learning_guide_ja.html` are translations sharing the same `<section id="...">` skeleton; keep all three in sync when changing guide content. Images live in `docs/assets/`.
- `docs/check_lang.py` — trilingual consistency checker (section IDs must match across zh/en/ja; ZH sections must start with Chinese). `docs/translate_sections.py` is a historical ad-hoc script with hardcoded absolute Windows paths.
- `video/` — English video series for the book: `video/README.md` (episode plan + script conventions), `video/scripts/en/epNN-*.md` (one file per episode; some full scripts, some outlines — see status table in video README). `video/tools/` generates actual MP4s (HTML/CSS slides rendered via headless Chrome + edge-tts narration + ffmpeg); finished videos organized by language in `video/output/en/`, `video/output/zh/`, `video/output/ja/`; `video/build/` is gitignored intermediate artifacts.
- `learning_guide.ipynb` — primary exercise notebook mirroring the HTML chapters. `demo.ipynb` (sorting task), `generate.ipynb` (GPT-2 generation).
- `mingpt/` — `model.py`, `trainer.py`, `bpe.py`, `utils.py` (`CfgNode` config class, `set_seed`). Training pattern: `GPT.get_default_config()` -> `Trainer(config, model, dataset).run()`; see `projects/adder/adder.py` for the canonical minimal example.
- `projects/adder` (GPT learns addition; watch the loss mask) and `projects/chargpt` (char-level LM).

## Gotchas

- **Model downloads**: `GPT.from_pretrained()` and the test download weights into the HF cache. `generate.ipynb` refuses `gpt2-medium/large/xl` unless `allow_large_models=True` — keep `model_type = 'gpt2'`. Training examples default to `gpt-nano` for speed; don't bump sizes casually.
- **Dataset contract**: datasets emit `(x, y)` `torch.LongTensor` pairs; labels of `-1` are ignored in the loss (adder's answer masking). This masking is a central teaching topic — don't "simplify" it away.
- **Comment style**: `mingpt/`, `tests/`, and scripts use trilingual comments (English / Chinese / Japanese). Preserve this style when editing library files.
