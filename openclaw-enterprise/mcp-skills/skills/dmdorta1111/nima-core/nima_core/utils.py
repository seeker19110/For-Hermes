"""
NIMA Core Utilities
====================
Shared helpers used across the package.

Author: NIMA Project
"""

import os
import json
import tempfile
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


def atomic_torch_save(data: Any, path: Path) -> None:
    """
    Atomically save data via torch.save.
    
    Writes to a temp file first, then does os.replace() which is
    atomic on POSIX. Prevents corruption if process dies mid-write.
    
    Args:
        data: Object to save
        path: Target file path
    """
    import torch
    
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        os.close(fd)
        torch.save(data, tmp_path)
        os.replace(tmp_path, path)
    except Exception:
        # Clean up temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def safe_torch_load(path: Path, device: str = 'cpu') -> Any:
    """
    Safely load a torch checkpoint file.
    
    Centralizes the weights_only=False pattern with logging.
    NIMA stores dicts with metadata (not just tensors), so weights_only=True
    would break. Only load files YOU created — never untrusted external data.
    
    Args:
        path: Path to .pt file
        device: Device to map tensors to (default 'cpu')
        
    Returns:
        Loaded checkpoint data
        
    Raises:
        FileNotFoundError: If path doesn't exist
        RuntimeError: If file is corrupted
    """
    import torch
    
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {path}")
    
    try:
        # weights_only=False: NIMA checkpoints contain dicts with metadata
        # (timestamps, config, string labels) alongside tensors.
        # SECURITY: Only load files from NIMA's own data directory.
        data = torch.load(path, map_location=device, weights_only=False)
        return data
    except Exception as e:
        logger.error(f"Failed to load checkpoint {path}: {e}")
        raise


def atomic_json_save(data: Dict, path: Path, indent: int = 2) -> None:
    """
    Atomically save JSON data.
    
    Writes to a temp file first, then does os.replace().
    
    Args:
        data: Dict to serialize
        path: Target file path
        indent: JSON indentation
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, indent=indent)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
