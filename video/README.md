# minGPT 学习书 · 视频系列（英文配音）

与 `docs/learning_guide.html`（中文主书）配套的英文视频讲解系列。**每一章一集**，讲稿在 `scripts/en/`。

## 系列总览

| 集 | 标题 | 覆盖的 HTML 章节 | 讲稿状态 | 目标时长 |
| --- | --- | --- | --- | --- |
| Ep 01 | Welcome & How to Use This Book | overview / glossary / preface / structure / workflow | ✅ 已成片 `output/en/ep01-welcome-en.mp4` | ~4.3 min |
| Ep 02 | What Language Modeling Really Does | first-principles / history | ✅ 已成片 `output/en/ep02-first-principles-en.mp4` | ~3.6 min |
| Ep 03 | From Text to Vectors: Tokenization & BPE | tokenization / bpe | ✅ 已成片 `output/en/ep03-tokens-embeddings-en.mp4` | ~3.6 min |
| Ep 04 | Self-Attention: The Core of the Transformer | attention | ✅ 已成片 `output/en/ep04-attention-en.mp4`（另有 zh/ja 版） | ~5.6 min |
| Ep 05 | Transformer Block & the Full GPT | architecture / block / gpt | ✅ 已成片 `output/en/ep05-block-and-gpt-en.mp4` | ~4.3 min |
| Ep 06 | Activations: GELU & Softmax | activations / gelu / softmax | ✅ 已成片 `output/en/ep06-activations-en.mp4` | ~3.4 min |
| Ep 07 | Training: Loss, Gradients, and the Loss Mask | training | ✅ 已成片 `output/en/ep07-training-en.mp4` | ~3.9 min |
| Ep 08 | Generation: One Token at a Time | generation | ✅ 已成片 `output/en/ep08-generation-en.mp4` | ~3.9 min |
| Ep 09 | Scaling, Fine-tuning & Position Encoding | finetuning / comparisons / scaling / position | ✅ 已成片 `output/en/ep09-scaling-finetuning-position-en.mp4` | ~3.3 min |
| Ep 10 | Hallucination & How to Evaluate LLMs | beyond / hallucination / evaluation | ✅ 已成片 `output/en/ep10-hallucination-evaluation-en.mp4` | ~3.5 min |
| Ep 11 | From GPT to Coding Agents | agent-engineering | ✅ 已成片 `output/en/ep11-coding-agents-en.mp4` | ~3.3 min |
| Ep 12 | Projects, Labs & Wrap-Up | implementation / utils / projects / labs / conclusion | ✅ 已成片 `output/en/ep12-projects-labs-wrapup-en.mp4` | ~3.0 min |

**英文全系列 12 集已成片**（1080p30，H.264 + AAC，共约 42 分钟）。

成片按语言分目录：`video/output/en/`（12 集）、`video/output/zh/`、`video/output/ja/`。

## 讲稿格式约定（所有集数统一）

讲稿**不是照读 HTML**，而是"导播脚本"：主持人用自己的话讲，脚本告诉你讲什么、什么时候展示哪张图、什么时候切到 notebook 跑代码。

标记含义：

| 标记 | 含义 |
| --- | --- |
| `[SAY]` | 逐字旁白（可直接照念） |
| `[SHOW: ...]` | 展示指定章节/图/交互玩具，指出要看的位置 |
| `[RUN: Step N · cell M]` | 切到 Jupyter，现场运行 `learning_guide.ipynb` 的对应 cell |
| `[EDIT: ...]` | 现场修改某个数值/参数，先让观众猜结果再运行 |
| `[TRY]` | 留给观众的家庭作业 |
| `[PAUSE]` | 停 2-3 秒，让图自己说话 |

硬性规则：

1. **每集至少现场跑 2 个代码 cell**——这是"可执行的书"的视频版，不能只放幻灯片。
2. **每张关键图至少停留一次**并讲解"颜色/箭头/形状分别是什么"，不要一笔带过。
3. 时间标记是近似值，按实际录制调整；单集不超过 15 分钟。
4. 术语第一次出现时念全称 + 缩写（例如 "Key-Value, or K/V"），并在口播里回应一次 glossary 的"三问法"。
5. 录制环境：`pip install torch numpy && pip install -e .`，双屏——左屏 HTML guide，右屏 Jupyter。模型一律 `gpt-nano`，禁止现场下载 `gpt2` 以上的权重（`generate.ipynb` 有保护，别绕过它）。

## 各集与 notebook 的对应

| Notebook 位置 | 用在哪几集 |
| --- | --- |
| Step 1 环境检查 | Ep 01 |
| Step 3 模型结构 / Step 4 前向传播 | Ep 05 |
| Step 4.5 注意力手算 | Ep 04 |
| Step 6 hooks 调试 | Ep 05（可选加映） |
| Step 7.5 adder loss mask | Ep 07（本系列最重要的现场实验） |
| Step 8 Trainer 训练 / Step 9 训练后生成 | Ep 07、Ep 08 |
| Step 10 autograd | Ep 07（可选） |
| generate.ipynb | Ep 08 |
| demo.ipynb | Ep 12 |

## 制作管线（已可用）

**Ep 04 已产出三语三支成片**（1080p，约 5.5–6.8 分钟，14 页幻灯 + 神经语音旁白）：

- `video/output/en/ep01-welcome-en.mp4` — Ep 01 英文成片（4.3 分钟，10 页）
- `video/output/en/ep04-attention-en.mp4`（英语 · Andrew）
- `video/output/zh/ep04-attention-zh.mp4`（中文 · 云希）
- `video/output/ja/ep04-attention-ja.mp4`（日语 · Keita）

注：英/中/日三语成片中，**英文质量最好**；中/日的 TTS 音色与文案仍需打磨，后续集数优先只出英文，中日文待配音方案确定后补。

管线：**HTML/CSS 幻灯片（flex/grid 排版，不会重叠）→ 无头 Chrome 截图（2x 超采样）→ edge-tts 旁白 → ffmpeg 合成**。矩阵数字全部由 numpy 按书中玩具默认 Q/K/V 真实计算，三语同源。

- `tools/make_slides_html.py` — 三语幻灯片内容（版式 + 文案 + 旁白文本），矩阵实时计算
- `tools/render_slides.py` — HTML → PNG（headless Chrome）
- `tools/build_ep04_video.py` — PNG + TTS → MP4（按语言复用已缓存的音频）
- `tools/slides_lib.py` — TTS/ffprobe/ffmpeg 组装库

重建命令：

```bash
.venv\Scripts\python.exe -X utf8 video\tools\make_slides_html.py   # 生成三语 HTML
.venv\Scripts\python.exe -X utf8 video\tools\render_slides.py      # HTML -> PNG
.venv\Scripts\python.exe -X utf8 video\tools\build_ep04_video.py   # -> MP4（可跟 en|zh|ja 单独构建）
```

依赖：`pip install pillow edge-tts`；系统需有 ffmpeg 与 Chrome。`video/build/` 为中间产物，已 gitignore。

新集做法：以 `make_slides_html.py` 的 EN/ZH/JA 结构为模板替换幻灯与旁白内容，三个脚本通用。

## 后续工作

- [x] 英文全系列 12 集成片（`video/output/{en,zh,ja}/*.mp4`）
- [ ] 中/日文配音质量打磨（Ep04 的 zh/ja 版为初版，音色与文案待改进）
- [ ] 后续集数如需中/日版，按 `make_slides_html.py` 的 EN/ZH/JA 结构扩写
- [ ] 如需真人口播/录屏混剪，讲稿标记 `[RUN]`/`[SHOW]` 可直接当导播单用
