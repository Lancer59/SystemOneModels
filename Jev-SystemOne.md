# Jev: TypeSafe AI's System One Model

> Research compiled from the LangChain blog, TypeSafe AI launch post, MarkTechPost, TrueFoundry, OmniaKey, and AIWiki — September 20, 2026.

---

## What Is Jev?

Jev is the first model released by **TypeSafe AI**, a company founded by Diogo Almeida (previously at OpenAI, one of the researchers behind the instruction-following work that became ChatGPT), Erik Gafni, and Sasha Sheng. It launched in September 2026 alongside a $40M seed round.

**Jev is not a Large Language Model.** It does not generate text. It is what TypeSafe calls a **System One model** — a class of AI model built specifically to make fast, structured decisions that software can consume directly, without a human in the loop.

The name comes from two sources:
- **William Stanley Jevons**, the economist whose paradox states that falling costs drive rising consumption.
- **Daniel Kahneman's "System 1"** (from *Thinking, Fast and Slow*) — fast, intuitive, automatic thinking, as opposed to the slow, deliberate "System 2."

---

## Why Does This Exist? The Problem It Solves

The core argument TypeSafe makes is:

> Models have been superhuman at chat for years. So where is all the automation?

The bottleneck, they argue, isn't raw intelligence — it's that a model which **replies in prose** is an awkward component to build software on top of. Today's AI was effectively trained on the assumption that a human always sits on the other side of it.

Inside any running AI agent or application, the decisions being made are mostly **small, repetitive, and structured**:
- Is this ticket urgent?
- Which queue does this message belong in?
- Does this response violate policy?
- Which of these candidates is the most relevant?

Sending each of those to a frontier chat model works, but you pay **generation latency and generation prices** for something that is closer to a lookup. That is the gap Jev targets.

---

## What Is a System One Model?

A System One model is defined by **what it gives up**.

| Property | Chat LLM | System One (Jev) |
|---|---|---|
| Output | Free-form strings | Typed values from a pre-declared schema |
| Sampling | Sequential, one token at a time | Parallel — all fields in one pass |
| Confidence | Overconfident, inconsistent | Calibrated probability on every field |
| Latency | 3–329 s (frontier models) | 70–500 ms (vendor-reported) |
| Input price | ~$0.20–$10 / MTok | $0.042 / MTok |
| Output price | Roughly 5x input | Free ("too cheap to meter") |
| Failure mode | Can hallucinate, refuse, or emit broken shapes | Cannot leave the schema; can still pick the wrong valid option |
| Best fit | Drafting, coding, multi-step reasoning | Classify, route, score, verify — decisions inside code |

Instead of generating a sequence of tokens until it forms a sentence, Jev evaluates the **entire structured answer space in one parallel pass**. You declare the output shape up front; the model fills it in with probabilities.

---

## How Jev Works: The API

You interact with Jev by sending it a **state** (the context — text, JSON, or an array of text values) and a set of **questions** about that state. It returns typed answers with calibrated probabilities.

**Single endpoint:** `POST https://api.typesafe.ai/v1/systemone`

### Example request

```json
{
  "model": "jev-latest",
  "state": "Hi, I've been trying to connect my Stripe account for 3 days and it keeps failing. I'm losing sales. Please help ASAP.",
  "questions": {
    "is_urgent": {
      "type": "noul",
      "instructions": "The message conveys urgency or time-sensitivity"
    }
  }
}
```

### Example response

```json
{
  "is_urgent": {
    "type": "noul",
    "noul": 0.999
  }
}
```

A 99.9% probability that this message is urgent — something your code can branch on directly.

---

## The Three Question Types

These are the core primitives of the API, not formatting options layered over generation.

### 1. Noul
A yes-or-no question. Returns a probability from 0 to 1 that the statement is true.

```python
"is_urgent": Noul(instructions="The message conveys urgency or time-sensitivity")
# Returns: {"noul": 0.999}
```

Best for: detection, verification, binary gates, guardrail checks.

---

### 2. Choice
Pick one option from a closed list. Returns the selected option, the probability distribution across all options, and a confidence score.

```python
"department": Choice(
    instructions="Which team should handle this?",
    criteria={
        "billing": "Payment issues",
        "technical": "Bugs and product failures",
        "sales": "Upgrade or pricing inquiries"
    }
)
# Returns: {"choice": "billing", "probabilities": {...}, "confidence": 0.84}
```

Supports up to 255 options. Best for: intent routing, classification, categorization.

---

### 3. Score
Rate an input against a set of **ordered descriptive levels** (e.g. low, medium, high). Returns a continuous score, the probability distribution over levels, and confidence.

```python
"severity": Score(
    instructions="Rate the business impact",
    levels=["low", "medium", "high", "critical"]
)
# Returns: {"score": 2.7, "probabilities": {...}, "confidence": 0.91}
```

