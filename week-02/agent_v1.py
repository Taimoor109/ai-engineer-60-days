import os
import json
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

# ===== Tool schemas (what Claude sees) =====
tools = [
    {
        "name": "get_current_time",
        "description": "Get the current date and time. Use this when the user asks about time or wants to know what time it is.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "calculate",
        "description": "Perform a basic arithmetic calculation. Use this when the user asks a math question.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A math expression to evaluate, e.g. '2 + 2' or '47 * 3.14'"
                }
            },
            "required": ["expression"]
        }
    }
]

# ===== Tool execution functions (what your code actually runs) =====
def execute_get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def execute_calculate(expression: str):
    try:
        # eval() is dangerous in production - we use it here for simplicity
        # In real systems, use a proper math parser
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"

def execute_tool(tool_name: str, tool_input: dict):
    """Dispatcher - takes a tool name and arguments, runs the right function."""
    if tool_name == "get_current_time":
        return execute_get_current_time()
    elif tool_name == "calculate":
        return execute_calculate(tool_input["expression"])
    else:
        return f"Unknown tool: {tool_name}"


# ===== The agent loop =====
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
        
        # Did Claude stop because it wants to use a tool, or because it's done?
        if response.stop_reason == "end_turn":
            # Claude is done - extract the final text and return
            final_text = ""
            for block in response.content:
                if block.type == "text":
                    final_text += block.text
            return final_text
        
        if response.stop_reason == "tool_use":
            # Claude wants to call one or more tools
            # First, add Claude's response to message history
            messages.append({"role": "assistant", "content": response.content})
            
            # Then execute each tool call and append results
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    if verbose:
                        print(f"Claude wants to call: {block.name}({json.dumps(block.input)})")
                    
                    result = execute_tool(block.name, block.input)
                    
                    if verbose:
                        print(f"Tool returned: {result}")
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            
            # Send tool results back to Claude in a user message
            messages.append({"role": "user", "content": tool_results})
            # Loop continues - Claude will see the results and decide what's next
        
        # Safety: don't run forever
        if iteration > 10:
            return "Agent stopped: too many iterations"


# ===== Test it on three questions =====
test_questions = [
    "What time is it right now?",
    "What's 1247 multiplied by 89?",
    "What time is it, and also what's 23 squared?"
]

for question in test_questions:
    print("\n" + "=" * 70)
    print(f"USER: {question}")
    print("=" * 70)
    answer = run_agent(question)
    print(f"\nFINAL ANSWER: {answer}")