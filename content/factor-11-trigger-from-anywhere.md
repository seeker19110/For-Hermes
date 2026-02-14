[← Back to README](https://github.com/humanlayer/12-factor-agents/blob/main/README.md)

### 11. Trigger from anywhere, meet users where they are

If you're waiting for the [humanlayer](https://humanlayer.dev) pitch, you made it. If you're doing [factor 6 - launch/pause/resume with simple APIs](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-06-launch-pause-resume.md) and [factor 7 - contact humans with tool calls](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-07-contact-humans-with-tools.md), you're ready to incorporate this factor.

![1b0-trigger-from-anywhere](https://github.com/humanlayer/12-factor-agents/blob/main/img/1b0-trigger-from-anywhere.png)

Enable users to trigger agents from slack, email, sms, or whatever other channel they want. Enable agents to respond via the same channels.

Benefits:

- **Meet users where they are**: This helps you build AI applications that feel like real humans, or at the very least, digital coworkers
- **Outer Loop Agents**: Enable agents to be triggered by non-humans, e.g. events, crons, outages, whatever else. They may work for 5, 20, 90 minutes, but when they get to a critical point, they can contact a human for help, feedback, or approval
- **High Stakes Tools**: If you're able to quickly loop in a variety of humans, you can give agents access to higher stakes operations like sending external emails, updating production data and more. Maintaining clear standards gets you auditability and confidence in agents that [perform bigger better things](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-10-small-focused-agents.md#what-if-llms-get-smarter)

### Claude Example

Trigger Claude agents from any channel and respond appropriately:

```python
from anthropic import Anthropic
from fastapi import FastAPI
import json

app = FastAPI()
client = Anthropic()

class MultiChannelClaudeAgent:
    """Agent that works across Slack, email, SMS, and webhooks"""
    
    async def run(self, message, channel, user_id):
        """Handle request from any channel"""
        
        # Build context with channel-specific metadata
        context = self._build_context(message, channel, user_id)
        
        thread = [{"role": "user", "content": context}]
        
        # Get response from Claude
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=thread,
            tools=self.tools
        )
        
        # Format response for the channel
        return self._format_for_channel(response, channel)
    
    def _build_context(self, message, channel, user_id):
        """Add channel context for Claude"""
        return f"""<request>
  <message>{message}</message>
  <channel>{channel}</channel>
  <user>{user_id}</user>
  <timestamp>{datetime.now().isoformat()}</timestamp>
</request>"""
    
    def _format_for_channel(self, response, channel):
        """Format Claude's response for specific channel"""
        content = response.content[0].text if response.content else ""
        
        if channel == "slack":
            return {
                "text": content,
                "blocks": [
                    {"type": "section", "text": {"type": "mrkdwn", "text": content}}
                ]
            }
        elif channel == "email":
            return {
                "subject": "Agent Response",
                "body": content,
                "html": f"<html><body>{content}</body></html>"
            }
        elif channel == "sms":
            # Truncate for SMS
            return content[:160] if len(content) > 160 else content
        else:
            return {"message": content}

# Slack trigger
@slack_events.on("app_mention")
async def slack_handler(event):
    agent = MultiChannelClaudeAgent()
    result = await agent.run(
        event["text"],
        channel="slack",
        user_id=event["user"]
    )
    await slack.post_message(event["channel"], result)

# Email trigger
@email_webhook.handler()
async def email_handler(email):
    agent = MultiChannelClaudeAgent()
    result = await agent.run(
        email.body,
        channel="email",
        user_id=email.from_addr
    )
    await send_email(email.from_addr, result)

# SMS trigger
@sms_webhook.handler()
async def sms_handler(sms):
    agent = MultiChannelClaudeAgent()
    result = await agent.run(
        sms.body,
        channel="sms",
        user_id=sms.from_number
    )
    await send_sms(sms.from_number, result)

# Cron/scheduled trigger
@scheduler.cron("0 9 * * *")
async def daily_standup():
    """Outer loop agent - triggered by time, not user"""
    agent = MultiChannelClaudeAgent()
    
    # Agent works autonomously, contacts humans when needed
    result = await agent.run(
        "Generate daily deployment status report",
        channel="slack",
        user_id="#deployments"
    )
    await slack.post_message("#deployments", result)

# Webhook trigger (GitHub, Linear, etc.)
@app.post("/webhook/github")
async def github_webhook(request: dict):
    """Trigger from external events"""
    if request.get("action") == "released":
        agent = MultiChannelClaudeAgent()
        result = await agent.run(
            f"New release {request['release']['tag_name']} published",
            channel="slack",
            user_id="#deployments"
        )
        return result

# HTTP API trigger
@app.post("/agent/chat")
async def chat_endpoint(request: dict):
    """Direct HTTP API"""
    agent = MultiChannelClaudeAgent()
    result = await agent.run(
        request["message"],
        channel="api",
        user_id=request.get("user_id", "anonymous")
    )
    return result

# Claude-specific: Vision trigger
@app.post("/agent/analyze-image")
async def analyze_image_endpoint(request: dict):
    """Trigger with image input using Claude's vision"""
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": request["question"]},
                {"type": "image", "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": request["image_base64"]
                }}
            ]
        }]
    )
    return {"analysis": response.content[0].text}
```

Multi-channel benefits with Claude:
- Consistent agent logic across all channels
- Claude formats responses appropriately for each medium
- Vision capabilities for image-based triggers
- Outer loop agents work autonomously
- Easy webhook integration for event-driven workflows

[← Small Focused Agents](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-10-small-focused-agents.md) | [Stateless Reducer →](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-12-stateless-reducer.md)