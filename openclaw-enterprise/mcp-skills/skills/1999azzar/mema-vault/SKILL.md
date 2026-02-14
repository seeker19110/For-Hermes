---
name: mema-vault
description: Secure credential manager for Mema. Uses AES-256 encryption and best practices to store, retrieve, and rotate secrets. NEVER output raw secrets in logs or casual chat.
---

# Mema Vault

## Setup (First Time)
1.  Copy `.env.example` to `.env`.
2.  Generate a master key: `openssl rand -base64 32`.
3.  Set `MEMA_VAULT_MASTER_KEY` in `.env`.
4.  Choose backend (`file` or `redis`).

## Usage
- **Role**: Secure Vault Keeper.
- **Trigger**: "Get API key for X", "Update password for Y", "Where is my token?".
- **Output**: Masked secrets (`sk-***`) or direct usage in a secure context (e.g. env var injection).

## Capabilities
1.  **Store**: Encrypt & save secrets (Redis/File).
2.  **Retrieve**: Decrypt & provide secrets securely.
3.  **Audit**: Track access to sensitive data.
4.  **Rotate**: Helper scripts for key rotation.

## Security Rules
- **NEVER** output full secrets to the user unless explicitly asked with "show me".
- **NEVER** log secrets to disk.
- Use `.gitignore` strictly.
- Prefer Environment Variables over config files.

## Reference Materials
- [Security Policy](references/security-policy.md)
