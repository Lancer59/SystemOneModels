# SystemOneModels

Exploring System One models — a new class of AI that makes fast, structured decisions (classification, routing, scoring) without generating text. Built for automation, not chat.

Named after Daniel Kahneman's "System 1" thinking: fast, intuitive, no deliberation.

---

## What's in here

| File | What it is |
|---|---|
| `explanation.md` | Deep dive into Jev — what it is, how RLCD works, the API primitives |
| `comparison.md` | Full comparison: Jev vs Laya vs Cerebellum-2B vs Kev-0.5B vs BERT vs XGBoost |
| `demo_laya.py` | Working demo — runs 6 support tickets through Laya English, 4 questions each |
| `demo_openjev.py` | OpenJev API demo — no local model needed, just an API key |
| `setup_laya.md` | Step-by-step setup guide for Laya |
| `Jev-SystemOne.md` | Notes and context on Jev/TypeSafe AI |

---

## Quick start — Laya demo

### 1. Install dependencies

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install laya transformers
```

### 2. Download the model

The model weights are not in this repo (808 MB, excluded via `.gitignore`). Download the English checkpoint only:

```bash
hf download convaiinnovations/laya --local-dir ./models/laya
```

Then delete the two subfolders you don't need (saves ~1.4 GB):

```bash
# Windows
Remove-Item -Recurse -Force models/laya/multilingual
Remove-Item -Recurse -Force models/laya/typed-decisions

# macOS / Linux
rm -rf models/laya/multilingual models/laya/typed-decisions
```

### 3. Run

```bash
python demo_laya.py
```

**What it does:** feeds 6 support tickets through Laya English and returns, per ticket:
- `department` — choice: billing / technical / sales / other
- `urgency` — score: not urgent / soon / critical
- `churn_risk` — noul: probability customer will leave
- `refund_req` — noul: probability they want money back

All 4 questions answered in a single forward pass.

---

## Quick start — OpenJev demo

No local model, no downloads. OpenJev is a hosted API that mirrors the Jev interface — just grab a key and run.

### 1. Get an API key

Sign up at [openjev.sh](https://openjev.sh) — free tier available.

### 2. Set the key

```bash
# copy the example and fill it in
cp .env.example .env
# then set OPENJEV_API_KEY in .env
```

Or export it inline:

```powershell
# Windows PowerShell
$env:OPENJEV_API_KEY = "your_key_here"
```

```bash
# macOS / Linux
export OPENJEV_API_KEY=your_key_here
```

### 3. Install requests and run

```bash
pip install requests
python demo_openjev.py
```

That's it — no GPU, no model weights, no other setup. The script sends a support ticket and prints the structured decision back.

> **Note on OpenJev pricing:** OpenJev is currently free — API calls are covered by trading fees from a `$JEV` crypto token, not by you. There's a live treasury on the site that pays TypeSafe's invoice on your behalf. Practically: sign up, get a key, call it as much as you want for now. The catch is it's a third-party proxy (not TypeSafe directly), your requests pass through their infra, and the free access depends on the `$JEV` token staying active — if the treasury runs dry, it stops. Fine for experimenting and learning. Don't depend on it for anything production-critical. For that, get on [TypeSafe's waitlist](https://typesafe.ai) directly.

---

## What is a System One model?

A System One model takes in a **state** (text, JSON, a support ticket) and a set of **typed questions**, and returns **typed answers with calibrated probabilities**. No text generation. No parsing.

Three question types:
- **Choice** — pick one from a defined set, returns full probability distribution
- **Score** — place the state on an ordered scale, returns a continuous value
- **Noul** — yes/no probability (0 to 1)

The key properties vs an LLM:
- Evaluates all questions in **one parallel pass** — adding questions barely changes latency
- Output is **schema-safe by construction** — can't return a value outside your declared answer space
- Trained with **RLCD** (Reinforcement Learning for Calibrated Decisions) — confidence scores are supposed to be honest

---

## Models covered

| Model | Params | Weights | Memory | Best for |
|---|---|---|---|---|
| **Jev** (TypeSafe AI) | Undisclosed | Closed API | API only | Zero-shot, up to 255 options, no setup |
| **Laya** (English) | 421M | Apache 2.0 | ~808 MB | Self-hosted English classification |
| **Laya** (multilingual) | 322M | Apache 2.0 | ~647 MB | 100+ languages |
| **Cerebellum-2B** | 2B | Apache 2.0 | 2.23 GB | Best reported accuracy + calibration |
| **Kev-0.5B** | 500M | Apache 2.0 | ~1.1 GB | Smallest, runs on any CPU |

---

## Notes

- CPU inference is ~2.5 sec/ticket on this machine. A GPU brings it to ~35ms.
- Laya base checkpoint is near-random on some benchmarks zero-shot — it does best on common-sense routing tasks like this demo. Fine-tuning on your own data gets you to benchmark accuracy.
- `models/` is gitignored. Clone the checkpoint yourself using the instructions above.
