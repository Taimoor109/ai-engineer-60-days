# Day 6 - June 19, 2026

What I did:
- Built prospect_research.py - combined scraper + lead qualifier
- Takes a list of URLs, fetches each homepage, sends content to Claude with tool use
- Output: structured prospect data with fit score, category, outreach angle, and draft message
- Saved to both JSON and CSV
- Tested on 5 sites including my own (Drovin)

What was hard:
- [your real answer - or "nothing major broke, mostly worked"]

What surprised me:
- Claude correctly identified Drovin as a competitor (not a prospect) just from reading my site
- The Drovin draft message was actually a viable peer-to-peer message I could send
- Fit scores aligned with intuition - tech companies low, competitors flagged correctly

What I'd improve:
- The outreach_angle field is sometimes too generic
- Need to refine the SYSTEM prompt with more specific buyer profile criteria
- Should test on 20-50 real agency URLs to stress-test the qualifier

Carrying into day 7:
- Polish week 1 - clean READMEs, project structure, the LinkedIn post
- This is the publish day - the public record of week 1 goes live