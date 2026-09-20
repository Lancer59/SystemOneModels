"""
demo_laya.py  —  Support-ticket triage with Laya (English checkpoint)
======================================================================
Loads convaiinnovations/laya (~808 MB, downloads once to HF cache).
Feeds 6 realistic support tickets through a single forward pass each,
asking 4 questions per ticket in parallel:
  - department  : choice  — which team owns this?
  - urgency     : score   — how time-sensitive is it?
  - churn_risk  : noul    — is the customer at risk of leaving?
  - refund_req  : noul    — are they asking for money back?

Run:
    python demo_laya.py
"""

import os
import time

# Prevent TensorFlow deadlock if TF happens to be installed
os.environ.setdefault("USE_TF", "0")

import laya  # noqa: E402


# ── colour helpers (work on any terminal, fall back gracefully) ────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
DIM    = "\033[2m"

def colour(text: str, code: str) -> str:
    return f"{code}{text}{RESET}"

def bar(value: float, width: int = 20) -> str:
    """Simple ASCII probability bar."""
    filled = round(value * width)
    return "[" + "█" * filled + "·" * (width - filled) + "]"


# ── question schema (reused for every ticket) ──────────────────────────────

QUESTIONS = {
    "department": {
        "type": "choice",
        "instructions": "Which team should handle this support ticket?",
        "criteria": {
            "billing":   "Payment issues, charges, refunds, invoices, subscriptions",
            "technical": "Bugs, crashes, errors, integrations, API problems, outages",
            "sales":     "Pricing, upgrades, plan changes, new features, discounts",
            "other":     "Everything else, unclear, or unrelated",
        },
    },
    "urgency": {
        "type": "score",
        "instructions": "How time-sensitive is this ticket?",
        "criteria": [
            "not urgent — can wait days",
            "soon — should be addressed within 24 hours",
            "critical — needs immediate attention, customer is losing money or blocked",
        ],
    },
    "churn_risk": {
        "type": "noul",
        "instructions": "The customer sounds like they might cancel or leave the product",
    },
    "refund_req": {
        "type": "noul",
        "instructions": "The customer is explicitly asking for a refund or money back",
    },
}

# ── sample tickets ─────────────────────────────────────────────────────────

TICKETS = [
    {
        "id": 1,
        "text": (
            "Hi, I've been charged twice for my March subscription. "
            "I need a refund for the duplicate charge immediately or I'm cancelling."
        ),
    },
    {
        "id": 2,
        "text": (
            "Our entire CI/CD pipeline is broken because your webhook endpoint "
            "has been returning 503 for the past 2 hours. We're blocking a production "
            "deploy. This needs to be fixed NOW."
        ),
    },
    {
        "id": 3,
        "text": (
            "Hey, could you tell me what the difference is between the Pro and "
            "Business plans? Trying to figure out if the Business plan is worth "
            "the upgrade for my team of 8."
        ),
    },
    {
        "id": 4,
        "text": (
            "I accidentally deleted a folder in my workspace. Is there any way "
            "to recover it? I don't see an undo option anywhere."
        ),
    },
    {
        "id": 5,
        "text": (
            "Your Stripe integration keeps failing with a 'card_declined' error "
            "even though my card works fine everywhere else. I'm losing sales. "
            "If this isn't fixed today I'm switching to a competitor."
        ),
    },
    {
        "id": 6,
        "text": (
            "Hi, just wanted to say the new dashboard update looks great! "
            "One small thing — the export button doesn't seem to work in Firefox. "
            "Not urgent at all, just flagging it."
        ),
    },
]


# ── formatting helpers ─────────────────────────────────────────────────────

URGENCY_LABELS = {0: "not urgent", 1: "soon", 2: "critical"}
URGENCY_COLOURS = {
    "not urgent": GREEN,
    "soon":       YELLOW,
    "critical":   RED,
}
DEPT_COLOURS = {
    "billing":   YELLOW,
    "technical": CYAN,
    "sales":     GREEN,
    "other":     DIM,
}


def format_noul(label: str, value: float, threshold: float = 0.5) -> str:
    pct = f"{value:.0%}"
    indicator = colour("YES", RED) if value >= threshold else colour("no", DIM)
    return f"{indicator}  {bar(value)}  {pct}"


