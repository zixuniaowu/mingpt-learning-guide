# Ep 06 — Activations: GELU & Softmax (OUTLINE — expand before recording)

Source: `docs/learning_guide.html` → #activations, #gelu, #softmax
Notebook: optional — plot GELU vs ReLU with matplotlib in a scratch cell
Target: ~9 min · Status: OUTLINE

## Cold open
Two tiny functions decide how "spiky" or "smooth" your network thinks. Meet the only two nonlinearities a GPT needs.

## Segments

1. **Why nonlinearity at all** (~2 min)
   - Key points: stacked linear layers = one linear layer; activations are the reason depth means anything.

2. **ReLU: the brutal gate** (~1.5 min)
   - [SHOW: #gelu — ReLU vs GELU curve figure]
   - Key points: max(0, x); dead-neuron problem; gradient is a step function.

3. **GELU: the soft gate** (~3 min)
   - [SHOW: the interactive GELU chart (#chart-gelu) — hover live on screen]
   - Key points: x · Φ(x) — "release proportional to Gaussian probability"; smooth, small negatives survive; NewGELU tanh approximation — same curve, cheaper; this is what minGPT uses.

4. **Softmax: scores to probabilities** (~2 min)
   - [SHOW: the interactive softmax chart (#chart-softmax)]
   - Key points: exponentiate then normalize; max-subtraction trick for numerical stability; appears TWICE in a GPT (attention weights + generation sampling) — connect to Ep 04 and Ep 08.

## Code moment (mandatory)
- [RUN: scratch cell — plot GELU exact vs NewGELU approximation vs ReLU in matplotlib; show max difference]
- [EDIT: change softmax input scale ×10 — watch it become one-hot; connect to temperature]

## Outro + [TRY]
- Try: numerically verify softmax invariance — softmax(x) == softmax(x + 100).
- Tease Ep 07: pieces assembled — now make the model learn.
