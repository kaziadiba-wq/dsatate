"""Weak-points log. Every miss is saved by tier + topic so sessions start on what you're worst at."""
import json
import time
from pathlib import Path

FILE = Path(__file__).with_name("progress.json")


def _load() -> dict:
    try:
        return json.loads(FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {"attempts": []}


def record(tier: int, topic: str, correct: bool, note: str = "", seconds: float | None = None) -> dict:
    data = _load()
    data["attempts"].append({"t": time.time(), "tier": tier, "topic": topic,
                             "correct": correct, "note": note, "seconds": seconds})
    FILE.write_text(json.dumps(data, indent=1))
    return {"saved": True}


def weak_points(tier: int | None = None, top: int = 5) -> list[dict]:
    """Topics ranked by miss rate (needs 1+ attempt). Recent misses count double."""
    stats: dict[str, dict] = {}
    attempts = [a for a in _load()["attempts"] if tier is None or a["tier"] == tier]
    for i, a in enumerate(attempts):
        w = 2 if i >= len(attempts) - 20 else 1
        s = stats.setdefault(f'T{a["tier"]}:{a["topic"]}', {"miss": 0, "n": 0, "notes": []})
        s["n"] += w
        if not a["correct"]:
            s["miss"] += w
            if a["note"]:
                s["notes"].append(a["note"])
    ranked = sorted(stats.items(), key=lambda kv: kv[1]["miss"] / kv[1]["n"], reverse=True)
    return [{"topic": k, "miss_rate": round(v["miss"] / v["n"], 2), "recent_notes": v["notes"][-3:]}
            for k, v in ranked[:top]]
