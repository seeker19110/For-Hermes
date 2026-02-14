[← Back to README](https://github.com/humanlayer/12-factor-agents/blob/main/README.md)

### 4. Tools are just structured outputs

Tools don't need to be complex. At their core, they're just structured output from your LLM that triggers deterministic code.

![140-tools-are-just-structured-outputs](https://github.com/humanlayer/12-factor-agents/blob/main/img/140-tools-are-just-structured-outputs.png)

For example, lets say you have two tools `CreateIssue` and `SearchIssues`. To ask an LLM to "use one of several tools" is just to ask it to output JSON we can parse into an object representing those tools.

```python

class Issue:
  title: str
  description: str
  team_id: str
  assignee_id: str

class CreateIssue:
  intent: "create_issue"
  issue: Issue

class SearchIssues:
  intent: "search_issues"
  query: str
  what_youre_looking_for: str
```

The pattern is simple:
1. LLM outputs structured JSON
3. Deterministic code executes the appropriate action (like calling an external API)
4. Results are captured and fed back into the context

This creates a clean separation between the LLM's decision-making and your application's actions. The LLM decides what to do, but your code controls how it's done. Just because an LLM "called a tool" doesn't mean you have to go execute a specific corresponding function in the same way every time.

If you recall our switch statement from above

```python
if nextStep.intent == 'create_payment_link':
    stripe.paymentlinks.create(nextStep.parameters)
    return # or whatever you want, see below
elif nextStep.intent == 'wait_for_a_while': 
    # do something monadic idk
else: #... the model didn't call a tool we know about
    # do something else
```

**Note**: there has been a lot said about the benefits of "plain prompting" vs. "tool calling" vs. "JSON mode" and the performance tradeoffs of each. We'll link some resources to that stuff soon, but not gonna get into it here. See [Prompting vs JSON Mode vs Function Calling vs Constrained Generation vs SAP](https://www.boundaryml.com/blog/schema-aligned-parsing), [When should I use function calling, structured outputs, or JSON mode?](https://www.vellum.ai/blog/when-should-i-use-function-calling-structured-outputs-or-json-mode#:~:text=We%20don%27t%20recommend%20using%20JSON,always%20use%20Structured%20Outputs%20instead) and [OpenAI JSON vs Function Calling](https://docs.llamaindex.ai/en/stable/examples/llm/openai_json_vs_function_calling/).

The "next step" might not be as atomic as just "run a pure function and return the result". You unlock a lot of flexibility when you think of "tool calls" as just a model outputting JSON describing what deterministic code should do. Put this together with [factor 8 own your control flow](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-08-own-your-control-flow.md).

### Claude Example

Claude's tool use API provides type-safe structured outputs via JSON Schema:

```python
from anthropic import Anthropic
import json

client = Anthropic()

# Define tools with JSON Schema - Claude validates outputs against these schemas
tools = [
    {
        "name": "create_issue",
        "description": "Create a Linear issue with title, description, and priority",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Issue title - be specific and actionable"
                },
                "description": {
                    "type": "string",
                    "description": "Detailed description of the issue"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "urgent"],
                    "description": "Issue priority level"
                },
                "team_id": {
                    "type": "string",
                    "description": "Linear team identifier"
                }
            },
            "required": ["title", "description", "priority"]
        }
    },
    {
        "name": "search_issues",
        "description": "Search for existing issues",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string"
                },
                "state": {
                    "type": "string",
                    "enum": ["backlog", "todo", "in_progress", "done", "canceled"],
                    "description": "Filter by issue state"
                }
            },
            "required": ["query"]
        }
    }
]

# Claude outputs structured JSON matching the schema
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    messages=[{
        "role": "user",
        "content": "Create a high priority issue about the login bug affecting production users"
    }],
    tools=tools
)

# Extract tool call from response
if response.content[0].type == "tool_use":
    tool_call = response.content[0]
    print(f"Tool: {tool_call.name}")
    print(f"Arguments: {json.dumps(tool_call.input, indent=2)}")
    # Output:
    # Tool: create_issue
    # Arguments: {
    #   "title": "Login bug affecting production users",
    #   "description": "Users are unable to log in to the production environment...",
    #   "priority": "high"
    # }
    
    # Execute deterministic code based on structured output
    if tool_call.name == "create_issue":
        result = linear_client.create_issue(**tool_call.input)
```

Claude's tool use provides:
- JSON Schema validation for type safety
- Automatic parameter extraction from natural language
- Support for complex nested objects
- Clear separation between LLM decision-making and code execution

[← Own Your Context Window](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md) | [Unify Execution State →](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-05-unify-execution-state.md)
