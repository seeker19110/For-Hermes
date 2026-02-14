---
name: cloudflare-manager
description: Manage Cloudflare DNS records, Tunnels (cloudflared), and Zero Trust policies. Use when user wants to "point domain", "expose localhost", or "block IP".
---

# Cloudflare Manager

## Configuration
Requires the following environment variables in `.env`:

| Variable | Description | Required? |
| :--- | :--- | :--- |
| `CLOUDFLARE_API_TOKEN` | API Token with Zone.DNS permissions | Yes |
| `CLOUDFLARE_ZONE_ID` | The Zone ID to manage | Yes |

Legacy support: `CF_API_TOKEN` and `CF_ZONE_ID` are also accepted.

## Installation
This skill requires Python dependencies (`requests`, `PyYAML`).
Run the install script to set up a local virtual environment:
```bash
./scripts/install.sh
```

## Usage
- **Role**: Cloud Engineer.
- **Trigger**: "Create DNS record", "Setup tunnel", "Expose port 3000".
- **Output**: JSON status or CLI command results.

### Commands
#### `scripts/cf_manager.py`
The main CLI wrapper. Use the venv python to run it.

**Syntax:**
```bash
.venv/bin/python3 scripts/cf_manager.py [OPTIONS] <COMMAND>
```

**Options:**
- `--dry-run`: Simulate actions without applying changes (DNS or Ingress).

**Examples:**
```bash
# List DNS Records
.venv/bin/python3 scripts/cf_manager.py list-dns

# Add DNS Record
.venv/bin/python3 scripts/cf_manager.py add-dns --type A --name subdomain --content 1.2.3.4

# Update Ingress (Tunnel)
.venv/bin/python3 scripts/cf_manager.py update-ingress --hostname app.example.com --service http://localhost:3000
```

## Security & Permissions
- **API Token Scope**: Follow the *Principle of Least Privilege*. Create a token with **Zone:DNS:Edit** and **Zone:Settings:Edit** permissions only for the specific zone. Avoid using Global API Keys.
- **Privileged Operations**:
  - The `update-ingress` command modifies `/etc/cloudflared/config.yml` and restarts the service.
  - **Sudo Access**: Requires sudo to run `tee` and `systemctl`.
  - **Least Privilege**: Do NOT grant full sudo. Use the example in `references/sudoers.example` to restrict sudo access to only the necessary commands.
  - **Safeguard**: Use `--dry-run` to preview the config changes without writing to disk or restarting services.

## Capabilities
1.  **DNS Management**: Add/Edit/Delete A/CNAME records.
2.  **Tunnels**: `cloudflared` config management (requires sudo).
3.  **Security**: Access Policies, WAF rules.

## Reference Materials
- [Tunnel Guide](references/tunnel-guide.md)
