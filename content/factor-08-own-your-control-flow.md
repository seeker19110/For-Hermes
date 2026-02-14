[← Back to README](https://github.com/humanlayer/12-factor-agents/blob/main/README.md)

### 8. Own your control flow

If you own your control flow, you can do lots of fun things.

![180-control-flow](https://github.com/humanlayer/12-factor-agents/blob/main/img/180-control-flow.png)


Build your own control structures that make sense for your specific use case. Specifically, certain types of tool calls may be reason to break out of the loop and wait for a response from a human or another long-running task like a training pipeline. You may also want to incorporate custom implementation of:

- summarization or caching of tool call results
- LLM-as-judge on structured output
- context window compaction or other [memory management](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md)
- logging, tracing, and metrics
- client-side rate limiting
- durable sleep / pause / "wait for event"


The below example shows three possible control flow patterns:


- request_clarification: model asked for more info, break the loop and wait for a response from a human
- fetch_git_tags: model asked for a list of git tags, fetch the tags, append to context window, and pass straight back to the model
- deploy_backend: model asked to deploy a backend, this is a high-stakes thing, so break the loop and wait for human approval

```python
def handle_next_step(thread: Thread):

  while True:
    next_step = await determine_next_step(thread_to_prompt(thread))
    
    # inlined for clarity - in reality you could put 
    # this in a method, use exceptions for control flow, or whatever you want
    if next_step.intent == 'request_clarification':
      thread.events.append({
        type: 'request_clarification',
          data: nextStep,
        })

      await send_message_to_human(next_step)
      await db.save_thread(thread)
      # async step - break the loop, we'll get a webhook later
      break
    elif next_step.intent == 'fetch_open_issues':
      thread.events.append({
        type: 'fetch_open_issues',
        data: next_step,
      })

      issues = await linear_client.issues()

      thread.events.append({
        type: 'fetch_open_issues_result',
        data: issues,
      })
      # sync step - pass the new context to the LLM to determine the NEXT next step
      continue
    elif next_step.intent == 'create_issue':
      thread.events.append({
        type: 'create_issue',
        data: next_step,
      })

      await request_human_approval(next_step)
      await db.save_thread(thread)
      # async step - break the loop, we'll get a webhook later
      break
```

This pattern allows you to interrupt and resume your agent's flow as needed, creating more natural conversations and workflows.

**Example** - the number one feature request I have for every AI framework out there is we need to be able to interrupt 
a working agent and resume later, ESPECIALLY between the moment of tool **selection** and the moment of tool **invocation**.

Without this level of resumability/granularity, there's no way to review/approve the tool call before it runs, which means
you're forced to either:

1. Pause the task in memory while waiting for the long-running thing to complete (think `while...sleep`) and restart it from the beginning if the process is interrupted
2. Restrict the agent to only low-stakes, low-risk calls like research and summarization
3. Give the agent access to do bigger, more useful things, and just yolo hope it doesn't screw up


You may notice this is closely related to [factor 5 - unify execution state and business state](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-05-unify-execution-state.md) and [factor 6 - launch/pause/resume with simple APIs](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-06-launch-pause-resume.md), but can be implemented independently.

### Claude Example

Build custom control flow with Claude to handle approval workflows, retries, and interrupts:

```python
from anthropic import Anthropic
import asyncio
from tenacity import retry, wait_exponential, stop_after_attempt

client = Anthropic()

class ClaudeAgentWithControlFlow:
    def __init__(self):
        self.thread = []
        self.consecutive_errors = 0
        self.max_steps = 20
    
    async def run_with_custom_control_flow(self, initial_message):
        """Custom control flow with interrupts and custom logic"""
        self.thread = [{"role": "user", "content": initial_message}]
        
        for step in range(self.max_steps):
            next_step = await self._get_next_step()
            
            # Add tool call to thread
            self.thread.append({
                "role": "assistant",
                "content": json.dumps(next_step)
            })
            
            # Custom control flow based on intent
            if next_step["intent"] == "done_for_now":
                return {"status": "completed", "result": next_step}
            
            elif next_step["intent"] == "request_clarification":
                # Async step: break loop and wait for human
                await self._send_clarification_request(next_step)
                return {
                    "status": "paused",
                    "reason": "awaiting_clarification",
                    "thread_id": await self._save_thread()
                }
            
            elif next_step["intent"] == "deploy_production":
                # High-stakes: interrupt before execution for approval
                await self._request_deployment_approval(next_step)
                return {
                    "status": "paused",
                    "reason": "awaiting_deployment_approval",
                    "pending_action": next_step,
                    "thread_id": await self._save_thread()
                }
            
            elif next_step["intent"] == "fetch_git_tags":
                # Sync step: execute and continue immediately
                try:
                    tags = await self._fetch_git_tags_with_retry()
                    self.thread.append({
                        "role": "user",
                        "content": f"Git tags: {json.dumps(tags)}"
                    })
                    self.consecutive_errors = 0  # Reset error counter
                    continue  # Pass immediately back to LLM
                except Exception as e:
                    # Factor 9: Error handling
                    self.consecutive_errors += 1
                    if self.consecutive_errors >= 3:
                        # Escalate to human after 3 failures
                        await self._escalate_to_human(e)
                        return {"status": "paused", "reason": "error_escalation"}
                    
                    # Add error to context and retry
                    self.thread.append({
                        "role": "user",
                        "content": f"<error>Failed to fetch tags: {str(e)}. Retrying...</error>"
                    })
                    continue
            
            elif next_step["intent"] == "summarize_logs":
                # Custom pre-processing before LLM call
                logs = await self._fetch_logs()
                
                # Summarize if logs are too long
                if len(logs) > 10000:
                    logs = await self._summarize_logs_with_claude(logs)
                
                self.thread.append({
                    "role": "user",
                    "content": f"Logs: {logs}"
                })
                continue
            
            elif next_step["intent"] == "rate_limited_api_call":
                # Client-side rate limiting
                await self._rate_limiter.acquire()
                result = await self._make_api_call()
                self.thread.append({
                    "role": "user",
                    "content": f"API result: {json.dumps(result)}"
                })
                continue
            
            elif next_step["intent"] == "wait_for_event":
                # Durable sleep/wait
                await self._schedule_resume(next_step.get("wait_duration", 300))
                return {
                    "status": "paused",
                    "reason": "scheduled_wait",
                    "resume_at": next_step.get("resume_time")
                }
        
        return {"status": "max_steps_reached"}
    
    @retry(wait=wait_exponential(multiplier=1, min=4, max=60))
    async def _fetch_git_tags_with_retry(self):
        """Retry with exponential backoff for Claude API"""
        return await git_client.list_tags()
    
    async def _summarize_logs_with_claude(self, logs):
        """Use Claude to compact large context"""
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"Summarize these deployment logs, focusing on errors and warnings:\n\n{logs[:50000]}"
            }]
        )
        return response.content[0].text
```

This custom control flow enables:
- Interrupt between tool selection and execution for approvals
- Client-side rate limiting for Claude API calls
- Automatic retry with exponential backoff
- Context window compaction for large data
- Error escalation after threshold
- Durable wait/sleep without holding memory

[← Contact Humans With Tools](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-07-contact-humans-with-tools.md) | [Compact Errors →](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-09-compact-errors.md)
