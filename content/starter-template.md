# Starter Template: Build a 12-Factor Agent

This page is a practical boilerplate for starting a new 12-factor-style agent project.

If you want a guided walkthrough, start with:
- [Python workshop walkthrough](https://github.com/humanlayer/12-factor-agents/blob/main/workshops/2025-07-16/walkthrough_python_enhanced.yaml)

## Suggested project layout

```text
my-agent/
  README.md
  pyproject.toml or package.json
  src/
    agent/
      prompts/
      tools/
      workflow/
      reducers/
      context/
      state/
  tests/
```

## Minimal implementation checklist

1. Define a small set of tool schemas (Factor 4).
2. Put prompts in source control with tests/examples (Factor 2).
3. Build context in code, not hidden framework magic (Factor 3).
4. Keep control flow explicit in deterministic code (Factor 8).
5. Persist execution + business state in one timeline (Factor 5).
6. Treat the agent loop as a reducer over prior events (Factor 12).

## Copy/paste starter loop (framework-agnostic pseudocode)

```python
events = load_events(thread_id)

while True:
    prompt = build_prompt(events)
    tool_or_reply = llm_call(prompt, tools=tool_schemas)

    if tool_or_reply.type == "final_reply":
        events.append({"type": "assistant_reply", "text": tool_or_reply.text})
        break

    result = run_tool(tool_or_reply.name, tool_or_reply.args)
    events.append({
        "type": "tool_result",
        "tool": tool_or_reply.name,
        "args": tool_or_reply.args,
        "result": result
    })

save_events(thread_id, events)
```

## "Done enough" criteria for v0

- You can replay a thread from stored events and get the same next action.
- All tool calls are schema-validated before execution.
- The agent can be paused and resumed without hidden in-memory state.
- Failures are compacted into context and retried with bounded attempts.
