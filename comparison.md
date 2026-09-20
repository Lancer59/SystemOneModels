# System One Model Alternatives: Complete Comparison

> Research compiled from LangChain, APIdog, Latent Space AINews, HuggingFace model cards (Laya, Cerebellum-2B), TrueFoundry, Powerdrill.ai, Omniakey — September 20, 2026.

---

## What We're Comparing

Jev kicked off a new category: **System One models** — fast, structured decision engines that take in context, evaluate typed questions, and return probabilities. No text generation at all. Within days of Jev's launch, the community shipped several open-source alternatives. This document maps the full landscape: what exists, how they compare, and which one to pick for your situation.

The contenders:

| Model | Developer | Status | Weights |
|---|---|---|---|
| **Jev 1.13.0** | TypeSafe AI | Closed API, early access | Proprietary |
| **Laya** | Convai Innovations | Open source | Apache 2.0 |
| **Cerebellum-2B** | Antigravity Team | Open source | Apache 2.0 |
| **Kev-0.5B** | Jared Palmer | Open source | Apache 2.0 |
| **OpenJev / SemIf** | Community | Open source | Apache 2.0 |
| **Bespoke Nimble** | Bespoke AI | Open source | Apache 2.0 |
| **Fine-tuned BERT/ModernBERT** | Various | Open source | Various |
| **XGBoost / Classical ML** | Various | Open source | N/A |
| **LLM + Structured Output** | OpenAI, Anthropic, etc. | API | Proprietary |

---

## The Quick Answer

| Goal | Best Pick |
|---|---|
| Zero setup, best zero-shot accuracy, needs to work today | **Jev** (TypeSafe API) |
| Open weights, self-hosted, best accuracy + calibration | **Cerebellum-2B** |
| Smallest model, runs on a MacBook, still open source | **Kev-0.5B** (0.5B params) |
| Multilingual (100+ languages) | **Laya-multilingual** |
| Lowest memory footprint on a server | **Laya** (421M, ~808MB) |
| Local, Mac, no cloud dependency | **Cerebellum-2B INT8** on Apple MPS, or **Kev-0.5B** |
| Already have labeled training data, stable categories | **Fine-tuned BERT** or **XGBoost** |
| Need generation AND classification in one system | **LLM + structured output** (GPT/Claude) |

---

## Head-to-Head Accuracy Benchmark

From Cerebellum-2B's evaluation on 95,000+ real-world agent routing, tool selection, and DOM automation tasks:

| Model | API/Tool Routing | DOM/Web | Customer Triage | Policy Rules | Safety/Escalation | Macro Avg |
|---|---|---|---|---|---|---|
| **Cerebellum-2B** | **94.90%** | **92.80%** | **96.40%** | **91.50%** | **95.20%** | **93.23%** |
| GPT-4o (Structured Output) | 89.20% | 86.10% | 91.50% | 87.80% | 82.00% | 88.67% |
| **Jev 1.13.0** | 81.10% | 78.40% | 86.20% | 84.50% | 79.00% | 82.48% |
| **Laya** | 83.80% | 80.50% | 87.10% | 77.20% | 71.50% | 80.72% |
| **Kev-0.5B** | 79.90% | 75.60% | 82.30% | 74.80% | 69.40% | 75.85% |

From Laya's benchmark on typed-decisions (different eval set, 2,000 decisions):

| Model | Accuracy | Soft Accuracy | ECE (lower = better) | Latency p50 |
|---|---|---|---|---|
| **Laya-typed-decisions** | **0.766** | 0.471 | 0.213 (0.081 after tuning) | ~33 ms |
| **Jev 1.13.0** | 0.727 | **0.580** | 0.144 | 236–276 ms |

