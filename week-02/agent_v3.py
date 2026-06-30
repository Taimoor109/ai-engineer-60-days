import os
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

# ===== Tool schemas =====
tools = [
    {
        "name": "fetch_website",
        "description": "Fetch the homepage content of a website URL. Returns the cleaned page text. Use this FIRST when researching a company.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL to fetch, including https://"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "extract_company_info",
        "description": "Extract structured company information from a block of website text. Returns company name, industry, size, services, and target market.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Raw text content from a company website"
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "score_fit",
        "description": "Score how well a company fits as a prospect for GHL+AI automation services for marketing agencies. Returns a score 0-100, category, and reasoning. Use this AFTER you have company info.",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string"},
                "industry": {"type": "string"},
                "size": {"type": "string"},
                "services": {"type": "string"},
                "target_market": {"type": "string"}
            },
            "required": ["company_name", "industry", "size", "services", "target_market"]
        }
    },
    {
        "name": "save_research",
        "description": "Save the final research output to a JSON file on disk. Call this as the LAST step after you have completed all research.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "The filename to save to, e.g. 'research_anthropic.json'"},
                "data": {
                    "type": "object",
                    "description": "The complete research data including url, company info, and fit score",
                    "properties": {
                        "url": {"type": "string"},
                        "company_name": {"type": "string"},
                        "industry": {"type": "string"},
                        "size": {"type": "string"},
                        "services": {"type": "string"},
                        "target_market": {"type": "string"},
                        "fit_score": {"type": "integer"},
                        "fit_category": {"type": "string"},
                        "reasoning": {"type": "string"}
                    },
                    "required": ["url", "company_name", "fit_score", "fit_category", "reasoning"]
                }
            },
            "required": ["filename", "data"]
        }
    }
]

# ===== Tool execution functions =====
def execute_fetch_website(url: str):
    try:
        response = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'footer']):
            tag.decompose()
        text = soup.get_text(separator=' ', strip=True)
        return text[:3500]
    except Exception as e:
        return f"Failed to fetch {url}: {str(e)}"


def execute_extract_company_info(text: str):
    """Uses Claude internally to extract structured info from raw text."""
    extract_tool = {
        "name": "company_extraction",
        "description": "Extract company info",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string"},
                "industry": {"type": "string"},
                "size": {"type": "string", "description": "small, medium, large, enterprise, or unknown"},
                "services": {"type": "string"},
                "target_market": {"type": "string"}
            },
            "required": ["company_name", "industry", "size", "services", "target_market"]
        }
    }
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        temperature=0.0,
        tools=[extract_tool],
        tool_choice={"type": "tool", "name": "company_extraction"},
        messages=[{
            "role": "user",
            "content": f"Extract company info from this website content:\n\n{text}"
        }]
    )
    for block in response.content:
        if block.type == "tool_use":
            return json.dumps(block.input, indent=2)
    return "Extraction failed"


def execute_score_fit(company_name, industry, size, services, target_market):
    """Uses Claude internally to score fit."""
    score_tool = {
        "name": "fit_scoring",
        "description": "Score prospect fit",
        "input_schema": {
            "type": "object",
            "properties": {
                "fit_score": {"type": "integer", "description": "0-100"},
                "fit_category": {
                    "type": "string",
                    "enum": ["strong_fit", "possible_fit", "wrong_fit", "competitor"]
                },
                "reasoning": {"type": "string"}
            },
            "required": ["fit_score", "fit_category", "reasoning"]
        }
    }
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=400,
        temperature=0.0,
        tools=[score_tool],
        tool_choice={"type": "tool", "name": "fit_scoring"},
        system=(
            "You score prospects for a GHL + AI automation specialist serving marketing agencies. "
            "Strong fit: marketing agencies, GHL operators, automation consultancies. "
            "Possible fit: SaaS serving agencies. "
            "Wrong fit: solo consultants, B2C brands, tech product companies. "
            "Competitor: other GHL/automation agencies."
        ),
        messages=[{
            "role": "user",
            "content": (f"Score this prospect:\n"
                       f"Company: {company_name}\n"
                       f"Industry: {industry}\n"
                       f"Size: {size}\n"
                       f"Services: {services}\n"
                       f"Target market: {target_market}")
        }]
    )
    for block in response.content:
        if block.type == "tool_use":
            return json.dumps(block.input, indent=2)
    return "Scoring failed"


def execute_save_research(filename: str, data: dict):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return f"Saved research to {filename}"
    except Exception as e:
        return f"Save failed: {str(e)}"


def execute_tool(tool_name: str, tool_input: dict):
    if tool_name == "fetch_website":
        return execute_fetch_website(tool_input["url"])
    elif tool_name == "extract_company_info":
        return execute_extract_company_info(tool_input["text"])
    elif tool_name == "score_fit":
        return execute_score_fit(
            tool_input["company_name"],
            tool_input["industry"],
            tool_input["size"],
            tool_input["services"],
            tool_input["target_market"]
        )
    elif tool_name == "save_research":
        return execute_save_research(tool_input["filename"], tool_input["data"])
    else:
        return f"Unknown tool: {tool_name}"


# ===== The agent loop =====
def run_agent(user_message: str, verbose: bool = True):
    messages = [{"role": "user", "content": user_message}]
    iteration = 0
    total_in = 0
    total_out = 0
    
    while True:
        iteration += 1
        if verbose:
            print(f"\n--- Loop iteration {iteration} ---")
        
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2000,
            tools=tools,
            messages=messages
        )
        
        total_in += response.usage.input_tokens
        total_out += response.usage.output_tokens
        
        if verbose:
            print(f"Stop reason: {response.stop_reason} | Tokens: in={response.usage.input_tokens}, out={response.usage.output_tokens}")
        
        if response.stop_reason == "end_turn":
            final_text = ""
            for block in response.content:
                if block.type == "text":
                    final_text += block.text
            if verbose:
                print(f"\nTotal tokens used: in={total_in}, out={total_out}")
                print(f"Approx cost: ${(total_in * 3 + total_out * 15) / 1_000_000:.4f}")
            return final_text
        
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    if verbose:
                        input_preview = json.dumps(block.input)
                        if len(input_preview) > 150:
                            input_preview = input_preview[:150] + "..."
                        print(f"Claude calls: {block.name}({input_preview})")
                    result = execute_tool(block.name, block.input)
                    if verbose:
                        preview = result if len(result) < 250 else result[:250] + "..."
                        print(f"  -> {preview}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            
            messages.append({"role": "user", "content": tool_results})
        
        if iteration > 12:
            return "Agent stopped: too many iterations"


# ===== Test on a real company =====
question = (
    "Research the company at https://drovinsolutions.com. "
    "Find out what they do, score them as a prospect for my GHL+AI automation services, "
    "and save the complete research to a JSON file."
)

print("=" * 70)
print(f"USER: {question}")
print("=" * 70)
answer = run_agent(question)
print(f"\n=== FINAL ANSWER ===\n{answer}")