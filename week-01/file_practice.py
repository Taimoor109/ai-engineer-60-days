import json

leads = [
    {'name':'ACME Roofing', 'budget': 8000},
    {'name':'Bright Marketing', 'budget':12000},
    {'name':'Local Plumber', 'budget':2000}
]

with open('leads.json','w') as f:
    json.dump(leads,f,indent = 2)

print('Wrote leads.json')

with open('leads.json', 'r') as f:
    loaded_leads = json.load(f)

print('---')
print('Read leads back from file:')
for lead in loaded_leads:
    print(f"{lead['name']}: ${lead['budget']}")