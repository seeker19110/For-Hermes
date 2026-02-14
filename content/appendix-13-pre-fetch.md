### Factor 13 - pre-fetch all the context you might need

If there's a high chance that your model will call tool X, don't waste token round trips telling the model to fetch it, that is, instead of a pseudo-prompt like:

```jinja
When looking at deployments, you will likely want to fetch the list of published git tags,
so you can use it to deploy to prod.

Here's what happened so far:

{{ thread.events }}

What's the next step?

Answer in JSON format with one of the following intents:

{
  intent: 'deploy_backend_to_prod',
  tag: string
} OR {
  intent: 'list_git_tags'
} OR {
  intent: 'done_for_now',
  message: string
}
```

and your code looks like

```python
thread = {"events": [initial_message]}
next_step = await determine_next_step(thread)

while True:
  switch next_step.intent:
    case 'list_git_tags':
      tags = await fetch_git_tags()
      thread["events"].append({
        type: 'list_git_tags',
        data: tags,
      })
    case 'deploy_backend_to_prod':
      deploy_result = await deploy_backend_to_prod(next_step.data.tag)
      thread["events"].append({
        "type": 'deploy_backend_to_prod',
        "data": deploy_result,
      })
    case 'done_for_now':
      await notify_human(next_step.message)
      break
    # ...
```

You might as well just fetch the tags and include them in the context window, like:

```diff
- When looking at deployments, you will likely want to fetch the list of published git tags,
- so you can use it to deploy to prod.

+ The current git tags are:

+ {{ git_tags }}


Here's what happened so far:

{{ thread.events }}

What's the next step?

Answer in JSON format with one of the following intents:

{
  intent: 'deploy_backend_to_prod',
  tag: string
- } OR {
-   intent: 'list_git_tags'
} OR {
  intent: 'done_for_now',
  message: string
}

```

and your code looks like

```diff
thread = {"events": [initial_message]}
+ git_tags = await fetch_git_tags()

- next_step = await determine_next_step(thread)
+ next_step = await determine_next_step(thread, git_tags)

while True:
  switch next_step.intent:
-    case 'list_git_tags':
-      tags = await fetch_git_tags()
-      thread["events"].append({
-        type: 'list_git_tags',
-        data: tags,
-      })
    case 'deploy_backend_to_prod':
      deploy_result = await deploy_backend_to_prod(next_step.data.tag)
      thread["events"].append({
        "type": 'deploy_backend_to_prod',
        "data": deploy_result,
      })
    case 'done_for_now':
      await notify_human(next_step.message)
      break
    # ...
```

or even just include the tags in the thread and remove the specific parameter from your prompt template:

```diff
thread = {"events": [initial_message]}
+ # add the request
+ thread["events"].append({
+  "type": 'list_git_tags',
+ })

git_tags = await fetch_git_tags()

+ # add the result
+ thread["events"].append({
+  "type": 'list_git_tags_result',
+  "data": git_tags,
+ })

- next_step = await determine_next_step(thread, git_tags)
+ next_step = await determine_next_step(thread)

while True:
  switch next_step.intent:
    case 'deploy_backend_to_prod':
      deploy_result = await deploy_backend_to_prod(next_step.data.tag)
      thread["events"].append(deploy_result)
    case 'done_for_now':
      await notify_human(next_step.message)
      break
    # ...
```

Overall:

> #### If you already know what tools you'll want the model to call, just call them DETERMINISTICALLY and let the model do the hard part of figuring out how to use their outputs

Again, AI engineering is all about [Context Engineering](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md).

### Claude Example

Leverage Claude's large context window to pre-fetch data and reduce API round trips:

