---
name: unifi
version: 1.1.1
homepage: https://github.com/odrobnik/unifi-skill
description: Monitor UniFi network infrastructure via the UniFi Site Manager API. Use to list hosts/sites/devices/APs and get high-level client/device counts.
metadata:
  openclaw:
    requires:
      env: ["UNIFI_API_KEY"]
      optionalEnv: ["UNIFI_BASE_URL"]
---

# UniFi Site Manager API

Monitor UniFi network infrastructure via the Site Manager API.

**Entry point:** `{baseDir}/scripts/unifi.py`

## Setup

See [SETUP.md](SETUP.md) for prerequisites and setup instructions.

## Commands

```bash
python3 {baseDir}/scripts/unifi.py list-hosts
python3 {baseDir}/scripts/unifi.py list-sites
python3 {baseDir}/scripts/unifi.py list-devices
python3 {baseDir}/scripts/unifi.py list-aps
```

Add `--json` for raw output.

## Notes
- Uses the **Site Manager API** (infrastructure/aggregates), not per-client tracking.
