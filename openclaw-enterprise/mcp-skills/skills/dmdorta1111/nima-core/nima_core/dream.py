"""Run NIMA dream consolidation.

Usage:
    python3 -m nima_core.dream [--hours 24] [--verbose]
"""

import argparse
import json
import sys
from typing import Any

from nima_core import NimaCore
from nima_core.config.auto import get_nima_config

__all__ = ["main"]


def main(argv=None) -> int:
    """Main entry point for dream consolidation.
    
    Args:
        argv: Command line arguments (defaults to sys.argv)
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--hours", type=int, default=24, help="How far back to consolidate (default: 24)")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--data-dir", help="Override data directory path")
    
    args = parser.parse_args(argv)
    
    try:
        # Get configuration
        config = get_nima_config()
        if args.data_dir:
            config["data_dir"] = args.data_dir
        
        # Initialize NimaCore
        nima = NimaCore(
            name="CLI Dream",
            data_dir=config["data_dir"]
        )
        
        # Run dream consolidation
        result: dict[str, Any] = nima.dream(hours=args.hours)
        
        # Output result
        status = result.get("status", "unknown")
        if args.verbose:
            print(json.dumps(result, indent=2))
        else:
            if status == "complete":
                memories_processed = result.get("memories_processed", 0)
                print(f"Dream consolidation completed successfully. Processed {memories_processed} memories.")
            elif status == "no_memories":
                print("Dream consolidation completed. No memories to process.")
            elif status == "error":
                error_msg = result.get("error", "Unknown error")
                print(f"Dream consolidation failed: {error_msg}", file=sys.stderr)
                return 1
            else:
                print(f"Dream consolidation finished with status: {status}")
        
        # Return 1 if status is error or None, 0 otherwise
        return 0 if status != "error" else 1
        
    except Exception as e:
        if args.verbose:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
