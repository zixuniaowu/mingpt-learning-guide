# -*- coding: utf-8 -*-
"""Ep 11 — From GPT to Coding Agents (EN deck + narration)."""
import os

import slides_kit as kit

kit.FOOTER = "minGPT Learning Book · Ep 11 · Coding Agents"
kit.TOTAL = 9

SLUG = "ep11-coding-agents"
PNG_SUBDIR = "ep11-en"
VOICE = "en-US-AndrewNeural"

NARR = [
    "Episode eleven. Codex, Claude Code, and every coding agent you've used are — at the bottom — the slot machine from episode eight. With one difference: one of the tokens it can emit is run this shell command. Everything this series taught you is the engine. This episode is the chassis: the loop that wraps the model until it can do work.",
    "The agent loop. The model doesn't answer; it emits a special action — a tool call: read this file, run these tests, search the code. The environment executes it, and the result comes back as tokens in the model's context. The model reads the observation and emits the next action. Observe, act, observe, act — until a stop condition. GPT plus tools plus this loop equals agent. There is no new magic in there — you've already met every part.",
    "Two engineering disciplines make the loop useful. Context engineering: deciding what enters THIS turn. The window from episode one is a scarce budget — system prompt, relevant files, memory, tool outputs — every token competes. Retrieval beats stuffing; stale context rots. Loop engineering: the outer mechanism that keeps the agent honest across turns — goals, plans, verification steps, and stop criteria, so it iterates instead of rambling or stopping early.",
    "And here is the bridge to episode ten: verification is the superpower. An agent that can RUN TESTS doesn't have to trust its own fluency — the environment grades it. Hallucinate an API? The import fails, the error lands in context, the loop tries again. Agents that can execute outperform agents that can only type, for exactly the reason you can now articulate: external truth versus internal plausibility.",
    "Everything from this series shows up in the products, with price tags attached. Tokenization — why agents bill per file read. Context window — why they summarize, re-grep, and forget. Temperature near zero — why code agents run cold and deterministic. The loss mask — why only assistant actions and tool calls carry training loss in agent fine-tuning. KV cache — why prompt caching makes repeat turns cheaper. The concepts were free; now they're line items.",
    "The toolscape, briefly and respectfully. Codex CLI, Claude Code, skills, hooks, subagents, MCP — they are the same loop with different ergonomics. Don't chase all of them. Pick one, learn its loop deeply, and you've learned them all — because now you know what to look for: what enters context, what executes tools, and what stops the loop.",
    "Your homework: draw the act-observe loop for your favorite AI tool. Label what enters context each turn, what executes actions, and what decides to stop. Next episode — the finale: the actual code, top to bottom, and three projects you can extend tonight.",
]


def deck():
    return [
        kit.title("minGPT LEARNING BOOK · EPISODE 11",
                  "From GPT to Coding Agents", "context engineering · loop engineering",
                  chips=["tool calls", "the loop", "verification"],
                  tagline="the slot machine, given hands", page=1),
        kit.statement('An agent is the Ep-08 slot machine \u2014 except one token can <span style="color:var(--green)">run a shell command</span>.',
                      "Everything this series taught you is the engine.<br><b>This episode is the chassis: the loop.</b>", page=2),
        kit.flow("THE AGENT LOOP", "act \u2192 observe \u2192 act",
                 [("Model", "emits a tool call", "var(--blue)"),
                  ("Environment", "executes it for real", "var(--orange)"),
                  ("Observation", "result \u2192 context", "var(--green)"),
                  ("Model again", "reads & decides", "var(--purple)"),
                  ("\u2026until stop", "goal met / budget", "var(--red)")],
                 page=3, gap=10,
                 note="no new magic: every part is one you already know \u2014 tools + tokens + the loop"),
        kit.two_panel("TWO DISCIPLINES", "What enters \u00b7 what stops",
                      "<div style='font-size:28px;line-height:1.9;color:var(--mut)'>"
                      "<b style='color:var(--ink)'>Context engineering</b> \u2014 what enters THIS turn.<br>"
                      "System prompt, files, memory, tool outputs: every token competes for a scarce window (Ep 01).<br>"
                      "Retrieval beats stuffing. Stale context rots.</div>",
                      "<div style='font-size:28px;line-height:1.9;color:var(--mut)'>"
                      "<b style='color:var(--ink)'>Loop engineering</b> \u2014 what keeps it honest across turns.<br>"
                      "Goals, plans, verification steps, stop criteria.<br>"
                      "So it iterates instead of rambling \u2014 or stopping early.</div>",
                      page=4, left_color="var(--blue)", right_color="var(--green)",
                      left_head="CONTEXT", right_head="LOOP"),
        kit.statement('Agents that can <span style="color:var(--green)">run tests</span> beat agents that can only type.',
                      "The environment grades the output \u2014 hallucinated API \u2192 import fails \u2192 error lands in context \u2192 retry.<br>"
                      "<b>External truth vs internal plausibility.</b> That's Ep 10, weaponized.", page=5),
        kit.table("THIS SERIES, ON YOUR INVOICE", "Where each concept shows up in products", 6,
                  ["Series concept", "Product reality"],
                  [["Tokenization (Ep 03)", "agents bill per file read \u2014 and code tokenizes worse than prose"],
                   ["Context window (Ep 01/09)", "why agents summarize, re-grep, and forget"],
                   ["Temperature (Ep 08)", "code agents run near zero \u2014 deterministic, sane"],
                   ["Loss mask (Ep 07)", "agent fine-tuning: only assistant actions carry loss"],
                   ["KV cache (Ep 08)", "prompt caching \u2192 cheaper repeat turns"]],
                  hl_col=0, widths="1fr 2.2fr"),
        kit.homework("HOMEWORK",
                     ["Draw the act/observe loop of your favorite AI tool.",
                      "Label: what enters context, what executes, what stops the loop."],
                     "Next episode \u2014 the finale", "Projects, Labs & Wrap-Up"),
        kit.end("Next episode", "Projects, Labs & Wrap-Up", "read every line \u00b7 extend the projects",
                read="Read along: docs/learning_guide.html · #agent-engineering",
                run="Try: any coding agent CLI \u2014 with your eyes open now"),
    ]


if __name__ == "__main__":
    kit.write_deck(os.path.join(os.path.dirname(__file__), "..", "build", "ep11", "html", "slides_ep11_en.html"),
                   "en", deck())
