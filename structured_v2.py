import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

sample_emails = [
    {"id": 1, "subject": "Need help with my account login",
     "body": "Hi, I cannot log into my account since yesterday. Please help."},
    {"id": 2, "subject": "Interested in your services for our agency",
     "body": "Hello, we run a 50-person marketing agency and need help with GHL automation. Budget around 10k USD. Can we hop on a call this week?"},
    {"id": 3, "subject": "WIN BIG with crypto investments!!!",
     "body": "Click here to make $5000 a day from home with our trading bot. Limited time offer!"},
    {"id": 4, "subject": "Quick question about pricing",
     "body": "What does your enterprise plan cost?"},
]

def classify_v2(email):
    prompt = f"""Classify this email and respond with JSON in this exact format:
{{
  "category": "lead" | "support" | "spam" | "other",
  "confidence": 0.0 to 1.0,
  "reasoning": "one short sentence"
}}

Subject: {email['subject']}
Body: {email['body']}"""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = message.content[0].text.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"category": "error", "confidence": 0, "reasoning": f"Bad JSON: {raw[:100]}"}

for email in sample_emails:
    result = classify_v2(email)
    print(f"Email {email['id']}: {result['category']} ({result['confidence']})")
    print(f"  Reasoning: {result['reasoning']}\n")