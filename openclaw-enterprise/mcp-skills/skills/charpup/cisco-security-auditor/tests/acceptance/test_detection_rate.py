"""
Acceptance tests - Detection rate validation
Target: 90%+ detection rate on 50 samples
"""

import os
import sys
import json
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib import SecurityAuditor, BatchScanner, ScanOptions


class TestDetectionRate:
    """
    Acceptance tests for detection rate requirements
    Target: >= 90% detection rate on 50 samples
    """
    
    @pytest.fixture(scope="class")
    def sample_dir(self):
        """Get test samples directory"""
        return Path(__file__).parent.parent.parent / "test_samples"
    
    @pytest.fixture(scope="class")
    def ground_truth(self, sample_dir):
        """Load ground truth data"""
        gt_path = sample_dir / "ground_truth.json"
        if gt_path.exists():
            with open(gt_path) as f:
                return json.load(f)
        return {}
    
    @pytest.fixture(scope="class")
    def batch_result(self, sample_dir, ground_truth):
        """Run batch scan and return results"""
        if not sample_dir.exists():
            pytest.skip("Test samples not found")
        
        scanner = BatchScanner()
        options = ScanOptions(use_yara=True, use_llm=False)  # YARA only for speed
        
        # Create full path ground truth
        full_gt = {str(sample_dir / k): v for k, v in ground_truth.items()}
        
        return scanner.scan_directory(str(sample_dir), options=options, ground_truth=full_gt)
    
    def test_minimum_sample_count(self, batch_result):
        """Verify we have at least 50 samples"""
        assert batch_result.total_samples >= 50, f"Need 50+ samples, got {batch_result.total_samples}"
    
    def test_detection_rate_target(self, batch_result):
        """
        Test: Detection rate must be >= 90%
        This is the primary acceptance criterion for Phase 2
        """
        metrics = batch_result.calculate_metrics()
        recall = metrics.get("recall", 0)
        
        print(f"\nDetection Metrics:")
        print(f"  True Positives: {metrics.get('true_positives', 0)}")
        print(f"  False Negatives: {metrics.get('false_negatives', 0)}")
        print(f"  Detection Rate (Recall): {recall:.1%}")
        print(f"  Precision: {metrics.get('precision', 0):.1%}")
        
        assert recall >= 0.90, f"Detection rate {recall:.1%} below target 90%"
    
    def test_false_positive_rate(self, batch_result):
        """
        Test: False positive rate should be < 10%
        """
        metrics = batch_result.calculate_metrics()
        fp_rate = metrics.get('false_positives', 0) / max(batch_result.total_samples, 1)
        
        assert fp_rate < 0.10, f"False positive rate {fp_rate:.1%} too high"
    
    def test_critical_findings_detected(self, batch_result):
        """
        Test: Critical severity findings should have high detection rate
        """
        critical_findings = []
        for result in batch_result.results:
            for finding in result.findings:
                if finding.severity.value == "CRITICAL":
                    critical_findings.append(finding)
        
        # Should detect at least some critical findings
        assert len(critical_findings) > 0, "Should detect critical severity issues"
    
    def test_scan_performance(self, batch_result):
        """
        Test: Average scan time should be reasonable
        """
        avg_time = batch_result.avg_scan_time_ms
        print(f"\nPerformance:")
        print(f"  Average scan time: {avg_time:.0f}ms per file")
        
        # Should complete in reasonable time (< 10 seconds per file on average)
        assert avg_time < 10000, f"Scan too slow: {avg_time:.0f}ms per file"


class TestYARACoverage:
    """Test YARA rule coverage"""
    
    def test_yara_rules_loaded(self):
        """Test YARA rules are properly loaded"""
        from lib.yara_engine import YaraEngine
        engine = YaraEngine()
        
        if engine.is_available():
            assert engine.rules is not None
    
    def test_attack_type_coverage(self):
        """Test coverage of different attack types"""
        from lib.yara_engine import YaraEngine
        
        sample_dir = Path(__file__).parent.parent.parent / "test_samples"
        if not sample_dir.exists():
            pytest.skip("Test samples not found")
        
        engine = YaraEngine()
        if not engine.is_available():
            pytest.skip("YARA not available")
        
        # Check different attack types are detected
        attack_types = set()
        for file in sample_dir.glob("*.py"):
            matches = engine.scan_file(str(file))
            for match in matches:
                attack_types.add(match.rule_name)
        
        # Should detect at least 5 different attack types
        assert len(attack_types) >= 5, f"Only detected {len(attack_types)} attack types"
        print(f"\nDetected attack types: {attack_types}")
