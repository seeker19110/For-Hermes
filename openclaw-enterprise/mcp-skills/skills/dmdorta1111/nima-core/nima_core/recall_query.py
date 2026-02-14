"""Query NIMA memories.

Usage:
    python3 -m nima_core.recall_query "search query" [--top-k 5] [--json-output]
    python3 -m nima_core.recall_query "weather" --since 24h
    python3 -m nima_core.recall_query "project" --since 2026-02-01 --until 2026-02-07
    python3 -m nima_core.recall_query --timeline --since 7d
    python3 -m nima_core.recall_query --timeline --since 24h --who Alice
"""

import argparse
import json
import sys
from typing import Any

from nima_core import NimaCore
from nima_core.config.auto import get_nima_config

__all__ = ["format_human_readable", "main"]


def format_human_readable(results: list[dict[str, Any]]) -> str:
    """Format recall results in a human-readable way."""
    if not results:
        return "No memories found."
    
    formatted = []
    for i, result in enumerate(results, 1):
        who = str(result.get('who', 'Unknown')).replace('\n', ' ')
        what = str(result.get('what', '')).replace('\n', ' ')
        importance = result.get('importance', 0)
        when = result.get('when') or result.get('timestamp_iso') or result.get('timestamp', '')
        
        formatted.append(f"{i}. [{importance:.2f}] {who}: {what}")
        if when and when != "None":
            formatted.append(f"   🕐 {when}")
        formatted.append("")
    
    return '\n'.join(formatted)


def main(argv=None) -> int:
    """Main entry point for querying memories.
    
    Args:
        argv: Command line arguments (defaults to sys.argv)
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("query", nargs="?", default=None, help="Search query (optional with --timeline)")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results (default: 5)")
    parser.add_argument("--since", help="Only memories after this time (e.g. '24h', '7d', '2026-02-01')")
    parser.add_argument("--until", help="Only memories before this time")
    parser.add_argument("--who", help="Filter by person")
    parser.add_argument("--timeline", action="store_true", help="Show memories by time (no search query needed)")
    parser.add_argument("--json-output", action="store_true", dest="json_output", help="Output as JSON (default: human-readable)")
    parser.add_argument("--data-dir", help="Override data directory path")
    
    args = parser.parse_args(argv)
    
    if args.top_k < 1:
        parser.error("--top-k must be a positive integer")
    
    if not args.query and not args.timeline:
        parser.error("either provide a search query or use --timeline")
    
    try:
        # Get configuration
        config = get_nima_config()
        if args.data_dir:
            config["data_dir"] = args.data_dir
        
        # Initialize NimaCore
        nima = NimaCore(
            name="CLI Recall",
            data_dir=config["data_dir"]
        )
        
        # Query memories
        if args.timeline:
            results = nima.temporal_recall(
                since=args.since,
                until=args.until,
                who=args.who,
                top_k=args.top_k,
            )
        else:
            results = nima.recall(
                args.query,
                top_k=args.top_k,
                since=args.since,
                until=args.until,
            )
        
        # Output results
        if args.json_output:
            print(json.dumps(results, indent=2))
        else:
            print(format_human_readable(results))
        
        return 0
        
    except Exception as e:
        if args.json_output:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
