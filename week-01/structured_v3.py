import os
import json
import csv
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

leads = [
    {"id": 1, "name": "Sarah K", "email": "sarah@brightagency.com",
     "message": "We run a 30-person marketing agency in Chicago focused on home services. Need help automating our GHL onboarding and lead nurture. Budget 8-12k. Want to start within 2 weeks."},
    {"id": 2, "name": "Anonymous", "email": "test@test.com",
     "message": "hi"},
    {"id": 3, "name": "Mike R", "email": "mike@solo-consulting.com",
     "message": "Just exploring options. Maybe in 6 months we'll need something. No budget yet."},
    {"id": 4, "name": "Crypto Bot", "email": "winner@crypto-rich.biz",
     "message": "MAKE $10000 PER DAY WITH OUR AUTOMATED TRADING SYSTEM!!! Click NOW!!!"},
    {"id": 5, "name": "Jennifer T", "email": "jen@growthlabs.io",
     "message": "Hi! We're a 50-person agency, GHL Pro plan, serving real estate. Our biggest pain is slow lead follow-up - SMS goes out 4+ hours after lead submission. Looking for someone to build an AI-driven workflow. Budget 5-10k. Available for a call this week."},
    {"id": 6, "name": "Tom", "email": "tom@gmail.com",
     "message": "Do you guys do websites? I need a website."},
    {"id": 7, "name": "Lisa H", "email": "lisa@scaledigital.com",
     "message": "We've been operating in GHL for 3 years. 80 clients, 5 staff. Need to systematize our delivery - we're drowning in fulfillment work. Looking for a technical partner. Budget flexible for the right fit."},
    {"id": 8, "name": "Newsletter", "email": "noreply@newsletter.com",
     "message": "Get our free guide to digital marketing! Subscribe today!"},
    {"id": 9, "name": "David P", "email": "david@quickwins.agency",
     "message": "GHL question - having trouble with 10DLC SMS registration. Our campaigns keep getting rejected. Need help asap."},
    {"id": 10, "name": "Karen M", "email": "karen@premierdental.com",
     "message": "Our dental office is using GoHighLevel and we want to add AI to handle initial patient inquiries. Where do we start?"},
]

qualify_tool = {
    "name": "qualify_lead",
    "description": "Qualify an inbound lead and recommend next actions",
    "input_schema": {
        "type": "object",
        "properties": {
            "score": {
                "type": "integer",
                "description": "Lead quality score from 0 to 100"
            },
            "category": {
                "type": "string",
                "enum": ["hot_lead", "warm_lead", "cold_lead", "wrong_fit", "spam"],
                "description": "Lead category"
            },
            "urgency": {
                "type": "string",
                "enum": ["high", "medium", "low"],
                "description": "How urgently to respond"
            },
            "suggested_pipeline_stage": {
                "type": "string",
                "enum": ["new_lead", "qualified", "discovery_call", "proposal", "nurture", "disqualified"],
                "description": "Recommended GHL pipeline stage"
            },
            "draft_response": {
                "type": "string",
                "description": "A short, warm, personalized first response (2-4 sentences). For spam or wrong_fit, return empty string."
            },
            "recommended_next_action": {
                "type": "string",
                "description": "One concrete next step (e.g. 'Book discovery call within 24h', 'Add to nurture sequence', 'Ignore')"
            },
            "reasoning": {
                "type": "string",
                "description": "One short sentence on why this scoring"
            }
        },
        "required": ["score", "category", "urgency", "suggested_pipeline_stage",
                     "draft_response", "recommended_next_action", "reasoning"]
    }
}

SYSTEM = (
    "You qualify inbound leads for a GHL and AI automation agency serving marketing agencies. "
    "High-quality leads: agencies with 10+ staff, clear pain, defined budget, ready to move soon. "
    "Wrong-fit: solo consultants, vague interest, no budget, or asking for services we don't offer (websites). "
    "Spam: promotional, irrelevant, bots. "
    "Draft responses should sound like a senior consultant, not a salesperson. Warm, specific, brief."
)

def qualify_lead(lead):
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=800,
        temperature=0.0,
        system=SYSTEM,
        tools=[qualify_tool],
        tool_choice={"type": "tool", "name": "qualify_lead"},
        messages=[{
            "role": "user",
            "content": f"Qualify this lead:\n\nName: {lead['name']}\nEmail: {lead['email']}\nMessage: {lead['message']}"
        }]
    )
    for block in message.content:
        if block.type == "tool_use":
            return block.input, message.usage
    return None, message.usage

results = []
total_in = 0
total_out = 0

print(f"Qualifying {len(leads)} leads...\n")

for lead in leads:
    print(f"Processing lead {lead['id']}: {lead['name']}")
    result, usage = qualify_lead(lead)
    total_in += usage.input_tokens
    total_out += usage.output_tokens
    if result:
        result['lead_id'] = lead['id']
        result['lead_name'] = lead['name']
        result['lead_email'] = lead['email']
        results.append(result)
        print(f"  -> {result['category']} (score: {result['score']}) | {result['recommended_next_action']}\n")
    else:
        print(f"  -> FAILED\n")

# Save to JSON
with open('qualified_leads.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

# Save to CSV
fieldnames = ['lead_id', 'lead_name', 'lead_email', 'score', 'category', 'urgency',
              'suggested_pipeline_stage', 'recommended_next_action', 'reasoning', 'draft_response']
with open('qualified_leads.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in results:
        writer.writerow({k: row.get(k, '') for k in fieldnames})

print(f"\n--- Done ---")
print(f"Processed: {len(results)} leads")
print(f"Total input tokens: {total_in}")
print(f"Total output tokens: {total_out}")
print(f"Approx cost: ${(total_in * 3 + total_out * 15) / 1_000_000:.4f}")
print(f"Output files: qualified_leads.json, qualified_leads.csv")