"""Clean utility module."""
import json
import logging
from typing import Dict

def process(data: Dict) -> str:
    """Process data."""
    return json.dumps(data)