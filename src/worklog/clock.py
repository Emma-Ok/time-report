from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

@dataclass(frozen=True)
class WorkWindow:
    start_h: int
    start_m: int
    end_h: int
    end_m: int

def parse_hhmm(value: str) -> tuple[int, int]:
    try:
        h, m = map(int, value.split(":"))
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError
        return h, m
    except Exception:
        raise ValueError(f"Formato inválido '{value}'. Usa HH:MM (ej: 07:00).")

def now(tz: ZoneInfo) -> datetime:
    return datetime.now(tz)

def iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")

def is_work_time(dt: datetime, w: WorkWindow) -> bool:
    # Lunes=0 ... Domingo=6
    if dt.weekday() >= 5:
        return False
    start = dt.replace(hour=w.start_h, minute=w.start_m, second=0, microsecond=0)
    end = dt.replace(hour=w.end_h, minute=w.end_m, second=0, microsecond=0)
    return start <= dt < end

def next_work_start(dt: datetime, w: WorkWindow) -> datetime:
    candidate = dt.replace(hour=w.start_h, minute=w.start_m, second=0, microsecond=0)
    if dt < candidate and dt.weekday() < 5:
        return candidate

    d = dt
    while True:
        d = (d + timedelta(days=1)).replace(hour=w.start_h, minute=w.start_m, second=0, microsecond=0)
        if d.weekday() < 5:
            return d

def seconds_until(target: datetime, tz: ZoneInfo) -> int:
    s = int((target - now(tz)).total_seconds())
    return max(0, s)
