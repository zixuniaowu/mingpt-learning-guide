# minGPT 中文可执行学习指南

这是一个面向学习的 minGPT 仓库版本，基于 Andrej Karpathy 的 [minGPT](https://github.com/karpathy/minGPT) 整理而来。这个仓库的重点不是生产训练，而是帮助你从第一性原理理解 GPT：

- 文本如何变成 token
- Dataset 为什么要构造 `(x, y)`
- attention、Transformer Block、GPT 前向传播怎么工作
- loss、反向传播、优化器如何更新参数
- adder 项目为什么反向编码答案、为什么用 `-1` 屏蔽 loss
- `generate.ipynb` 为什么会下载 GPT-2 权重，以及怎样避免误下大模型

## 最重要的入口

直接打开：

```text
docs/learning_guide.html
```

这是中文 HTML 学习书，也是这个仓库最主要的内容。它被设计成“一本可以边读边运行的书”：

1. 用浏览器打开 `docs/learning_guide.html`
2. 同时用 Jupyter 打开 `learning_guide.ipynb`
3. 看到 HTML 里的代码卡片时，在 Notebook 里运行对应代码
4. 对照 HTML 里的逐行解释理解输出、维度和训练流程

英文版本在：

```text
docs/learning_guide_en.html
```

## 仓库里新增/重点文件

```text
docs/
├── learning_guide.html       # 中文 HTML 学习书，主要入口
├── learning_guide.css        # HTML 样式
├── learning_guide.js         # HTML 交互逻辑
├── learning_guide_en.html    # 英文版
├── check_lang.py             # 文档检查辅助脚本
└── translate_sections.py     # 翻译/同步辅助脚本

learning_guide.ipynb          # 配合 HTML 运行的练习 Notebook
generate.ipynb                # 安全版 GPT-2 生成示例，默认只用 gpt2
demo.ipynb                    # minGPT 原始 demo 的学习版
run_notebook.py               # Notebook 运行辅助脚本

mingpt/                       # 加了大量中文教学注释的 minGPT 代码
projects/adder/               # GPT 学加法示例，重点理解数据构造与 loss mask
projects/chargpt/             # 字符级语言模型示例
```

## 环境准备

建议使用 Python 3.10+。在仓库根目录执行：

```bash
pip install -e .
pip install torch numpy transformers
```

如果只学习从零训练小模型，主要需要：

```bash
pip install torch numpy
pip install -e .
```

如果运行 `generate.ipynb` 加载预训练 GPT-2，则还需要：

```bash
pip install transformers
```

## 如何阅读

推荐顺序：

1. `docs/learning_guide.html`
2. `learning_guide.ipynb`
3. `projects/adder/adder.py`
4. `mingpt/model.py`
5. `mingpt/trainer.py`
6. `generate.ipynb`

学习时重点看三个问题：

- `x` 是模型看到的内容，`y` 是它要预测的下一个 token
- `loss` 决定哪些位置真正参与学习
- `attention` 让每个位置从左侧上下文中取信息

## 关于 generate.ipynb 的磁盘提醒

`generate.ipynb` 会通过 `from_pretrained(model_type)` 下载 Hugging Face 上的 GPT-2 权重。

当前默认设置是：

```python
model_type = 'gpt2'
allow_large_models = False
```

不要随手改成：

```python
model_type = 'gpt2-xl'
```

`gpt2-xl` 会下载数 GB 权重，并且加载时需要大量内存/显存。学习生成流程用 `gpt2` 就够了。

如果硬盘空间紧张，可以清理 Hugging Face 缓存：

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.cache\huggingface\hub\models--gpt2*"
```

## 这个版本相对原版 minGPT 改了什么

- 增加中文 HTML 学习书
- 增加练习 Notebook
- 给 `mingpt/model.py`, `trainer.py`, `bpe.py` 等文件加入教学注释
- 修正学习材料里的若干概念错误和会误导运行的示例
- 给 `generate.ipynb` 增加大模型下载保护
- 强化 adder 项目的解释：反向编码和 `ignore_index=-1` 是两件不同的事

## 运行检查

轻量检查：

```bash
python -m json.tool learning_guide.ipynb
python -m json.tool generate.ipynb
node --check docs/learning_guide.js
```

原始测试：

```bash
python -m unittest discover tests
```

注意：部分测试可能涉及 Hugging Face GPT-2 权重加载，可能触发模型下载。

## 上游项目

原始 minGPT：

```text
https://github.com/karpathy/minGPT
```

本仓库是学习注释版，保留 minGPT 的教育用途，同时增加中文可执行学习文档。

## License

MIT
