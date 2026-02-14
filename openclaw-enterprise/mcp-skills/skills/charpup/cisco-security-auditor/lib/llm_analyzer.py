"""
LLM Semantic Analyzer for intent-based detection
"""

import os
import json
import logging
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import requests

logger = logging.getLogger(__name__)


@dataclass
class SemanticResult:
    """LLM semantic analysis result"""
    malicious: bool
    intent: str
    confidence: float
    reasoning: str
    attack_chain: List[str]
    indicators: List[str]


class LLMSemanticAnalyzer:
    """LLM-based semantic intent analysis engine"""
    
    DEFAULT_MODEL = "kimi-k2.5"
    API_ENDPOINT = "https://api.moonshot.cn/v1/chat/completions"
    
    SYSTEM_PROMPT = """You are a security code analyzer specializing in identifying malicious intent in Python code.
Analyze the provided code for:
1. Malicious intent (data exfiltration, backdoors, privilege escalation, etc.)
2. Obfuscation or evasion techniques
3. Suspicious network activity
4. Unauthorized access attempts

Respond ONLY with a JSON object in this exact format:
{
    "malicious": true/false,
    "intent": "brief description of intent (e.g., 'data_exfiltration', 'backdoor', 'none')",
    "confidence": 0.0-1.0,
    "reasoning": "detailed explanation of why this code is or isn't malicious",
    "attack_chain": ["step1", "step2", ...],
    "indicators": ["indicator1", "indicator2", ...]
}

Rules:
- Be strict: flag only clear security issues
- Confidence > 0.8 for clear malicious patterns
- Confidence 0.5-0.8 for suspicious but ambiguous patterns
- Confidence < 0.5 for likely benign code
- Consider context and common coding patterns
"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, 
                 timeout: int = 5000):
        """
        Initialize LLM analyzer
        
        Args:
            api_key: Moonshot API key (defaults to MOONSHOT_API_KEY env var)
            model: Model to use (defaults to kimi-k2.5)
            timeout: API timeout in milliseconds
        """
        self.api_key = api_key or os.getenv("MOONSHOT_API_KEY")
        self.model = model or os.getenv("LLM_MODEL", self.DEFAULT_MODEL)
        self.timeout = timeout / 1000  # Convert to seconds
        
        if not self.api_key:
            logger.warning("No API key provided. LLM analysis will be unavailable.")
    
    def is_available(self) -> bool:
        """Check if LLM analyzer is available"""
        return self.api_key is not None
    
    def analyze(self, code: str, context: Optional[Dict[str, Any]] = None) -> SemanticResult:
        """
        Analyze code for malicious intent using LLM
        
        Args:
            code: Source code to analyze
            context: Additional context (filename, etc.)
            
        Returns:
            SemanticResult with analysis results
        """
        if not self.is_available():
            logger.warning("LLM not available, returning default result")
            return SemanticResult(
                malicious=False,
                intent="unknown",
                confidence=0.0,
                reasoning="LLM analysis unavailable",
                attack_chain=[],
                indicators=[]
            )
        
        try:
            # Prepare prompt
            filename = context.get("filename", "unknown") if context else "unknown"
            prompt = f"""File: {filename}

```python
{code}
```

Analyze this code for security issues."""

            # Make API request
            response = requests.post(
                self.API_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"}
                },
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Parse result
            content = data["choices"][0]["message"]["content"]
            result = json.loads(content)
            
            return SemanticResult(
                malicious=result.get("malicious", False),
                intent=result.get("intent", "unknown"),
                confidence=result.get("confidence", 0.0),
                reasoning=result.get("reasoning", ""),
                attack_chain=result.get("attack_chain", []),
                indicators=result.get("indicators", [])
            )
            
        except requests.exceptions.Timeout:
            logger.error("LLM API timeout")
            return self._fallback_result("API timeout")
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM API request failed: {e}")
            return self._fallback_result(f"API error: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return self._fallback_result("Parse error")
        except Exception as e:
            logger.error(f"Unexpected error in LLM analysis: {e}")
            return self._fallback_result(f"Error: {e}")
    
    def _fallback_result(self, reason: str) -> SemanticResult:
        """Create fallback result when LLM fails"""
        return SemanticResult(
            malicious=False,
            intent="unknown",
            confidence=0.0,
            reasoning=f"LLM analysis failed: {reason}",
            attack_chain=[],
            indicators=[]
        )
    
    def analyze_batch(self, codes: List[tuple]) -> List[SemanticResult]:
        """
        Analyze multiple code snippets
        
        Args:
            codes: List of (code, context) tuples
            
        Returns:
            List of SemanticResult
        """
        results = []
        for code, context in codes:
            result = self.analyze(code, context)
            results.append(result)
        return results
