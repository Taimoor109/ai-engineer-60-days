import requests
from bs4 import BeautifulSoup
import csv

urls = [
    'https://www.python.org',
    'https://www.anthropic.com',
    'https://www.langchain.com',
    'https://drovinsolutions.com',
]

results= []

for url in urls:
    print(f"Fetching: {url}")
    try:
        response = requests.get(url,timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title= soup.title.string if soup.title else 'No title found'
        title = title.strip()
        results.append({'url':url, 'title': title, 'error':''})
        print(f" ->{title[:60]}")
    except requests.exceptions.RequestExceptions as e:
        print(f" ->Failed: {e}")
        results.append({'url':url,'title':'','error':str(e)})

with open('site_titles.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter (f, fieldnames=['url', 'title', 'error'])
    writer.writeheader()
    writer.writerows(results)

print(f"\nDone. Wrote {len(results)} rows to site_titles.csv")