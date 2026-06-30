import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

prompt = "Suggest one createive business name for a Pakiatan-based AI automation agency. just the name, nothing else."

print("===Temperature 0.0 (deterministic) ===")
for i in range(3):
    response = client.messages.create(
        model ="claude-sonnet-4-5",
        max_tokens=50,
        temperature=0.0,
        messages=[{"role": "user", "content":prompt}]
    )
    print(f"Run {i+1}: {response.content[0].text}")

print()
print("=== Temperature 1.0 (creative) ===")

for i in range(3):
    response = client.messages.create(
        model = "claude-sonnet-4-5",
        max_tokens=50,
        temperature=1.0,
        messages=[{"role":"user", "content": prompt}]
    )

    print(f"Run {i+1}: {response.content[0].text}")

