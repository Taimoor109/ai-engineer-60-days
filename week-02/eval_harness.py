import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

# Load the test set
with open('test_leads.json', 'r', encoding='utf-8') as f:
    test_data = json.load(f)

test_cases = test_data['test_cases']

# ===== The prompt we're evaluating =====
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

SYSTEM = (
    "You qualify inbound leads for a GHL and AI automation specialist serving marketing agencies. "
    "High-quality leads: agencies with 10+ staff, clear pain, defined budget, ready to move soon. "
    "Wrong-fit: solo consultants, vague interest, no budget, asking for unrelated services. "
    "Spam: promotional, irrelevant, bots, test messages."
)

def qualify(message):
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=400,
        temperature=0.0,
        system=SYSTEM,
        tools=[qualify_tool],
        tool_choice={"type": "tool", "name": "qualify_lead"},
        messages=[{"role": "user", "content": f"Qualify this lead:\n\n{message}"}]
    )
    for block in response.content:
        if block.type == "tool_use":
            return block.input
    return None


def check_case(case, result):
    """Returns a dict describing pass/fail and why."""
    if not result:
        return {"pass": False, "reason": "No result returned"}
    
    expected_cat = case['expected_category']
    actual_cat = result['category']
    actual_score = result['score']
    
    category_match = (expected_cat == actual_cat)
    
    score_min = case.get('expected_score_min', 0)
    score_max = case.get('expected_score_max', 100)
    score_in_range = (score_min <= actual_score <= score_max)
    
    if category_match and score_in_range:
        return {"pass": True, "reason": "OK"}
    
    failures = []
    if not category_match:
        failures.append(f"expected {expected_cat}, got {actual_cat}")
    if not score_in_range:
        failures.append(f"score {actual_score} outside [{score_min}, {score_max}]")
    
    return {"pass": False, "reason": "; ".join(failures)}


# Run the eval
print(f"Running eval on {len(test_cases)} cases...\n")
print(f"{'ID':<4} {'PASS':<6} {'EXPECTED':<12} {'GOT':<12} {'SCORE':<6} REASON")
print("-" * 80)

results = []
passes = 0

for case in test_cases:
    result = qualify(case['message'])
    check = check_case(case, result)
    if check['pass']:
        passes += 1
    
    actual_cat = result['category'] if result else 'ERROR'
    actual_score = result['score'] if result else 0
    pass_str = "PASS" if check['pass'] else "FAIL"
    
    print(f"{case['id']:<4} {pass_str:<6} {case['expected_category']:<12} {actual_cat:<12} {actual_score:<6} {check['reason']}")
    
    results.append({
        'id': case['id'],
        'case_type': case['case_type'],
        'message': case['message'][:60],
        'expected_category': case['expected_category'],
        'actual_category': actual_cat,
        'actual_score': actual_score,
        'passed': check['pass'],
        'failure_reason': check['reason']
    })

print("-" * 80)
print(f"\nResult: {passes}/{len(test_cases)} passed ({100 * passes / len(test_cases):.1f}%)")

# Save detailed results
with open('eval_results_v1.json', 'w', encoding='utf-8') as f:
    json.dump({
        'pass_rate': passes / len(test_cases),
        'total': len(test_cases),
        'passed': passes,
        'cases': results
    }, f, indent=2)

print(f"\nDetailed results saved to eval_results_v1.json")