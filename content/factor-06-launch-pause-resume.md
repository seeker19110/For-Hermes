[← Back to README](https://github.com/humanlayer/12-factor-agents/blob/main/README.md)

### 6. Launch/Pause/Resume with simple APIs

Agents are just programs, and we have things we expect from how to launch, query, resume, and stop them.

[![pause-resume animation](https://github.com/humanlayer/12-factor-agents/blob/main/img/165-pause-resume-animation.gif)](https://github.com/user-attachments/assets/feb1a425-cb96-4009-a133-8bd29480f21f)

<details>
<summary><a href="https://github.com/humanlayer/12-factor-agents/blob/main/img/165-pause-resume-animation.gif">GIF Version</a></summary>

![pause-resume animation](https://github.com/humanlayer/12-factor-agents/blob/main/img/165-pause-resume-animation.gif)

</details>


It should be easy for users, apps, pipelines, and other agents to launch an agent with a simple API.

Agents and their orchestrating deterministic code should be able to pause an agent when a long-running operation is needed.

External triggers like webhooks should enable agents to resume from where they left off without deep integration with the agent orchestrator.

Closely related to [factor 5 - unify execution state and business state](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-05-unify-execution-state.md) and [factor 8 - own your control flow](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-08-own-your-control-flow.md), but can be implemented independently.



**Note** - often AI orchestrators will allow for pause and resume, but not between the moment of tool selection and tool execution. See also [factor 7 - contact humans with tool calls](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-07-contact-humans-with-tools.md) and [factor 11 - trigger from anywhere, meet users where they are](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-11-trigger-from-anywhere.md).

### Claude Example

Implement durable execution with Claude using webhooks for resumption:

```python
from anthropic import Anthropic
from fastapi import FastAPI
import json
import redis

app = FastAPI()
client = Anthropic()
redis_client = redis.Redis()

class ResumableClaudeAgent:
    def __init__(self):
        self.thread = []
    
    async def run(self, initial_message):
        """Launch agent with initial request"""
        self.thread = [{"role": "user", "content": initial_message}]
        return await self._continue()
    
    async def _continue(self):
        """Continue execution until pause or completion"""
        while True:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=self.thread,
                tools=self.get_tools()
            )
            
            if response.content[0].type == "tool_use":
                tool_call = response.content[0]
                
                # Add tool call to thread
                self.thread.append({
                    "role": "assistant",
                    "content": json.dumps({
                        "tool": tool_call.name,
                        "arguments": tool_call.input
                    })
                })
                
                # Check if we should pause
                if tool_call.name == "request_human_input":
                    # Pause and save state
                    thread_id = await self._save_state()
                    await self._notify_human(tool_call.input, thread_id)
                    return {
                        "status": "paused",
                        "reason": "awaiting_human_input",
                        "thread_id": thread_id
                    }
                
                elif tool_call.name == "deploy_production":
                    # Pause for approval before executing high-stakes tool
                    thread_id = await self._save_state()
                    await self._request_approval(tool_call.input, thread_id)
                    return {
                        "status": "paused",
                        "reason": "awaiting_approval",
                        "thread_id": thread_id
                    }
                
                # Execute tool and continue
                result = await self._execute_tool(tool_call)
                self.thread.append({
                    "role": "user",
                    "content": f"Tool result: {json.dumps(result)}"
                })
            else:
                # Task complete
                return {
                    "status": "completed",
                    "message": response.content[0].text
                }
    
    async def resume(self, thread_id, human_response):
        """Resume from webhook callback"""
        # Load thread from Redis
        thread_data = redis_client.get(thread_id)
        self.thread = json.loads(thread_data)
        
        # Add human response to thread
        self.thread.append({
            "role": "user",
            "content": f"Human response: {json.dumps(human_response)}"
        })
        
        # Continue execution
        return await self._continue()
    
    async def _save_state(self):
        """Save thread to Redis for later resumption"""
        thread_id = f"claude_thread_{hash(str(self.thread))}"
        redis_client.setex(thread_id, 86400, json.dumps(self.thread))  # 24h TTL
        return thread_id

# HTTP endpoint to start agent
@app.post("/agent/start")
async def start_agent(request: dict):
    agent = ResumableClaudeAgent()
    result = await agent.run(request["message"])
    return result

# Webhook endpoint for human responses
@app.post("/webhook/human-response")
async def human_response_webhook(request: dict):
    """Resume agent after human responds"""
    agent = ResumableClaudeAgent()
    result = await agent.resume(
        request["thread_id"],
        request["response"]
    )
    return result

# Webhook endpoint for approvals
@app.post("/webhook/approval")
async def approval_webhook(request: dict):
    """Resume after approval/denial"""
    agent = ResumableClaudeAgent()
    
    if request["approved"]:
        # Add approval to thread and continue
        result = await agent.resume(
            request["thread_id"],
            {"approved": True, "note": request.get("note", "")}
        )
    else:
        # Handle rejection
        result = await agent.resume(
            request["thread_id"],
            {"approved": False, "reason": request.get("reason", "")}
        )
    
    return result
```

This pattern enables:
- Clean pause/resume between tool selection and execution
- No in-memory state to lose
- Easy webhook integration
- Support for long-running human-in-the-loop workflows

[← Unify Execution State](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-05-unify-execution-state.md) | [Contact Humans With Tools →](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-07-contact-humans-with-tools.md)