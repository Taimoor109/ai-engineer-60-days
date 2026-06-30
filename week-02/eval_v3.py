import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

with open('test_leads.json', 'r', encoding='utf-8') as f:
    test_data = json.load(f)
test_cases = test_data['test_cases']

SYSTEM_V1 = (
    "You qualify inbound leads for a GHL and AI automation specialist serving marketing agencies. "
    "High-quality leads: agencies with 10+ staff, clear pain, defined budget, ready to move soon. "
    "Wrong-fit: solo consultants, vague interest, no budget, asking for unrelated services. "
    "Spam: promotional, irrelevant, bots, test messages."
)

with open('prompt_v2_system.txt', 'r', encoding='utf-8') as f:
    SYSTEM_V2 = f.read()

with open('prompt_v3_system.txt', 'r', encoding='utf-8') as f:
    SYSTEM_V3 = f.read()

qualify_tool = {
    "name": "qualify_lead",
    "description": "Qualify an inbound lead",
    "input_schema": {
        "type": "object",
        "properties": {
            "score": {"type": "integer", "description": "Lead quality score 0-100"},
            "category": {
                "type": "string",
                "enum": ["hot_lead", "warm_lead", "cold_lead", "wrong_fit", "spam"]
            },
            "reasoning": {"type": "string"}
        },
        "required": ["score", "category", "reasoning"]
    }
}


def qualify(message, system_prompt):
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=400,
        temperature=0.0,
        system=system_prompt,
        tools=[qualify_tool],
        tool_choice={"type": "tool", "name": "qualify_lead"},
        messages=[{"role": "user", "content": f"Qualify this lead:\n\n{message}"}]
    )
    for block in response.content:
        if block.type == "tool_use":
            return block.input
    return None


def check_case(case, result):
    if not result:
        return False
    cat_match = case['expected_category'] == result['category']
    score_min = case.get('expected_score_min', 0)
    score_max = case.get('expected_score_max', 100)
    score_ok = score_min <= result['score'] <= score_max
    return cat_match and score_ok


print(f"Comparing 3 prompts on {len(test_cases)} cases...\n")
print(f"{'ID':<4} {'TYPE':<28} {'V1':<6} {'V2':<6} {'V3':<6}")
print("-" * 60)

v1_passes = 0
v2_passes = 0
v3_passes = 0
detailed = []

for case in test_cases:
    r1 = qualify(case['message'], SYSTEM_V1)
    r2 = qualify(case['message'], SYSTEM_V2)
    r3 = qualify(case['message'], SYSTEM_V3)
    
    p1 = check_case(case, r1)
    p2 = check_case(case, r2)
    p3 = check_case(case, r3)
    
    if p1: v1_passes += 1
    if p2: v2_passes += 1
    if p3: v3_passes += 1
    
    print(f"{case['id']:<4} {case['case_type']:<28} {'PASS' if p1 else 'FAIL':<6} {'PASS' if p2 else 'FAIL':<6} {'PASS' if p3 else 'FAIL':<6}")
    
    detailed.append({
        'id': case['id'],
        'type': case['case_type'],
        'expected': case['expected_category'],
        'v1': {'category': r1['category'], 'score': r1['score'], 'pass': p1},
        'v2': {'category': r2['category'], 'score': r2['score'], 'pass': p2},
        'v3': {'category': r3['category'], 'score': r3['score'], 'pass': p3},
    })

n = len(test_cases)
print("-" * 60)
print(f"\nV1: {v1_passes}/{n} ({100*v1_passes/n:.1f}%)")
print(f"V2: {v2_passes}/{n} ({100*v2_passes/n:.1f}%)")
print(f"V3: {v3_passes}/{n} ({100*v3_passes/n:.1f}%)")

# Find the winner
best = max(v1_passes, v2_passes, v3_passes)
if v3_passes == best:
    winner = "V3"
elif v2_passes == best:
    winner = "V2"
else:
    winner = "V1"
print(f"\nWinner: {winner}")

# Show v3-specific changes
v3_fixes = [d for d in detailed if d['v3']['pass'] and not d['v1']['pass']]
v3_regressions = [d for d in detailed if d['v1']['pass'] and not d['v3']['pass']]

if v3_fixes:
    print(f"\nV3 fixed (vs V1):")
    for d in v3_fixes:
        print(f"  Case {d['id']} ({d['type']}): {d['v1']['category']} ({d['v1']['score']}) -> {d['v3']['category']} ({d['v3']['score']})")

if v3_regressions:
    print(f"\nV3 regressed (vs V1):")
    for d in v3_regressions:
        print(f"  Case {d['id']} ({d['type']}): {d['v1']['category']} ({d['v1']['score']}) -> {d['v3']['category']} ({d['v3']['score']})")

with open('eval_three_way.json', 'w', encoding='utf-8') as f:
    json.dump({
        'pass_rates': {'v1': v1_passes/n, 'v2': v2_passes/n, 'v3': v3_passes/n},
        'winner': winner,
        'cases': detailed
    }, f, indent=2)
print(f"\nFull results: eval_three_way.json")