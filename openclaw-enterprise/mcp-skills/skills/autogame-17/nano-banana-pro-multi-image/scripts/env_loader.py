
import os

def load_env_file(filepath=".env"):
    """Simple .env parser using standard library"""
    try:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    os.environ[key] = value
    except FileNotFoundError:
        pass

# Try to load .env from current directory or parent directories
current_dir = os.getcwd()
while True:
    env_path = os.path.join(current_dir, ".env")
    if os.path.exists(env_path):
        load_env_file(env_path)
        break
    parent_dir = os.path.dirname(current_dir)
    if parent_dir == current_dir:
        break
    current_dir = parent_dir
