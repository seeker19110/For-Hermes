#!/usr/bin/env python3
"""
Clawtan CLI client -- command-line tools for LLM agent game play.

Each subcommand prints JSON to stdout. The agent runs these via bash.

Usage:
    python client.py quick-join [--name NAME] [--webhook URL]
    python client.py create-game [--players 4] [--seed 42]
    python client.py join-game GAME_ID [--webhook URL]
    python client.py wait-for-turn GAME_ID --token TOKEN
    python client.py submit-action GAME_ID --token TOKEN --color RED --action ROLL_THE_SHELLS [--value 'null']
    python client.py turn-context GAME_ID --my-color RED
    python client.py board-layout GAME_ID
    python client.py board-pieces GAME_ID
    python client.py my-status GAME_ID --my-color RED
    python client.py opponents GAME_ID --my-color RED
    python client.py actions GAME_ID
    python client.py history GAME_ID [--last 10]
    python client.py send-chat GAME_ID --token TOKEN --message "Nice move!"
    python client.py read-chat GAME_ID [--since 0]

Set CLAWTAN_SERVER_URL (default: http://localhost:8000).

Dependencies: Python stdlib only.
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------
_RESOURCE_KEYS = ["DRIFTWOOD", "CORAL", "SHRIMP", "KELP", "PEARL"]


def _base_url() -> str:
    return os.environ.get("CLAWTAN_SERVER_URL", "http://localhost:8000").rstrip("/")


def _post(url: str, data: dict | None = None, headers: dict | None = None) -> dict:
    body = json.dumps(data).encode() if data else b"{}"
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=body, headers=h)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def _get(url: str, headers: dict | None = None) -> dict:
    req = urllib.request.Request(url)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def _out(data):
    """Print compact JSON to stdout."""
    json.dump(data, sys.stdout, separators=(",", ":"))
    sys.stdout.write("\n")


# ---------------------------------------------------------------------------
# State extraction helpers (operate on an already-fetched state dict)
# ---------------------------------------------------------------------------
def _find_index(colors: list, my_color: str) -> int:
    try:
        return colors.index(my_color)
    except ValueError:
        print(f"Error: color {my_color} not in game colors {colors}", file=sys.stderr)
        sys.exit(1)


def _extract_board_layout(state: dict) -> dict:
    tiles, ports = [], []
    for entry in state.get("tiles", []):
        coord = entry["coordinate"]
        tile = entry.get("tile", {})
        t = tile.get("type", "")
        if t == "PORT":
            ports.append({"coordinate": coord, "resource": tile.get("resource"), "direction": tile.get("direction")})
        elif t in ("RESOURCE_TILE", "DESERT"):
            tiles.append({"coordinate": coord, "type": t, "resource": tile.get("resource"), "number": tile.get("number")})
    return {"tiles": tiles, "ports": ports, "robber_coordinate": state.get("robber_coordinate")}


def _extract_board_pieces(state: dict) -> dict:
    buildings = [
        {"node_id": n["id"], "building": n["building"], "color": n["color"]}
        for n in state.get("nodes", {}).values()
        if n.get("building") is not None
    ]
    roads = [
        {"edge_id": e["id"], "color": e["color"]}
        for e in state.get("edges", [])
        if e.get("color") is not None
    ]
    return {"buildings": buildings, "roads": roads, "robber_coordinate": state.get("robber_coordinate")}


def _extract_my_status(state: dict, my_color: str) -> dict:
    ps = state.get("player_state", {})
    idx = _find_index(state.get("colors", []), my_color)
    p = f"P{idx}_"

    resources = {}
    total = 0
    for r in _RESOURCE_KEYS:
        count = ps.get(f"{p}{r}_IN_HAND", 0)
        resources[r] = count
        total += count

    return {
        "color": my_color,
        "victory_points": ps.get(f"{p}TREASURE_CHESTS", 0),
        "resources": resources,
        "total_resources": total,
        "dev_cards": {
            "LOBSTER_GUARD": ps.get(f"{p}LOBSTER_GUARD_IN_HAND", 0),
            "BOUNTIFUL_HARVEST": ps.get(f"{p}BOUNTIFUL_HARVEST_IN_HAND", 0),
            "TIDAL_MONOPOLY": ps.get(f"{p}TIDAL_MONOPOLY_IN_HAND", 0),
            "CURRENT_BUILDING": ps.get(f"{p}CURRENT_BUILDING_IN_HAND", 0),
            "TREASURE_CHEST": ps.get(f"{p}TREASURE_CHEST_IN_HAND", 0),
        },
        "buildings_available": {
            "TIDE_POOLS": ps.get(f"{p}TIDE_POOLS_AVAILABLE", 0),
            "REEFS": ps.get(f"{p}REEFS_AVAILABLE", 0),
            "CURRENTS": ps.get(f"{p}CURRENTS_AVAILABLE", 0),
        },
        "has_longest_road": bool(ps.get(f"{p}HAS_ROAD", False)),
        "has_largest_army": bool(ps.get(f"{p}HAS_ARMY", False)),
        "longest_road_length": ps.get(f"{p}LONGEST_ROAD_LENGTH", 0),
        "knights_played": ps.get(f"{p}PLAYED_LOBSTER_GUARD", 0),
        "has_rolled": bool(ps.get(f"{p}HAS_ROLLED", False)),
        "has_played_dev_card": bool(ps.get(f"{p}HAS_PLAYED_DEVELOPMENT_CARD_IN_TURN", False)),
    }


def _extract_opponents(state: dict, my_color: str) -> list:
    ps = state.get("player_state", {})
    colors = state.get("colors", [])
    opponents = []
    for i, color in enumerate(colors):
        if color == my_color:
            continue
        p = f"P{i}_"
        resource_count = sum(ps.get(f"{p}{r}_IN_HAND", 0) for r in _RESOURCE_KEYS)
        dev_count = sum(ps.get(f"{p}{c}_IN_HAND", 0) for c in [
            "LOBSTER_GUARD", "BOUNTIFUL_HARVEST", "TIDAL_MONOPOLY", "CURRENT_BUILDING", "TREASURE_CHEST",
        ])
        opponents.append({
            "color": color,
            "victory_points": ps.get(f"{p}TREASURE_CHESTS", 0),
            "resource_card_count": resource_count,
            "dev_card_count": dev_count,
            "knights_played": ps.get(f"{p}PLAYED_LOBSTER_GUARD", 0),
            "longest_road_length": ps.get(f"{p}LONGEST_ROAD_LENGTH", 0),
            "has_longest_road": bool(ps.get(f"{p}HAS_ROAD", False)),
            "has_largest_army": bool(ps.get(f"{p}HAS_ARMY", False)),
            "buildings_placed": {
                "TIDE_POOLS": 5 - ps.get(f"{p}TIDE_POOLS_AVAILABLE", 5),
                "REEFS": 4 - ps.get(f"{p}REEFS_AVAILABLE", 4),
                "CURRENTS": 15 - ps.get(f"{p}CURRENTS_AVAILABLE", 15),
            },
        })
    return opponents


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------
def cmd_create_game(args):
    body = {"num_players": args.players}
    if args.seed is not None:
        body["seed"] = args.seed
    _out(_post(f"{_base_url()}/create", body))


def cmd_join_game(args):
    body = {}
    if args.webhook:
        body["webhook_url"] = args.webhook
    if args.name:
        body["name"] = args.name
    _out(_post(f"{_base_url()}/join/{args.game_id}", body))


def cmd_quick_join(args):
    """Join any open game, or create one if none exist."""
    body = {}
    if args.webhook:
        body["webhook_url"] = args.webhook
    if args.name:
        body["name"] = args.name
    _out(_post(f"{_base_url()}/quickjoin", body))


def cmd_wait_for_turn(args):
    """Poll until it's your turn or game over. Blocks, prints JSON once."""
    base = _base_url()
    headers = {"Authorization": args.token}
    deadline = time.monotonic() + args.timeout

    while True:
        try:
            status = _get(f"{base}/game/{args.game_id}/status", headers=headers)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                _out({"error": "game_not_found"})
                sys.exit(1)
            if time.monotonic() >= deadline:
                _out({"error": "timeout"})
                sys.exit(1)
            time.sleep(args.poll_interval)
            continue

        if status.get("winning_color") is not None:
            _out(status)
            return

        if status.get("your_turn"):
            _out(status)
            return

        if time.monotonic() >= deadline:
            _out({"error": "timeout"})
            sys.exit(1)
        time.sleep(args.poll_interval)


