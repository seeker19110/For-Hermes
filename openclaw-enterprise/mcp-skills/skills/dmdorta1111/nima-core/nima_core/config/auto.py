"""Auto-detection and configuration for OpenClaw integration."""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any


def detect_openclaw() -> Optional[Dict[str, Any]]:
    """Detect if running in OpenClaw environment.
    
    Returns:
        Dict with OpenClaw config if detected, None otherwise
    """
    # Check for OpenClaw config file
    home = Path.home()
    openclaw_config = home / ".openclaw" / "openclaw.json"
    
    if openclaw_config.exists():
        try:
            with open(openclaw_config) as f:
                config = json.load(f)
            return {
                "detected": True,
                "config_path": str(openclaw_config),
                "workspace": config.get("workspace", str(home / ".openclaw" / "workspace")),
                "version": config.get("version", "unknown")
            }
        except (OSError, json.JSONDecodeError) as e:
            print(f"Warning: OpenClaw config found but couldn't parse: {e}")
            return None
    
    # Check for workspace env var
    workspace = os.getenv("OPENCLAW_WORKSPACE")
    if workspace:
        return {
            "detected": True,
            "workspace": workspace,
            "source": "environment"
        }
    
    return None


def get_nima_config() -> Dict[str, Any]:
    """Get NIMA configuration with auto-detection.
    
    Returns:
        Complete NIMA config with paths resolved
    """
    openclaw = detect_openclaw()
    
    if openclaw:
        # Running in OpenClaw - use workspace paths
        workspace = Path(openclaw["workspace"]).expanduser().resolve()
        return {
            "mode": "openclaw",
            "data_dir": str(workspace / "nima_data"),
            "models_dir": str(workspace / "nima_models"),
            "openclaw": openclaw
        }
    else:
        # Standalone mode - use user home
        nima_home = Path.home() / ".nima"
        nima_home.mkdir(exist_ok=True)
        return {
            "mode": "standalone",
            "data_dir": str(nima_home / "data"),
            "models_dir": str(nima_home / "models"),
            "openclaw": None
        }


def setup_paths(config: Dict[str, Any]) -> None:
    """Create necessary directories from config.
    
    Args:
        config: Config dict from get_nima_config()
    """
    for key in ["data_dir", "models_dir"]:
        path = Path(config[key])
        path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        if key == "data_dir":
            (path / "sessions").mkdir(exist_ok=True)
            (path / "schemas").mkdir(exist_ok=True)
            (path / "cache").mkdir(exist_ok=True)
