import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

# Test lead - complex enough that prompt structure matters
test_lead = {
    "name": "Jennifer T",
    "company": "GrowthLabs Marketing",
    "size": "50 people",
    "message": "Hi! We're a 50-person agency on GHL Pro, serving real estate. Our biggest "
               "pain is slow lead follow-up - SMS goes out 4+ hours after lead submission. "
               "Looking for someone to build an AI-driven workflow. Budget 5-10k. Available "
               "for a call this week."
}

# ===== VERSION A: unstructured prompt =====
unstructured_prompt = f"""You are a senior consultant qualifying leads for a GHL + AI automation agency. 
A good lead has clear budget, specific pain, defined timeline. Bad leads are vague, solo operators, 
or asking for unrelated services. Here are some examples of how to qualify: a 50-person agency with 
$10k budget asking about automation = hot_lead. A solo consultant exploring options = cold_lead. 
A bot promoting crypto = spam. Now classify this lead and give me a score 0-100, a category, 
and a one-sentence reasoning. Lead info: name is {test_lead['name']} from {test_lead['company']}, 
{test_lead['size']}, they said: {test_lead['message']}"""

# ===== VERSION B: structured with XML tags =====
structured_prompt = f"""<role>
You are a senior consultant qualifying leads for a GHL + AI automation agency.
</role>

<criteria>
Good leads have: clear budget, specific pain point, defined timeline, decision-making authority.
Bad leads: vague interest, solo operators, asking for unrelated services.
</criteria>

<examples>
<example>
<input>50-person agency, $10k budget, asking about automation workflow</input>
<output>category: hot_lead, score: 90, reasoning: clear budget, specific need, agency-scale operation</output>
</example>

<example>
<input>solo consultant, exploring options, no timeline mentioned</input>
<output>category: cold_lead, score: 20, reasoning: no scale, no specifics, exploring phase</output>
</example>

<example>
<input>promotional message about cryptocurrency trading</input>
<output>category: spam, score: 0, reasoning: unrelated promotional content</output>
</example>
</examples>

<lead_to_classify>
Name: {test_lead['name']}
Company: {test_lead['company']}
Size: {test_lead['size']}
Message: {test_lead['message']}
</lead_to_classify>

<task>
Classify this lead. Provide:
- category (hot_lead, warm_lead, cold_lead, wrong_fit, or spam)
- score (0-100)
- reasoning (one sentence)
</task>"""


def get_classification(prompt):
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=300,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


print("=" * 70)
print("VERSION A — UNSTRUCTURED PROMPT")
print("=" * 70)
print(get_classification(unstructured_prompt))
print()

print("=" * 70)
print("VERSION B — STRUCTURED WITH XML TAGS")
print("=" * 70)
print(get_classification(structured_prompt))