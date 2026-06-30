import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

# ===== Fake article database (in real life this would be a search API + scraper) =====
ARTICLES = {
    "https://example.com/agent-loops": {
        "title": "Understanding the Agent Loop",
        "content": (
            "The agent loop is the core pattern in tool-using AI systems. "
            "The loop runs until the API response has stop_reason='end_turn', "
            "which signals the model is finished. While stop_reason='tool_use', "
            "the loop continues. Each iteration sends the full message history "
            "back to the model so it can decide the next action."
        )
    },
    "https://example.com/prompt-engineering": {
        "title": "Five Prompt Engineering Techniques That Matter",
        "content": (
            "The most effective prompt engineering techniques in 2026 are: "
            "1) Clear roles and instructions, 2) Multishot prompting with worked examples, "
            "3) XML tags for structure, 4) Chain of thought reasoning, "
            "and 5) Prefilling assistant responses to force format compliance."
        )
    },
    "https://example.com/tool-use-basics": {
        "title": "Tool Use Fundamentals",
        "content": (
            "Tool use in Claude works through a request/response pattern. "
            "The model never executes tools directly. Instead, it returns a tool_use "
            "block with the tool name and arguments, and your application code "
            "executes the tool and returns the result via a tool_result block. "
            "The tool_use_id field connects requests to results."
        )
    },
    "https://example.com/ghl-automation": {
        "title": "GHL Automation Patterns for Marketing Agencies",
        "content": (
            "GoHighLevel automation for marketing agencies centers on a few patterns: "
            "lead routing via tags and pipelines, A2P 10DLC compliance for SMS, "
            "Conversation AI for first-response automation, and snapshot-based "
            "client onboarding to reduce per-client setup time."
        )
    },
}

# ===== Tool schemas =====
tools = [
    {
        "name": "search_articles",
        "description": "Search a database of technical articles. Returns a list of matching articles with their titles and URLs. Call this first when you need to find information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords or topic to find articles about"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "read_article",
        "description": "Read the full content of a specific article by URL. Use this after search_articles has given you URLs to choose from.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the article to read"
                }
            },
            "required": ["url"]
        }
    }
]

# ===== Tool execution =====
def execute_search_articles(query: str):
    """Naive keyword matching - real search would use embeddings."""
    query_words = query.lower().split()
    matches = []
    for url, article in ARTICLES.items():
        title_lower = article["title"].lower()
        content_lower = article["content"].lower()
        if any(word in title_lower or word in content_lower for word in query_words):
            matches.append({"url": url, "title": article["title"]})
    
    if not matches:
        return "No articles found matching that query."
    
    result = f"Found {len(matches)} articles:\n"
    for m in matches:
        result += f"  - {m['title']} ({m['url']})\n"
    return result

def execute_read_article(url: str):
    if url not in ARTICLES:
        return f"Article not found at {url}"
    article = ARTICLES[url]
    return f"Title: {article['title']}\n\nContent: {article['content']}"

def execute_tool(tool_name: str, tool_input: dict):
    if tool_name == "search_articles":
        return execute_search_articles(tool_input["query"])
    elif tool_name == "read_article":
        return execute_read_article(tool_input["url"])
    else:
        return f"Unknown tool: {tool_name}"


# ===== The agent loop (same shape as v1) =====
def run_agent(user_message: str, verbose: bool = True):
    messages = [{"role": "user", "content": user_message}]
    iteration = 0
    
    while True:
        iteration += 1
        if verbose:
            print(f"\n--- Loop iteration {iteration} ---")
        
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )
        
        if verbose:
            print(f"Stop reason: {response.stop_reason}")
        
        if response.stop_reason == "end_turn":
            final_text = ""
            for block in response.content:
                if block.type == "text":
                    final_text += block.text
            return final_text
        
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    if verbose:
                        print(f"Claude wants to call: {block.name}({json.dumps(block.input)})")
                    result = execute_tool(block.name, block.input)
                    if verbose:
                        # Truncate long results for readable output
                        preview = result if len(result) < 200 else result[:200] + "..."
                        print(f"Tool returned: {preview}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            
            messages.append({"role": "user", "content": tool_results})
        
        if iteration > 10:
            return "Agent stopped: too many iterations"


# ===== Test questions =====
test_questions = [
    "What does the article on agent loops say about the stop_reason field?",
    "What are the GHL automation patterns mentioned in the database?",
    "Find articles about prompt engineering and summarize the main techniques.",
]

for question in test_questions:
    print("\n" + "=" * 70)
    print(f"USER: {question}")
    print("=" * 70)
    answer = run_agent(question)
    print(f"\nFINAL ANSWER: {answer[:500]}{'...' if len(answer) > 500 else ''}")