"""Capture a message into NIMA memory.

Usage:
    python3 -m nima_core.capture_message "who" "what happened" [--importance 0.5] [--type conversation]
    
    # Pipe from stdin
    echo "important event" | python3 -m nima_core.capture_message "system" --importance 0.9
"""

import argparse
import json
import sys

from nima_core import NimaCore
from nima_core.config.auto import get_nima_config

__all__ = ["main"]


def main(argv=None) -> int:
    """Main entry point for capturing messages.
    
    Args:
        argv: Command line arguments (defaults to sys.argv)
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("who", help="Who said/did it")
    parser.add_argument("what", nargs="?", help="What happened (can come from stdin)")
    parser.add_argument("--importance", type=float, default=0.5, help="Importance score [0-1] (default: 0.5)")
    parser.add_argument("--type", dest="memory_type", default="conversation", help="Memory type (default: conversation)")
    parser.add_argument("--data-dir", help="Override data directory path")
    parser.add_argument("--json-output", action="store_true", dest="json_output", help="Output as JSON (default: human-readable)")
    
    args = parser.parse_args(argv)
    
    # Validate importance range
    if not 0.0 <= args.importance <= 1.0:
        error_msg = f"Importance must be between 0.0 and 1.0, got {args.importance}"
        if args.json_output:
            print(json.dumps({"error": error_msg}), file=sys.stderr)
        else:
            print(f"Error: {error_msg}", file=sys.stderr)
        return 1
    
    # Read 'what' from stdin if not provided as argument
    what = args.what
    if what is None:
        if sys.stdin.isatty():
            parser.error("the following arguments are required: what")
        what = sys.stdin.read().strip()
        if not what:
            error_msg = "Empty input from stdin"
            if args.json_output:
                print(json.dumps({"error": error_msg}), file=sys.stderr)
            else:
                print(f"Error: {error_msg}", file=sys.stderr)
            return 1
    
    try:
        # Get configuration
        config = get_nima_config()
        if args.data_dir:
            config["data_dir"] = args.data_dir
        
        # Initialize NimaCore
        nima = NimaCore(
            name="CLI Capture",
            data_dir=config["data_dir"]
        )
        
        # Capture the message
        result = nima.capture(
            who=args.who,
            what=what,
            importance=args.importance,
            memory_type=args.memory_type
        )
        
        # Output result
        if args.json_output:
            output = {
                "success": result,
                "who": args.who,
                "what": what,
                "importance": args.importance,
                "type": args.memory_type
            }
            print(json.dumps(output))
        else:
            status = "✅ Captured" if result else "❌ Failed"
            print(f"{status}: [{args.importance}] {args.who}: {what}")
        
        return 0 if result else 1
        
    except Exception as e:
        if args.json_output:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
