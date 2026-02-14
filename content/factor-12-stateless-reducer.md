[← Back to README](https://github.com/humanlayer/12-factor-agents/blob/main/README.md)

### 12. Make your agent a stateless reducer

Okay so we're over 1000 lines of markdown at this point. This one is mostly just for fun.

![1c0-stateless-reducer](https://github.com/humanlayer/12-factor-agents/blob/main/img/1c0-stateless-reducer.png)


![1c5-agent-foldl](https://github.com/humanlayer/12-factor-agents/blob/main/img/1c5-agent-foldl.png)

### Claude Example

Model Claude agents as pure stateless reducers:

```python
from anthropic import Anthropic
from typing import List, Dict, Any
import json

client = Anthropic()

def claude_reducer(
    thread: List[Dict[str, Any]], 
    event: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Pure function: (state, event) -> new_state
    No side effects, deterministic, testable
    """
    # Create new thread (immutable state)
    new_thread = thread.copy()
    new_thread.append(event)
    
    # Get Claude's response (deterministic given the same inputs)
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=new_thread,
        tools=tools
    )
    
    # Add Claude's response to thread
    if response.content[0].type == "text":
        new_thread.append({
            "role": "assistant",
            "content": response.content[0].text
        })
    elif response.content[0].type == "tool_use":
        new_thread.append({
            "role": "assistant",
            "content": json.dumps({
                "tool": response.content[0].name,
                "arguments": response.content[0].input
            })
        })
    
    return new_thread

# Example usage - pure function composition
def run_agent(initial_event: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Run agent by folding over events"""
    thread = []
    
    # Fold: reduce events into final state
    for event in generate_events(initial_event):
        thread = claude_reducer(thread, event)
    
    return thread

# Testing is easy with pure functions
def test_claude_reducer():
    """Unit test the reducer"""
    initial_thread = [
        {"role": "user", "content": "Hello"}
    ]
    
    event = {"role": "user", "content": "Deploy v1.2.3"}
    
    new_thread = claude_reducer(initial_thread, event)
    
    # Assert thread grew by 2 (event + Claude's response)
    assert len(new_thread) == len(initial_thread) + 2
    assert new_thread[-1]["role"] == "assistant"

# Forking is just copying the thread
def fork_thread(thread: List[Dict[str, Any]], at_index: int) -> List[Dict[str, Any]]:
    """Create branch at specific point"""
    return thread[:at_index].copy()

# Time travel debugging
def replay_thread(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Replay all events from start"""
    thread = []
    for event in events:
        thread = claude_reducer(thread, event)
    return thread

# Functional composition example
from functools import reduce

agent_workflow = [
    {"role": "user", "content": "List git tags"},
    {"role": "tool_result", "content": "[v1.2.3, v1.2.2]"},
    {"role": "user", "content": "Deploy v1.2.3 to production"},
    {"role": "tool_result", "content": "Awaiting approval"},
    {"role": "user", "content": "Approved"},
    {"role": "tool_result", "content": "Deployment successful"}
]

# Reduce events to final state
final_thread = reduce(claude_reducer, agent_workflow, [])
```

The stateless reducer pattern with Claude:
- Pure functions enable easy testing and debugging
- Immutable state prevents bugs
- Forking and time travel are trivial
- Composable with functional programming patterns
- Predictable and reproducible

[← Trigger From Anywhere](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-11-trigger-from-anywhere.md) | [Appendix - Pre-Fetch Context →](https://github.com/humanlayer/12-factor-agents/blob/main/content/appendix-13-pre-fetch.md)
