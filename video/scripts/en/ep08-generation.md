# Ep 08 — Generation: One Token at a Time

Source: `docs/learning_guide.html` → #generation
Notebook: `learning_guide.ipynb` Step 9, `generate.ipynb`
Target: ~11 min · Status: FULL SCRIPT

---

## Cold open (0:00–0:45)

**[SAY]**
"When ChatGPT answers a long question, it is not handing you a completed thought. It is playing a slot machine — thousands of times. Predict one token. Append it. Predict again.
That sounds too dumb to work. Today we'll see why it works, what temperature and top-k actually do to the slot machine, and we'll make two models talk: a *randomly initialized* one — pure gibberish — and a pretrained GPT-2 — fluent English. Same code, one difference: training."

---

## Segment 1 — The autoregressive loop (0:45–2:30)

**[SHOW: #generation — the autoregressive loop figure: read context → predict next → append → repeat]**

**[SAY]**
"Here is `generate()`, the whole thing:
Take your prompt — a list of token IDs. Run the forward pass. Take the logits from the *last position only* — the model's guess for what comes next. Pick one token from that distribution. Append it to the sequence. Feed the whole thing back in. Repeat until you hit a length limit or an end-of-text token.
That's it. Twenty lines of code in minGPT. No planner, no memory of the paragraph it's writing, no intention — just next-token prediction, recursively eating its own output. When people say 'autoregressive', this loop is what they mean.
And notice what this explains for free: why LLM answers *unroll* token by token in chat interfaces. You are literally watching the loop run."

---

## Segment 2 — A random model writes… (2:30–4:00)

**[RUN: Step 9 · cell 1 — generate from the trained-in-Step-8 model AND contrast with random init]**

**[SAY]**
"First, our adder-trained nano model tries to 'write'. What comes out is digit soup — of course it is: we trained it only on arithmetic answers, so digits are the only future it has ever been rewarded for predicting.
This is worth a slow beat: the model has no notion of 'topic'. Its output distribution *is* its training data, compressed. Change the data, and generation changes personality."

**[EDIT: swap in a freshly initialized model, regenerate — viewers predict the difference before running]**

---

## Segment 3 — Temperature and top-k (4:00–7:00)

**[SHOW: the sampler playground toy in the HTML book (#sampler-toy)]**

**[SAY]**
"So how do we pick the next token? The book has a live playground — five candidate words with fixed logits. Let's play.
At temperature one — that's raw softmax, the model's honest opinion. Now drag temperature *down*, toward zero point three: the distribution sharpens; 'the' dominates. Low temperature makes the model *boring and safe* — same answers every time. Now push it *up*, to two: the distribution flattens; even 'xyz' — the junk token — occasionally wins. High temperature is *creative and drunk*.
Temperature works by dividing the logits before softmax. Below one: amplify differences. Above one: mute them. Temperature zero — just always take the argmax — is called greedy decoding: deterministic, and prone to repetition loops."

**[EDIT: set top-k to 2, click sample several times; then temperature 0.3, sample again]**

**[SAY]**
"Top-k is the second dial, and it's a *safety net*, not a flavor knob. It says: whatever the temperature did, only the k most likely candidates may survive; everything else gets minus infinity before softmax.
Why do you want that? Because a flattened distribution gives every token — including 'xyz' — a non-zero chance. Top-k draws a hard floor: the tail of the distribution is *banned*, not just unlikely.
MinGPT's generate does exactly this: temperature divide, top-k cutoff, softmax, multinomial sample. Three lines, and they are the same three lines inside every production LLM API you've ever called."

---

## Segment 4 — Real GPT-2, real English (7:00–9:00)

**[RUN: generate.ipynb · load gpt2 + generate]**

**[SAY]**
"Now the payoff episode moment: the same generate loop, but the weights come from OpenAI's pretrained GPT-2 — one hundred twenty-four million parameters, trained on WebText.
Same minGPT class, same sampling code — one call to `from_pretrained` swaps in trained weights. Watch it complete 'Hello, my dog is a little'…
Fluent, grammatical, weirdly confident. And also — remember this for the evaluation episode — *plausible nonsense* at times. Fluency and truth are different skills; GPT-2 already had the first one in 2019.
One safety note, on screen: this notebook refuses to download gpt2-medium and larger unless you explicitly flip a flag. The guard exists because those checkpoints are gigabytes and add nothing to the lesson. Leave it alone."

**[PAUSE: let the generated text stay on screen]**

---

## Segment 5 — The cost of simplicity (9:00–10:30)

**[SHOW: #generation — cache discussion, or a whiteboard: T grows each step]**

**[SAY]**
"One honest engineering note. Our generate recomputes the *entire* forward pass for the *entire* sequence, every single step. Generate one hundred tokens from a ten-token prompt: over a hundred full passes, most of them recomputing attention over tokens it has already seen — every time.
Production inference engines fix this with the KV cache: remember each token's Keys and Values from the moment you computed them, and each new step only processes *one* token instead of the whole history. Faster, and the output is identical.
minGPT skips the cache on purpose — caching would double the code of this chapter for zero extra insight. But now that you can name the inefficiency, you understand what every inference library is selling."

## Outro (10:30–11:00)

**[SAY]**
"Recap: generation is the next-token loop eating its own output; temperature sharpens or flattens the choice; top-k amputates the tail; KV caches make it fast.
That completes the technical core of the series: tokens in, attention, blocks, training, generation. The remaining episodes zoom out — scaling laws, hallucination and evaluation, and how all of this became the coding agents you use every day.
Homework: in the sampler playground, find a temperature where 'xyz' wins about one time in ten. Then explain — using the softmax curve — why that temperature is exactly where it is."

**[TRY]**
Sampler playground: tune temperature until the junk token wins ~10% of samples; justify the value via the softmax curve.
