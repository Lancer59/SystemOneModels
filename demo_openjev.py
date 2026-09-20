import os
import requests

url = "https://api.openjev.sh/v1/systemone"
api_key = os.environ.get("OPENJEV_API_KEY", "")  # set via environment variable, never hardcode

payload = {
    "model": "openjev",
    "state": "My card was charged twice. Please help ASAP.",
    "questions": {
        "urgent": {
            "type": "noul",
            "instructions": "Does this message convey urgency?",
            "criteria": {
                "true": "Explicitly time-sensitive",
                "false": "No urgency expressed"
            }
        },
        "team": {
            "type": "choice",
            "instructions": "Which team should handle this?",
            "criteria": {
                "billing": "Payments and refunds",
                "technical": "Bugs and integrations",
                "sales": "Pricing and new accounts"
            }
        }
    }
}

r = requests.post(
    url,
    headers={"Authorization": f"Bearer {api_key}"},
    json=payload
)

print(r.status_code)
print(r.json())