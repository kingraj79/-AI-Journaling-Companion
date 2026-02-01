# storage.py
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

# Folder + file where data lives
DATA_DIR = Path(__file__).parent / "data"
DATA_FILE = DATA_DIR / "goalbot.json"


def now_ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _default_data() -> dict:
    return {
        "goals": [
            {"name": "Improve sleep routine", "status": "active"},
            {"name": "Exercise consistently", "status": "active"},
            {"name": "Reduce work stress", "status": "active"},
            {"name": "Learn a new skill", "status": "active"},
            {"name": "Practice mindfulness", "status": "active"},
        ],
        "updates": [],
        "ai_events": []
    }


def _ensure_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps(_default_data(), indent=2), encoding="utf-8")


def load_data() -> dict:
    """
    Safe loader:
    - Creates file if missing
    - If file exists but is empty/corrupt, resets to defaults
    """
    _ensure_file()
    raw = DATA_FILE.read_text(encoding="utf-8").strip()

    if not raw:
        data = _default_data()
        save_data(data)
        return data

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # backup corrupt file
        backup = DATA_DIR / f"goalbot_corrupt_{now_ts().replace(':','-')}.json"
        DATA_FILE.replace(backup)
        data = _default_data()
        save_data(data)
        return data

    # Ensure required keys exist
    data.setdefault("goals", [])
    data.setdefault("updates", [])
    data.setdefault("ai_events", [])
    return data


def save_data(data: dict) -> None:
    """
    Safe writer (atomic):
    Write to a temp file then replace the real file.
    Prevents half-written JSON if app stops mid-write.
    """
    _ensure_file()
    tmp = DATA_DIR / "goalbot.tmp.json"
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(DATA_FILE)
