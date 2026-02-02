from dataclasses import dataclass
import argparse

@dataclass(frozen=True)
class RunConfig:
    minutes: int
    base_dir: str
    start: str
    end: str
    tags: str
    notify: bool
    immediate: bool
    tz_name: str
    break_start: str
    break_end: str
    break_enabled: bool

@dataclass(frozen=True)
class SummaryConfig:
    base_dir: str
    tz_name: str
    week: str            # "current" o "YYYY-Www" (ISO week)
    include_details: bool

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="worklog", description="Worklog PRO (Windows + horario Colombia)")
    sub = p.add_subparsers(dest="command", required=True)

    # run
    pr = sub.add_parser("run", help="Ejecutar el worklog interactivo")
    pr.add_argument("--minutes", type=int, default=60, help="Intervalo en minutos (default: 60).")
    pr.add_argument("--base-dir", type=str, default="logs", help="Carpeta de salida (default: logs).")
    pr.add_argument("--start", type=str, default="07:00", help="Inicio jornada HH:MM (default: 07:00).")
    pr.add_argument("--end", type=str, default="17:00", help="Fin jornada HH:MM (default: 17:00).")
    pr.add_argument("--tags", type=str, default="", help="Tags por defecto (ej: ado,backend,meetings).")
    pr.add_argument("--notify", dest="notify", action="store_true", default=True, help="Notificación en cada tick (default: activado).")
    pr.add_argument("--no-notify", dest="notify", action="store_false", help="Desactiva notificaciones.")
    pr.add_argument("--immediate", action="store_true", help="Pide registro inmediatamente al iniciar.")
    pr.add_argument("--tz", type=str, default="America/Bogota", help="Timezone IANA (default: America/Bogota).")
    pr.add_argument("--break-start", type=str, default="13:00", help="Inicio de break HH:MM (default: 13:00).")
    pr.add_argument("--break-end", type=str, default="14:00", help="Fin de break HH:MM (default: 14:00).")
    pr.add_argument("--no-break", dest="break_enabled", action="store_false", default=True, help="Desactiva el break automático.")

    # summary
    ps = sub.add_parser("summary", help="Generar resumen semanal")
    ps.add_argument("--base-dir", type=str, default="logs", help="Carpeta donde están los logs (default: logs).")
    ps.add_argument("--tz", type=str, default="America/Bogota", help="Timezone IANA (default: America/Bogota).")
    ps.add_argument("--week", type=str, default="current", help="Semana ISO: 'current' o 'YYYY-Www' (ej: 2026-W05).")
    ps.add_argument("--details", action="store_true", help="Incluye detalle (tabla por entradas).")

    return p

def parse_args():
    p = build_parser()
    a = p.parse_args()

    if a.command == "run":
        minutes = max(1, int(a.minutes))
        return a.command, RunConfig(
            minutes=minutes,
            base_dir=a.base_dir,
            start=a.start,
            end=a.end,
            tags=a.tags,
            notify=bool(a.notify),
            immediate=bool(a.immediate),
            tz_name=a.tz,
            break_start=a.break_start,
            break_end=a.break_end,
            break_enabled=bool(a.break_enabled),
        )

    # summary
    return a.command, SummaryConfig(
        base_dir=a.base_dir,
        tz_name=a.tz,
        week=a.week,
        include_details=bool(a.details),
    )
