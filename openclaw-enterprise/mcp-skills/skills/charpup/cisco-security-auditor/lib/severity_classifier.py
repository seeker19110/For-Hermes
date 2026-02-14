"""
Severity Classifier for vulnerability scoring
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .models import Finding, SeverityLevel

logger = logging.getLogger(__name__)


class SeverityClassifier:
    """Classify and score vulnerability severity"""
    
    # Default severity mapping
    DEFAULT_SEVERITY_MAP = {
        "remote_code_execution": {
            "severity": "CRITICAL",
            "score_range": [9.0, 10.0],
            "keywords": ["eval", "exec", "__import__", "subprocess.call", "os.system"]
        },
        "data_exfiltration": {
            "severity": "CRITICAL",
            "score_range": [9.0, 10.0],
            "keywords": ["requests.post", "urllib.request", "socket.send"]
        },
        "backdoor": {
            "severity": "CRITICAL",
            "score_range": [9.0, 10.0],
            "keywords": ["socket.bind", "socket.listen", "exec(command)"]
        },
        "privilege_escalation": {
            "severity": "HIGH",
            "score_range": [7.0, 8.9],
            "keywords": ["sudo", "su -", "chmod 777", "setuid", "chown root"]
        },
        "dependency_confusion": {
            "severity": "HIGH",
            "score_range": [7.0, 8.9],
            "keywords": ["internal", "private", "corp"]
        },
        "obfuscated_code": {
            "severity": "HIGH",
            "score_range": [7.0, 8.9],
            "keywords": ["base64.b64decode", "eval(compile", "exec(decode"]
        },
        "typosquatting": {
            "severity": "MEDIUM",
            "score_range": [4.0, 6.9],
            "keywords": ["reqests", "urllib", "josn"]
        },
        "suspicious_network": {
            "severity": "MEDIUM",
            "score_range": [4.0, 6.9],
            "keywords": ["requests.get", "urllib", "http.client"]
        },
        "information_disclosure": {
            "severity": "MEDIUM",
            "score_range": [4.0, 6.9],
            "keywords": ["print(password", "log.debug", "traceback.format_exc"]
        },
        "weak_crypto": {
            "severity": "MEDIUM",
            "score_range": [4.0, 6.9],
            "keywords": ["md5", "sha1", "DES", "RC4"]
        },
        "debug_code": {
            "severity": "LOW",
            "score_range": [1.0, 3.9],
            "keywords": ["print(", "console.log", "debugger"]
        },
        "test_files": {
            "severity": "LOW",
            "score_range": [1.0, 3.9],
            "keywords": ["test_", "_test.py", "mock"]
        },
        "style_issues": {
            "severity": "INFO",
            "score_range": [0, 0.9],
            "keywords": ["TODO", "FIXME", "HACK"]
        }
    }
    
    def __init__(self, severity_map_path: Optional[str] = None):
        """
        Initialize classifier
        
        Args:
            severity_map_path: Path to custom severity map JSON
        """
        self.severity_map = self.DEFAULT_SEVERITY_MAP.copy()
        
        if severity_map_path and Path(severity_map_path).exists():
            try:
                with open(severity_map_path, 'r') as f:
                    custom_map = json.load(f)
                    self.severity_map.update(custom_map)
                logger.info(f"Loaded custom severity map from {severity_map_path}")
            except Exception as e:
                logger.error(f"Failed to load severity map: {e}")
    
    def classify(self, finding: Finding) -> SeverityLevel:
        """
        Classify finding severity based on vulnerability type
        
        Args:
            finding: Security finding to classify
            
        Returns:
            SeverityLevel enum value
        """
        # Look up in severity map first
        vuln_type = finding.type.lower()
        
        for key, config in self.severity_map.items():
            if key.lower() in vuln_type or vuln_type in key.lower():
                return SeverityLevel(config["severity"])
        
        # Default classification based on keywords
        evidence = finding.evidence.lower()
        for key, config in self.severity_map.items():
            for keyword in config.get("keywords", []):
                if keyword.lower() in evidence:
                    return SeverityLevel(config["severity"])
        
        # Default to MEDIUM if unknown
        logger.debug(f"Unknown finding type '{finding.type}', defaulting to MEDIUM")
        return SeverityLevel.MEDIUM
    
    def calculate_confidence(self, finding: Finding) -> float:
        """
        Calculate confidence score for a finding
        
        Args:
            finding: Security finding
            
        Returns:
            Confidence score 0.0-1.0
        """
        base_confidence = finding.confidence
        
        # Boost confidence for clear patterns
        evidence = finding.evidence.lower()
        
        high_confidence_patterns = [
            "eval(", "exec(", "__import__", "os.system", "subprocess.call",
            "socket.bind", "requests.post", "urllib.request.urlopen"
        ]
        
        for pattern in high_confidence_patterns:
            if pattern in evidence:
                base_confidence = min(1.0, base_confidence + 0.1)
        
        return base_confidence
    
    def get_severity_score(self, severity: SeverityLevel) -> float:
        """Get numeric score for severity level"""
        scores = {
            SeverityLevel.CRITICAL: 9.5,
            SeverityLevel.HIGH: 8.0,
            SeverityLevel.MEDIUM: 5.5,
            SeverityLevel.LOW: 2.5,
            SeverityLevel.INFO: 0.5
        }
        return scores.get(severity, 5.0)
    
    def save_severity_map(self, path: str):
        """Save current severity map to file"""
        with open(path, 'w') as f:
            json.dump(self.severity_map, f, indent=2)
        logger.info(f"Saved severity map to {path}")
