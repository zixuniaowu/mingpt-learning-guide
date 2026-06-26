# minGPT Learning Workspace

This is a learning workspace for studying Andrej Karpathy's [minGPT](https://github.com/karpathy/minGPT) — a minimal, clean, educational PyTorch implementation of the OpenAI GPT model.

## Quick Reference

- **Language**: Python (PyTorch)
- **Main Format**: Jupyter notebooks (.ipynb) and Python modules
- **Core Project**: https://github.com/karpathy/minGPT
- **Status**: Semi-archived (educational focus; newer [nanoGPT](https://github.com/karpathy/nanoGPT) for production use)

## Project Structure

```
mingpt/              # Main library (3 core files)
├── model.py        # Transformer architecture (~300 lines, clean and minimal)
├── bpe.py          # Byte Pair Encoder for tokenization
└── trainer.py      # PyTorch training boilerplate

projects/           # Example projects demonstrating usage
├── adder/          # Trains GPT to add numbers from scratch
└── chargpt/        # Character-level language model

demo.ipynb          # Simple sorting task example
generate.ipynb      # Load pretrained GPT-2 and generate text
tests/              # Unit test suite
setup.py            # Package installation
```

## Core Concepts

### Three Main Components

1. **Model** (`mingpt/model.py`)
   - Pure Transformer decoder architecture
   - ~300 lines of interpretable code
   - Supports different sizes (GPT-1, GPT-2, GPT-3-style configs)
   - Clean initialization following original papers
   - Uses layer normalization, GELU activation, learned position embeddings

2. **Tokenizer** (`mingpt/bpe.py`)
   - Byte Pair Encoding implementation (from OpenAI)
   - Converts between text and integer sequences
   - Vocabulary size typically 50,257 for GPT-2

3. **Trainer** (`mingpt/trainer.py`)
   - Config-based training loop
   - Handles batching, mixed precision, device management
   - Works with any `torch.utils.data.Dataset` subclass

### Training Workflow

```python
from mingpt.model import GPT
from mingpt.trainer import Trainer

# 1. Define model
model_config = GPT.get_default_config()
model_config.model_type = 'gpt2'
model = GPT(model_config)

# 2. Prepare dataset (subclass torch.utils.data.Dataset)
train_dataset = YourDataset()

# 3. Configure and run trainer
train_config = Trainer.get_default_config()
train_config.max_iters = 1000
train_config.batch_size = 32
trainer = Trainer(train_config, model, train_dataset)
trainer.run()

# 4. Generate with model.generate()
```

## Common Tasks

### Setting Up the Environment
```bash
pip install torch numpy
pip install -e .  # Install minGPT as editable package
```

### Running Tests
```bash
python -m unittest discover tests
```

### Running Notebooks
- Open `demo.ipynb` to understand basic model and trainer usage on a sorting task
- Open `generate.ipynb` to load pretrained GPT-2 weights and generate text

### Creating a Custom Project
1. Create dataset by subclassing `torch.utils.data.Dataset` that emits `(x, y)` pairs where x and y are `torch.LongTensor` with integers in range `[0, vocab_size)`
2. Use GPT and Trainer classes with configs from examples
3. Follow the structure in `projects/adder` or `projects/chargpt`

## Key Design Patterns

- **Config-driven**: Both `GPT` and `Trainer` use `.get_default_config()` pattern
- **Interpretability first**: Code prioritizes clarity over optimization (this is educational software)
- **Minimal dependencies**: Just PyTorch, numpy, and tokenizers
- **Dataset abstraction**: Any `torch.utils.data.Dataset` works, supports arbitrary sequence lengths up to context window

## Important Notes

- **Context window**: Default is 1024 tokens (block_size)
- **Vocabulary**: GPT-2 uses 50,257 tokens
- **Architecture details**: Follow GPT-2 modifications (pre-normalization, learned position embeddings)
- **Educational focus**: Code favors clarity; not optimized for production scale training

## Learning Path

1. Start with [README.md](README.md) for project overview
2. Study [mingpt/model.py](mingpt/model.py) — understand the Transformer architecture
3. Run [demo.ipynb](demo.ipynb) — see training in action on sorting task
4. Study [mingpt/trainer.py](mingpt/trainer.py) — understand training loop
5. Explore [projects/adder](projects/adder) — minimal training example
6. Run [generate.ipynb](generate.ipynb) — generate text with pretrained GPT-2
7. Create your own dataset and train on [projects/chargpt](projects/chargpt) pattern

## When Working with Code

- Study `mingpt/model.py` line-by-line to understand Transformer architecture
- Trace through `demo.ipynb` to see training and generation in action
- Examine `projects/adder` to understand how to create a minimal training setup
- Modify `projects/chargpt` to train on different text files (GPT-2 fine-tuning analogue)

## Project Status

This project is in "semi-archived" state. It remains an excellent educational reference. For production or larger-scale experiments, consider:
- [nanoGPT](https://github.com/karpathy/nanoGPT) by Karpathy (updated, production-ready)
- [Hugging Face Transformers](https://github.com/huggingface/transformers) (full-featured)