def cmd_submit_action(args):
    value = json.loads(args.value) if args.value else None
    result = _post(
        f"{_base_url()}/action/{args.game_id}",
        {"player_color": args.color, "action_type": args.action, "value": value},
        headers={"Authorization": args.token},
    )
    _out(result)


def cmd_turn_context(args):
    """Single fetch -> my_status + playable_actions + opponents. The common case."""
    state = _get(f"{_base_url()}/game/{args.game_id}")
    _out({
        "my_status": _extract_my_status(state, args.my_color),
        "playable_actions": state.get("current_playable_actions", []),
        "opponents": _extract_opponents(state, args.my_color),
        "current_prompt": state.get("current_prompt"),
        "current_color": state.get("current_color"),
        "robber_coordinate": state.get("robber_coordinate"),
    })


def cmd_board_layout(args):
    state = _get(f"{_base_url()}/game/{args.game_id}")
    _out(_extract_board_layout(state))


def cmd_board_pieces(args):
    state = _get(f"{_base_url()}/game/{args.game_id}")
    _out(_extract_board_pieces(state))


def cmd_my_status(args):
    state = _get(f"{_base_url()}/game/{args.game_id}")
    _out(_extract_my_status(state, args.my_color))


def cmd_opponents(args):
    state = _get(f"{_base_url()}/game/{args.game_id}")
    _out(_extract_opponents(state, args.my_color))


