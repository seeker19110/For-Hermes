#!/usr/bin/env python3
"""
MoltFlow Group Monitor - WhatsApp Group Monitoring & Lead Detection
"""
# Required Scopes: groups:manage
# Chat History: Not required
import os
import requests

API_KEY = os.environ.get("MOLTFLOW_API_KEY")
BASE_URL = os.environ.get("MOLTFLOW_API_URL", "https://apiv2.waiflow.app")

if not API_KEY:
    print("Error: MOLTFLOW_API_KEY environment variable not set")
    exit(1)

headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}


def list_monitored_groups():
    """List all monitored WhatsApp groups."""
    r = requests.get(f"{BASE_URL}/api/v2/groups", headers=headers)
    r.raise_for_status()
    return r.json()


def list_available_groups(session_id: str):
    """List available WhatsApp groups for a session (not yet monitored)."""
    r = requests.get(
        f"{BASE_URL}/api/v2/groups/available/{session_id}",
        headers=headers,
    )
    r.raise_for_status()
    return r.json()


def add_monitored_group(
    session_id: str,
    wa_group_id: str,
    name: str = None,
    monitor_mode: str = "first_message",
    monitor_keywords: list = None,
    monitor_prompt: str = None,
    auto_respond: bool = False,
    response_template: str = None,
    auto_label_leads: bool = False,
    lead_label_id: str = None,
    webhook_url: str = None,
):
    """Add a WhatsApp group to monitoring.

    monitor_mode: first_message, keyword, ai_prompt
    monitor_keywords: list of keyword strings (for keyword mode)
    monitor_prompt: AI prompt (for ai_prompt mode)
    auto_respond: send automatic response to detected leads
    auto_label_leads: auto-apply a label to detected leads
    """
    data = {
        "session_id": session_id,
        "wa_group_id": wa_group_id,
        "monitor_mode": monitor_mode,
        "auto_respond": auto_respond,
        "auto_label_leads": auto_label_leads,
    }
    if name:
        data["name"] = name
    if monitor_keywords:
        data["monitor_keywords"] = monitor_keywords
    if monitor_prompt:
        data["monitor_prompt"] = monitor_prompt
    if response_template:
        data["response_template"] = response_template
    if lead_label_id:
        data["lead_label_id"] = lead_label_id
    if webhook_url:
        data["webhook_url"] = webhook_url
    r = requests.post(f"{BASE_URL}/api/v2/groups", headers=headers, json=data)
    r.raise_for_status()
    return r.json()


def get_monitored_group(group_id: str):
    """Get monitored group details."""
    r = requests.get(f"{BASE_URL}/api/v2/groups/{group_id}", headers=headers)
    r.raise_for_status()
    return r.json()


def update_monitored_group(group_id: str, **kwargs):
    """Update monitoring settings.

    Accepts: name, monitor_mode, monitor_keywords, monitor_prompt,
             auto_respond, response_template, auto_label_leads,
             lead_label_id, webhook_url, is_active
    """
    r = requests.patch(
        f"{BASE_URL}/api/v2/groups/{group_id}",
        headers=headers,
        json={k: v for k, v in kwargs.items() if v is not None},
    )
    r.raise_for_status()
    return r.json()


def delete_monitored_group(group_id: str):
    """Stop monitoring a group and remove it."""
    r = requests.delete(f"{BASE_URL}/api/v2/groups/{group_id}", headers=headers)
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    print("MoltFlow Group Monitor")
    print("=" * 40)

    data = list_monitored_groups()
    groups = data.get("items", [])
    print(f"\nMonitored Groups: {data.get('total', len(groups))}")

    for g in groups:
        status = "active" if g.get("is_active") else "paused"
        mode = g.get("monitor_mode", "unknown")
        leads = g.get("leads_detected", 0)
        msgs = g.get("messages_processed", 0)
        print(f"  - {g['name']} [{status}] mode={mode} leads={leads} msgs={msgs}")
