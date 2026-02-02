import os
import csv
import json
import logging
from dataclasses import asdict
from typing import List
from .domain import Entry

logger = logging.getLogger(__name__)

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def paths_for_day(base_dir: str, day: str) -> dict:
    ensure_dir(base_dir)
    return {
        "jsonl": os.path.join(base_dir, f"{day}_worklog.jsonl"),
        "csv":   os.path.join(base_dir, f"{day}_worklog.csv"),
        "md":    os.path.join(base_dir, f"{day}_worklog.md"),
    }

def init_csv_if_needed(path: str) -> None:
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "start", "end", "minutes", "activity", "tags"])

def append_jsonl(path: str, entry: Entry) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")

def append_csv(path: str, entry: Entry) -> None:
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([entry.date, entry.start, entry.end, entry.minutes, entry.activity, entry.tags])

def read_jsonl(path: str) -> List[Entry]:
    if not os.path.exists(path):
        return []
    out: List[Entry] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                out.append(Entry(**d))
            except Exception:
                logger.warning("Invalid JSONL line ignored in %s", path)
                continue
    return out