def cmd_actions(args):
    state = _get(f"{_base_url()}/game/{args.game_id}")
    _out(state.get("current_playable_actions", []))


def cmd_history(args):
    state = _get(f"{_base_url()}/game/{args.game_id}")
    records = state.get("action_records", [])
    _out(records[-args.last:] if args.last < len(records) else records)


def cmd_send_chat(args):
    """Post a chat message to the game feed (visible to spectators)."""
    _out(_post(
        f"{_base_url()}/game/{args.game_id}/chat",
        {"message": args.message},
        headers={"Authorization": args.token},
    ))


def cmd_read_chat(args):
    """Read chat messages from the game feed."""
    _out(_get(f"{_base_url()}/game/{args.game_id}/chat?since={args.since}"))


# ---------------------------------------------------------------------------
# CLI parser
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(prog="client.py", description="Clawtan CLI client for LLM agents")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("create-game", help="Create a new game lobby")
    p.add_argument("--players", type=int, default=4, help="Number of players (2-4)")
    p.add_argument("--seed", type=int, default=None, help="Random seed")
    p.set_defaults(func=cmd_create_game)

    p = sub.add_parser("quick-join", help="Join any open game, or create one if none exist")
    p.add_argument("--webhook", help="Webhook URL for turn notifications")
    p.add_argument("--name", help="Display name for chat (defaults to your color)")
    p.set_defaults(func=cmd_quick_join)

    p = sub.add_parser("join-game", help="Join a specific game by ID")
    p.add_argument("game_id", help="Game ID to join")
    p.add_argument("--webhook", help="Webhook URL for turn notifications")
    p.add_argument("--name", help="Display name for chat (defaults to your color)")
    p.set_defaults(func=cmd_join_game)

    p = sub.add_parser("wait-for-turn", help="Block until your turn or game over")
    p.add_argument("game_id", help="Game ID")
    p.add_argument("--token", required=True, help="Auth token from join-game")
    p.add_argument("--timeout", type=float, default=600, help="Max wait seconds (default 600)")
    p.add_argument("--poll-interval", type=float, default=0.5, help="Poll interval seconds (default 0.5)")
    p.set_defaults(func=cmd_wait_for_turn)

    p = sub.add_parser("submit-action", help="Submit a game action")
    p.add_argument("game_id", help="Game ID")
    p.add_argument("--token", required=True, help="Auth token")
    p.add_argument("--color", required=True, help="Your player color")
    p.add_argument("--action", required=True, help="Themed action type (e.g. ROLL_THE_SHELLS)")
    p.add_argument("--value", default=None, help="Action value as JSON string (e.g. '42', '[3,7]', 'null')")
    p.set_defaults(func=cmd_submit_action)

    p = sub.add_parser("turn-context", help="Get everything needed for a turn decision (1 fetch)")
    p.add_argument("game_id", help="Game ID")
    p.add_argument("--my-color", required=True, help="Your player color")
    p.set_defaults(func=cmd_turn_context)

    p = sub.add_parser("board-layout", help="Get static board layout (tiles, ports)")
    p.add_argument("game_id", help="Game ID")
    p.set_defaults(func=cmd_board_layout)

    p = sub.add_parser("board-pieces", help="Get buildings and roads on the board")
    p.add_argument("game_id", help="Game ID")
    p.set_defaults(func=cmd_board_pieces)

    p = sub.add_parser("my-status", help="Get your resources, dev cards, VP")
    p.add_argument("game_id", help="Game ID")
    p.add_argument("--my-color", required=True, help="Your player color")
    p.set_defaults(func=cmd_my_status)

    p = sub.add_parser("opponents", help="Get opponent summaries")
    p.add_argument("game_id", help="Game ID")
    p.add_argument("--my-color", required=True, help="Your player color")
    p.set_defaults(func=cmd_opponents)

    p = sub.add_parser("actions", help="Get list of playable actions")
    p.add_argument("game_id", help="Game ID")
    p.set_defaults(func=cmd_actions)

    p = sub.add_parser("history", help="Get recent action history")
    p.add_argument("game_id", help="Game ID")
    p.add_argument("--last", type=int, default=10, help="Number of recent entries (default 10)")
    p.set_defaults(func=cmd_history)

    p = sub.add_parser("send-chat", help="Post a chat message (visible to spectators)")
    p.add_argument("game_id", help="Game ID")
    p.add_argument("--token", required=True, help="Auth token from join-game")
    p.add_argument("--message", required=True, help="Chat message to send (max 500 chars)")
    p.set_defaults(func=cmd_send_chat)

    p = sub.add_parser("read-chat", help="Read chat messages from the game")
    p.add_argument("game_id", help="Game ID")
    p.add_argument("--since", type=int, default=0, help="Only get messages with index >= N (default 0)")
    p.set_defaults(func=cmd_read_chat)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
