"""
Integration tests for Security Auditor
"""

import os
import sys
import json
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib import SecurityAuditor, BatchScanner, ScanOptions, SeverityLevel


class TestSecurityAuditor:
    """Integration tests for SecurityAuditor"""
    
    @pytest.fixture
    def auditor(self):
        """Create auditor instance"""
        return SecurityAuditor()
    
    @pytest.fixture
    def sample_dir(self):
        """Get test samples directory"""
        return Path(__file__).parent.parent.parent / "test_samples"
    
    def test_scan_nonexistent_file(self, auditor):
        """Test scanning non-existent file raises error"""
        with pytest.raises(FileNotFoundError):
            auditor.scan("/nonexistent/file.py")
    
    def test_scan_single_file(self, auditor, sample_dir):
        """Test scanning a single malicious file"""
        test_file = sample_dir / "backdoor_001.py"
        if test_file.exists():
            result = auditor.scan(str(test_file))
            assert result.target == str(test_file)
            assert isinstance(result.findings, list)
            assert result.scan_time_ms >= 0
    
    def test_scan_with_yara_only(self, auditor, sample_dir):
        """Test scanning with only YARA enabled"""
        test_file = sample_dir / "backdoor_001.py"
        if test_file.exists():
            options = ScanOptions(use_yara=True, use_llm=False)
            result = auditor.scan(str(test_file), options)
            assert "yara" in result.engines_used or result.engines_used == []
    
    def test_deduplication(self, auditor):
        """Test finding deduplication"""
        from lib.models import Finding
        findings = [
            Finding("1", "test", SeverityLevel.HIGH, 0.8, "same", "file.py"),
            Finding("2", "test", SeverityLevel.HIGH, 0.8, "same", "file.py"),
        ]
        unique = auditor._deduplicate_findings(findings)
        assert len(unique) == 1


class TestBatchScanner:
    """Integration tests for BatchScanner"""
    
    @pytest.fixture
    def scanner(self):
        """Create batch scanner"""
        return BatchScanner()
    
    @pytest.fixture
    def sample_dir(self):
        """Get test samples directory"""
        return Path(__file__).parent.parent.parent / "test_samples"
    
    def test_scan_directory(self, scanner, sample_dir):
        """Test batch scanning directory"""
        if sample_dir.exists():
            result = scanner.scan_directory(str(sample_dir))
            assert result.total_samples > 0
            assert result.scanned_samples > 0
            assert 0 <= result.detection_rate <= 1
    
    def test_scan_nonexistent_directory(self, scanner):
        """Test scanning non-existent directory"""
        with pytest.raises(FileNotFoundError):
            scanner.scan_directory("/nonexistent/dir")
    
    def test_batch_metrics_calculation(self, scanner, sample_dir):
        """Test metrics calculation with ground truth"""
        if sample_dir.exists():
            gt_path = sample_dir / "ground_truth.json"
            ground_truth = {}
            if gt_path.exists():
                with open(gt_path) as f:
                    ground_truth = json.load(f)
            
            result = scanner.scan_directory(str(sample_dir), ground_truth=ground_truth)
            metrics = result.calculate_metrics()
            
            assert "precision" in metrics
            assert "recall" in metrics
            assert 0 <= metrics["precision"] <= 1
            assert 0 <= metrics["recall"] <= 1
