import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

print("Claude is thinking...\n")

with client.messages.stream(
    model="claude-sonnet-4-5",
    max_tokens=400,
    messages=[
        {"role": "user", "content": "Explain how a vector database works in 4 short sentences."}
    ]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

print("\n\n--- Done ---")