> Jev wins on soft accuracy (its full probability distributions are closer to the teacher model's). Laya wins on hard argmax accuracy after fine-tuning on that specific benchmark's training split.

---

## Latency Comparison

| Model | Single Request Latency | Decoding Method |
|---|---|---|
| **Cerebellum-2B** | **25 ms** (batched GPU) | Non-autoregressive, O(1) |
| **Laya** | 32–40 ms (GPU) | Non-autoregressive, O(1) |
| **Kev-0.5B** | ~40 ms | Non-autoregressive, O(1) |
| **OpenJev** | ~60–100 ms | Logit read off frozen Qwen |
| **Jev 1.13.0** | 70–500 ms (API round-trip ~190–276 ms) | O(1) block mask, but adds network |
| **Fine-tuned BERT** | 10–50 ms (self-hosted) | Encoder forward pass |
| **LLM + Structured Output** | 1,500–2,800 ms | Sequential token generation |

Key insight: all of the System One alternatives are dramatically faster than LLMs. The open-source ones are also faster than Jev itself, because they run locally (no network latency).

---

## Memory / Model Size

This is where the alternatives split sharply. If you're running on CPU, edge hardware, or a small VM, this matters a lot.

| Model | Parameters | Memory Footprint | Runs On |
|---|---|---|---|
| **Kev-0.5B** | 500M (Qwen2.5-0.5B base) | ~1.1 GB | MacBook, any GPU, CPU |
| **Laya-multilingual** | 322M (mmBERT-base) | ~647 MB | Any GPU, CPU |
| **Laya** (English) | 421M (ModernBERT-large) | ~808 MB | Any GPU, CPU |
| **Cerebellum-2B INT8** | 2B (Qwen3.5-2B base) | **2.23 GB** | 16GB M4 MacBook, ~16GB VRAM GPU |
| **Cerebellum-2B FP8** | 2B | 2.23 GB | Cloud GPU (vLLM/FastAPI) |
| **Cerebellum-2B BF16** | 2B | 3.76 GB | GPU Cloud (training/eval) |
| **Bespoke Nimble** | 9B (Qwen3.5-9B base LoRA) | ~18 GB | A100/H100 class |
| **Jev 1.13.0** | Undisclosed | API only | N/A (hosted) |
| **Fine-tuned BERT-base** | 110M | ~440 MB | CPU, any GPU |
| **Fine-tuned ModernBERT-large** | 395M | ~800 MB | Any GPU |
| **XGBoost** | Varies | < 100 MB typically | CPU |

**Smallest runnable models:** Laya-multilingual (647MB) > Laya English (808MB) > Kev-0.5B (1.1GB)

---

## Cost Comparison

| Model | API Cost | Self-Host Cost |
|---|---|---|
| **Jev 1.13.0** | $0.042 / 1M input tokens (output free) | N/A (no weights) |
| **Laya** | Free (self-host) | GPU/CPU electricity only |
| **Cerebellum-2B** | Free (self-host) | GPU/CPU electricity only |
| **Kev-0.5B** | Free (self-host) | Practically $0 on CPU/MacBook |
| **OpenJev** | Free (self-host) | RTX 3090 class |
| **GPT-4o structured output** | ~$2.50–$10 / 1M input tokens | N/A |
| **Fine-tuned BERT** | Free (self-host) | Minimal |
| **XGBoost** | Free | Near zero |

Jev is already the cheapest hosted API in this space. But self-hosted open models cost essentially nothing per call, which matters for high-volume workloads.

---

## Calibration: Are the Probabilities Trustworthy?

Calibration is arguably the most important metric for automation — if a model says 80% confident, it should be right 80% of the time. A poorly calibrated model with high accuracy can still be dangerous to automate around.

| Model | Brier Score (lower = better) | Calibration Method |
|---|---|---|
| **Cerebellum-2B** | **0.0271** | Trained with RLCD + ActEscalateHead |
| **Laya** | 0.062 (ECE), 0.081 after temperature scaling | RLCD (strictly proper scoring rules) |
| **Kev-0.5B** | 0.0810 | LoRA + readout head |
| **Jev 1.13.0** | 0.1140 | RLCD (vendor-trained) |
| **GPT-4o** | 0.1620 | Overconfident logprobs |
| **XGBoost / sklearn** | Varies | Platt scaling / isotonic calibration needed |

> Cerebellum-2B actually beats Jev on calibration by a large margin in this benchmark. Laya also beats Jev after temperature scaling. This is notable because Jev's calibration is TypeSafe's central selling point.
>
> These benchmarks are from the open-source model developers themselves, not independent third parties. Take with appropriate salt.

---

## Calibration: Confident Error Rate

How often does a model say it's confident (p > 0.8) but still get it wrong?

| Model | Confident Error Rate |
|---|---|
| **Cerebellum-2B** | **2.10%** |
| Jev 1.13.0 | 5.80% |
| Laya | 7.20% |
| Kev-0.5B | 8.90% |
| GPT-4o | 11.40% |

Lower is better. Cerebellum-2B is the safest for high-stakes automation.

---

## Permutation Invariance: Order Bias

If you shuffle the order of your choice options, does the model pick differently? LLMs are notoriously sensitive to option order (primacy/recency bias). System One models are designed to be invariant.

| Model | Permutation Invariance |
|---|---|
| **Cerebellum-2B** | **99.40%** (0.60% delta) |
| Laya | 91.20% |
| Kev-0.5B | 88.50% |
| Jev 1.13.0 | 89.40% |
| GPT-4o | 84.50% (15.5% positional bias) |

Cerebellum-2B uses isolated branch attention masks to enforce this. Jev and Laya are similar. GPT-4o is the worst — this is a real production problem if you dynamically order your options.

---

## Model-by-Model Deep Dive

### Jev 1.13.0 (TypeSafe AI)

The original. Closed-source, API-only, early access (waitlist).

**Strengths:**
- Best zero-shot decision accuracy with no setup or labeled data
- Natively supports all three primitives (Choice, Score, Noul) out of the box
- Highest cardinality: up to 255 options per Choice question
- Soft accuracy is the best (probability distributions are closest to a frontier teacher model)
- 64K context window
- No GPU needed on your end

**Weaknesses:**
- No local/offline option — weights are not public
- Network round-trip adds latency (~190–276 ms measured, vs. 25–40 ms for local models)
- Calibration is worse than Cerebellum-2B and Laya-after-temperature-scaling
- English-primary; non-English accuracy not benchmarked
- Struggles on high-cardinality tasks and Banking77-style 70+ label tasks
- Weak on: arithmetic, dates, multi-hop reasoning, adversarial input

**Best for:** Teams that want it working today with zero infrastructure, or that need the full 255-option cardinality.

---

### Laya (Convai Innovations)

The most polished open-source alternative. Apache 2.0.

Three checkpoints:
- `laya` (English, 421M, ModernBERT-large) — 808 MB
- `laya-multilingual` (100+ languages, 322M, mmBERT-base) — 647 MB  
- `laya-typed-decisions` (fine-tuned for workflows) — 421M

**Strengths:**
- The only model with genuine multilingual support (100+ languages, tested on 51)
- After temperature scaling, ECE of 0.081 — **3x better calibrated than Jev**
- Beats Jev on argmax accuracy (0.766 vs 0.727) on typed-decisions benchmark after fine-tuning
- Smallest footprint of any multi-primitive model (647 MB for multilingual)
- Supports all three primitives (Choice, Score, Noul)
- Same RLCD training objective as Jev (strictly proper scoring rules)
- Smart Router: auto-detects language and dispatches to correct checkpoint in <0.5ms
- Free, fully local, no API key, no waitlist
- 6–8x faster than Jev on a single-question latency

**Weaknesses:**
- Base checkpoints are near-random on typed-decisions zero-shot (0.362) — needs fine-tuning for serious work
- Weak on high-cardinality (50+ options) at default context budget — Jev handles Banking77 at 0.870 vs Laya's 0.425
- Ordinal score questions are the weakest primitive (SST-5: 0.372)
- Calibration needs temperature scaling step on your own data
- Context limited to 512 tokens (English) or 1024 (multilingual) by default

**Best for:** Multilingual use cases, cost-sensitive/self-hosted deployments, teams willing to fine-tune on their own data.

---

### Cerebellum-2B (Antigravity Team)

The most capable open-source alternative, and the one that **beats everyone on accuracy and calibration** in its own benchmarks. Apache 2.0.

Three quantization levels:
- `Cerebellum-2B-BF16` — 3.76 GB (research/cloud training)
- `Cerebellum-2B-FP8` — 2.23 GB (production cloud)
- `Cerebellum-2B-INT8` — 2.23 GB (edge/MacBook)

**Strengths:**
- **94.92% accuracy** on agent routing vs Jev's 81.10% — the biggest accuracy gap in this comparison
- **25ms** O(1) non-autoregressive inference — fastest in the class
- **0.0271 Brier score** — best calibration by a wide margin
- **2.10% confident error rate** — safest for high-stakes automation
- **99.40% permutation invariance** — near-immune to option order bias
- Built-in `ActEscalateHead` — detects ambiguous/OOD cases and flags them for human review, zero prompting required
- Runs on a 16GB M4 MacBook at ~40ms via Apple MPS
- 320+ QPS on a single 24GB GPU
- Zero KV-cache, stateless, 0 MB memory overhead between requests

**Weaknesses:**
- Larger than Laya/Kev (2.23 GB minimum vs 647MB for Laya-multilingual)
- These benchmarks are self-reported by the model developer
- Only exposes a simplified `decide()` API — not the full Jev-compatible `{state, questions}` schema natively
- No multilingual benchmark
- Community project: less documentation, newer

**Best for:** Teams that want the highest accuracy + best calibration in a self-hosted setting. The go-to if you have a 16GB+ GPU or M-series Mac.

---

### Kev-0.5B (Jared Palmer)

The tiniest option. LoRA adapter + readout head on Qwen2.5-0.5B. Apache 2.0.

**Strengths:**
- **0.5B parameters — smallest model in this list**
- ~1.1 GB RAM — runs comfortably on any modern CPU or MacBook
- One forward pass, no decoding
- Answers many typed questions in parallel from a single prefill
- MIT/Apache 2.0

**Weaknesses:**
- Lowest accuracy (79.90% on routing vs 94.90% for Cerebellum-2B)
- Weakest calibration (Brier 0.0810)
- Lacks Score primitive (only choice and noul in initial release)
- Very new — limited production testing

**Best for:** Edge devices, constrained environments, prototyping on a laptop with no GPU. If you just need "does this work at all" with minimal resources, Kev is your starting point.

---

### OpenJev / SemIf

Community clone. Reads logits off a frozen Qwen3.5-4B. MIT license.

- Runs on a single RTX 3090
- 0.845 modal agreement with Jev (author's own eval on 102 rows)
- No HTTP server (CLI only)
- Does not reproduce RLCD — just a softmax over option logits
- Probabilities are a ranking gap, not calibrated confidence

**Best for:** Experimenting locally with the Jev interface pattern. Not for production.

---

### Bespoke Nimble

LoRA fine-tune of Qwen3.5-9B using contrastive synthetic data. Apache 2.0.

- 90% on its own curated eval vs Jev's 93%
- ~100ms on H100
- Requires 9B+ model RAM (~18GB)
- Closest to Jev's accuracy among the LoRA-based approaches
- Better for teams who have H100-class GPUs and want near-Jev quality self-hosted

---

### Fine-tuned BERT / ModernBERT

The pre-Jev standard for cheap, fast classification.

**Strengths:**
- Extremely well understood
- 10–50ms latency self-hosted
- 110M–395M params (440 MB – 800 MB)
- 1–2 orders of magnitude cheaper than LLM prompting (arxiv.org/pdf/2602.06370)
- Works well when you have labeled data and a stable category set

**Weaknesses:**
- Needs labeled training data — can't describe a new category in natural language at request time
- One model per task — no multi-question parallel evaluation
- No calibrated probabilities by default
- Retraining required for every schema change

**Best for:** Stable, high-volume, single-task classification where you have lots of labeled data and categories don't change.

---

### XGBoost / Classical ML

Still the fastest and most resource-efficient option when it works.

**Strengths:**
- Fits in < 100 MB
- Runs on pure CPU, very fast
- Highly interpretable
- Rock-solid for tabular features

**Weaknesses:**
- Can't understand free-form text without feature engineering
- No natural language schema
- Needs labeled data
- No concept of calibrated semantic uncertainty

**Best for:** Tabular data, structured features, or text that's already been reduced to features. Not a Jev replacement.

---

### LLM + Structured Output (GPT-4o, Claude, etc.)

The "just use the LLM" approach with JSON mode or tool calling.

| Metric | LLM Structured Output |
|---|---|
| Accuracy | 88.67% macro avg (GPT-4o) |
| Latency | 1,500–2,800 ms |
| Cost | $2.50–$10 / 1M tokens |
| Positional bias | 15.5% |
| Calibration | Overconfident (Brier 0.1620) |

**Strengths:**
- You already have it
- Handles generation AND classification in one call
- No schema pre-declaration
- Strong reasoning on complex tasks

**Weaknesses:**
- Slowest option by 10–100x
- Most expensive by 60–250x
- Worst calibration
- Worst positional bias
- Overkill for pure classification

**Best for:** Low-volume tasks where you also need generation, or tasks too complex/open-ended for any System One model.

---

## Comparison Table: Everything at a Glance

| | **Jev** | **Laya** | **Cerebellum-2B** | **Kev-0.5B** | **Fine-tuned BERT** | **LLM Structured** |
|---|---|---|---|---|---|---|
| **Parameters** | Undisclosed | 322M–421M | 2B | 500M | 110M–395M | 7B–700B+ |
| **Weights** | ❌ Closed | ✅ Apache 2.0 | ✅ Apache 2.0 | ✅ Apache 2.0 | ✅ Open | ❌ Mostly closed |
| **Memory** | API only | 647MB–808MB | 2.23GB–3.76GB | ~1.1GB | 440MB–800MB | API only |
| **Latency** | 190–276ms (API) | 33–40ms | 25ms | ~40ms | 10–50ms | 1,500–2,800ms |
| **Accuracy (routing)** | 81.10% | 83.80% | **94.92%** | 79.90% | Task-specific | 89.20% |
| **Calibration (Brier)** | 0.1140 | 0.062 | **0.0271** | 0.0810 | Varies | 0.1620 |
| **Multilingual** | English primary | ✅ 100+ languages | ❌ Not benchmarked | ❌ | Depends on model | ✅ |
| **Zero-shot** | ✅ No training needed | ⚠️ Base is weak; needs fine-tuning | ✅ Strong zero-shot | ⚠️ Limited | ❌ Needs labels | ✅ |
| **Multi-question parallel** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **All 3 primitives** | ✅ Choice/Score/Noul | ✅ | ✅ (via decide API) | ⚠️ Limited | ❌ | ⚠️ With prompting |
| **High-cardinality (50+ options)** | ✅ Up to 255 | ⚠️ Degrades at 50+ | ✅ | ⚠️ | ✅ | ✅ |
| **Local / offline** | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Edge / Mac compatible** | ❌ | ✅ | ✅ (INT8, 2.23GB) | ✅ (~1.1GB) | ✅ | ❌ |
| **API cost** | $0.042/MTok | $0 | $0 | $0 | $0 | $2.50–$10/MTok |
| **Escalation head** | ❌ | ❌ | ✅ Built-in | ❌ | ❌ | ❌ |
| **Context window** | 64K tokens | 512–1024 tokens | Not published | Not published | 512 tokens | 128K+ |

---

## Which One Is Better?

There's no single answer because "better" depends on your constraint.

**If accuracy is the only thing that matters:** Cerebellum-2B wins on its own benchmarks by a significant margin over Jev. But these are self-reported benchmarks — Jev's internal benchmarks show the opposite. Until there's independent third-party evaluation on a shared benchmark, treat both sets of numbers as directional.

**If calibration is the only thing that matters:** Cerebellum-2B again (Brier 0.0271 vs Jev's 0.1140 and GPT-4o's 0.1620). Laya after temperature scaling is close.

**If latency is the only thing that matters:** All local models are faster than Jev's API round-trip. Cerebellum-2B at 25ms is technically the fastest, but Laya and Kev are close enough that real-world differences are negligible.

**If you want zero setup:** Jev is the only option — the open-source models require GPU/CPU infrastructure, Python setup, and in some cases fine-tuning.

**The honest answer** is that Jev's biggest advantage is that it works out of the box with no training data and handles 255 options in a single request. The open-source alternatives (Laya, Cerebellum-2B) either require fine-tuning to match Jev's accuracy, or break down on high-cardinality label spaces. But for many real-world tasks (routing, triage, guardrails with a moderate number of options), the open-source models match or beat Jev's numbers while running faster and costing nothing.

---

## Which One for Low Resource / Small Footprint?

**Absolute smallest:** `laya-multilingual` at **647 MB** — runs on CPU, works in 100+ languages, ~193–464ms on CPU, ~33ms on GPU.

**Smallest + still viable for production:** `Kev-0.5B` at **~1.1 GB** — 0.5B parameters, runs on any MacBook, CPU inference in seconds.

**Best performance-to-size ratio:** `Cerebellum-2B-INT8` at **2.23 GB** — the sweet spot if you have a 16GB MacBook or small cloud VM. 94.92% accuracy, 25ms latency, runs completely offline on Apple Silicon at ~40ms.

**If you're purely on CPU with no GPU at all:** `laya-multilingual` or fine-tuned `BERT-base` (440MB). Both run in under 500ms on modern CPUs.

---

## Practical Decision Guide

```
Do you need text generation?
├── Yes → LLM with structured output (GPT/Claude)
└── No → Continue ↓

Do you have labeled training data and stable categories?
├── Yes (many thousands of examples) → Fine-tuned BERT or XGBoost
└── No → Continue ↓

Do you need multilingual support?
├── Yes → Laya (multilingual checkpoint, 647MB, 100+ languages)
└── No → Continue ↓

Can you run a local model?
├── No (API only) → Jev (TypeSafe API)
└── Yes → Continue ↓

What's your memory constraint?
├── < 1GB → Laya-multilingual (647MB) or Laya English (808MB)
├── 1–2GB → Kev-0.5B (~1.1GB)
├── 2–4GB → Cerebellum-2B-INT8 (2.23GB) ← recommended sweet spot
└── 4GB+ → Cerebellum-2B-BF16 or Bespoke Nimble

Do you need 50+ choice options in one request?
├── Yes → Jev (up to 255 natively) or raise context budget in Laya
└── No → Any of the above
```

---

## What None of Them Do Well

All of these models share the same limits:

- **No arithmetic or date math.** Keep exact calculations in code.
- **No text generation.** If you need to write a reply, use an LLM.
- **No long reasoning chains.** Multi-hop indirection breaks them all.
- **Adversarial inputs** can mislead all of them — Jev explicitly documents this, and the open-source ones have no defense beyond Cerebellum-2B's escalation head.
- **Context window is smaller than LLMs.** Jev has 64K; Laya defaults to 512–1024 tokens; Cerebellum-2B doesn't publish a limit. Filter your state down to what the question actually needs.

---

## Summary

Jev created the category. The community responded in 48 hours with five open-source alternatives, and some of those alternatives now outperform Jev on publicly reported benchmarks — though none of those benchmarks are independently verified yet.

For production use today:
- **Jev** if you want it working without infrastructure and can tolerate early access waiting
- **Cerebellum-2B** if you want the highest reported accuracy and calibration, self-hosted
- **Laya** if you need multilingual or want the smallest possible footprint
- **Kev-0.5B** if you need something tiny and local for prototyping

The direction is clear regardless of which model wins: AI production stacks are splitting into "fast System One models for decisions" + "LLMs for generation." The question is which System One model fits your constraints.

---

*Sources: [LangChain Blog](https://www.langchain.com/blog/building-a-harness-with-jev) · [APIdog Open Alternatives Roundup](https://apidog.com/blog/openjev-open-source-jev-alternatives/) · [Latent Space AINews](https://www.latent.space/p/ainews-here-are-6-clones-of-jev-in) · [Laya HuggingFace Card](https://huggingface.co/convaiinnovations/laya) · [Cerebellum-2B HuggingFace Card](https://huggingface.co/mkzero/Cerebellum-2B-BF16) · [TrueFoundry](https://www.truefoundry.com/blog/typesafe-ai-jev) · [Powerdrill.ai](https://powerdrill.ai/blog/jev-typesafe-ai) · [MarkTechPost](https://www.marktechpost.com/2026/09/19/typesafe-ai-releases-jev/) · [OmniaKey](https://omniakey.com/blog/jev-model-explained)*