Best for: severity rating, quality scoring, risk bands, urgency levels.

---

## Asking Multiple Questions in One Request

One of Jev's most practical features: **all questions in a single request are evaluated in parallel**, against the same state.

```python
from langchain_typesafe import Noul, Choice, TypeSafeClassifier

classifier = TypeSafeClassifier()

response = classifier.invoke(
    state="The deploy failed twice and customers are seeing 500s. Can someone look now?",
    questions={
        "department": Choice(
            instructions="Which team owns this?",
            criteria={"backend": "Server errors", "sre": "Deployment issues"}
        ),
        "urgent": Noul(instructions="Does this need attention right now?"),
        "severity": Score(
            instructions="Rate the business impact",
            levels=["low", "medium", "high", "critical"]
        )
    },
)
```

Adding more questions **barely changes response time** and costs only the extra input tokens, which are cheap. This is a direct consequence of parallel sampling — there is no sequential token-by-token generation bottleneck.

---

## How It Differs from a Traditional Classifier

Jev is not a traditional ML classifier either. The key difference is **request-time flexibility**:

| Dimension | Jev | Traditional Classifier |
|---|---|---|
| Output space | Defined per request | Fixed by training |
| New rubric | Describe it in the request | Collect data and retrain |
| Probabilities | First-class API output | Common, if exposed |
| Text generation | No | No |
| Best role | Semantic branch inside a workflow | Stable high-volume task with labeled data |

You don't need labeled training data or a fine-tuning run to add a new classification category. You describe what you want in natural language in the request itself.

---

## The Training Method: RLCD

TypeSafe trained Jev using **Reinforcement Learning for Calibrated Decisions (RLCD)**.

The key distinction from standard RLHF (Reinforcement Learning from Human Feedback) used to train chat models:
- **RLHF** optimizes for human preference — which response people like more.
- **RLCD** optimizes for **calibrated probabilities** — the confidence score should actually match accuracy across groups of predictions. If Jev says 80% confident, it should be right roughly 80% of the time on comparable cases.

This calibration is what makes the model useful for automation: a model that is right 95% of the time but cannot tell you which 5% are wrong cannot be fully automated around. One with honest uncertainty can be — route the low-confidence cases to a human or a bigger model.

TypeSafe has not disclosed the model architecture or parameter count.

---

## Speed and Cost Claims

TypeSafe reports:
- **70–500 ms** end-to-end response time
- **$0.042 per million input tokens** (output is currently free)
- Up to **193.6x faster** and **444.6x cheaper** than frontier LLMs on System One-shaped tasks

For context, a single call in their demo: Jev finished in **0.114 seconds for $0.000081**. GPT-5.6 Terra took **8.566 seconds for $0.013880** on the same task.

