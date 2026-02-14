[← Back to README](https://github.com/humanlayer/12-factor-agents/blob/main/README.md)

# Building 12-Factor Agents with Claude

This guide provides comprehensive best practices for implementing the 12-factor agents methodology using Anthropic's Claude models. Claude's unique capabilities—such as its large context window (up to 200K tokens), sophisticated tool use API, and strong reasoning abilities—make it an excellent choice for building production-grade agents.

## Why Claude for 12-Factor Agents?

Claude offers several advantages for building reliable agents:

1. **Large Context Window**: Up to 200K tokens enables handling complex, multi-step workflows without losing context
2. **Strong Tool Use API**: Native support for function calling with precise JSON output
3. **Excellent Reasoning**: Strong performance on complex reasoning tasks requiring multiple steps
4. **Safety and Alignment**: Built-in safety features reduce the risk of harmful outputs
5. **Vision Capabilities**: Claude can process images and documents alongside text

## Quick Start: Claude + 12-Factor Agents

### Installation

```bash
pip install anthropic
```

### Basic Agent Loop with Claude

```python
from anthropic import Anthropic
import json

client = Anthropic()

class Agent:
    def __init__(self):
        self.client = Anthropic()
        self.thread = []
    
    def system_prompt(self):
        return """You are a helpful assistant that manages deployments.
        
You have access to the following tools:
- list_git_tags: List available git tags
- deploy_backend: Deploy backend to specified environment
- request_human_input: Ask a human for clarification or approval
- done_for_now: Complete the task and provide a summary

Always respond with a JSON object containing an "intent" field and relevant parameters."""
    
    async def determine_next_step(self, thread):
        """Factor 1: Natural Language to Tool Calls"""
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=self.system_prompt(),
            messages=thread,
            tools=[
                {
                    "name": "list_git_tags",
                    "description": "List available git tags",
                    "input_schema": {"type": "object", "properties": {}}
                },
                {
                    "name": "deploy_backend",
                    "description": "Deploy backend to environment",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "tag": {"type": "string"},
                            "environment": {"type": "string", "enum": ["staging", "production"]}
                        },
                        "required": ["tag", "environment"]
                    }
                },
                {
                    "name": "request_human_input",
                    "description": "Request input from a human",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "urgency": {"type": "string", "enum": ["low", "medium", "high"]}
                        },
                        "required": ["question"]
                    }
                },
                {
                    "name": "done_for_now",
                    "description": "Complete the task",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string"}
                        },
                        "required": ["message"]
                    }
                }
            ]
        )
        
        # Extract tool use from response (Factor 4: Tools are structured outputs)
        if response.content and response.content[0].type == "tool_use":
            return {
                "intent": response.content[0].name,
                **response.content[0].input
            }
        return {"intent": "done_for_now", "message": "Task completed"}
    
    async def run(self, initial_message):
        """Main agent loop"""
        self.thread = [{"role": "user", "content": initial_message}]
        
        while True:
            next_step = await self.determine_next_step(self.thread)
            
            # Add the tool call to context (Factor 3: Own your context window)
            self.thread.append({
                "role": "assistant",
                "content": json.dumps(next_step)
            })
            
            # Handle the structured output (Factor 8: Own your control flow)
            if next_step["intent"] == "done_for_now":
                return next_step["message"]
            
            elif next_step["intent"] == "list_git_tags":
                result = await self.list_git_tags()
                self.thread.append({
                    "role": "user",
                    "content": f"list_git_tags_result: {json.dumps(result)}"
                })
            
            elif next_step["intent"] == "deploy_backend":
                # Factor 8: Interrupt for human approval
                if next_step.get("environment") == "production":
                    await self.request_human_approval(next_step)
                    break  # Pause and wait for webhook
                
                result = await self.deploy_backend(next_step["tag"], next_step["environment"])
                self.thread.append({
                    "role": "user",
                    "content": f"deploy_backend_result: {json.dumps(result)}"
                })
            
            elif next_step["intent"] == "request_human_input":
                await self.request_human_approval(next_step)
                break  # Pause and wait for response
    
    async def list_git_tags(self):
        # Implementation
        return ["v1.0.0", "v1.1.0", "v1.2.0"]
    
    async def deploy_backend(self, tag, environment):
        # Implementation
        return {"status": "success", "tag": tag, "environment": environment}
    
    async def request_human_approval(self, step):
        # Factor 6: Pause and save state
        thread_id = await self.save_thread()
        await self.notify_human(step, thread_id)
    
    async def save_thread(self):
        # Serialize thread for resumption (Factor 5: Unify execution and business state)
        return "thread_123"
    
    async def notify_human(self, step, thread_id):
        # Send notification via Slack/email (Factor 7: Contact humans with tools)
        pass
    
    async def resume_from_webhook(self, thread_id, human_response):
        # Factor 6: Resume from webhook
        self.thread = await self.load_thread(thread_id)
        self.thread.append({
            "role": "user",
            "content": f"human_response: {json.dumps(human_response)}"
        })
        return await self.run_continue()
    
    async def load_thread(self, thread_id):
        # Load serialized thread
        return []
    
    async def run_continue(self):
        # Continue execution after resume
        while True:
            next_step = await self.determine_next_step(self.thread)
            # ... continue loop
```

## Factor-by-Factor Claude Best Practices

### Factor 1: Natural Language to Tool Calls

Claude excels at converting natural language to structured tool calls:

```python
# Claude can parse ambiguous requests into precise tool calls
user_input = "deploy the latest version to prod"

# Claude outputs:
{
    "intent": "deploy_backend",
    "tag": "v1.2.3",  # Inferred as "latest"
    "environment": "production"  # "prod" normalized
}
```

**Best Practice**: Use Claude's tool use API rather than manual JSON parsing for more reliable structured outputs.

### Factor 2: Own Your Prompts

With Claude, you have full control over prompts:

```python
# Direct control over system prompt
system_prompt = """You are a deployment assistant. Follow these rules:

1. Always verify git tags exist before deploying
2. Request human approval for production deployments
3. Use structured JSON output with "intent" field
4. If uncertain, use request_human_input tool

Current git tags: {{ git_tags }}
"""

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    system=system_prompt,
    messages=thread,
    # ... tools
)
```

### Factor 3: Own Your Context Window

Claude's 200K context window allows sophisticated context engineering:

```python
# Custom XML-style context format works well with Claude
context = """<conversation_history>
    <event type="user_request">
        Deploy backend v1.2.3 to production
    </event>
    <event type="tool_call" name="list_git_tags">
        Result: ["v1.2.1", "v1.2.2", "v1.2.3"]
    </event>
    <event type="human_approval" status="pending">
        Requested approval for production deployment
    </event>
</conversation_history>

What is the next step?"""

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=[{"role": "user", "content": context}]
)
```

### Factor 4: Tools Are Structured Outputs

Claude's tool use API provides type-safe structured outputs:

```python
# Define tools with JSON schema
tools = [{
    "name": "create_issue",
    "description": "Create a Linear issue",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]}
        },
        "required": ["title", "description"]
    }
}]

# Claude returns validated JSON matching the schema
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=messages,
    tools=tools
)
```

### Factor 5: Unify Execution State and Business State

With Claude, store the conversation thread as the single source of truth:

```python
class ThreadStore:
    def save(self, thread_id: str, messages: list):
        """Serialize Claude conversation for resumption"""
        redis.set(thread_id, json.dumps(messages))
    
    def load(self, thread_id: str) -> list:
        """Restore Claude conversation"""
        return json.loads(redis.get(thread_id))

# Execution state is derived from the thread
def get_execution_state(thread):
    """Infer execution state from conversation context"""
    last_message = thread[-1] if thread else None
    if last_message and "tool_use" in last_message:
        return {"waiting_for": "tool_execution"}
    return {"waiting_for": "llm_response"}
```

### Factor 6: Launch/Pause/Resume with Simple APIs

Implement durable execution with Claude:

```python
@app.post("/agent/start")
async def start_agent(request: StartRequest):
    agent = Agent()
    thread_id = await agent.run(request.message)
    return {"thread_id": thread_id, "status": "paused_waiting_human"}

@app.post("/webhook/human-response")
async def human_response_webhook(request: WebhookRequest):
    """Resume agent after human response"""
    agent = Agent()
    result = await agent.resume_from_webhook(
        request.thread_id,
        request.human_response
    )
    return {"result": result}
```

### Factor 7: Contact Humans with Tool Calls

Use Claude to generate human-readable requests:

```python
# Tool schema for human contact
human_contact_tool = {
    "name": "request_human_input",
    "description": "Request approval or clarification from a human",
    "input_schema": {
        "type": "object",
        "properties": {
            "question": {"type": "string"},
            "context": {"type": "string"},
            "options": {
                "type": "object",
                "properties": {
                    "format": {"type": "string", "enum": ["free_text", "yes_no", "multiple_choice"]},
                    "choices": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "required": ["question"]
    }
}

# Claude generates the specific question
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=thread,
    tools=[human_contact_tool]
)

# Result might be:
# {
#     "intent": "request_human_input",
#     "question": "Deploy v1.2.3 to production? This will affect live users.",
#     "context": "Production deployment requested by @alex",
#     "options": {"format": "yes_no"}
# }
```

### Factor 8: Own Your Control Flow

Implement sophisticated control flow with Claude:

```python
async def handle_next_step(thread, next_step):
    """Custom control flow with Claude"""
    
    if next_step["intent"] == "deploy_production":
        # Break for human approval
        await request_human_approval(next_step)
        return {"status": "paused", "reason": "awaiting_approval"}
    
    elif next_step["intent"] == "summarize_logs":
        # Synchronous step - continue loop
        logs = await fetch_logs()
        thread.append({"role": "user", "content": f"logs: {logs}"})
        return {"status": "continue"}
    
    elif next_step["intent"] == "retry_with_backoff":
        # Custom retry logic
        await asyncio.sleep(2 ** attempt_count)
        return {"status": "retry"}
```

### Factor 9: Compact Errors into Context Window

Enable self-healing with Claude:

```python
async def execute_with_error_recovery(thread, tool_call):
    """Factor 9: Self-healing with error feedback"""
    try:
        result = await execute_tool(tool_call)
        return result
    except Exception as e:
        # Add formatted error to context
        error_message = format_error_for_claude(e)
        thread.append({
            "role": "user",
            "content": f"<error>\n{error_message}\n</error>"
        })
        
        # Let Claude suggest recovery
        recovery_step = await agent.determine_next_step(thread)
        return recovery_step

def format_error_for_claude(error):
    """Format errors for Claude's understanding"""
    return f"""Error Type: {type(error).__name__}
Message: {str(error)}
Suggestion: Check if the resource exists and you have proper permissions."""
```

### Factor 10: Small, Focused Agents

Design focused Claude agents:

```python
# Good: Focused agent for a single task
class GitTagAgent:
    """Handles git tag operations only"""
    def __init__(self):
        self.tools = ["list_git_tags", "create_git_tag"]
        self.max_steps = 5

# Bad: Monolithic agent trying to do everything
class MegaAgent:
    """Tries to handle deployments, code review, testing..."""
    def __init__(self):
        self.tools = ["deploy", "review_code", "run_tests", "...50 more tools"]
```

### Factor 11: Trigger From Anywhere

Trigger Claude agents from multiple channels:

```python
# Slack trigger
@slack_events.on("app_mention")
async def handle_slack_mention(event):
    agent = Agent()
    result = await agent.run(event["text"])
    await slack.post_message(event["channel"], result)

# Email trigger
@email_webhook.handler()
async def handle_email(email):
    agent = Agent()
    result = await agent.run(email.body)
    await send_email(email.from_addr, result)

# Cron trigger
@scheduler.cron("0 9 * * *")
async def daily_report():
    agent = Agent()
    report = await agent.run("Generate daily status report")
    await slack.post_message("#reports", report)
```

### Factor 12: Stateless Reducer

Model Claude agents as pure functions:

```python
# Pure function: (state, event) -> new_state
def agent_reducer(thread: list, event: dict) -> list:
    """
    Stateless reducer pattern with Claude.
    Returns new thread state without side effects.
    """
    new_thread = thread.copy()
    new_thread.append(event)
    
    # Deterministic state transition
    if should_process(new_thread):
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=new_thread
        )
        new_thread.append({
            "role": "assistant",
            "content": response.content[0].text
        })
    
    return new_thread
```

## Claude-Specific Tips

### 1. Use XML Tags for Structure

Claude understands XML-style tags well:

```python
context = """<task>
    <description>Deploy backend service</description>
    <environment>production</environment>
</task>

<context>
    <git_tags>
        <tag>v1.2.3</tag>
        <tag>v1.2.2</tag>
    </git_tags>
    <current_deployment>v1.2.2</current_deployment>
</context>

What should I do next?"""
```

### 2. Leverage Claude's Reasoning

Ask Claude to think step by step:

```python
system_prompt = """Before making tool calls, think through the problem:

1. What is the user asking for?
2. What information do I need?
3. What tools should I use?
4. What could go wrong?

Provide your reasoning in <thinking> tags, then make the tool call."""
```

### 3. Handle Rate Limits

Claude has rate limits - implement backoff:

```python
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5)
)
async def call_claude_with_retry(messages, tools):
    return client.messages.create(
        model="claude-3-5-sonnet-20241022",
        messages=messages,
        tools=tools
    )
```

### 4. Use Vision for Documents

Claude can process images and documents:

```python
# Include screenshots or documents in context
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "What's wrong with this error message?"},
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": screenshot_base64}}
        ]
    }]
)
```

## Example: Complete Deployment Agent

Here's a complete example combining all 12 factors:

```python
import asyncio
from anthropic import Anthropic
from fastapi import FastAPI
import json

app = FastAPI()
client = Anthropic()

class DeploymentAgent:
    """12-Factor Agent for managing deployments"""
    
    def __init__(self):
        self.client = Anthropic()
        self.thread = []
    
    def system_prompt(self):
        # Factor 2: Own your prompts
        return """You are a deployment assistant managing backend deployments.

Available tools:
- list_git_tags: List available git tags
- deploy_backend: Deploy to staging or production
- request_human_input: Ask for clarification or approval
- done_for_now: Complete the task

Rules:
1. Always list git tags before deploying
2. Get human approval for production deployments
3. Respond with JSON containing "intent" field"""
    
    def tools(self):
        # Factor 4: Tools are structured outputs
        return [
            {
                "name": "list_git_tags",
                "description": "List available git tags",
                "input_schema": {"type": "object", "properties": {}}
            },
            {
                "name": "deploy_backend",
                "description": "Deploy backend to environment",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "tag": {"type": "string"},
                        "environment": {"type": "string", "enum": ["staging", "production"]}
                    },
                    "required": ["tag", "environment"]
                }
            },
            {
                "name": "request_human_input",
                "description": "Request input from human",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "urgency": {"type": "string", "enum": ["low", "medium", "high"]}
                    },
                    "required": ["question"]
                }
            },
            {
                "name": "done_for_now",
                "description": "Complete the task",
                "input_schema": {
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                    "required": ["message"]
                }
            }
        ]
    
    async def determine_next_step(self):
        # Factor 1: Natural language to tool calls
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=self.system_prompt(),
            messages=self.thread,
            tools=self.tools()
        )
        
        if response.content[0].type == "tool_use":
            return {
                "intent": response.content[0].name,
                **response.content[0].input
            }
        return {"intent": "done_for_now", "message": "Task completed"}
    
    async def run(self, initial_message):
        # Factor 3: Own your context window
        self.thread = [{"role": "user", "content": initial_message}]
        
        # Factor 10: Small, focused agent (max 10 steps)
        for step in range(10):
            next_step = await self.determine_next_step()
            
            # Add to context
            self.thread.append({
                "role": "assistant",
                "content": json.dumps(next_step)
            })
            
            # Factor 8: Own your control flow
            if next_step["intent"] == "done_for_now":
                return {"status": "completed", "message": next_step["message"]}
            
            elif next_step["intent"] == "list_git_tags":
                # Factor 13: Pre-fetch context (just fetch tags)
                tags = await self.list_git_tags()
                self.thread.append({
                    "role": "user",
                    "content": f"Available tags: {', '.join(tags)}"
                })
            
            elif next_step["intent"] == "deploy_backend":
                # Factor 7: Contact humans with tool calls
                if next_step.get("environment") == "production":
                    await self.pause_for_approval(next_step)
                    return {"status": "paused", "thread_id": await self.save_thread()}
                
                try:
                    result = await self.deploy_backend(
                        next_step["tag"],
                        next_step["environment"]
                    )
                    self.thread.append({
                        "role": "user",
                        "content": f"Deployment successful: {json.dumps(result)}"
                    })
                except Exception as e:
                    # Factor 9: Compact errors into context window
                    self.thread.append({
                        "role": "user",
                        "content": f"<error>Deployment failed: {str(e)}</error>"
                    })
            
            elif next_step["intent"] == "request_human_input":
                await self.pause_for_approval(next_step)
                return {"status": "paused", "thread_id": await self.save_thread()}
        
        return {"status": "max_steps_reached"}
    
    async def pause_for_approval(self, step):
        # Factor 6: Launch/Pause/Resume
        thread_id = await self.save_thread()
        await self.notify_human(step, thread_id)
    
    async def save_thread(self):
        # Factor 5: Unify execution and business state
        thread_id = f"thread_{hash(str(self.thread))}"
        # Save to Redis/DB
        return thread_id
    
    async def load_thread(self, thread_id):
        # Load from Redis/DB
        return []
    
    async def resume(self, thread_id, human_response):
        # Factor 6: Resume from webhook
        self.thread = await self.load_thread(thread_id)
        self.thread.append({
            "role": "user",
            "content": f"Human response: {json.dumps(human_response)}"
        })
        return await self.run_continue()
    
    async def run_continue(self):
        # Continue after resume
        return await self.run("")  # Continue from current thread
    
    # Tool implementations
    async def list_git_tags(self):
        return ["v1.0.0", "v1.1.0", "v1.2.0"]
    
    async def deploy_backend(self, tag, environment):
        # Implementation
        return {"status": "success", "tag": tag}
    
    async def notify_human(self, step, thread_id):
        # Send notification
        pass

# Factor 11: Trigger from anywhere
@app.post("/deploy")
async def start_deployment(request: dict):
    """HTTP trigger"""
    agent = DeploymentAgent()
    result = await agent.run(request["message"])
    return result

@app.post("/webhook/approval")
async def approval_webhook(request: dict):
    """Resume after human approval"""
    agent = DeploymentAgent()
    result = await agent.resume(request["thread_id"], request["response"])
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Further Reading

- [Anthropic's Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Claude Tool Use Documentation](https://docs.anthropic.com/claude/docs/tool-use)
- [12-Factor Agents README](../README.md)

 [← Back to README](https://github.com/humanlayer/12-factor-agents/blob/main/README.md)
