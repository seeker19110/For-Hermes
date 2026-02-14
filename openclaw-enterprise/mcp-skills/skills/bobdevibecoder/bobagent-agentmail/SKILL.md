---
name: agentmail
description: Give your AI agent its own email inbox. Use when the bot needs to create an email account, send emails, receive emails, or manage its inbox. Powered by AgentMail (YC S25).
metadata:
  {
    "clawdbot":
      {
        "emoji": "📧",
        "homepage": "https://agentmail.to",
        "requires": { "bins": ["curl", "jq"] },
      },
  }
---

# AgentMail - Email for AI Agents

Give your OpenClaw agent its own email inbox using AgentMail API.

## Setup

1. Get API key from https://www.agentmail.to (FREE tier: 3 inboxes, 3000 emails/month)
2. Save to config:

```bash
mkdir -p ~/.openclaw/skills/agentmail
cat > ~/.openclaw/skills/agentmail/config.json << 'CONFIG'
{
  "apiKey": "YOUR_AGENTMAIL_API_KEY"
}
CONFIG
```

## Usage

### Create an inbox for the bot
```bash
scripts/agentmail.sh create-inbox milanclawdbot
```
This creates: milanclawdbot@agentmail.to

### Send an email
```bash
scripts/agentmail.sh send "recipient@example.com" "Subject" "Body text"
```

### Check inbox
```bash
scripts/agentmail.sh inbox
```

### Read specific email
```bash
scripts/agentmail.sh read <message_id>
```

## Use Cases

- **Sign up for services** - Bot can create accounts using its own email
- **Apply for API access** - Bankr, Convex, etc.
- **Receive notifications** - Alerts from trading platforms
- **Business communications** - Respond to inquiries autonomously
