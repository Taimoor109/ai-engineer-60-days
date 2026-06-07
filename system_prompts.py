import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

system_prompt = (
    "You are a neutral, balanced technical advisor. Present both sides "
    "fairly with evidence. Avoid sarcasm and persona. Keep under 100 words."
)

message = client.messages.create(
    model = "claude-sonnet-4-5",
    max_tokens=300,
    system=system_prompt,
    messages=[
        {"role": "user", "content": "Should I learn Langraph or CrewAI"}
    ]
)

print(message.content[0].text)