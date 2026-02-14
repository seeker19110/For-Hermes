#!/usr/bin/env python3
"""
MoltFlow Leads - Lead Detection, Pipeline Tracking, Bulk Operations
"""
# Required Scopes: leads:manage, custom-groups:manage
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


def list_leads(status: str = None, source_group_id: str = None, limit: int = 50, offset: int = 0):
    """List leads with optional filters."""
    params = {"limit": limit, "offset": offset}
    if status:
        params["status"] = status
    if source_group_id:
        params["source_group_id"] = source_group_id
    r = requests.get(f"{BASE_URL}/api/v2/leads", headers=headers, params=params)
    r.raise_for_status()
    return r.json()


def get_lead(lead_id: str):
    """Get lead details."""
    r = requests.get(f"{BASE_URL}/api/v2/leads/{lead_id}", headers=headers)
    r.raise_for_status()
    return r.json()


def update_lead_status(lead_id: str, status: str):
    """Update lead status. Statuses: new, contacted, qualified, converted, lost."""
    r = requests.patch(
        f"{BASE_URL}/api/v2/leads/{lead_id}/status",
        headers=headers,
        json={"status": status},
    )
    r.raise_for_status()
    return r.json()


def bulk_update_status(lead_ids: list, status: str):
    """Bulk update lead statuses."""
    r = requests.post(
        f"{BASE_URL}/api/v2/leads/bulk/status",
        headers=headers,
        json={"lead_ids": lead_ids, "status": status},
    )
    r.raise_for_status()
    return r.json()


def bulk_add_to_group(lead_ids: list, custom_group_id: str):
    """Bulk add leads to a custom group."""
    r = requests.post(
        f"{BASE_URL}/api/v2/leads/bulk/add-to-group",
        headers=headers,
        json={"lead_ids": lead_ids, "custom_group_id": custom_group_id},
    )
    r.raise_for_status()
    return r.json()


def export_leads_csv(status: str = None):
    """Export leads as CSV."""
    params = {}
    if status:
        params["status"] = status
    r = requests.get(
        f"{BASE_URL}/api/v2/leads/export/csv",
        headers=headers,
        params=params,
    )
    r.raise_for_status()
    return r.text


def export_leads_json(status: str = None):
    """Export leads as JSON."""
    params = {}
    if status:
        params["status"] = status
    r = requests.get(
        f"{BASE_URL}/api/v2/leads/export/json",
        headers=headers,
        params=params,
    )
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    print("MoltFlow Lead Pipeline")
    print("=" * 40)

    leads = list_leads()
    total = leads.get("total", 0) if isinstance(leads, dict) else 0
    print(f"\nTotal Leads: {total}")

    # Status breakdown
    for status in ["new", "contacted", "qualified", "converted", "lost"]:
        by_status = list_leads(status=status, limit=1)
        count = by_status.get("total", 0) if isinstance(by_status, dict) else 0
        print(f"  {status.capitalize()}: {count}")