**Important caveats (TypeSafe's own disclosures):**
- The workflow benchmarks were created by TypeSafe's own model-capabilities team.
- The reference answer is the average of GPT-6 Astra and Fable 5.1, which may bias results.
- Latency runs were made from company laptops on the US West Coast.
- TypeSafe acknowledges these figures represent the **high end** of expected real-world gains.
- They cannot prove the price is not subsidized.

Take the specific multiples with appropriate skepticism. The directional claim — that parallel structured sampling over a constrained output space is faster and cheaper than sequential token generation — is mechanically sound.

---

## "Zero Hallucinations" — What That Actually Means

TypeSafe markets Jev as unable to hallucinate. This claim is precise in one sense and misleading in another.

**What is true:** Jev cannot generate a value outside the declared answer schema. A Choice answer cannot invent a fourth option that was not in your list. This eliminates a major class of parsing failures and schema errors. It is **schema safety by construction**, not an empirical measurement.

**What is still possible:** Jev can still select the **wrong valid option** with high confidence. Calibration is TypeSafe's answer to this, but calibration needs independent testing.

TypeSafe's own Jev 1.13 documentation lists known failure modes:
- Literal readings and missed implied intent
- Unreliable counting, arithmetic, dates, and numeric precision
- Multi-hop indirection (reasoning through several steps)
- Long state containing irrelevant detail (accuracy degrades)
- Adversarial or prompt-injected content
- Contradictory instructions and criteria
- Probabilities that do not obey intuitive identities across separately phrased questions
- Any task that requires text generation

The practical guarantee is **zero out-of-schema generation**, not zero decision error.

---

## Context Limits

- **64K tokens** total per request (state + all questions combined)
- **32K tokens** for state + the single longest question
- More context is not automatically better — TypeSafe's own documentation warns that irrelevant detail causes accuracy to fall ("jaggedness")

---

## Where Jev Fits in the Agent Loop

The typical agent loop:

```
LLM decides what to do → tool executes → model evaluates results → repeat
```

Every step currently requires a full LLM call. Jev is designed to replace the **evaluation and routing decisions** in that loop — the parts that don't need text generation.

### Model Routing

```python
from langchain_typesafe.experimental.middleware import ModelRouterMiddleware, ModelChoice

router = ModelRouterMiddleware(
    choices={
        "fast": ModelChoice(
            model="openai:luna",
            criteria="Direct lookups, extraction, and localized changes.",
        ),
        "powerful": ModelChoice(
            model="openai:sol",
            criteria="Architecture and high-stakes decisions.",
        ),
    },
    instructions="Choose the least costly model that can complete the task.",
)
```

Jev assesses each incoming request and routes it to the cheapest model that can handle it. Fast and cheap for simple tasks, more capable for complex ones.

### Agent Guardrails (Auto Mode)

```python
from langchain_typesafe.experimental.middleware import AutoModeMiddleware

guardrail = AutoModeMiddleware(tools=["bash"])
agent = create_agent("openai:gpt-5.6-luna", middleware=[guardrail])
```

`AutoModeMiddleware` uses Jev to check every tool call before it executes. Classifies actions as deny, ask, or allow. Guardrails have to run on every call, so cost and latency are the binding constraint — this is exactly the kind of task Jev targets.

---

## Real-World Use Cases (Community Reports)

Within days of launch, the developer community built:

| Project | What it does |
|---|---|
| Vercel CEO (Guillermo Rauch) | Command safety classifier, reported up to 18x faster at p95 than GPT Luna |
| Bryo AI | Email triage at scale — Gemini was slightly more accurate but 10–20x more expensive |
| Browser Use | `jev-ultrafast` drove a Google Flights search in 7.1 seconds |
| Droidrun | Mobile agent ran Uber on a real Android phone, 9 actions in ~21 seconds |
| jevmeter | Scores every sentence of a debate for ~$0.05 |
| Steve Krouse's Typewriter | Updates 16 judgments live as you type |
| pg-jev | Adds plain-language filters to Postgres |
| HA-Jev | Turns Jev answers into Home Assistant entities |
| jev-guard | Rates each tool call as deny/ask/allow |

---

## Good Fit vs. Poor Fit

### Jev is well-suited when:
- The answer space is **bounded** (known set of categories, levels, or yes/no)
- The judgment is **semantic** rather than mathematical
- Another piece of software will **consume the result directly**
- You need to run the check on **every call** (guardrails, routing, triage)
- You need **multiple signals** about the same state simultaneously

### Jev is a poor fit for:
- Writing, summarization, drafting
- Code generation or explanation
- Open-ended extraction
- Exact arithmetic, date comparison, counting
- Long causal or multi-step reasoning
- Tasks requiring text generation of any kind
- Non-English content (English is currently strongest; CJK scripts are accepted but not benchmarked equally)

---

## Availability and Pricing

| Item | Value |
|---|---|
| Developer | TypeSafe AI |
| Model class | System One Model |
| Current versioned ID | jev-1.13.0 |
| Stable alias | jev-latest |
| Input price | $0.042 per 1M tokens |
| Output price | Free |
| Context window | 64K tokens total |
| Release status | Early access (waitlist) |
| Rate limits | 250,000 tokens/s and 1,200 req/min (subject to change) |
| Language support | English primary; other languages work but accuracy is not equally validated |

Python SDK: `pip install typesafe-sdk` (requires 3.10+)
JavaScript SDK: `@typesafe-ai/sdk`
LangChain integration: `pip install langchain-typesafe` via `TypeSafeClassifier`

---

## Summary

Jev represents a genuinely different bet in the AI landscape: that the useful next step is not a smarter chat model but a **dependable one that software can call like any other function**. Its design is coherent — parallel sampling over a constrained output space is mechanically why it is fast and cheap. The RLCD training objective, targeting calibration rather than human preference, is why the probabilities are supposed to be trustworthy enough to automate around.

It is not a replacement for an LLM. It is a **complement** — use an LLM for open-ended reasoning and generation, use Jev for fast, structured decisions along the way.

The benchmark multiples are vendor-run and should be validated on your own data. The strongest claim — calibration — has not yet been independently tested. But the direction the launch signals is real: production AI stacks are moving toward **a mix of model types chosen per task**, not a single model chosen per company.

---

*Sources: [LangChain Blog](https://www.langchain.com/blog/building-a-harness-with-jev) · [MarkTechPost](https://www.marktechpost.com/2026/09/19/typesafe-ai-releases-jev/) · [TrueFoundry](https://www.truefoundry.com/blog/typesafe-ai-jev) · [OmniaKey](https://omniakey.com/blog/jev-model-explained) · [AIWiki](https://aiwiki.ai/wiki/jev) · [TheNeuron](https://www.theneuron.ai/explainer-articles/typesafe-jev-system-one-models-explained/) · [DataCamp](https://www.datacamp.com/blog/system-one-models-jev)*
