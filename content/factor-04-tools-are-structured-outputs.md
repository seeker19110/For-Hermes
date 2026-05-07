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

#### Tool contracts should describe outputs too

If a tool returns structured data, its contract should describe both sides of
the exchange:

1. the structured input the model is allowed to request
2. the structured output deterministic code will append back to state or context

Input schemas help the model and runtime agree on how to call a tool. Output
schemas help the model and runtime agree on what kind of data will come back.
That closes an important gap for planning, validation, and context management.

For example, a tool registry entry can include an `output_schema` next to the
input schema. In JSON-based protocols this might be exposed as `outputSchema`;
the naming matters less than making the output contract discoverable.

```python
class SearchIssues:
  intent: "search_issues"
  input_schema: {
    "type": "object",
    "required": ["query"],
    "properties": {
      "query": {"type": "string"}
    }
  }
  output_schema: {
    "type": "object",
    "required": ["issues"],
    "properties": {
      "issues": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["id", "title", "status"],
          "properties": {
            "id": {"type": "string"},
            "title": {"type": "string"},
            "status": {"type": "string"},
            "url": {"type": "string"}
          }
        }
      }
    }
  }
```

Once the runtime knows the output shape, it can do a few useful things before
the result goes back into the agent loop:

- validate that the actual tool result matches the advertised contract
- generate typed client objects for deterministic code
- compare expected vs. actual outputs in logs and traces
- let the model request a projection of the result, such as only `issues[].url`

The last point is especially useful when a tool can return a large payload. If
the model knows the output schema up front, it can ask for the small piece of
data it needs instead of forcing the whole response into the context window.

[← Own Your Context Window](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md) | [Unify Execution State →](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-05-unify-execution-state.md)