def format_choice(choice: str, probs: dict, conf: float) -> str:
    dept_colour = DEPT_COLOURS.get(choice, RESET)
    lines = [colour(f"→ {choice.upper()}", dept_colour + BOLD) + f"  (conf {conf:.0%})"]
    for k, v in sorted(probs.items(), key=lambda x: -x[1]):
        marker = " ◀" if k == choice else "  "
        lines.append(f"     {k:<12} {bar(v, 14)} {v:.0%}{marker}")
    return "\n".join(lines)


def format_score(score: float, legend: dict, probs: dict, conf: float) -> str:
    n = len(legend)
    level_idx = min(round(score), n - 1)
    level_name = legend[str(level_idx)]
    level_colour = URGENCY_COLOURS.get(level_name.split("—")[0].strip(), RESET)
    lines = [
        colour(f"→ {score:.2f} / {n - 1}", level_colour + BOLD)
        + f"  {level_name}  (conf {conf:.0%})"
    ]
    for i, label in legend.items():
        p = probs[i]
        lines.append(f"     [{i}] {label[:35]:<35} {bar(p, 12)} {p:.0%}")
    return "\n".join(lines)


def print_ticket(ticket: dict, result: dict, elapsed_ms: float) -> None:
    answers = result["answers"]
    tokens  = result["usage"]["input_tokens"]

    print(colour("─" * 66, DIM))
    print(colour(f"  Ticket #{ticket['id']}", BOLD + CYAN))
    print(f"  {DIM}{ticket['text'][:90]}{'…' if len(ticket['text']) > 90 else ''}{RESET}")
    print(colour("─" * 66, DIM))

    # Department
    dept = answers["department"]
    print(colour("  DEPARTMENT", BOLD))
    print("  " + format_choice(dept["choice"], dept["probabilities"], dept["confidence"]))

    # Urgency
    urg = answers["urgency"]
    print(colour("\n  URGENCY", BOLD))
    print("  " + format_score(urg["score"], urg["legend"], urg["probabilities"], urg["confidence"]))

    # Churn risk
    churn = answers["churn_risk"]
    print(colour("\n  CHURN RISK", BOLD))
    print(f"  {format_noul('churn_risk', churn['noul'])}")

    # Refund requested
    refund = answers["refund_req"]
    print(colour("\n  REFUND REQUESTED", BOLD))
    print(f"  {format_noul('refund_req', refund['noul'])}")

    print(f"\n  {DIM}⏱  {elapsed_ms:.0f} ms  ·  {tokens} input tokens{RESET}")
    print()


# ── main ───────────────────────────────────────────────────────────────────

def main() -> None:
    print()
    print(colour("╔══════════════════════════════════════════════════════════════╗", CYAN))
    print(colour("║        Laya English — Support Ticket Triage Demo             ║", CYAN + BOLD))
    print(colour("╚══════════════════════════════════════════════════════════════╝", CYAN))
    print()
    # Local path — model was cloned to models/laya, multilingual & typed-decisions removed
    model_path = os.path.join(os.path.dirname(__file__), "models", "laya")
    print(f"  {DIM}Loading Laya English from {model_path}…{RESET}")
    print()

    load_start = time.perf_counter()
    agent = laya.load(model_path)
    load_ms = (time.perf_counter() - load_start) * 1000
    print(f"  {GREEN}Model loaded in {load_ms:.0f} ms{RESET}\n")

    total_tokens = 0
    total_ms = 0.0

    for ticket in TICKETS:
        t0 = time.perf_counter()
        result = agent.predict(ticket["text"], QUESTIONS)
        elapsed = (time.perf_counter() - t0) * 1000
        total_ms += elapsed
        total_tokens += result["usage"]["input_tokens"]
        print_ticket(ticket, result, elapsed)

    print(colour("═" * 66, DIM))
    print(colour("  SUMMARY", BOLD))
    print(f"  {len(TICKETS)} tickets  ·  {total_tokens} total tokens  ·  "
          f"{total_ms:.0f} ms total  ·  avg {total_ms / len(TICKETS):.0f} ms/ticket")
    print(colour("═" * 66, DIM))
    print()


if __name__ == "__main__":
    main()
