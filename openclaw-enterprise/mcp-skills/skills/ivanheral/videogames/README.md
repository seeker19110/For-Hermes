# Videogames 🎮

A skill for [OpenClaw](https://github.com/openclaw/openclaw) that allows you to query video game information, search for deals, and compare prices across multiple stores.

## Features

- 🔎 **Search**: Find games by name on Steam.
- 💰 **Deals**: Search for the lowest price across more than 25 stores (powered by CheapShark).
- ℹ️ **Details**: Get description, price, developers, and Metacritic score.
- 🏷️ **Offers**: Check current featured offers on Steam.
- 👥 **Players**: View current concurrent player counts.
- � **Trends**: diverse lists like Top Sellers and New Releases on Steam.
- 🔝 **Top Played**: See the games with the most current players on Steam.
- 📰 **News**: Read the latest news for a game.
- 🏆 **Achievements**: View the rarest global achievements for a game.
- ⭐ **Reviews**: Get a summary of user reviews for a game.

## Installation

### From ClawHub (Recommended)
```bash
npx clawhub@latest install ivanheral/videogames
```

### Manually
1. Clone this repository into your global or workspace skills folder:
   ```bash
   git clone https://github.com/ivanheral/videogames ~/.openclaw/skills/videogames
   ```
2. Ensure the script has execution permissions:
   ```bash
   chmod +x ~/.openclaw/skills/videogames/scripts/game_tool.py
   ```

## Usage

Simply ask OpenClaw for what you need:

> "Where is Elden Ring cheapest?"
> "Search for Stardew Valley price on Steam"
> "Tell me today's featured offers on Steam"
> "How many people are playing Dota 2 right now?"
> "What are the most popular games on Steam?"
> "Show me the rarest achievements for Hollow Knight"

### Command Line Usage (Advanced)

You can also use the script directly if needed:

- **Search Deals (CheapShark)**: `python3 scripts/game_tool.py deals "Game Name"`
- **Search Steam**: `python3 scripts/game_tool.py search "Game Name"`
- **Game Details**: `python3 scripts/game_tool.py details <APPID>`
- **Featured Offers**: `python3 scripts/game_tool.py offers`
- **Player Count**: `python3 scripts/game_tool.py players <APPID>`
- **Game News**: `python3 scripts/game_tool.py news <APPID>`
- **Trends (Top Sellers/New)**: `python3 scripts/game_tool.py trends`
- **Most Played Games**: `python3 scripts/game_tool.py top`
- **Achievements**: `python3 scripts/game_tool.py achievements <APPID>`
- **Reviews**: `python3 scripts/game_tool.py reviews <APPID>`

## Requirements

- Python 3.x
- Internet connection (uses public Steam and CheapShark APIs)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
