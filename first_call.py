import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[
        {"role":"user","content":"Hello Claude. This is my first API call from my own code. Briefly say hi bak and tell me one interesting fact about Pakistan"}
    ]
)

print(message.content[0].text)