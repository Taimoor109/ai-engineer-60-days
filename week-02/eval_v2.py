import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

# Load test set
with open('test_leads.json', 'r', encoding='utf-8') as f:
    test_data = json.load(f)
test_cases = test_data['test_cases']

# Load both prompts
SYSTEM_V1 = (
    "You qualify inbound leads for a GHL and AI automation specialist serving marketing agencies. "
    "High-quality leads: agencies with 10+ staff, clear pain, defined budget, ready to move soon. "
    "Wrong-fit: solo consultants, vague interest, no budget, asking for unrelated services. "
    "Spam: promotional, irrelevant, bots, test messages."
)

with open('prompt_v2_system.txt', 'r', encoding='utf-8') as f:
    SYSTEM_V2 = f.read()

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
    expected_cat = case['expected_category']
    actual_cat = result['category']
    actual_score = result['score']
    
    category_match = (expected_cat == actual_cat)
    score_min = case.get('expected_score_min', 0)
    score_max = case.get('expected_score_max', 100)
    score_in_range = (score_min <= actual_score <= score_max)
    
    return category_match and score_in_range


# Run both prompts on all cases
print(f"Running head-to-head eval on {len(test_cases)} cases...\n")
print(f"{'ID':<4} {'TYPE':<28} {'V1':<6} {'V2':<6} CHANGE")
print("-" * 70)

v1_passes = 0
v2_passes = 0
v1_only = []  # Cases v1 passed but v2 failed
v2_only = []  # Cases v2 passed but v1 failed
both_passed = []
both_failed = []

for case in test_cases:
    result_v1 = qualify(case['message'], SYSTEM_V1)
    result_v2 = qualify(case['message'], SYSTEM_V2)
    
    v1_pass = check_case(case, result_v1)
    v2_pass = check_case(case, result_v2)
    
    if v1_pass:
        v1_passes += 1
    if v2_pass:
        v2_passes += 1
    
    if v1_pass and v2_pass:
        change = "both pass"
        both_passed.append(case['id'])
    elif v1_pass and not v2_pass:
        change = "REGRESSION (v1 passed, v2 failed)"
        v1_only.append((case, result_v1, result_v2))
    elif not v1_pass and v2_pass:
        change = "IMPROVEMENT (v1 failed, v2 passed)"
        v2_only.append((case, result_v1, result_v2))
    else:
        change = "both fail"
        both_failed.append((case, result_v1, result_v2))
    
    v1_str = "PASS" if v1_pass else "FAIL"
    v2_str = "PASS" if v2_pass else "FAIL"
    print(f"{case['id']:<4} {case['case_type']:<28} {v1_str:<6} {v2_str:<6} {change}")

print("-" * 70)
print(f"\nV1: {v1_passes}/{len(test_cases)} ({100 * v1_passes / len(test_cases):.1f}%)")
print(f"V2: {v2_passes}/{len(test_cases)} ({100 * v2_passes / len(test_cases):.1f}%)")

improvement = v2_passes - v1_passes
if improvement > 0:
    print(f"\nV2 wins: {improvement} more cases passing")
elif improvement < 0:
    print(f"\nV2 regressed: {abs(improvement)} fewer cases passing")
else:
    print(f"\nNet zero - same pass count, but cases may differ")

if v2_only:
    print(f"\nImprovements (v1 failed, v2 passed):")
    for case, r1, r2 in v2_only:
        print(f"  Case {case['id']} ({case['case_type']}): {r1['category']} ({r1['score']}) -> {r2['category']} ({r2['score']})")

if v1_only:
    print(f"\nRegressions (v1 passed, v2 failed):")
    for case, r1, r2 in v1_only:
        print(f"  Case {case['id']} ({case['case_type']}): {r1['category']} ({r1['score']}) -> {r2['category']} ({r2['score']})")

# Save full results
with open('eval_comparison_v1_vs_v2.json', 'w', encoding='utf-8') as f:
    json.dump({
        'v1_pass_rate': v1_passes / len(test_cases),
        'v2_pass_rate': v2_passes / len(test_cases),
        'improvement': improvement,
        'v2_wins': [c['id'] for c, _, _ in v2_only],
        'v1_wins': [c['id'] for c, _, _ in v1_only],
        'both_passed': both_passed,
    }, f, indent=2)

print(f"\nFull comparison saved to eval_comparison_v1_vs_v2.json")