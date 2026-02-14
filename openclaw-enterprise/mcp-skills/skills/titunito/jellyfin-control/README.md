# Jellyfin Control Skill

A powerful, fault-tolerant skill to control your Jellyfin media server via OpenClaw.

## Features

- **Smart Resume:** Automatically finds the next unplayed episode for any TV show.
- **Rewatch Support:** If a show is fully watched, it plays the last available episode.
- **LG WebOS / Tizen Fix:** Implements a `Play` + `Seek` strategy to fix resumption issues on Smart TVs.
- **Remote Control:** Full control (Play, Pause, Stop, Next, Volume) for any active session.
- **User Activity:** Check playback history for any user (`activity/history`).
- **Statistics:** Quick overview of your library size.
- **Library Scan:** Trigger a library refresh on demand.

## Installation

This skill is designed for OpenClaw.

1. Install dependencies:
   ```bash
   npm install
   ```

2. Configure environment variables (in `.env` or passed to the agent):
   ```bash
   JF_URL=http://your-jellyfin-ip:8096  # or with /jellyfin base path
   JF_API_KEY=your_api_key_here         # Generate in Jellyfin Dashboard > API Keys
   JF_USER=your_username                # Optional: For user-specific actions
   JF_PASS=your_password                # Optional: Required for admin tasks (listing users)
   ```

## Usage

### Resume / Play Content
Finds the best match and plays it on the most active device (or specific device).

```bash
# Resume "Breaking Bad" (Next Up or First Unplayed)
node cli.js resume "Breaking Bad"

# Target a specific device
node cli.js resume "The Matrix" --device "Chromecast"
```

### Remote Control
Control the currently playing media.

```bash
node cli.js control pause
node cli.js control play
node cli.js control next
node cli.js control vol 50
```

### User History
See what users have been watching.

```bash
# Current user history
node cli.js history

# Specific user history (Requires Admin JF_PASS)
node cli.js history jorge
```

### Library Management
```bash
# Show library stats
node cli.js stats

# Trigger scan
node cli.js scan
```

### Search
Debug content IDs.
```bash
node cli.js search "Star Wars"
```

## Requirements

- Node.js
- Access to Jellyfin API

## License

MIT
