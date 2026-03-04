import json
import os

def _default_config():
    # Minimal safe defaults so the app won't crash if config.json is missing.
    # These values are placeholders and should be updated using the calibration tool.
    return {
        "light_roi": [0, 0, 50, 50],
        "lane_polygon": [[0, 0], [100, 0], [100, 100], [0, 100]],
        "stop_line": [[0, 0], [100, 0]],
        "violation_zone": [[0, 0], [100, 0], [100, 100], [0, 100]]
    }

def load_config(file_path="data/config.json"):
    # If config exists, load it. If not, create a default config file and return defaults.
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)

    # Create directories if needed and write default config
    default = _default_config()
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    try:
        with open(file_path, 'w') as f:
            json.dump(default, f, indent=4)
    except Exception:
        # If write fails, still return the defaults in-memory so the app can continue.
        pass
    return default

def save_config(data, file_path="data/config.json"):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)