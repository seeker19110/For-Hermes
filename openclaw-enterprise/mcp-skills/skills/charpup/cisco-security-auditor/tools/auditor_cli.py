#!/usr/bin/env python3
"""
Skill Security Auditor CLI
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib import SecurityAuditor, BatchScanner, ScanOptions, SeverityLevel

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Skill Security Auditor - Detect malicious patterns in OpenClaw skills'
    )
    parser.add_argument('target', help='File or directory to scan')
    parser.add_argument('-o', '--output', help='Output file for JSON report')
    parser.add_argument('--batch', action='store_true', help='Batch scan directory')
    parser.add_argument('--no-yara', action='store_true', help='Disable YARA scanning')
    parser.add_argument('--no-llm', action='store_true', help='Disable LLM analysis')
    parser.add_argument('--confidence', type=float, default=0.7,
                        help='Confidence threshold (0.0-1.0)')
    parser.add_argument('--severity', nargs='+',
                        choices=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'],
                        help='Filter by severity levels')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--yara-rules', help='Path to custom YARA rules')
    parser.add_argument('--severity-map', help='Path to custom severity map')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize auditor
    auditor = SecurityAuditor(
        yara_rules_path=args.yara_rules,
        severity_map_path=args.severity_map,
        llm_api_key=os.getenv("MOONSHOT_API_KEY")
    )
    
    # Prepare options
    options = ScanOptions(
        use_yara=not args.no_yara,
        use_llm=not args.no_llm,
        confidence_threshold=args.confidence,
        severity_filter=[SeverityLevel(s) for s in args.severity] if args.severity else None
    )
    
    if args.batch or os.path.isdir(args.target):
        # Batch scan
        scanner = BatchScanner(auditor)
        result = scanner.scan_directory(args.target, options=options)
        
        print(f"\n{'='*60}")
        print("BATCH SCAN RESULTS")
        print(f"{'='*60}")
        print(f"Total samples: {result.total_samples}")
        print(f"Scanned: {result.scanned_samples}")
        print(f"Failed: {result.failed_samples}")
        print(f"Detection rate: {result.detection_rate:.1%}")
        print(f"Avg scan time: {result.avg_scan_time_ms:.0f}ms")
        
        metrics = result.calculate_metrics()
        if metrics.get("precision") > 0 or metrics.get("recall") > 0:
            print(f"\nMetrics (with ground truth):")
            print(f"  Precision: {metrics['precision']:.2%}")
            print(f"  Recall: {metrics['recall']:.2%}")
            print(f"  F1 Score: {metrics['f1']:.2%}")
        
        if args.output:
            scanner.generate_report(result, args.output)
    else:
        # Single file scan
        result = auditor.scan(args.target, options)
        
        print(f"\n{'='*60}")
        print(f"SCAN RESULT: {result.target}")
        print(f"{'='*60}")
        print(f"Engines used: {', '.join(result.engines_used)}")
        print(f"Scan time: {result.scan_time_ms}ms")
        print(f"Total findings: {len(result.findings)}")
        
        if result.findings:
            print(f"\nFINDINGS:")
            for finding in result.findings:
                print(f"\n  [{finding.severity.value}] {finding.type}")
                print(f"  Rule: {finding.rule_id}")
                print(f"  Confidence: {finding.confidence:.0%}")
                print(f"  Evidence: {finding.evidence[:100]}...")
                if finding.description:
                    print(f"  Description: {finding.description[:150]}...")
        else:
            print("\n✅ No security issues found")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result.to_dict(), f, indent=2)
            print(f"\nReport saved to {args.output}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
