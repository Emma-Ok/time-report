import os
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
from typing import Dict, List

from .storage import read_jsonl, read_csv, ensure_dir, paths_for_day, legacy_paths_for_day
from .domain import Entry
from .config import SummaryConfig


def _parse_iso_week(week: str, tz: ZoneInfo) -> tuple[date, date, str]:
    """
    Retorna (monday, sunday, label) para una semana ISO.
    - week = "current" o "YYYY-Www"
    """
    if week == "current":
        today = datetime.now(tz).date()
        iso_year, iso_week, _ = today.isocalendar()
    else:
        try:
            y_str, w_str = week.split("-W")
            iso_year = int(y_str)
            iso_week = int(w_str)
        except Exception:
            raise ValueError("Formato inválido para --week. Usa 'current' o 'YYYY-Www' (ej: 2026-W05).")

    monday = date.fromisocalendar(iso_year, iso_week, 1)
    sunday = date.fromisocalendar(iso_year, iso_week, 7)
    label = f"{iso_year}-W{iso_week:02d}"
    return monday, sunday, label


def _day_range(d1: date, d2: date) -> List[date]:
    out = []
    d = d1
    while d <= d2:
        out.append(d)
        d += timedelta(days=1)
    return out


def _collect_week_entries(base_dir: str, days: List[date]) -> List[Entry]:
    entries: List[Entry] = []
    for d in days:
        day_str = d.strftime("%Y-%m-%d")

        day_paths = paths_for_day(base_dir, day_str)
        jsonl_path = day_paths["jsonl"]
        day_entries = read_jsonl(jsonl_path)
        if day_entries:
            entries.extend(day_entries)
            continue

        csv_entries = read_csv(day_paths["csv"])
        if csv_entries:
            entries.extend(csv_entries)
            continue

        legacy_paths = legacy_paths_for_day(base_dir, day_str)
        legacy_jsonl_entries = read_jsonl(legacy_paths["jsonl"])
        if legacy_jsonl_entries:
            entries.extend(legacy_jsonl_entries)
            continue

        entries.extend(read_csv(legacy_paths["csv"]))
    return entries


def _summarize(entries: List[Entry]) -> dict:
    total_minutes = sum(e.minutes for e in entries)

    by_day: Dict[str, int] = {}
    by_tag: Dict[str, int] = {}

    for e in entries:
        by_day[e.date] = by_day.get(e.date, 0) + e.minutes
        tags = [t.strip() for t in (e.tags or "").split(",") if t.strip()] or ["(sin tags)"]
        for t in tags:
            by_tag[t] = by_tag.get(t, 0) + e.minutes

    return {
        "total_minutes": total_minutes,
        "by_day": dict(sorted(by_day.items())),
        "by_tag": dict(sorted(by_tag.items(), key=lambda kv: kv[1], reverse=True)),
    }


def _write_weekly_md(out_path: str, label: str, monday: date, sunday: date, entries: List[Entry], include_details: bool) -> None:
    s = _summarize(entries)
    total = s["total_minutes"]

    lines: List[str] = []
    lines.append(f"# Weekly Worklog {label}")
    lines.append("")
    lines.append(f"**Rango:** {monday} → {sunday}")
    lines.append(f"**Total:** {total} min ({round(total/60, 2)} h)")
    lines.append("")

    lines.append("## Totales por día")
    if s["by_day"]:
        for day, mins in s["by_day"].items():
            lines.append(f"- **{day}**: {mins} min ({round(mins/60, 2)} h)")
    else:
        lines.append("- (sin registros)")

    lines.append("")
    lines.append("## Totales por tags")
    if s["by_tag"]:
        for tag, mins in s["by_tag"].items():
            lines.append(f"- **{tag}**: {mins} min ({round(mins/60, 2)} h)")
    else:
        lines.append("- (sin registros)")

    if include_details:
        lines.append("")
        lines.append("## Detalle")
        lines.append("")
        lines.append("| Fecha | Inicio | Fin | Min | Actividad | Tags |")
        lines.append("|---|---|---|---:|---|---|")

        # Ordenar por (date, start)
        def key(e: Entry):
            return (e.date, e.start)

        for e in sorted(entries, key=key):
            start = e.start.split("T")[1]
            end = e.end.split("T")[1]
            act = (e.activity or "").replace("\n", "<br>")
            tags = (e.tags or "").replace("\n", " ")
            lines.append(f"| {e.date} | {start} | {end} | {e.minutes} | {act} | {tags} |")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).strip() + "\n")


def weekly_summary(cfg: SummaryConfig) -> None:
    tz = ZoneInfo(cfg.tz_name)
    monday, sunday, label = _parse_iso_week(cfg.week, tz)

    # Para tu caso laboral, puedes quedarte con L–V.
    # Aun así, el resumen lee toda la semana ISO (L–D). Si no hay logs sábado/domingo, da igual.
    days = _day_range(monday, sunday)

    entries = _collect_week_entries(cfg.base_dir, days)

    out_dir = os.path.join(cfg.base_dir, "worklog_md", "weekly")
    ensure_dir(out_dir)
    out_path = os.path.join(out_dir, f"{label}_summary.md")

    _write_weekly_md(out_path, label, monday, sunday, entries, cfg.include_details)

    print(f"✅ Weekly summary generado: {out_path}")
