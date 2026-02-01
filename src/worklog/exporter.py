from typing import List, Dict
from .domain import Entry

def export_markdown(md_path: str, entries: List[Entry]) -> None:
    def fmt_activity(a: str) -> str:
        if "\n" not in a:
            return a.strip()
        lines = [x.strip() for x in a.splitlines() if x.strip()]
        return "\n".join([f"- {x}" for x in lines])

    tag_map: Dict[str, int] = {}
    total = 0

    for e in entries:
        total += e.minutes
        tags = [t.strip() for t in (e.tags or "").split(",") if t.strip()] or ["(sin tags)"]
        for t in tags:
            tag_map[t] = tag_map.get(t, 0) + e.minutes

    day = entries[0].date if entries else "N/A"

    lines: List[str] = []
    lines.append(f"# Worklog {day}")
    lines.append("")
    lines.append(f"**Total:** {total} min ({round(total/60, 2)} h)")
    lines.append("")
    lines.append("## Resumen por tags")

    if tag_map:
        for k, v in sorted(tag_map.items(), key=lambda kv: kv[1], reverse=True):
            lines.append(f"- **{k}**: {v} min ({round(v/60, 2)} h)")
    else:
        lines.append("- (sin registros)")

    lines.append("")
    lines.append("## Detalle cronológico")
    lines.append("")
    lines.append("| Inicio | Fin | Min | Actividad | Tags |")
    lines.append("|---|---|---:|---|---|")

    for e in entries:
        start = e.start.split("T")[1]
        end = e.end.split("T")[1]
        activity = fmt_activity(e.activity).replace("\n", "<br>")
        tags = (e.tags or "").replace("\n", " ")
        lines.append(f"| {start} | {end} | {e.minutes} | {activity} | {tags} |")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).strip() + "\n")
