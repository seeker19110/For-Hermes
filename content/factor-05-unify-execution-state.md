[← Back to README](https://github.com/humanlayer/12-factor-agents/blob/main/README.md)

### 5. Unify execution state and business state

Even outside the AI world, many infrastructure systems try to separate "execution state" from "business state". For AI apps, this might involve complex abstractions to track things like current step, next step, waiting status, retry counts, etc. This separation creates complexity that may be worthwhile, but may be overkill for your use case. 

As always, it's up to you to decide what's right for your application. But don't think you *have* to manage them separately.

More clearly:

- **Execution state**: current step, next step, waiting status, retry counts, etc. 
- **Business state**: What's happened in the agent workflow so far (e.g. list of OpenAI messages, list of tool calls and results, etc.)

If possible, SIMPLIFY - unify these as much as possible. 

[![155-unify-state](https://github.com/humanlayer/12-factor-agents/blob/main/img/155-unify-state-animation.gif)](https://github.com/user-attachments/assets/e5a851db-f58f-43d8-8b0c-1926c99fc68d)


<details>
<summary><a href="https://github.com/humanlayer/12-factor-agents/blob/main/img/155-unify-state-animation.gif">GIF Version</a></summary>

![155-unify-state](https://github.com/humanlayer/12-factor-agents/blob/main/img/155-unify-state-animation.gif)

</details>

In reality, you can engineer your application so that you can infer all execution state from the context window. In many cases, execution state (current step, waiting status, etc.) is just metadata about what has happened so far.

You may have things that can't go in the context window, like session ids, password contexts, etc, but your goal should be to minimize those things. By embracing [factor 3](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md) you can control what actually goes into the LLM 

This approach has several benefits:

1. **Simplicity**: One source of truth for all state
2. **Serialization**: The thread is trivially serializable/deserializable
3. **Debugging**: The entire history is visible in one place
4. **Flexibility**: Easy to add new state by just adding new event types
5. **Recovery**: Can resume from any point by just loading the thread
6. **Forking**: Can fork the thread at any point by copying some subset of the thread into a new context / state ID
7. **Human Interfaces and Observability**: Trivial to convert a thread into a human-readable markdown or a rich Web app UI

### Claude Example

With Claude, the conversation thread serves as the single source of truth:

```python
from anthropic import Anthropic
import json
import redis

client = Anthropic()

class ClaudeAgent:
    def __init__(self):
        self.thread = []
        self.redis = redis.Redis()
    
    async def run(self, initial_message):
        """Business state IS the execution state"""
        self.thread = [{"role": "user", "content": initial_message}]
        
        while True:
            # Infer execution state from thread
            state = self.infer_state_from_thread()
            
            if state["waiting_for"] == "human_approval":
                thread_id = await self.save_thread()
                return {"status": "paused", "thread_id": thread_id}
            
            # Continue execution...
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                messages=self.thread,
                tools=self.tools
            )
            
            # Update thread (business state)
            if response.content[0].type == "tool_use":
                self.thread.append({
                    "role": "assistant",
                    "content": json.dumps({
                        "tool_call": response.content[0].name,
                        "arguments": response.content[0].input
                    })
                })
    
    def infer_state_from_thread(self):
        """Derive execution state from business state (thread)"""
        if not self.thread:
            return {"waiting_for": "initial_request"}
        
        last_message = self.thread[-1]
        
        # Check for pending human approval
        if "tool_call" in last_message.get("content", ""):
            tool_data = json.loads(last_message["content"])
            if tool_data.get("tool_call") == "request_human_input":
                return {"waiting_for": "human_approval"}
        
        return {"waiting_for": "llm_response"}
    
    async def save_thread(self):
        """Serialize thread for resumption"""
        thread_id = f"thread_{hash(str(self.thread))}"
        self.redis.set(thread_id, json.dumps(self.thread))
        return thread_id
    
    async def load_and_resume(self, thread_id):
        """Resume from saved state"""
        thread_data = self.redis.get(thread_id)
        self.thread = json.loads(thread_data)
        return await self.run_continue()
    
    async def fork_thread(self, thread_id, event_index):
        """Fork thread at specific point"""
        thread_data = self.redis.get(thread_id)
        original_thread = json.loads(thread_data)
        
        # Create new thread from subset
        new_thread = original_thread[:event_index]
        new_thread_id = f"fork_{hash(str(new_thread))}"
        self.redis.set(new_thread_id, json.dumps(new_thread))
        
        return new_thread_id
```

With Claude:
- The message thread contains all business logic and execution state
- No separate "workflow state" to manage
- Easy serialization via JSON
- Simple forking by copying message subsets
- Full observability by inspecting the thread

[← Tools Are Structured Outputs](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-04-tools-are-structured-outputs.md) | [Launch/Pause/Resume →](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-06-launch-pause-resume.md)
