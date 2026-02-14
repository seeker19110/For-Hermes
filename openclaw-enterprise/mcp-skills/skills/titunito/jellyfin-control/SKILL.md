---
name: jellyfin-control
description: Control Jellyfin media server. Search content, resume playback on remote devices (TVs), and manage sessions. Smart "Resume" logic handles finding the next unplayed episode for TV shows.
metadata: {"version": "1.0.0", "author": "Francis via OpenClaw", "openclaw": {"requires": {"env": ["JF_URL", "JF_API_KEY", "JF_USER"]}}}
---

# Jellyfin Control

A robust, fault-tolerant skill to control Jellyfin playback via CLI.

## Features

- **Smart Resume:** Automatically finds the next unplayed episode for series.
- **Resume Position:** Resumes Movies/Episodes exactly where left off (with `Seek` fallback for LG WebOS/Tizen).
- **Device Discovery:** Auto-detects controllable sessions (TVs, Phones, Web).
- **Search:** Find content IDs and details.

## Configuration

Set environment variables in `.env` or `SECRETOS.md`:

```bash
JF_URL=http://your-jellyfin-ip:8096
JF_API_KEY=your_api_key_here
JF_USER=your_username
```

## Usage

### Resume / Play Smart
Finds the best match for "Breaking Bad", determines the next unplayed episode, finds the active TV, and plays it.

```bash
node skills/jellyfin-control/cli.js resume "Breaking Bad"
```

Target a specific device (fuzzy match):
```bash
node skills/jellyfin-control/cli.js resume "Matrix" --device "Chromecast"
```

### Search Content
```bash
node skills/jellyfin-control/cli.js search "Star Wars"
```

## Architecture

- `lib/jellyfin.js`: Core API logic (Auth, Search, Session, Play/Seek).
- `cli.js`: User-friendly command line interface.
