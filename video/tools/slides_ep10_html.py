# -*- coding: utf-8 -*-
"""Ep 10 — Hallucination & Evaluation (EN deck + narration)."""
import os

import slides_kit as kit

kit.FOOTER = "minGPT Learning Book · Ep 10 · Hallucination & Evaluation"
kit.TOTAL = 9

SLUG = "ep10-hallucination-evaluation"
PNG_SUBDIR = "ep10-en"
VOICE = "en-US-AndrewNeural"

NARR = [
    "Episode ten. Ask GPT-2 for a biography of a person who doesn't exist. It writes one — fluent, detailed, completely fabricated. It was never lying. It was never capable of not. Today we make hallucination make sense, and then we ask the harder question: how would you even measure whether a language model is any good?",
    "First, the honest definition. A language model is a next-token distribution conditioned on context. It is not a database. It has no truth module, no source citations, no memory beyond its window. What it has is an objective that rewarded PLAUSIBLE continuations for trillions of tokens. Fluency and truth are different skills — and only one of them is directly optimized.",
    "So hallucination is structural, not a bug to patch. The model asked about something outside its weights doesn't say I don't know — nothing in the objective ever rewarded that. It samples from the nearest plausible manifold: fluent fabrication, delivered with total confidence. Which is why confidence tells you nothing: confidence measures probability under the model, not correctness in the world.",
    "The standard mitigations, one line each. Grounding: put real documents in the context — retrieval-augmented generation. Tool use: let the model look things up instead of guessing. Calibration: train the model to say unsure when it should. All three manage the symptom by adding truth from outside. None changes the underlying machine — remember that the next time a demo looks magical.",
    "Now measurement. Internal quality: perplexity — literally e to the power of the average loss from episode seven. Loss two-point-three over a ten-word vocabulary is perplexity ten: the model is effectively as uncertain as a ten-sided die. Task quality: benchmarks — multiple choice, code tests, math. And perplexity has a catch: it measures the model against ITS training distribution, not against your needs.",
    "Benchmarks have their own traps, and each one has burned the field. Contamination: the test set leaked into the training data. Saturation: a benchmark stops discriminating once everyone aces it. Goodhart's law: once a benchmark becomes the target, it ceases to be a good measure. When you read model-X-beats-model-Y, ask: same eval? same prompts? same answer parser? contamination checked?",
    "Which builds your skeptic's checklist, top to bottom. One: same benchmark for both models? Two: identical prompts and format? Three: who parsed the answers — a fair script or the authors' code? Four: is the benchmark older than the models — could it be in the training data? Five runs, error bars: did they? Default to running evals yourself. It's the real bottleneck of agent progress — and the bridge to next episode.",
    "Your homework: find one claim from any LLM this week and trace it to a primary source. Note how often plausible is not true. Next episode: how all of this became the coding agents you use every day — context engineering and loop engineering.",
]


def deck():
    return [
        kit.title("minGPT LEARNING BOOK · EPISODE 10",
                  "Hallucination & Evaluation", "fluent \u2260 true \u00b7 how to measure a language model",
                  chips=["plausible \u2260 correct", "perplexity", "Goodhart"],
                  tagline="the skeptic's episode", page=1),
        kit.statement("Ask GPT-2 for a biography of someone who <span style=\"color:var(--orange)\">doesn't exist</span>.",
                      "It writes one \u2014 fluent, detailed, fabricated.<br>"
                      "It was never lying. <b style='color:var(--blue)'>It was never capable of not.</b>", page=2),
        kit.two_panel("KNOW WHAT YOU'RE USING", "What it is \u00b7 what it isn't",
                      "<div style='font-size:28px;line-height:2;color:var(--mut)'>"
                      "\u2713 A next-token distribution, conditioned on context<br>"
                      "\u2713 A compressor of its training data's patterns<br>"
                      "\u2713 Optimized, for trillions of tokens, on <b style='color:var(--ink)'>plausibility</b></div>",
                      "<div style='font-size:28px;line-height:2;color:var(--mut)'>"
                      "\u2717 A database of facts<br>"
                      "\u2717 A truth module with citations<br>"
                      "\u2717 Able to say \u201cI don't know\u201d \u2014 nothing ever rewarded that</div>",
                      page=3, left_color="var(--green)", right_color="var(--orange)",
                      left_head="IT IS", right_head="IT IS NOT"),
        kit.cards("WHY HALLUCINATION IS STRUCTURAL", "Not a bug to patch", [
            ("MECHANISM", "Plausible was the reward", "Fabrication that reads well scores the same as truth under next-token loss.", "var(--orange)"),
            ("MECHANISM", "No lookup by default", "Weights are frozen at training time; the world moved on. No source to cite.", "var(--purple)"),
            ("MECHANISM", "Confidence \u2260 calibration", "Confidence measures probability under the model \u2014 not correctness in the world.", "var(--red)"),
        ], page=4, note="mitigations manage the symptom with outside truth: RAG \u00b7 tool use \u00b7 calibration training"),
        kit.table("MEASURING A LANGUAGE MODEL", "Two lenses, both with traps", 5,
                  ["Lens", "What it measures", "The trap"],
                  [["Perplexity", "exp(avg loss) \u2014 internal fit", "measures fit to ITS training distribution, not your needs"],
                   ["Task benchmarks", "accuracy on curated tasks", "contamination \u00b7 saturation \u00b7 Goodhart's law"]],
                  note="perplexity example: loss 2.30 over a 10-token vocab \u2192 ppl = 10 \u2014 a fair ten-sided die of uncertainty",
                  hl_col=1, widths="0.8fr 1.4fr 1.8fr"),
        kit.flow("THE SKEPTIC'S CHECKLIST", "Before believing \u201cmodel X beats model Y\u201d",
                 [("Same eval?", "for both models", "var(--blue)"),
                  ("Same prompts?", "format matters", "var(--purple)"),
                  ("Fair parser?", "who graded the answers", "var(--orange)"),
                  ("Contamination?", "is the test in the training data", "var(--red)")],
                 page=6,
                 note="and: error bars over several runs? \u2014 when in doubt, run the eval yourself"),
        kit.homework("HOMEWORK",
                     ["Find one LLM claim this week; trace it to a primary source.",
                      "Note how often \u201cplausible\u201d \u2260 \u201ctrue\u201d."],
                     "Next episode", "From GPT to Coding Agents"),
        kit.end("Next episode", "From GPT to Coding Agents", "context engineering \u00b7 loop engineering",
                read="Read along: docs/learning_guide.html · #hallucination, #evaluation",
                run="Run along: generate.ipynb \u2014 make it hallucinate, live"),
    ]


if __name__ == "__main__":
    kit.write_deck(os.path.join(os.path.dirname(__file__), "..", "build", "ep10", "html", "slides_ep10_en.html"),
                   "en", deck())
