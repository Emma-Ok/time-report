import typer

from .config import RunConfig, SummaryConfig
from .runner import run
from .weekly import weekly_summary

app = typer.Typer(help="Worklog PRO (Windows + horario Colombia)")


@app.command("run")
def run_command(
    minutes: int = typer.Option(60, help="Intervalo en minutos."),
    base_dir: str = typer.Option("logs", help="Carpeta de salida."),
    start: str = typer.Option("07:00", help="Inicio jornada HH:MM."),
    end: str = typer.Option("17:00", help="Fin jornada HH:MM."),
    tags: str = typer.Option("", help="Tags por defecto."),
    notify: bool = typer.Option(True, "--notify/--no-notify", help="Notificaciones en cada tick."),
    immediate: bool = typer.Option(False, "--immediate", help="Pedir registro inmediatamente al iniciar."),
    tz: str = typer.Option("America/Bogota", help="Timezone IANA."),
    break_start: str = typer.Option("13:00", help="Inicio de break HH:MM."),
    break_end: str = typer.Option("14:00", help="Fin de break HH:MM."),
    break_enabled: bool = typer.Option(True, "--break/--no-break", help="Break automático."),
    input_timeout: int = typer.Option(120, help="Segundos para esperar respuesta antes de auto-registrar."),
) -> None:
    cfg = RunConfig(
        minutes=max(1, int(minutes)),
        base_dir=base_dir,
        start=start,
        end=end,
        tags=tags,
        notify=bool(notify),
        immediate=bool(immediate),
        tz_name=tz,
        break_start=break_start,
        break_end=break_end,
        break_enabled=bool(break_enabled),
        input_timeout_sec=max(0, int(input_timeout)),
    )
    run(cfg)


@app.command("summary")
def summary_command(
    base_dir: str = typer.Option("logs", help="Carpeta donde están los logs."),
    tz: str = typer.Option("America/Bogota", help="Timezone IANA."),
    week: str = typer.Option("current", help="Semana ISO: current o YYYY-Www."),
    details: bool = typer.Option(False, "--details", help="Incluye detalle por entradas."),
) -> None:
    cfg = SummaryConfig(
        base_dir=base_dir,
        tz_name=tz,
        week=week,
        include_details=bool(details),
    )
    weekly_summary(cfg)
