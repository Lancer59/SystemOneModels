# Setup: Laya (English) — Local System One Model

This guide sets up the Laya English checkpoint (`convaiinnovations/laya`) locally and runs
a support-ticket triage demo. No API key needed. No waitlist. Runs fully offline after the
first model download.

---

## What We're Building

A support-ticket triage script that feeds raw customer messages into Laya and gets back:

- **Department routing** (billing / technical / sales / other)
- **Urgency score** (not urgent → soon → critical)
- **Churn risk** (noul — probability the customer will leave)
- **Refund requested** (noul — yes/no probability)

All four questions are answered in a single forward pass (~35 ms on GPU, ~200–500 ms on CPU).

---

## Prerequisites

| Requirement | Version used here |
|---|---|
| Python | 3.13 (any 3.10+ works) |
| pip | 26.x |
| OS | Windows 11 / macOS / Linux |
| GPU | Optional — CUDA GPU speeds things up, but CPU works fine |

---

## Project Structure

```
SystemOneModels/
├── setup.md          ← you are here
├── explanation.md
├── comparison.md
├── context.md
├── demo_laya.py      ← the script we're about to build
└── requirements.txt
```

---

## Install Steps

### 1. Create a virtual environment (recommended)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

On macOS/Linux:
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install PyTorch

CPU-only (lighter, works on any machine):
```powershell
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

CUDA 12.x (if you have an NVIDIA GPU):
```powershell
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### 3. Install Laya and dependencies

```powershell
pip install laya transformers
```

Laya pulls in `transformers` and `huggingface-hub` automatically, but pinning them
explicitly avoids surprises.

### 4. (Optional) Suppress TensorFlow deadlock

If you have TensorFlow installed alongside this, set the env var before running:

```powershell
$env:USE_TF = "0"
python demo_laya.py
```

Or on macOS/Linux:
```bash
USE_TF=0 python demo_laya.py
```

---

## First Run — Model Download

On first run Laya downloads the English checkpoint from HuggingFace:

```
convaiinnovations/laya  (~808 MB)
```

This happens automatically via `laya.load()`. Subsequent runs load from the local cache
(`~/.cache/huggingface/hub`) with no network needed.

---

## What to Expect

When the script runs you'll see output like:

```
╔══════════════════════════════════════════════════════════════╗
║           Laya English — Support Ticket Triage Demo          ║
╚══════════════════════════════════════════════════════════════╝

Ticket 1: "Hi, I've been trying to connect my Stripe account for 3 days..."
  department  → billing       (confidence: 0.87)
  urgency     → 2.1 / 2.0     (critical deadline)
  churn_risk  → 0.74          (74% chance of churn)
  refund_req  → 0.11          (unlikely asking for refund)

...
```

---

## Key Things to Know

**Laya is not zero-shot by default.** The base `laya` checkpoint needs fine-tuning on your
own data to reach the 0.766 typed-decisions accuracy from the benchmarks. What we're doing
here is zero-shot inference — it will still work well for common-sense routing and urgency,
but don't expect benchmark-level numbers without fine-tuning.

**Context is limited.** The English checkpoint uses 512 tokens max. Keep your state (ticket
text) concise — irrelevant detail hurts accuracy.

**Probabilities need temperature scaling.** Raw confidence numbers from the base checkpoint
can be over- or under-confident. For production use, calibrate thresholds against your own
labelled sample.

**This is not an LLM.** Laya will not explain itself, write a reply, or generate any text.
It only returns probabilities for the questions you defined.

---

## Running the Demo

```powershell
python demo_laya.py
```

That's it. The first run downloads the model. Every run after that is fully offline.