```python
from anthropic import Anthropic

client = Anthropic()

# WITHOUT pre-fetch (wastes token round trips)
def deploy_without_prefetch():
    thread = [{"role": "user", "content": "Deploy to production"}]
    
    # Turn 1: Claude asks for git tags
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        messages=thread,
        tools=[list_git_tags_tool, deploy_tool]
    )
    
    if response.content[0].name == "list_git_tags":
        tags = fetch_git_tags()  # API call
        thread.append({"role": "tool", "content": str(tags)})
        
        # Turn 2: Claude asks for deployment status
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=thread,
            tools=[check_status_tool, deploy_tool]
        )
        
        if response.content[0].name == "check_status":
            status = check_deployment_status()  # Another API call
            # ... more turns

# WITH pre-fetch (single turn, more efficient)
def deploy_with_prefetch():
    # Pre-fetch all likely-needed data
    git_tags = fetch_git_tags()
    current_status = check_deployment_status()
    recent_commits = fetch_recent_commits(10)
    pending_migrations = check_pending_migrations()
    
    # Include everything in initial context
    context = f"""<deployment_context>
  <git_tags>
    {chr(10).join(f'<tag>{tag}</tag>' for tag in git_tags)}
  </git_tags>
  <current_status>
    <version>{current_status.version}</version>
    <health>{current_status.health}</health>
  </current_status>
  <recent_commits>
    {chr(10).join(f'<commit>{c}</commit>' for c in recent_commits)}
  </recent_commits>
  <pending_migrations count="{len(pending_migrations)}">
    {chr(10).join(f'<migration>{m}</migration>' for m in pending_migrations)}
  </pending_migrations>
</deployment_context>

Deploy to production"""
    
    thread = [{"role": "user", "content": context}]
    
    # Single turn - Claude has all context needed
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        messages=thread,
        tools=[deploy_tool]  # Only need deployment tool
    )
    
    return response.content[0]

# Pre-fetch strategies for Claude

class PrefetchStrategy:
    """Determine what data to pre-fetch based on request type"""
    
    def __init__(self):
        self.prefetch_rules = {
            "deploy": ["git_tags", "deployment_status", "recent_commits"],
            "debug": ["recent_logs", "error_metrics", "deployment_history"],
            "analyze": ["user_metrics", "performance_data", "recent_changes"]
        }
    
    async def build_context(self, request_type, user_message):
        """Build rich context with pre-fetched data"""
        data_to_fetch = self.prefetch_rules.get(request_type, [])
        
        # Fetch all data in parallel
        fetched_data = await asyncio.gather(*[
            self.fetch_data(key) for key in data_to_fetch
        ])
        
        # Build XML context for Claude
        context_parts = [f"<request>{user_message}</request>"]
        
        for key, data in zip(data_to_fetch, fetched_data):
            context_parts.append(f"<{key}>{self.format_data(data)}</{key}>")
        
        return "\n".join(context_parts)
    
    def format_data(self, data):
        """Format data for Claude's understanding"""
        if isinstance(data, list):
            return "\n".join(f"<item>{item}</item>" for item in data)
        elif isinstance(data, dict):
            return "\n".join(f"<key name='{k}'>{v}</key>" for k, v in data.items())
        return str(data)

# Claude's 200K context window enables aggressive pre-fetching
async def aggressive_prefetch_example():
    """Use Claude's large context window to include extensive documentation"""
    
    # Pre-fetch extensive context
    context = {
        "api_documentation": fetch_api_docs(),  # 50K tokens
        "error_logs": fetch_last_24h_logs(),    # 30K tokens  
        "user_guide": fetch_user_guide(),       # 20K tokens
        "deployment_history": fetch_history(),  # 10K tokens
        "current_request": "Debug the authentication error"
    }
    
    # Claude can handle all 110K tokens in one request
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": f"""<context>
{chr(10).join(f'<{k}>{v}</{k}>' for k, v in context.items())}
</context>

Based on all this context, what is causing the authentication error?"""
        }]
    )
    
    return response.content[0].text
```

Pre-fetching with Claude:
- Reduces latency by avoiding multiple API round trips
- Leverages Claude's 200K context window for rich context
- Enables single-turn complex reasoning
- Better token efficiency than multiple small requests
- Works great with XML-structured context

 [← Stateless Reducer](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-12-stateless-reducer.md) | [Further Reading →](https://github.com/humanlayer/12-factor-agents/blob/main/README.md#related-resources)
