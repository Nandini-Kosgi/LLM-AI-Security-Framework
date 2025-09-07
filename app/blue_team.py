import os, json, time
from typing import Dict, Any
from pathlib import Path

LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
REQ_LOG = LOG_DIR / "requests.log"
SEC_LOG = LOG_DIR / "security.log"

def _write_jsonl(path: Path, obj: Dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def anomaly_score(payload: Dict[str, Any]) -> float:
    """Very simple heuristic score you can replace with ML/embeddings later."""
    score = 0.0
    if payload.get("pre_hits"): score += 0.5
    if payload.get("post_hits"): score += 0.5
    return min(score, 1.0)

def log_request(event: Dict[str, Any]) -> None:
    event["ts"] = time.time()
    _write_jsonl(REQ_LOG, event)

def log_security(event: Dict[str, Any]) -> None:
    event["ts"] = time.time()
    event["score"] = anomaly_score(event)
    _write_jsonl(SEC_LOG, event)
