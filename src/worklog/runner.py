import time
from datetime import datetime

from dataclasses import dataclass
from zoneinfo import ZoneInfo

from .config import RunConfig
from .domain import Entry
from .clock import (
    WorkWindow,
    parse_hhmm,
    now,
    iso,
    is_work_time,
    next_work_start,
    seconds_until,
)
from . import storage
from .exporter import export_markdown
from .ui import (
    prompt_multiline,
    sprint_menu,
    choose_activity,
    maybe_edit,
    ask_tags,
    update_sprint,
)
from .notifier import notify_windows


@dataclass
class RuntimeState:
    paths: dict[str, str]
    tick_start: datetime
    next_tick: float
    last_activities: list[str]


# -------------------------
# Helpers de inicialización
# -------------------------

def _build_window(cfg: RunConfig) -> WorkWindow:
    sh, sm = parse_hhmm(cfg.start)
    eh, em = parse_hhmm(cfg.end)
    return WorkWindow(sh, sm, eh, em)


def _current_day(tz: ZoneInfo) -> str:
    return now(tz).strftime("%Y-%m-%d")


def _load_sprint_activities(jsonl_path: str) -> list[str]:
    entries = storage.read_jsonl(jsonl_path)
    unique = []
    for e in reversed(entries):
        if e.activity and e.activity not in unique:
            unique.append(e.activity)
        if len(unique) >= 9:
            break
    return list(reversed(unique))


def _print_banner(cfg: RunConfig, paths: dict) -> None:
    print(f"✅ Worklog PRO (TZ={cfg.tz_name})")
    print(f"📁 JSONL: {paths['jsonl']}")
    print(f"📁  CSV: {paths['csv']}")
    print(f"📁   MD: {paths['md']}")
    print(f"🕘 Horario: L–V {cfg.start}–{cfg.end}")
    print(f"⏱️ Intervalo: {cfg.minutes} min")
    print("🛑 Salir: Ctrl+C\n")


def _sleep_until_next_work_start(tz: ZoneInfo, window: WorkWindow) -> None:
    n = now(tz)
    if is_work_time(n, window):
        return

    nxt = next_work_start(n, window)
    wait = seconds_until(nxt, tz)
    print(f"🧊 Fuera de horario. Próximo inicio: {iso(nxt)} (en {wait//60} min).")

    try:
        time.sleep(wait)
    except KeyboardInterrupt:
        print("\n👋 Worklog detenido por el usuario.")
        raise SystemExit(0)



def _init_state(cfg: RunConfig, tz: ZoneInfo, window: WorkWindow) -> RuntimeState:
    day = _current_day(tz)
    paths = storage.paths_for_day(cfg.base_dir, day)
    storage.init_csv_if_needed(paths["csv"])

    last_activities = _load_sprint_activities(paths["jsonl"])

    _print_banner(cfg, paths)
    _sleep_until_next_work_start(tz, window)

    tick_start = now(tz)
    interval_seconds = cfg.minutes * 60
    next_tick = time.time() + (0 if cfg.immediate else interval_seconds)

    return RuntimeState(
        paths=paths,
        tick_start=tick_start,
        next_tick=next_tick,
        last_activities=last_activities,
    )


# -------------------------
# Helpers de ciclo (loop)
# -------------------------

def _rotate_if_new_day(cfg: RunConfig, tz: ZoneInfo, state: RuntimeState) -> None:
    day = _current_day(tz)
    if state.paths["jsonl"].endswith(f"{day}_worklog.jsonl"):
        return

    state.paths = storage.paths_for_day(cfg.base_dir, day)
    storage.init_csv_if_needed(state.paths["csv"])
    state.tick_start = now(tz)

    # recargar sprint list del nuevo día (si existe)
    state.last_activities = _load_sprint_activities(state.paths["jsonl"])

    print(f"\n📆 Nuevo día detectado: {day}. Rotando logs.")


