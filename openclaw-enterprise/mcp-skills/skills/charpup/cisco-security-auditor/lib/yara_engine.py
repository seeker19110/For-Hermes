"""
YARA Rule Engine for pattern-based detection
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import yara
    YARA_AVAILABLE = True
except ImportError:
    YARA_AVAILABLE = False
    logging.warning("yara-python not installed. YARA detection disabled.")

logger = logging.getLogger(__name__)


class YaraMatch:
    """YARA rule match result"""
    def __init__(self, rule_name: str, namespace: str, tags: List[str], 
                 meta: Dict[str, Any], strings: List[tuple]):
        self.rule_name = rule_name
        self.namespace = namespace
        self.tags = tags
        self.meta = meta
        self.strings = strings


class YaraEngine:
    """YARA rule-based pattern detection engine"""
    
    # Default YARA rules for common attack patterns
    DEFAULT_RULES = '''
rule dependency_confusion {
    meta:
        description = "Detects potential dependency confusion attacks"
        severity = "HIGH"
        confidence = "85"
    strings:
        $import1 = /from\s+[a-z_][a-z0-9_]*\s+import/
        $import2 = /import\s+[a-z_][a-z0-9_]*/
        $internal = /(internal|corp|company|private)\s*[=:]/ nocase
        $external = /(requests|urllib|http\.client)/
    condition:
        ($import1 or $import2) and $internal and $external
}

rule privilege_escalation {
    meta:
        description = "Detects privilege escalation attempts"
        severity = "HIGH"
        confidence = "90"
    strings:
        $sudo = /sudo\s+[-a-zA-Z]*\s+/ nocase
        $su = /su\s+-\s*\w+/ nocase
        $chmod = /chmod\s+[0-9]*7[0-9]*/
        $chown = /chown\s+root/ nocase
        $setuid = /setuid\s*\(/ nocase
    condition:
        any of them
}

rule typosquatting {
    meta:
        description = "Detects potential typosquatting in imports"
        severity = "MEDIUM"
        confidence = "75"
    strings:
        $req_typo = /(reqests|reuqests|request|reqeust)/
        $url_typo = /(urrlib|urllib3|urlib)/
        $json_typo = /(jsob|josn|jsonn)/
    condition:
        any of them
}

rule data_exfiltration {
    meta:
        description = "Detects potential data exfiltration patterns"
        severity = "CRITICAL"
        confidence = "90"
    strings:
        $post_file = /post\s*\(\s*['"].*['"]\s*,.*\s*open\s*\(/
        $post_data = /(requests|urllib)\..*post.*data\s*=/
        $encode = /base64\.(b64encode|encode)/
        $encrypt = /(cryptography|Crypto|pycryptodome)/ nocase
    condition:
        ($post_file or $post_data) and ($encode or $encrypt)
}

rule obfuscated_code {
    meta:
        description = "Detects obfuscated or encoded code"
        severity = "HIGH"
        confidence = "80"
    strings:
        $base64_exec = /exec\s*\(\s*(base64|decode)/
        $eval_exec = /eval\s*\(\s*compile/
        $chr_obf = /(chr\s*\(\s*\d+\s*\)\s*\+?\s*){5,}/
        $hex_obf = /\\\\x[a-f0-9]{2}/
    condition:
        any of them
}

rule backdoor_shell {
    meta:
        description = "Detects potential backdoor or shell patterns"
        severity = "CRITICAL"
        confidence = "95"
    strings:
        $socket_bind = /socket\..*bind.*0\.0\.0\.0/
        $socket_listen = /socket\..*listen/
        $exec_cmd = /os\.system\s*\(\s*request/ nocase
        $shell_exec = /(subprocess|os\.popen).*shell\s*=\s*True/
        $reverse_shell = /socket\..*connect.*\(\s*['\"]\d+\.\d+\.\d+\.\d+['\"]/
        $socket_accept = /socket.*accept\s*\(/
    condition:
        any of them
}

rule remote_code_execution {
    meta:
        description = "Detects remote code execution vulnerabilities"
        severity = "CRITICAL"
        confidence = "90"
    strings:
        $eval_input = /eval\s*\(\s*\w*\s*\)/
        $eval_user = /eval\s*\(\s*.*user/ nocase
        $exec_input = /exec\s*\(\s*\w*\s*\)/
        $os_system = /os\.system\s*\(/ nocase
        $subprocess_call = /subprocess\.call\s*\(/ nocase
    condition:
        any of them
}

rule base64_obfuscation {
    meta:
        description = "Detects base64 obfuscation patterns"
        severity = "HIGH"
        confidence = "85"
    strings:
        $base64_decode = /base64\.b64decode/
        $exec_decode = /exec\s*\(.*base64/
        $eval_decode = /eval\s*\(.*base64/
        $compile_decode = /compile\s*\(.*b64decode/
    condition:
        any of them
}

rule suspicious_network {
    meta:
        description = "Detects suspicious network activity"
        severity = "MEDIUM"
        confidence = "75"
    strings:
        $ip_pattern = /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/
        $suspicious_domain = /(pastebin|gist\.github|transfer\.sh)/ nocase
        $user_agent = /User-Agent.*python/i
    condition:
        2 of them
}
'''

    def __init__(self, rules_path: Optional[str] = None):
        """Initialize YARA engine with rules"""
        self.rules = None
        self.rules_path = rules_path
        
        if not YARA_AVAILABLE:
            logger.error("YARA not available. Install with: pip install yara-python")
            return
            
        self._load_rules()
    
    def _load_rules(self):
        """Load YARA rules from file or use defaults"""
        try:
            if self.rules_path and os.path.exists(self.rules_path):
                self.rules = yara.compile(filepath=self.rules_path)
                logger.info(f"Loaded YARA rules from {self.rules_path}")
            else:
                self.rules = yara.compile(source=self.DEFAULT_RULES)
                logger.info("Loaded default YARA rules")
        except Exception as e:
            logger.error(f"Failed to load YARA rules: {e}")
            try:
                self.rules = yara.compile(source=self.DEFAULT_RULES)
            except Exception as e2:
                logger.error(f"Failed to load default rules: {e2}")
    
    def scan_file(self, file_path: str) -> List[YaraMatch]:
        """
        Scan a file against YARA rules
        
        Args:
            file_path: Path to file to scan
            
        Returns:
            List of YaraMatch objects
        """
        if not YARA_AVAILABLE or self.rules is None:
            logger.warning("YARA not available, skipping scan")
            return []
        
        try:
            matches = self.rules.match(file_path)
            results = []
            
            for match in matches:
                # Handle string matches properly
                string_matches = []
                for s in match.strings:
                    # s is a StringMatch object with identifier, instances attributes
                    for instance in s.instances:
                        string_matches.append((s.identifier, instance.offset, instance.matched_length))
                
                yara_match = YaraMatch(
                    rule_name=match.rule,
                    namespace=match.namespace,
                    tags=list(match.tags),
                    meta=dict(match.meta),
                    strings=string_matches
                )
                results.append(yara_match)
            
            logger.debug(f"YARA scan found {len(results)} matches in {file_path}")
            return results
            
        except Exception as e:
            logger.error(f"YARA scan failed for {file_path}: {e}")
            return []
    
    def scan_data(self, data: bytes) -> List[YaraMatch]:
        """
        Scan data against YARA rules
        
        Args:
            data: Bytes to scan
            
        Returns:
            List of YaraMatch objects
        """
        if not YARA_AVAILABLE or self.rules is None:
            return []
        
        try:
            matches = self.rules.match(data=data)
            results = []
            
            for match in matches:
                # Handle string matches properly
                string_matches = []
                for s in match.strings:
                    for instance in s.instances:
                        string_matches.append((s.identifier, instance.offset, instance.matched_length))
                
                yara_match = YaraMatch(
                    rule_name=match.rule,
                    namespace=match.namespace,
                    tags=list(match.tags),
                    meta=dict(match.meta),
                    strings=string_matches
                )
                results.append(yara_match)
            
            return results
            
        except Exception as e:
            logger.error(f"YARA data scan failed: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if YARA engine is available"""
        return YARA_AVAILABLE and self.rules is not None
