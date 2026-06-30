import os
import csv
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

prospects = [
    'https://www.anthropic.com',
    'https://www.langchain.com',
    'https://drovinsolutions.com',
    'https://www.gohighlevel.com',
    'https://www.python.org',
]

research_tool = {
    "name": "research_prospect",
    "description": "Research a prospect company based on their website",
    "input_schema": {
        "type": "object",
        "properties": {
            "company_name": {"type": "string"},
            "industry": {"type": "string"},
            "estimated_size": {
                "type": "string",
                "enum": ["solo", "small", "medium", "large", "enterprise", "unknown"]
            },
            "primary_service": {"type": "string"},
            "fit_score": {
                "type": "integer",
                "description": "How well this prospect fits as a buyer for GHL+AI automation services (0-100)"
            },
            "fit_category": {
                "type": "string",
                "enum": ["strong_fit", "possible_fit", "wrong_fit", "competitor"]
            },
            "outreach_angle": {
                "type": "string",
                "description": "One specific reason this prospect might need GHL+AI automation help"
            },
            "draft_message": {
                "type": "string",
                "description": "A short personalized first outreach message (2-3 sentences). Reference something specific from their site."
            },
            "reasoning": {"type": "string"}
        },
        "required": ["company_name", "industry", "estimated_size", "primary_service",
                     "fit_score", "fit_category", "outreach_angle", "draft_message", "reasoning"]
    }
}

SYSTEM = (
    "You research prospects for a GHL + AI automation specialist serving marketing agencies. "
    "Strong fit: marketing agencies (any size), GHL operators, automation consultancies, "
    "agencies that serve home services or local SMBs. "
    "Possible fit: SaaS companies serving agencies, AI tooling companies. "
    "Wrong fit: solo consultants, B2C brands, individual practitioners. "
    "Competitor: other GHL/automation agencies offering the same services. "
    "Draft messages should sound like a peer reaching out, not a sales pitch. Specific, brief, no flattery."
)

def fetch_page_text(url):
    try:
        response = requests.get(url, timeout=15,
            headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'footer']):
            tag.decompose()
        text = soup.get_text(separator=' ', strip=True)
        return text[:3500]
    except Exception as e:
        return None

def research_with_claude(url, page_text):
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=800,
        temperature=0.0,
        system=SYSTEM,
        tools=[research_tool],
        tool_choice={"type": "tool", "name": "research_prospect"},
        messages=[{
            "role": "user",
            "content": f"Research this prospect:\n\nURL: {url}\n\nWebsite content:\n{page_text}"
        }]
    )
    for block in message.content:
        if block.type == "tool_use":
            return block.input, message.usage
    return None, message.usage

results = []
total_in = 0
total_out = 0
failed = []

print(f"Researching {len(prospects)} prospects...\n")

for url in prospects:
    print(f"Fetching: {url}")
    page_text = fetch_page_text(url)
    if not page_text:
        print(f"  -> FAILED to fetch")
        failed.append({'url': url, 'reason': 'fetch_failed'})
        continue
    
    print(f"  -> Got {len(page_text)} chars, sending to Claude...")
    result, usage = research_with_claude(url, page_text)
    total_in += usage.input_tokens
    total_out += usage.output_tokens
    
    if result:
        result['url'] = url
        results.append(result)
        print(f"  -> {result['fit_category']} (fit: {result['fit_score']}) | {result['company_name']}\n")
    else:
        print(f"  -> Claude analysis failed\n")
        failed.append({'url': url, 'reason': 'analysis_failed'})

# Save JSON
with open('prospect_research.json', 'w', encoding='utf-8') as f:
    json.dump({'results': results, 'failed': failed}, f, indent=2)

# Save CSV
fieldnames = ['url', 'company_name', 'industry', 'estimated_size', 'primary_service',
              'fit_score', 'fit_category', 'outreach_angle', 'reasoning', 'draft_message']
with open('prospect_research.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in results:
        writer.writerow({k: row.get(k, '') for k in fieldnames})

print(f"\n--- Done ---")
print(f"Processed: {len(results)} prospects ({len(failed)} failed)")
print(f"Input tokens: {total_in}, Output tokens: {total_out}")
print(f"Approx cost: ${(total_in * 3 + total_out * 15) / 1_000_000:.4f}")
print(f"Files: prospect_research.json, prospect_research.csv")