def _ensure_work_time_or_sleep(cfg: RunConfig, tz: ZoneInfo, window: WorkWindow, state: RuntimeState) -> None:
    n = now(tz)
    if is_work_time(n, window):
        return

    export_markdown(state.paths["md"], storage.read_jsonl(state.paths["jsonl"]))

    nxt = next_work_start(n, window)
    wait = seconds_until(nxt, tz)
    print(f"🧊 Fuera de horario. Próximo inicio: {iso(nxt)} (en {wait//60} min).")

    try:
        time.sleep(wait)
    except KeyboardInterrupt:
        print("\n👋 Worklog detenido por el usuario.")
        raise SystemExit(0)

    state.tick_start = now(tz)
    interval_seconds = cfg.minutes * 60
    state.next_tick = time.time() + (0 if cfg.immediate else interval_seconds)



def _should_tick(state: RuntimeState) -> bool:
    return time.time() >= state.next_tick


def _notify_if_enabled(cfg: RunConfig, tick_start: datetime, tick_end: datetime) -> None:
    if not cfg.notify:
        return
    notify_windows(
        "Worklog",
        f"Registrar actividad ({tick_start.strftime('%H:%M')}–{tick_end.strftime('%H:%M')})",
    )


def _collect_activity(choice: str, last_activities: list[str]) -> str:
    picked = choose_activity(choice, last_activities)

    if not picked and choice not in ("s", "b"):
        picked = prompt_multiline("Describe lo que hiciste (multilínea):")
    else:
        picked = maybe_edit(picked)

    return picked.strip() or "(sin detalle)"


def _build_entry(tick_start, tick_end, activity: str, tags: str) -> Entry:
    block_minutes = max(1, int((tick_end - tick_start).total_seconds() / 60))
    return Entry(
        date=tick_start.strftime("%Y-%m-%d"),
        start=iso(tick_start),
        end=iso(tick_end),
        minutes=block_minutes,
        activity=activity,
        tags=tags,
    )


def _persist_and_export(state: RuntimeState, entry: Entry) -> None:
    storage.append_jsonl(state.paths["jsonl"], entry)
    storage.append_csv(state.paths["csv"], entry)
    export_markdown(state.paths["md"], storage.read_jsonl(state.paths["jsonl"]))
    print("💾 Guardado + Markdown actualizado.\n")


def _handle_tick(cfg: RunConfig, tz: ZoneInfo, state: RuntimeState) -> bool:
    tick_end = now(tz)
    _notify_if_enabled(cfg, state.tick_start, tick_end)

    block_minutes = max(1, int((tick_end - state.tick_start).total_seconds() / 60))
    print("=" * 70)
    print(f"🕒 Bloque: {state.tick_start.strftime('%H:%M')}–{tick_end.strftime('%H:%M')} ({block_minutes} min)")
    print("Opciones: [Enter]=nuevo  /  (s)=skip  /  (b)=break  /  (q)=salir")
    sprint_menu(state.last_activities)

    choice = input("> ").strip().lower()
    if choice == "q":
        export_markdown(state.paths["md"], storage.read_jsonl(state.paths["jsonl"]))
        print(f"👋 Cerrando. Markdown exportado: {state.paths['md']}")
        return False

    activity = _collect_activity(choice, state.last_activities)
    tags = ask_tags(cfg.tags)

    entry = _build_entry(state.tick_start, tick_end, activity, tags)
    state.last_activities = update_sprint(state.last_activities, activity)

    _persist_and_export(state, entry)

    # avanzar ventana
    state.tick_start = tick_end
    state.next_tick = time.time() + (cfg.minutes * 60)
    return True


# -------------------------
# API pública
# -------------------------

def run(cfg: RunConfig) -> None:
    tz = ZoneInfo(cfg.tz_name)
    window = _build_window(cfg)
    state = _init_state(cfg, tz, window)

    try:
        while True:
            _rotate_if_new_day(cfg, tz, state)
            _ensure_work_time_or_sleep(cfg, tz, window, state)

            if _should_tick(state) and not _handle_tick(cfg, tz, state):
                return

            time.sleep(1)

    except KeyboardInterrupt:
        export_markdown(state.paths["md"], storage.read_jsonl(state.paths["jsonl"]))
        print(f"\n👋 Interrumpido. Markdown exportado: {state.paths['md']}")
