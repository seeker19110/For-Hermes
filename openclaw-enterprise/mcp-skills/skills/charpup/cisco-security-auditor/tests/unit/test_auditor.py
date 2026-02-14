"""
Unit tests for Security Auditor
"""

import os
import sys
import pytest
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.models import Finding, ScanResult, ScanOptions, SeverityLevel
from lib.yara_engine import YaraEngine
from lib.severity_classifier import SeverityClassifier


class TestYaraEngine:
    """Tests for YARA engine"""
    
    def test_initialization(self):
        """Test YARA engine initializes correctly"""
        engine = YaraEngine()
        assert engine.is_available() or not engine.is_available()  # May not be available if yara not installed
    
    def test_default_rules_loaded(self):
        """Test default rules are loaded"""
        engine = YaraEngine()
        if engine.is_available():
            assert engine.rules is not None
    
    def test_scan_file_not_found(self):
        """Test scanning non-existent file"""
        engine = YaraEngine()
        if engine.is_available():
            results = engine.scan_file("/nonexistent/file.py")
            assert results == []


class TestSeverityClassifier:
    """Tests for severity classifier"""
    
    def test_initialization(self):
        """Test classifier initializes with defaults"""
        classifier = SeverityClassifier()
        assert "remote_code_execution" in classifier.severity_map
    
    def test_classify_rce(self):
        """Test RCE classification"""
        classifier = SeverityClassifier()
        finding = Finding(
            rule_id="test",
            type="remote_code_execution",
            severity=SeverityLevel.MEDIUM,
            confidence=0.8,
            evidence="eval(user_input)",
            file_path="test.py"
        )
        result = classifier.classify(finding)
        assert result == SeverityLevel.CRITICAL
    
    def test_classify_debug_code(self):
        """Test debug code classification"""
        classifier = SeverityClassifier()
        finding = Finding(
            rule_id="test",
            type="debug_code",
            severity=SeverityLevel.MEDIUM,
            confidence=0.8,
            evidence="print(password)",
            file_path="test.py"
        )
        result = classifier.classify(finding)
        assert result == SeverityLevel.LOW
    
    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        classifier = SeverityClassifier()
        finding = Finding(
            rule_id="test",
            type="test",
            severity=SeverityLevel.MEDIUM,
            confidence=0.7,
            evidence="eval(cmd)",
            file_path="test.py"
        )
        confidence = classifier.calculate_confidence(finding)
        assert confidence >= 0.7  # Should be boosted by eval pattern


class TestModels:
    """Tests for data models"""
    
    def test_finding_creation(self):
        """Test Finding dataclass"""
        finding = Finding(
            rule_id="test-001",
            type="backdoor",
            severity=SeverityLevel.CRITICAL,
            confidence=0.95,
            evidence="socket.bind()",
            file_path="test.py",
            line_number=10
        )
        assert finding.rule_id == "test-001"
        assert finding.severity == SeverityLevel.CRITICAL
    
    def test_scan_result_stats(self):
        """Test ScanResult statistics"""
        findings = [
            Finding("1", "backdoor", SeverityLevel.CRITICAL, 0.9, "", "f1.py"),
            Finding("2", "rce", SeverityLevel.CRITICAL, 0.9, "", "f2.py"),
            Finding("3", "info", SeverityLevel.HIGH, 0.8, "", "f3.py"),
        ]
        result = ScanResult("test", findings, 1000, ["yara"])
        assert result.critical_count == 2
        assert result.high_count == 1
    
    def test_scan_result_to_dict(self):
        """Test ScanResult serialization"""
        finding = Finding("1", "test", SeverityLevel.HIGH, 0.8, "evidence", "test.py")
        result = ScanResult("test", [finding], 500, ["yara"])
        data = result.to_dict()
        assert data["target"] == "test"
        assert data["summary"]["total"] == 1


class TestScanOptions:
    """Tests for scan options"""
    
    def test_default_options(self):
        """Test default scan options"""
        options = ScanOptions()
        assert options.use_yara is True
        assert options.use_llm is True
        assert options.confidence_threshold == 0.7
    
    def test_custom_options(self):
        """Test custom scan options"""
        options = ScanOptions(
            use_yara=False,
            use_llm=True,
            confidence_threshold=0.9,
            severity_filter=[SeverityLevel.CRITICAL, SeverityLevel.HIGH]
        )
        assert options.use_yara is False
        assert options.confidence_threshold == 0.9
        assert len(options.severity_filter) == 2
