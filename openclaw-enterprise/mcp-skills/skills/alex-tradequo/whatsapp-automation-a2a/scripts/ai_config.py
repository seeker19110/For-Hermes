#!/usr/bin/env python3
"""
MoltFlow AI - Knowledge Base, Style Profiles, and Reply Generation
"""
# Required Scopes: ai:manage
# Chat History: Required — style training reads message history
import os
import requests

API_KEY = os.environ.get("MOLTFLOW_API_KEY")
BASE_URL = os.environ.get("MOLTFLOW_API_URL", "https://apiv2.waiflow.app")

if not API_KEY:
    print("Error: MOLTFLOW_API_KEY environment variable not set")
    exit(1)

headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}


# ============================================================================
# Knowledge Base (RAG)
# ============================================================================

def upload_document(file_path: str):
    """Upload a document to the knowledge base (PDF or TXT)."""
    with open(file_path, "rb") as f:
        r = requests.post(
            f"{BASE_URL}/api/v2/ai/knowledge/ingest",
            headers={"X-API-Key": API_KEY},
            files={"file": f},
        )
    r.raise_for_status()
    return r.json()


def search_knowledge(query: str, top_k: int = 5):
    """Semantic search across uploaded documents."""
    r = requests.post(
        f"{BASE_URL}/api/v2/ai/knowledge/search",
        headers=headers,
        json={"query": query, "top_k": top_k},
    )
    r.raise_for_status()
    return r.json()


def list_documents():
    """List all indexed documents."""
    r = requests.get(f"{BASE_URL}/api/v2/ai/knowledge/sources", headers=headers)
    r.raise_for_status()
    return r.json()


def delete_document(source_id: str):
    """Delete a document from the knowledge base."""
    r = requests.delete(f"{BASE_URL}/api/v2/ai/knowledge/{source_id}", headers=headers)
    r.raise_for_status()
    return {"deleted": True}


# ============================================================================
# Style Profiles
# ============================================================================

def train_style(session_id: str = None, wa_chat_id: str = None, name: str = None):
    """Train a style profile. Omit session_id/wa_chat_id for general profile."""
    data = {}
    if session_id:
        data["session_id"] = session_id
    if wa_chat_id:
        data["wa_chat_id"] = wa_chat_id
    if name:
        data["name"] = name
    r = requests.post(f"{BASE_URL}/api/v2/ai/style/train", headers=headers, json=data)
    r.raise_for_status()
    return r.json()


def list_profiles():
    """List all style profiles."""
    r = requests.get(f"{BASE_URL}/api/v2/ai/style/profiles", headers=headers)
    r.raise_for_status()
    return r.json()


def get_profile(contact_id: str = None):
    """Get a style profile by contact ID."""
    params = {}
    if contact_id:
        params["contact_id"] = contact_id
    r = requests.get(f"{BASE_URL}/api/v2/ai/style/profile", headers=headers, params=params)
    r.raise_for_status()
    return r.json()


# ============================================================================
# AI Reply Generation
# ============================================================================

def generate_reply(contact_id: str, context: str, use_rag: bool = True, apply_style: bool = True):
    """Generate an AI reply suggestion."""
    r = requests.post(
        f"{BASE_URL}/api/v2/ai/generate-reply",
        headers=headers,
        json={
            "contact_id": contact_id,
            "context": context,
            "use_rag": use_rag,
            "apply_style": apply_style,
        },
    )
    r.raise_for_status()
    return r.json()


def preview_reply(contact_id: str, context: str, use_rag: bool = True, apply_style: bool = True):
    """Preview an AI reply without counting usage."""
    r = requests.get(
        f"{BASE_URL}/api/v2/ai/preview",
        headers=headers,
        params={
            "contact_id": contact_id,
            "context": context,
            "use_rag": str(use_rag).lower(),
            "apply_style": str(apply_style).lower(),
        },
    )
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    print("MoltFlow AI Features")
    print("=" * 40)

    # Knowledge base
    docs = list_documents()
    print(f"\nKnowledge Base: {len(docs)} documents")
    for d in docs:
        print(f"  - {d.get('name')} ({d.get('chunk_count', 0)} chunks, {d.get('status')})")

    # Style profiles
    profiles = list_profiles()
    print(f"\nStyle Profiles: {len(profiles)}")
    for p in profiles:
        print(f"  - {p.get('name', 'unnamed')} ({p.get('sample_count', 0)} samples)")
