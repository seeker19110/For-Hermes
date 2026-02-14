#!/usr/bin/env python3
"""
NIMA Consolidation Service
===========================
Run dream consolidation on demand or via cron.

Usage:
    python -m nima_core.services.consolidation --hours 24 --data-dir ./my_data
    python -m nima_core.services.consolidation --help

Author: NIMA Project
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def run_consolidation(
    nima = None,
    hours: int = 24,
    data_dir: Optional[str] = None,
    verbose: bool = False,
):
    """
    Run dream consolidation.
    
    Args:
        nima: Existing NimaCore instance (creates new if None)
        hours: How many hours of memories to consolidate
        data_dir: Override NIMA_DATA_DIR
        verbose: Enable detailed logging
    
    Returns:
        Dict with consolidation results
    """
    from ..core import NimaCore
    
    if nima is None:
        if data_dir:
            os.environ["NIMA_DATA_DIR"] = str(data_dir)
        nima = NimaCore(auto_init=True)
    
    if verbose:
        logger.info(f"Starting consolidation: {hours}h of memories")
    
    result = nima.dream(hours=hours)
    
    if verbose:
        logger.info(f"Consolidation complete: {result.get('status', 'unknown')}")
    
    return result


def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="NIMA Dream Consolidation Service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Consolidate last 24 hours
  python -m nima_core.services.consolidation
  
  # Consolidate last 72 hours from custom directory
  python -m nima_core.services.consolidation --hours 72 --data-dir /path/to/data
  
  # Verbose output
  python -m nima_core.services.consolidation --hours 24 --verbose
        """
    )
    
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Hours of memories to consolidate (default: 24)"
    )
    
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Override NIMA_DATA_DIR (default: use environment or ./nima_data)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    try:
        result = run_consolidation(
            hours=args.hours,
            data_dir=args.data_dir,
            verbose=args.verbose,
        )
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n{'='*50}")
            print("NIMA Consolidation Results")
            print(f"{'='*50}")
            print(f"Status: {result.get('status', 'unknown')}")
            print(f"Memories processed: {result.get('memories_processed', 0)}")
            print(f"Timestamp: {result.get('timestamp', datetime.now().isoformat())}")
            print(f"{'='*50}\n")
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Consolidation failed: {e}", exc_info=args.verbose)
        sys.exit(1)


if __name__ == "__main__":
    main()
