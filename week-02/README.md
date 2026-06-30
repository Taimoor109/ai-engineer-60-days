# Week 2 — Prompt Engineering Depth and Agent Foundations

Week 2 of building toward a GHL-native AI lead response system. The focus
shifted from "can I call an AI?" to "can I measure whether my AI is good,
and can I make it act autonomously?"

## What I built this week

### Day 8: Prompt engineering techniques
Three small scripts demonstrating techniques that matter in production:

- `prompt_clarity.py` — vague prompts vs. clear prompts with explicit rules.
  Same model, same task, completely different output reliability.
- `prompt_examples.py` — multishot prompting. Showing Claude 4 worked
  examples beats describing rules in words. The technique encodes business
  judgment in a way instructions cannot.
- `prompt_xml.py` — XML tags for prompt structure. Doesn't change what
  Claude thinks. Changes how reliably Claude formats output.

The lesson: prompt engineering at production teams isn't tweaking and hoping.
It's encoding judgment via curated examples, in structured prompts, then
measuring whether the change improved or regressed quality.

### Day 9: Evaluation harnesses
The leap from "prompts as craft" to "prompts as engineering."

- `test_leads.json` — 20 test cases covering obvious and ambiguous lead
  categories. The hard cases (pricing inquiries, operational-signal-only
  leads, adjacent-market real-need cases) are deliberately included because
  that's where prompts actually fail in production.
- `eval_v1.py` — runs one prompt against the test set, computes pass rate
  with category and score-range checks.
- `eval_v2.py` — runs two prompts head-to-head, identifies regressions and
  improvements specifically.
- `eval_v3.py` — three-way comparison.

The iteration arc:
- V1 (no examples): 85% pass rate baseline
- V2 (5 examples, all "be more inclusive"): regressed to 65% — examples
  biased the model in one direction
- V3 (5 balanced examples + boundary clarifications): 85% with different
  cases passing
- After updating test labels to reflect actual business judgment: 95%

Cost per full eval run: about $0.15 in API calls.

### Day 10: Multi-tool agents
The shift from "AI returns answers" to "AI decides what to do."

- `agent_v1.py` — first multi-tool agent with two trivial tools
  (time, calc). Built to show the loop pattern: while stop_reason equals
  tool_use, execute and continue.
- `agent_v2.py` — chained tools. Search first, then read the specific
  article that came back. Agent decides which URL to fetch based on what
  search returned.
- `agent_v3.py` — real research agent with four tools (fetch_website,
  extract_company_info, score_fit, save_research). Takes a one-sentence
  prompt like "research this company and save the result" and autonomously
  orchestrates 5 iterations to complete the task. Two of the four tools
  internally use Claude themselves (nested LLM calls).

Test run: pointed the agent at drovinsolutions.com (my own brand).
The agent correctly classified Drovin as a competitor to itself —
recognized the GHL+AI automation positioning by reading the site.

## Stack additions

- Tool use with auto choice (vs. forced choice from week 1)
- Multi-iteration agent loop in raw Python
- Test set construction with edge case curation
- Evaluation harness pattern (test cases + check function + scorecard)

## What's next

Week 3 — Retrieval augmented generation (RAG). Adding memory and knowledge
base context to AI responses. This is the pattern behind "chat with your
documents" tools.

Week 4-5 — LangGraph and the full lead response system. Agent code with
state management, human-in-the-loop checkpoints, and CRM integration.
Today's `agent_v3.py` is the working skeleton week 5 will extend.

Public log: see LOG.md in week-01.