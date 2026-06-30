import os
import csv
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

urls = [
    'https://www.python.org',
    'https://www.anthropic.com',
    'https://www.langchain.com',
    'https://drovinsolutions.com',
]

results = []

def fetch_page_text(url):
    response = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    for tag in soup(['script', 'style', 'nav', 'footer']):
        tag.decompose()
    text = soup.get_text(separator=' ', strip=True)
    return text[:3000]

def analyze_with_claude(url, page_text):
    prompt = f"""Below is the content of a website's homepage. Based on this content, tell me in 2 short sentences:
1. What this company or project does
2. Who their primary audience appears to be

URL: {url}

Content:
{page_text}"""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=200,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

for url in urls:
    print(f"\nProcessing: {url}")
    try:
        page_text = fetch_page_text(url)
        summary = analyze_with_claude(url, page_text)
        results.append({'url': url, 'summary': summary, 'error': ''})
        print(f"  Summary: {summary[:80]}...")
    except Exception as e:
        print(f"  Failed: {e}")
        results.append({'url': url, 'summary': '', 'error': str(e)})

with open('smart_research.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['url', 'summary', 'error'])
    writer.writeheader()
    writer.writerows(results)

print(f"\n--- Done. Wrote {len(results)} rows to smart_research.csv ---")