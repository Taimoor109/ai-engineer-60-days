def qualify_lead(lead):
    score=0
    if lead.get('budget',0)>5000:
        score += 40
    if lead.get('timeline_days', 999)<30:
        score += 30
    if lead.get('decision_maker'):
        score += 30
    return score


leads = [
    {'name':'ACME Roofing', 'budget': 8000, 'timeline_days': 14, 'decision_maker': True},
    {'name':'ACME Roofing', 'budget': 12000, 'timeline_days': 60, 'decision_maker': True},
    {'name':'ACME Roofing', 'budget': 2000, 'timeline_days': 10, 'decision_maker': False},
    {'name':'ACME Roofing', 'budget': 25000, 'timeline_days': 20, 'decision_maker': True},
]

for lead in leads:
    score = qualify_lead(lead)
    print(f"{lead['name']}:{score}")
    print("--")