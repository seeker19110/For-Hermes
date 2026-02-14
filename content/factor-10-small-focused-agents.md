[← Back to README](https://github.com/humanlayer/12-factor-agents/blob/main/README.md)

### 10. Small, Focused Agents

Rather than building monolithic agents that try to do everything, build small, focused agents that do one thing well. Agents are just one building block in a larger, mostly deterministic system.

![1a0-small-focused-agents](https://github.com/humanlayer/12-factor-agents/blob/main/img/1a0-small-focused-agents.png)

The key insight here is about LLM limitations: the bigger and more complex a task is, the more steps it will take, which means a longer context window. As context grows, LLMs are more likely to get lost or lose focus. By keeping agents focused on specific domains with 3-10, maybe 20 steps max, we keep context windows manageable and LLM performance high.

> #### As context grows, LLMs are more likely to get lost or lose focus

Benefits of small, focused agents:

1. **Manageable Context**: Smaller context windows mean better LLM performance
2. **Clear Responsibilities**: Each agent has a well-defined scope and purpose
3. **Better Reliability**: Less chance of getting lost in complex workflows
4. **Easier Testing**: Simpler to test and validate specific functionality
5. **Improved Debugging**: Easier to identify and fix issues when they occur

### What if LLMs get smarter? 

Do we still need this if LLMs get smart enough to handle 100-step+ workflows?

tl;dr yes. As agents and LLMs improve, they **might** naturally expand to be able to handle longer context windows. This means handling MORE of a larger DAG. This small, focused approach ensures you can get results TODAY, while preparing you to slowly expand agent scope as LLM context windows become more reliable. (If you've refactored large deterministic code bases before, you may be nodding your head right now).

[![gif](https://github.com/humanlayer/12-factor-agents/blob/main/img/1a5-agent-scope-grow.gif)](https://github.com/user-attachments/assets/0cd3f52c-046e-4d5e-bab4-57657157c82f
)

<details>
<summary><a href="https://github.com/humanlayer/12-factor-agents/blob/main/img/1a5-agent-scope-grow.gif">GIF Version</a></summary>
![gif](https://github.com/humanlayer/12-factor-agents/blob/main/img/1a5-agent-scope-grow.gif)
</details>

Being intentional about size/scope of agents, and only growing in ways that allow you to maintain quality, is key here. As the [team that built NotebookLM put it](https://open.substack.com/pub/swyx/p/notebooklm?selection=08e1187c-cfee-4c63-93c9-71216640a5f8&utm_campaign=post-share-selection&utm_medium=web):

> I feel like consistently, the most magical moments out of AI building come about for me when I'm really, really, really just close to the edge of the model capability

Regardless of where that boundary is, if you can find that boundary and get it right consistently, you'll be building magical experiences. There are many moats to be built here, but as usual, they take some engineering rigor.

### Claude Example

Design small, focused Claude agents that excel at specific tasks:

```python
from anthropic import Anthropic

client = Anthropic()

# GOOD: Focused agent with clear scope
class GitTagAgent:
    """Handles only git tag operations - 3-5 steps max"""
    
    def __init__(self):
        self.tools = [
            {
                "name": "list_git_tags",
                "description": "List all git tags",
                "input_schema": {"type": "object", "properties": {}}
            },
            {
                "name": "get_latest_tag",
                "description": "Get the most recent tag",
                "input_schema": {"type": "object", "properties": {}}
            },
            {
                "name": "done_for_now",
                "description": "Complete the task",
                "input_schema": {
                    "type": "object",
                    "properties": {"result": {"type": "string"}}
                }
            }
        ]
        self.max_steps = 5
    
    async def run(self, request):
        """Simple focused workflow"""
        thread = [{"role": "user", "content": request}]
        
        for _ in range(self.max_steps):
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=thread,
                tools=self.tools
            )
            
            if response.content[0].type == "tool_use":
                tool = response.content[0]
                
                if tool.name == "done_for_now":
                    return tool.input.get("result")
                
                # Execute tool
                result = await self.execute_tool(tool.name, tool.input)
                thread.append({
                    "role": "user",
                    "content": f"Result: {result}"
                })
        
        return "Max steps reached"

# GOOD: Composable agents in a DAG
class DeploymentCoordinator:
    """Coordinates multiple focused agents"""
    
    def __init__(self):
        self.tag_agent = GitTagAgent()
        self.test_agent = TestVerificationAgent()
        self.deploy_agent = DeploymentExecutionAgent()
    
    async def deploy_workflow(self, user_request):
        """Chain focused agents together"""
        
        # Step 1: Get tags (3-5 steps)
        tag_info = await self.tag_agent.run("Get latest stable tag")
        
        # Step 2: Run tests (5-10 steps)
        test_result = await self.test_agent.run(f"Verify {tag_info} passes tests")
        
        if test_result != "passed":
            return {"status": "failed", "stage": "tests"}
        
        # Step 3: Deploy (5-10 steps)
        deploy_result = await self.deploy_agent.run(f"Deploy {tag_info}")
        
        return deploy_result

# BAD: Monolithic agent trying to do too much
class MegaAgent:
    """Tries to handle everything - leads to context window issues"""
    
    def __init__(self):
        self.tools = [
            # 50+ tools covering everything
            "list_git_tags", "create_git_tag", "delete_git_tag",
            "run_unit_tests", "run_integration_tests", "run_e2e_tests",
            "deploy_staging", "deploy_production", "rollback",
            "create_ticket", "update_ticket", "close_ticket",
            "send_email", "send_slack", "send_sms",
            # ... 40 more tools
        ]
        self.max_steps = 100  # Too many steps!
    
    async def run(self, request):
        """Massive context window, easy to get lost"""
        # After 20+ steps, Claude likely loses focus
        pass

# BEST PRACTICE: Agent boundaries with Claude
async def claude_agent_best_practices():
    """
    Guidelines for Claude agent scope:
    
    1. Keep context window under 10K tokens when possible
    2. Limit to 3-10 steps per agent
    3. Use 3-7 tools per agent
    4. Clear single responsibility
    5. Chain agents in deterministic DAGs
    """
    
    # Example: Clear boundaries
    agents = {
        "tag_manager": {
            "tools": ["list", "create", "delete"],
            "scope": "Git tag operations only",
            "max_steps": 5
        },
        "test_runner": {
            "tools": ["run_tests", "check_coverage"],
            "scope": "Test execution only",
            "max_steps": 8
        },
        "deployer": {
            "tools": ["deploy", "rollback", "check_status"],
            "scope": "Deployment operations only",
            "max_steps": 10
        }
    }
```

Claude performs best with small agents because:
- Smaller context windows = better attention
- Clearer scope = more accurate tool selection
- Easier to test and debug
- Composable into larger workflows

[← Compact Errors](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-09-compact-errors.md) | [Trigger From Anywhere →](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-11-trigger-from-anywhere.md)
