[← Back to README](https://github.com/humanlayer/12-factor-agents/blob/main/README.md)

### 9. Compact Errors into Context Window

This one is a little short but is worth mentioning. One of these benefits of agents is "self-healing" - for short tasks, an LLM might call a tool that fails. Good LLMs have a fairly good chance of reading an error message or stack trace and figuring out what to change in a subsequent tool call.


Most frameworks implement this, but you can do JUST THIS without doing any of the other 11 factors. Here's an example: 


```python
thread = {"events": [initial_message]}

while True:
  next_step = await determine_next_step(thread_to_prompt(thread))
  thread["events"].append({
    "type": next_step.intent,
    "data": next_step,
  })
  try:
    result = await handle_next_step(thread, next_step) # our switch statement
  except Exception as e:
    # if we get an error, we can add it to the context window and try again
    thread["events"].append({
      "type": 'error',
      "data": format_error(e),
    })
    # loop, or do whatever else here to try to recover
```

You may want to implement an errorCounter for a specific tool call, to limit to ~3 attempts of a single tool, or whatever other logic makes sense for your use case. 

```python
consecutive_errors = 0

while True:

  # ... existing code ...

  try:
    result = await handle_next_step(thread, next_step)
    thread["events"].append({
      "type": next_step.intent + '_result',
      data: result,
    })
    # success! reset the error counter
    consecutive_errors = 0
  except Exception as e:
    consecutive_errors += 1
    if consecutive_errors < 3:
      # do the loop and try again
      thread["events"].append({
        "type": 'error',
        "data": format_error(e),
      })
    else:
      # break the loop, reset parts of the context window, escalate to a human, or whatever else you want to do
      break
  }
}
```
Hitting some consecutive-error-threshold might be a great place to [escalate to a human](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-07-contact-humans-with-tools.md), whether by model decision or via deterministic takeover of the control flow.

[![195-factor-09-errors](https://github.com/humanlayer/12-factor-agents/blob/main/img/195-factor-09-errors.gif)](https://github.com/user-attachments/assets/cd7ed814-8309-4baf-81a5-9502f91d4043)


<details>
<summary>[GIF Version](https://github.com/humanlayer/12-factor-agents/blob/main/img/195-factor-09-errors.gif)</summary>

![195-factor-09-errors](https://github.com/humanlayer/12-factor-agents/blob/main/img/195-factor-09-errors.gif)

</details>

Benefits:

1. **Self-Healing**: The LLM can read the error message and figure out what to change in a subsequent tool call
2. **Durable**: The agent can continue to run even if one tool call fails

I'm sure you will find that if you do this TOO much, your agent will start to spin out and might repeat the same error over and over again. 

That's where [factor 8 - own your control flow](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-08-own-your-control-flow.md) and [factor 3 - own your context building](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md) come in - you don't need to just put the raw error back on, you can completely restructure how it's represented, remove previous events from the context window, or whatever deterministic thing you find works to get an agent back on track. 

But the number one way to prevent error spin-outs is to embrace [factor 10 - small, focused agents](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-10-small-focused-agents.md).

### Claude Example

Leverage Claude's reasoning capabilities for self-healing error recovery:

```python
from anthropic import Anthropic
import json
import traceback

client = Anthropic()

class SelfHealingClaudeAgent:
    def __init__(self):
        self.thread = []
        self.consecutive_errors = 0
        self.max_retries = 3
    
    async def execute_with_error_recovery(self, tool_call):
        """Execute tool with Claude-powered error recovery"""
        try:
            result = await self._execute_tool(tool_call)
            self.consecutive_errors = 0
            return result
            
        except Exception as e:
            self.consecutive_errors += 1
            
            # Format error for Claude's understanding
            error_context = self._format_error_for_claude(e, tool_call)
            
            # Add error to thread
            self.thread.append({
                "role": "user",
                "content": error_context
            })
            
            if self.consecutive_errors >= self.max_retries:
                # Escalate to human after max retries
                return await self._escalate_error_to_human(e, tool_call)
            
            # Let Claude suggest recovery action
            recovery_step = await self._get_recovery_suggestion()
            
            # Execute recovery if Claude suggests a fix
            if recovery_step.get("intent") == "retry_with_modification":
                modified_call = recovery_step.get("modified_tool_call", tool_call)
                return await self.execute_with_error_recovery(modified_call)
            
            return recovery_step
    
    def _format_error_for_claude(self, error, tool_call):
        """Format errors in a way Claude can analyze and suggest fixes"""
        tb = traceback.format_exc()
        
        return f"""<tool_execution_error>
  <tool>{tool_call.get('intent', 'unknown')}</tool>
  <arguments>{json.dumps(tool_call.get('arguments', {}))}</arguments>
  <error_type>{type(error).__name__}</error_type>
  <error_message>{str(error)}</error_message>
  <stack_trace>
{tb}
  </stack_trace>
  <attempt_count>{self.consecutive_errors}</attempt_count>
  <max_retries>{self.max_retries}</max_retries>
</tool_execution_error>

The tool call failed. What should I do next? Options:
1. Retry with the same parameters
2. Retry with modified parameters (specify changes)
3. Try a different approach
4. Escalate to human for help"""
    
    async def _get_recovery_suggestion(self):
        """Ask Claude how to recover from the error"""
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=self.thread,
            tools=[
                {
                    "name": "retry_same",
                    "description": "Retry the same tool call",
                    "input_schema": {"type": "object", "properties": {}}
                },
                {
                    "name": "retry_with_modification",
                    "description": "Retry with modified parameters",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "modified_tool_call": {"type": "object"},
                            "reasoning": {"type": "string"}
                        }
                    }
                },
                {
                    "name": "try_different_approach",
                    "description": "Use an alternative tool or method",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "alternative_intent": {"type": "string"},
                            "reasoning": {"type": "string"}
                        }
                    }
                },
                {
                    "name": "escalate_to_human",
                    "description": "Get human help with this error",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "error_summary": {"type": "string"}
                        }
                    }
                }
            ]
        )
        
        if response.content[0].type == "tool_use":
            return {
                "intent": response.content[0].name,
                **response.content[0].input
            }
        return {"intent": "escalate_to_human"}
    
    async def _escalate_error_to_human(self, error, tool_call):
        """Escalate persistent errors to human with Claude-generated summary"""
        # Use Claude to generate a helpful error summary
        summary_prompt = f"""Summarize this error for a human developer:

Error: {type(error).__name__}: {str(error)}
Tool: {tool_call.get('intent')}
Attempts: {self.consecutive_errors}

Provide:
1. What went wrong in plain English
2. What was being attempted
3. What the human should check"""
        
        summary_response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[{"role": "user", "content": summary_prompt}]
        )
        
        error_summary = summary_response.content[0].text
        
        # Add to thread and pause
        self.thread.append({
            "role": "user",
            "content": f"<escalation>Error escalated to human: {error_summary}</escalation>"
        })
        
        await self._notify_human_of_error(error_summary)
        return {"status": "escalated", "summary": error_summary}

# Example usage showing self-healing
async def deploy_with_self_healing():
    agent = SelfHealingClaudeAgent()
    
    thread = [
        {"role": "user", "content": "Deploy v1.2.3 to production"}
    ]
    
    # Try to deploy
    result = await agent.execute_with_error_recovery({
        "intent": "deploy_backend",
        "arguments": {"tag": "v1.2.3", "environment": "production"}
    })
    
    # If deployment fails, Claude might suggest:
    # 1. Retry with "production" instead of "prod"
    # 2. Check if tag exists first
    # 3. Escalate if deployment service is down
```

Claude's error handling advantages:
- Analyzes stack traces and suggests specific fixes
- Can propose parameter modifications for retry
- Generates human-readable error summaries
- Understands error context from XML-formatted errors

[← Own Your Control Flow](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-08-own-your-control-flow.md) | [Small Focused Agents →](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-10-small-focused-agents.md)
