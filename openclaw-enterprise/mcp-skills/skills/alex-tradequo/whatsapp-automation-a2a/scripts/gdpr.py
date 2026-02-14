#!/usr/bin/env python3
"""
MoltFlow GDPR - Contact Erasure & Data Export
"""
# Required Scopes: gdpr:manage
# Chat History: Not required
import os
import json
import requests

API_KEY = os.environ.get("MOLTFLOW_API_KEY")
BASE_URL = os.environ.get("MOLTFLOW_API_URL", "https://apiv2.waiflow.app")

if not API_KEY:
    print("Error: MOLTFLOW_API_KEY environment variable not set")
    exit(1)

headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}


def erase_contact(phone: str, reason: str = "gdpr_request"):
    """Erase all data for a contact phone number (GDPR Article 17).

    Deletes messages, reviews, anonymizes chats and group memberships.
    phone: e.g. "972501234567" or "972501234567@c.us"
    """
    r = requests.post(
        f"{BASE_URL}/api/v2/gdpr/contact-erasure",
        headers=headers,
        json={"phone": phone, "reason": reason},
    )
    r.raise_for_status()
    return r.json()


def export_my_data():
    """Export all account data as JSON (GDPR Article 20 - Data Portability).

    Returns profile, sessions, chats, messages, groups, labels, webhooks, etc.
    """
    r = requests.get(f"{BASE_URL}/api/v2/users/me/export", headers=headers)
    r.raise_for_status()
    return r.json()


def save_export(filepath: str = None):
    """Export account data and save to a JSON file."""
    data = export_my_data()
    if not filepath:
        from datetime import datetime
        filepath = f"moltflow-data-export-{datetime.utcnow().strftime('%Y%m%d')}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath


def delete_account(password: str):
    """Delete your account and all associated data (GDPR Article 17).

    Requires password confirmation. Permanently removes all tenant-scoped
    data (32+ tables) including sessions, messages, groups, labels, etc.
    """
    # current_password is required in the request body for identity confirmation
    r = requests.delete(
        f"{BASE_URL}/api/v2/users/me",
        headers=headers,
        json={"current_password": password},
    )
    r.raise_for_status()
    return {"status": "deleted"}


if __name__ == "__main__":
    print("MoltFlow GDPR Tools")
    print("=" * 40)
    print("\nAvailable operations:")
    print("  erase_contact(phone, reason)  - Erase all data for a contact")
    print("  export_my_data()              - Export all account data as JSON")
    print("  save_export(filepath)         - Export and save to file")
    print("  delete_account(password)      - Delete account and all data")
    print("\nExample:")
    print('  from gdpr import erase_contact')
    print('  result = erase_contact("972501234567")')
    print(f"  print(result)")
