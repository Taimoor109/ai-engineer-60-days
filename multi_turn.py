import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

system_prompt = (
    "You are a senior AI engineer helping a junior developer plan their first agent project."
    "Ask one clarifying question at a time. Keep responses under 60 words."
)

conversation = []

def chat(user_message):
    conversation.append({"role":"user", "content": user_message})

    response = client.messages.create(
        model = "claude-sonnet-4-5",
        max_tokens=500,
        system=system_prompt,
        messages=conversation
    )

    assistant_reply = response.content[0].text
    conversation.append({"role":"assistant", "content": assistant_reply})
    return assistant_reply

print("User: I want to build my first AI agent.")
print("Claude:", chat("i want it to score leads and draft a first-response email"))
print()

print("User: I want it to score leads and draft a first-response email.")
print("Claude:", chat("I want it to score leads and draft a first-response email."))
print()

print("--- Total messages in conversation:", len(conversation))

print()
print("=== Full conversation history at the end: ===")
import json
print(json.dumps(conversation, indent=2))