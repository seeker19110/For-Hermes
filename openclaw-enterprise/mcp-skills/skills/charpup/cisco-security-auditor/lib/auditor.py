"""
Main Security Auditor orchestrator
"""

import os
import time
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from .models import Finding, ScanResult, ScanOptions, SeverityLevel
from .yara_engine import YaraEngine
from .llm_analyzer import LLMSemanticAnalyzer
from .severity_classifier import SeverityClassifier

logger = logging.getLogger(__name__)


class SecurityAuditor:
    """Main security auditing orchestrator"""
    
    def __init__(self, 
                 yara_rules_path: Optional[str] = None,
                 severity_map_path: Optional[str] = None,
                 llm_api_key: Optional[str] = None):
        """
        Initialize security auditor
        
        Args:
            yara_rules_path: Path to YARA rules file
            severity_map_path: Path to severity map JSON
            llm_api_key: API key for LLM analysis
        """
        self.yara_engine = YaraEngine(yara_rules_path)
        self.llm_analyzer = LLMSemanticAnalyzer(llm_api_key)
        self.severity_classifier = SeverityClassifier(severity_map_path)
        
        logger.info("SecurityAuditor initialized")
        logger.info(f"  - YARA available: {self.yara_engine.is_available()}")
        logger.info(f"  - LLM available: {self.llm_analyzer.is_available()}")
    
    def scan(self, target: str, options: Optional[ScanOptions] = None) -> ScanResult:
        """
        Scan a target for security issues
        
        Args:
            target: Path to file or directory to scan
            options: Scan configuration options
            
        Returns:
            ScanResult with findings
        """
        options = options or ScanOptions()
        start_time = time.time()
        
        if not os.path.exists(target):
            raise FileNotFoundError(f"Target not found: {target}")
        
        findings = []
        engines_used = []
        
        # YARA scan
        if options.use_yara and self.yara_engine.is_available():
            logger.info("Running YARA scan...")
            engines_used.append("yara")
            yara_findings = self._scan_with_yara(target)
            findings.extend(yara_findings)
        
        # LLM semantic analysis
        if options.use_llm and self.llm_analyzer.is_available():
            logger.info("Running LLM semantic analysis...")
            engines_used.append("llm")
            llm_findings = self._scan_with_llm(target)
            findings.extend(llm_findings)
        
        # Deduplicate findings
        findings = self._deduplicate_findings(findings)
        
        # Filter by confidence threshold
        findings = [f for f in findings if f.confidence >= options.confidence_threshold]
        
        # Filter by severity if specified
        if options.severity_filter:
            findings = [f for f in findings if f.severity in options.severity_filter]
        
        scan_time_ms = int((time.time() - start_time) * 1000)
        
        return ScanResult(
            target=target,
            findings=findings,
            scan_time_ms=scan_time_ms,
            engines_used=engines_used
        )
    
    def _scan_with_yara(self, target: str) -> List[Finding]:
        """Scan with YARA engine"""
        findings = []
        
        if os.path.isfile(target):
            matches = self.yara_engine.scan_file(target)
            for match in matches:
                meta = match.meta
                severity_str = meta.get("severity", "MEDIUM")
                confidence = float(meta.get("confidence", 0.7))
                
                finding = Finding(
                    rule_id=f"yara:{match.rule_name}",
                    type=match.rule_name,
                    severity=SeverityLevel(severity_str),
                    confidence=confidence,
                    evidence=str(match.strings[:3]) if match.strings else "Pattern match",
                    file_path=target,
                    description=meta.get("description", f"YARA rule: {match.rule_name}"),
                    remediation=f"Review {match.rule_name} pattern"
                )
                findings.append(finding)
        else:
            # Scan directory recursively
            for root, _, files in os.walk(target):
                for file in files:
                    if file.endswith(('.py', '.js', '.yaml', '.yml', '.json')):
                        file_path = os.path.join(root, file)
                        matches = self.yara_engine.scan_file(file_path)
                        for match in matches:
                            meta = match.meta
                            finding = Finding(
                                rule_id=f"yara:{match.rule_name}",
                                type=match.rule_name,
                                severity=SeverityLevel(meta.get("severity", "MEDIUM")),
                                confidence=float(meta.get("confidence", 0.7)),
                                evidence=str(match.strings[:3]) if match.strings else "Pattern match",
                                file_path=file_path,
                                description=meta.get("description", f"YARA rule: {match.rule_name}")
                            )
                            findings.append(finding)
        
        return findings
    
    def _scan_with_llm(self, target: str) -> List[Finding]:
        """Scan with LLM semantic analyzer"""
        findings = []
        
        if os.path.isfile(target):
            try:
                with open(target, 'r', encoding='utf-8', errors='ignore') as f:
                    code = f.read()
                
                result = self.llm_analyzer.analyze(code, {"filename": os.path.basename(target)})
                
                if result.malicious and result.confidence >= 0.7:
                    finding = Finding(
                        rule_id=f"llm:{result.intent}",
                        type=result.intent,
                        severity=self._severity_from_intent(result.intent),
                        confidence=result.confidence,
                        evidence=result.indicators[0] if result.indicators else "LLM detected malicious intent",
                        file_path=target,
                        description=result.reasoning,
                        remediation="Review code for security issues"
                    )
                    findings.append(finding)
            except Exception as e:
                logger.error(f"LLM scan failed for {target}: {e}")
        else:
            # Scan directory
            for root, _, files in os.walk(target):
                for file in files:
                    if file.endswith(('.py', '.js')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                code = f.read()
                            
                            result = self.llm_analyzer.analyze(code, {"filename": file})
                            
                            if result.malicious and result.confidence >= 0.7:
                                finding = Finding(
                                    rule_id=f"llm:{result.intent}",
                                    type=result.intent,
                                    severity=self._severity_from_intent(result.intent),
                                    confidence=result.confidence,
                                    evidence=result.indicators[0] if result.indicators else "LLM detected malicious intent",
                                    file_path=file_path,
                                    description=result.reasoning
                                )
                                findings.append(finding)
                        except Exception as e:
                            logger.error(f"LLM scan failed for {file_path}: {e}")
        
        return findings
    
    def _deduplicate_findings(self, findings: List[Finding]) -> List[Finding]:
        """Remove duplicate findings"""
        seen = set()
        unique = []
        
        for finding in findings:
            key = (finding.file_path, finding.type, finding.evidence[:50])
            if key not in seen:
                seen.add(key)
                unique.append(finding)
        
        return unique
    
    def _severity_from_intent(self, intent: str) -> SeverityLevel:
        """Map LLM intent to severity level"""
        critical_intents = ["backdoor", "data_exfiltration", "remote_code_execution", "rce"]
        high_intents = ["privilege_escalation", "obfuscated_code", "malicious"]
        
        intent_lower = intent.lower()
        
        if any(i in intent_lower for i in critical_intents):
            return SeverityLevel.CRITICAL
        elif any(i in intent_lower for i in high_intents):
            return SeverityLevel.HIGH
        else:
            return SeverityLevel.MEDIUM
