from dataclasses import dataclass

@dataclass(frozen=True)
class Entry:
    date: str       # YYYY-MM-DD
    start: str      # ISO local
    end: str        # ISO local
    minutes: int
    activity: str
    tags: str
