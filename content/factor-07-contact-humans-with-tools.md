[← Back to README](https://github.com/humanlayer/12-factor-agents/blob/main/README.md)

### 7. Contact humans with tool calls

By default, LLM APIs rely on a fundamental HIGH-STAKES token choice: Are we returning plaintext content, or are we returning structured data?

![170-contact-humans-with-tools](https://github.com/humanlayer/12-factor-agents/blob/main/img/170-contact-humans-with-tools.png)

You're putting a lot of weight on that choice of first token, which, in the `the weather in tokyo` case, is

> "the"

but in the `fetch_weather` case, it's some special token to denote the start of a JSON object.

> |JSON>

You might get better results by having the LLM *always* output json, and then declare it's intent with some natural language tokens like `request_human_input` or `done_for_now` (as opposed to a "proper" tool like `check_weather_in_city`). 

Again, you might not get any performance boost from this, but you should experiment, and ensure you're free to try weird stuff to get the best results.

```python

class Options:
  urgency: Literal["low", "medium", "high"]
  format: Literal["free_text", "yes_no", "multiple_choice"]
  choices: List[str]

# Tool definition for human interaction
class RequestHumanInput:
  intent: "request_human_input"
  question: str
  context: str
  options: Options

# Example usage in the agent loop
if nextStep.intent == 'request_human_input':
  thread.events.append({
    type: 'human_input_requested',
    data: nextStep
  })
  thread_id = await save_state(thread)
  await notify_human(nextStep, thread_id)
  return # Break loop and wait for response to come back with thread ID
else:
  # ... other cases
```

Later, you might receive a webhook from a system that handles slack, email, sms, or other events.

```python

@app.post('/webhook')
def webhook(req: Request):
  thread_id = req.body.threadId
  thread = await load_state(thread_id)
  thread.events.push({
    type: 'response_from_human',
    data: req.body
  })
  # ... simplified for brevity, you likely don't want to block the web worker here
  next_step = await determine_next_step(thread_to_prompt(thread))
  thread.events.append(next_step)
  result = await handle_next_step(thread, next_step)
  # todo - loop or break or whatever you want

  return {"status": "ok"}
```

The above includes patterns from [factor 5 - unify execution state and business state](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-05-unify-execution-state.md), [factor 8 - own your control flow](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-08-own-your-control-flow.md), [factor 3 - own your context window](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md), and [factor 4 - tools are just structured outputs](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-04-tools-are-structured-outputs.md), and several others.

If we were using the XML-y formatted from [factor 3 - own your context window](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md), our context window after a few turns might look like this:

```xml

(snipped for brevity)

<slack_message>
    From: @alex
    Channel: #deployments
    Text: Can you deploy backend v1.2.3 to production?
    Thread: []
</slack_message>

<request_human_input>
    intent: "request_human_input"
    question: "Would you like to proceed with deploying v1.2.3 to production?"
    context: "This is a production deployment that will affect live users."
    options: {
        urgency: "high"
        format: "yes_no"
    }
</request_human_input>

<human_response>
    response: "yes please proceed"
    approved: true
    timestamp: "2024-03-15T10:30:00Z"
    user: "alex@company.com"
</human_response>

<deploy_backend>
    intent: "deploy_backend"
    tag: "v1.2.3"
    environment: "production"
</deploy_backend>

<deploy_backend_result>
    status: "success"
    message: "Deployment v1.2.3 to production completed successfully."
    timestamp: "2024-03-15T10:30:00Z"
</deploy_backend_result>
```


Benefits:

1. **Clear Instructions**: Tools for different types of human contact allow for more specificity from the LLM
2. **Inner vs Outer Loop**: Enables agents workflows **outside** of the traditional chatGPT-style interface, where the control flow and context initialization may be `Agent->Human` rather than `Human->Agent` (think, agents kicked off by a cron or an event)
3. **Multiple Human Access**: Can easily track and coordinate input from different humans through structured events
4. **Multi-Agent**: Simple abstraction can be easily extended to support `Agent->Agent` requests and responses
5. **Durable**: Combined with [factor 6 - launch/pause/resume with simple APIs](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-06-launch-pause-resume.md), this makes for durable, reliable, and introspectable multiplayer workflows

[More on Outer Loop Agents over here](https://theouterloop.substack.com/p/openais-realtime-api-is-a-step-towards)

![175-outer-loop-agents](https://github.com/humanlayer/12-factor-agents/blob/main/img/175-outer-loop-agents.png)

Works great with [factor 11 - trigger from anywhere, meet users where they are](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-11-trigger-from-anywhere.md)

### Claude Example

Use Claude's tool use API to generate human contact requests:

```python
from anthropic import Anthropic
import json

client = Anthropic()

# Define human contact tools with detailed schemas
human_contact_tools = [
    {
        "name": "request_human_input",
        "description": "Request clarification or information from a human",
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Specific question to ask the human"
                },
                "context": {
                    "type": "string",
                    "description": "Background information to help the human understand"
                },
                "urgency": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "How urgent is this request"
                },
                "response_format": {
                    "type": "string",
                    "enum": ["free_text", "yes_no", "multiple_choice"],
                    "description": "Expected response format"
                },
                "options": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Options for multiple_choice format"
                }
            },
            "required": ["question"]
        }
    },
    {
        "name": "request_approval",
        "description": "Request approval for a high-stakes action",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Description of the action to approve"
                },
                "risks": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Potential risks of this action"
                },
                "mitigations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Steps taken to mitigate risks"
                }
            },
            "required": ["action"]
        }
    }
]

async def handle_deployment_request(user_message):
    """Claude determines when to contact humans"""
    
    thread = [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": "I'll help you with that deployment. Let me check the current state first."},
        {"role": "user", "content": "Current version: v1.2.2, Git tags: [v1.2.3, v1.2.2, v1.2.1]"}
    ]
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=thread,
        tools=human_contact_tools + deployment_tools
    )
    
    if response.content[0].type == "tool_use":
        tool_call = response.content[0]
        
        if tool_call.name == "request_human_input":
            # Claude generated a question for the human
            question = tool_call.input["question"]
            context = tool_call.input.get("context", "")
            urgency = tool_call.input.get("urgency", "medium")
            
            # Send to human via Slack/email
            await send_to_slack({
                "channel": "#deployments",
                "text": f"🤖 Agent needs input (Priority: {urgency})",
                "blocks": [
                    {"type": "section", "text": {"type": "mrkdwn", "text": question}},
                    {"type": "context", "elements": [{"type": "mrkdwn", "text": context}]},
                    {"type": "actions", "elements": [
                        {"type": "button", "text": "Respond", "action_id": "respond_to_agent"}
                    ]}
                ]
            })
            
            # Pause and save state
            return {"status": "paused", "waiting_for": "human_input"}
        
        elif tool_call.name == "request_approval":
            # High-stakes action needs approval
            action = tool_call.input["action"]
            risks = tool_call.input.get("risks", [])
            
            await send_to_slack({
                "channel": "#deployments",
                "text": f"🔴 Approval Required: {action}",
                "blocks": [
                    {"type": "section", "text": {"type": "mrkdwn", "text": f"*Action:* {action}"}},
                    {"type": "section", "text": {"type": "mrkdwn", "text": "*Risks:*\n" + "\n".join(f"• {r}" for r in risks)}},
                    {"type": "actions", "elements": [
                        {"type": "button", "text": "✅ Approve", "style": "primary", "action_id": "approve"},
                        {"type": "button", "text": "❌ Deny", "style": "danger", "action_id": "deny"}
                    ]}
                ]
            })
            
            return {"status": "paused", "waiting_for": "approval"}
```

This approach:
- Always returns JSON (no plaintext vs structured dilemma)
- Uses natural language intents like "request_human_input"
- Enables outer loop agents triggered by events
- Works across Slack, email, SMS, or any channel

[← Launch/Pause/Resume](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-06-launch-pause-resume.md) | [Own Your Control Flow →](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-08-own-your-control-flow.md)
