#!/bin/bash

CONFIG_FILE="$HOME/.openclaw/skills/agentmail/config.json"
API_BASE="https://api.agentmail.to/v1"

if [ ! -f "$CONFIG_FILE" ]; then
  echo '{"error": "Config not found. Create ~/.openclaw/skills/agentmail/config.json with your API key"}'
  exit 1
fi

API_KEY=$(jq -r '.apiKey' "$CONFIG_FILE")

if [ -z "$API_KEY" ] || [ "$API_KEY" == "null" ]; then
  echo '{"error": "API key not configured"}'
  exit 1
fi

case "$1" in
  create-inbox)
    USERNAME="$2"
    if [ -z "$USERNAME" ]; then
      echo '{"error": "Usage: agentmail.sh create-inbox <username>"}'
      exit 1
    fi
    curl -s -X POST "$API_BASE/inboxes"       -H "Authorization: Bearer $API_KEY"       -H "Content-Type: application/json"       -d "{\"username\": \"$USERNAME\", \"domain\": \"agentmail.to\"}"
    ;;

  send)
    TO="$2"
    SUBJECT="$3"
    BODY="$4"
    if [ -z "$TO" ] || [ -z "$SUBJECT" ]; then
      echo '{"error": "Usage: agentmail.sh send <to> <subject> <body>"}'
      exit 1
    fi
    curl -s -X POST "$API_BASE/messages"       -H "Authorization: Bearer $API_KEY"       -H "Content-Type: application/json"       -d "{\"to\": \"$TO\", \"subject\": \"$SUBJECT\", \"body\": \"$BODY\"}"
    ;;

  inbox)
    curl -s "$API_BASE/inboxes"       -H "Authorization: Bearer $API_KEY"
    ;;

  messages)
    INBOX_ID="$2"
    curl -s "$API_BASE/inboxes/$INBOX_ID/messages"       -H "Authorization: Bearer $API_KEY"
    ;;

  read)
    MSG_ID="$2"
    curl -s "$API_BASE/messages/$MSG_ID"       -H "Authorization: Bearer $API_KEY"
    ;;

  *)
    echo '{"usage": {
      "create-inbox": "agentmail.sh create-inbox <username>",
      "send": "agentmail.sh send <to> <subject> <body>",
      "inbox": "agentmail.sh inbox",
      "messages": "agentmail.sh messages <inbox_id>",
      "read": "agentmail.sh read <message_id>"
    }}'
    ;;
esac
