"""
Batch Scanner for processing multiple samples
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

from .models import ScanResult, ScanOptions
from .auditor import SecurityAuditor

logger = logging.getLogger(__name__)


@dataclass
class BatchResult:
    """Batch scan result container"""
    total_samples: int
    scanned_samples: int
    failed_samples: int
    detection_rate: float
    avg_scan_time_ms: float
    results: List[ScanResult] = field(default_factory=list)
    ground_truth: Optional[Dict[str, bool]] = None
    
    def calculate_metrics(self) -> Dict[str, float]:
        """Calculate detection metrics"""
        if not self.results:
            return {"precision": 0, "recall": 0, "f1": 0}
        
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        true_negatives = 0
        
        for result in self.results:
            has_finding = len(result.findings) > 0
            is_malicious = self.ground_truth.get(result.target, False) if self.ground_truth else has_finding
            
            if has_finding and is_malicious:
                true_positives += 1
            elif has_finding and not is_malicious:
                false_positives += 1
            elif not has_finding and is_malicious:
                false_negatives += 1
            else:
                true_negatives += 1
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "true_negatives": true_negatives,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "accuracy": (true_positives + true_negatives) / self.total_samples if self.total_samples > 0 else 0
        }


class BatchScanner:
    """Batch processing for multiple samples"""
    
    def __init__(self, auditor: Optional[SecurityAuditor] = None):
        """
        Initialize batch scanner
        
        Args:
            auditor: SecurityAuditor instance (creates default if None)
        """
        self.auditor = auditor or SecurityAuditor()
    
    def scan_directory(self, directory: str, recursive: bool = True,
                       options: Optional[ScanOptions] = None,
                       ground_truth: Optional[Dict[str, bool]] = None) -> BatchResult:
        """
        Scan all files in a directory
        
        Args:
            directory: Path to directory containing samples
            recursive: Whether to scan subdirectories
            options: Scan configuration options
            ground_truth: Optional dict mapping file paths to malicious status
            
        Returns:
            BatchResult with aggregate statistics
        """
        options = options or ScanOptions()
        
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Collect files
        files = []
        if recursive:
            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    if filename.endswith(('.py', '.js', '.yaml', '.yml')):
                        files.append(os.path.join(root, filename))
        else:
            files = [os.path.join(directory, f) for f in os.listdir(directory)
                     if f.endswith(('.py', '.js', '.yaml', '.yml'))]
        
        logger.info(f"Found {len(files)} files to scan in {directory}")
        
        # Scan each file
        results = []
        failed = 0
        total_time = 0
        
        for file_path in files:
            try:
                result = self.auditor.scan(file_path, options)
                results.append(result)
                total_time += result.scan_time_ms
            except Exception as e:
                logger.error(f"Failed to scan {file_path}: {e}")
                failed += 1
        
        # Calculate statistics
        scanned = len(results)
        total = len(files)
        
        detected = sum(1 for r in results if len(r.findings) > 0)
        detection_rate = detected / scanned if scanned > 0 else 0
        avg_time = total_time / scanned if scanned > 0 else 0
        
        batch_result = BatchResult(
            total_samples=total,
            scanned_samples=scanned,
            failed_samples=failed,
            detection_rate=detection_rate,
            avg_scan_time_ms=avg_time,
            results=results,
            ground_truth=ground_truth
        )
        
        return batch_result
    
    def generate_report(self, batch_result: BatchResult, output_path: str):
        """
        Generate detailed report from batch results
        
        Args:
            batch_result: Batch scan results
            output_path: Path to write report JSON
        """
        metrics = batch_result.calculate_metrics()
        
        report = {
            "summary": {
                "total_samples": batch_result.total_samples,
                "scanned": batch_result.scanned_samples,
                "failed": batch_result.failed_samples,
                "detection_rate": batch_result.detection_rate,
                "avg_scan_time_ms": batch_result.avg_scan_time_ms
            },
            "metrics": metrics,
            "findings_summary": self._summarize_findings(batch_result.results),
            "detailed_results": [r.to_dict() for r in batch_result.results]
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to {output_path}")
    
    def _summarize_findings(self, results: List[ScanResult]) -> Dict[str, Any]:
        """Summarize findings across all results"""
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        type_counts = {}
        
        for result in results:
            for finding in result.findings:
                severity_counts[finding.severity.value] += 1
                type_counts[finding.type] = type_counts.get(finding.type, 0) + 1
        
        return {
            "by_severity": severity_counts,
            "by_type": type_counts,
            "total_findings": sum(severity_counts.values())
        }
