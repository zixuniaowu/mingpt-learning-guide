# Ep 11 — From GPT to Coding Agents (OUTLINE — expand before recording)

Source: `docs/learning_guide.html` → #agent-engineering
Notebook: none — this episode is concept + live product demos (optional CLI screencast)
Target: ~14 min · Status: OUTLINE

## Cold open
"Codex and Claude Code are, at the bottom, the same slot machine from Ep 08 — except one of the tokens it can emit is *run this shell command*. Everything you've learned this series is the engine; this episode is the chassis."

## Segments

1. **The agent loop: act → observe → act** (~3 min)
   - [SHOW: #agent-engineering — the agent loop diagram]
   - Key points: model emits a tool call; environment executes; result returns as a token in context; repeat until a stop condition. GPT + tools + loop = agent. No new magic.

2. **Context engineering** (~3 min)
   - [SHOW: the context-window budget figure]
   - Key points: deciding what enters THIS turn — system prompt, files, memories, tool outputs; the window is a scarce resource you spend deliberately; retrieval vs stuffing; context rot as conversations grow.

3. **Loop engineering** (~3 min)
   - Key points: the outer mechanism that keeps an agent useful across turns — goals, plans, verification steps, stop criteria; "the model proposes, the loop disposes"; why agents that can RUN TESTS outperform agents that can only type code (ties back to Ep 10: verification against hallucination).

4. **Where your series knowledge shows up in real products** (~3 min)
   - Mapping table on screen:
     - tokens/BPE (Ep 03) → why agent CLIs bill per file read
     - context window (Ep 01/09) → why agents summarize and re-grep
     - temperature/top-k (Ep 08) → why code agents run near temperature 0
     - loss mask (Ep 07) → chat training: only assistant turns (or tool calls) carry loss
     - KV cache (Ep 08) → prompt caching pricing tiers

5. **A respectful toolscape** (~1.5 min)
   - Key points: Codex CLI, Claude Code, skills, hooks, subagents, MCP — same loop, different ergonomics; pick one and learn it deeply; the concepts transfer.

## Code moment (mandatory)
- [RUN: a scripted 60-second terminal session of any coding agent fixing a trivial bug with a test loop — record заранее, cut tight]
- Narrate live: "watch for: tool call → observation → refined attempt" — name each loop iteration as it happens.

## Outro + [TRY]
- Try: draw the act/observe loop for your favorite AI tool; label what enters context each turn.
- Tease Ep 12: the finale — where all the code lives, and how to keep learning after the series.
