#!/usr/bin/env python3
"""
Send WhatsApp Message Helper
Simple wrapper for the most common task — sending a text message via the REST API.
"""
# Required Scopes: messages:send
# Chat History: Not required (send-only)
import argparse
import os
import sys
import json
import requests

BASE_URL = os.environ.get("MOLTFLOW_API_URL", "https://apiv2.waiflow.app")
API_KEY = os.environ.get("MOLTFLOW_API_KEY")


def main():
    parser = argparse.ArgumentParser(description="Send a WhatsApp message via MoltFlow API.")
    parser.add_argument("--session", required=True, help="Session UUID")
    parser.add_argument("--to", required=True, help="Target chat ID (e.g. 1234567890@c.us)")
    parser.add_argument("--text", required=True, help="Message text content")
    parser.add_argument("--key", default=API_KEY, help="API key (default: MOLTFLOW_API_KEY env)")

    args = parser.parse_args()

    if not args.key:
        print("Error: provide --key or set MOLTFLOW_API_KEY env var")
        sys.exit(1)

    response = requests.post(
        f"{BASE_URL}/api/v2/messages/send",
        headers={"X-API-Key": args.key, "Content-Type": "application/json"},
        json={
            "session_id": args.session,
            "chat_id": args.to,
            "message": args.text,
        },
    )

    result = response.json()
    print(json.dumps(result, indent=2))

    if not response.ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
