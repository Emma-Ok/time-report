import time
import logging
from datetime import datetime, timedelta

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
    update_sprint,
)
from .notifier import notify_windows

logger = logging.getLogger(__name__)
DEFAULT_ACTIVITY = "(sin detalle)"

try:
    import msvcrt
except Exception:
    msvcrt = None


@dataclass
class RuntimeState:
    paths: dict[str, str]
    tick_start: datetime
    next_tick: float
    last_activities: list[str]
    break_start: tuple[int, int] | None
    break_end: tuple[int, int] | None


# -------------------------
# Helpers de inicialización
# -------------------------

def _build_window(cfg: RunConfig) -> WorkWindow:
    sh, sm = parse_hhmm(cfg.start)
    eh, em = parse_hhmm(cfg.end)
    return WorkWindow(sh, sm, eh, em)


def _build_break_window(cfg: RunConfig) -> tuple[tuple[int, int] | None, tuple[int, int] | None]:
    if not cfg.break_enabled:
        return None, None
    bh, bm = parse_hhmm(cfg.break_start)
    eh, em = parse_hhmm(cfg.break_end)
    return (bh, bm), (eh, em)


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
    print(f"🔔 Notificaciones: {'ON' if cfg.notify else 'OFF'}")
    print("🛑 Salir: Ctrl+C\n")
    logger.info("Run started: tz=%s start=%s end=%s minutes=%s", cfg.tz_name, cfg.start, cfg.end, cfg.minutes)


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
    break_start, break_end = _build_break_window(cfg)

    return RuntimeState(
        paths=paths,
        tick_start=tick_start,
        next_tick=next_tick,
        last_activities=last_activities,
        break_start=break_start,
        break_end=break_end,
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
    logger.info("Rotated logs to day=%s", day)


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



def _should_tick(cfg: RunConfig, tz: ZoneInfo, state: RuntimeState) -> bool:
    return now(tz) >= state.tick_start + timedelta(minutes=cfg.minutes)


def _notify_if_enabled(cfg: RunConfig, tz: ZoneInfo, tick_start: datetime, tick_end: datetime) -> None:
    if not cfg.notify:
        return

    lag_seconds = (now(tz) - tick_end).total_seconds()
    if lag_seconds > 90:
        return

    notify_windows(
        "Worklog",
        f"Registrar actividad ({tick_start.strftime('%H:%M')}–{tick_end.strftime('%H:%M')})",
    )


def _input_with_timeout(prompt: str, timeout_seconds: int, default: str = "") -> tuple[str, bool]:
    if timeout_seconds <= 0 or msvcrt is None:
        return input(prompt), False

    print(prompt, end="", flush=True)
    chars: list[str] = []
    deadline = time.time() + timeout_seconds

    while time.time() < deadline:
        value, is_done = _consume_keyboard_input(chars)
        if is_done:
            print("")
            return value, False
        time.sleep(0.05)

    print("")
    return default, True


def _consume_keyboard_input(chars: list[str]) -> tuple[str, bool]:
    if not msvcrt or not msvcrt.kbhit():
        return "", False

    ch = msvcrt.getwche()
    if ch in ("\r", "\n"):
        return "".join(chars), True
    if ch == "\003":
        raise KeyboardInterrupt
    if ch in ("\x00", "\xe0"):
        if msvcrt.kbhit():
            msvcrt.getwche()
        return "", False
    if ch == "\b":
        if chars:
            chars.pop()
        return "", False

    chars.append(ch)
    return "", False


def _is_break_block(state: RuntimeState, tick_start: datetime, tick_end: datetime) -> bool:
    if not state.break_start or not state.break_end:
        return False
    bs_h, bs_m = state.break_start
    be_h, be_m = state.break_end
    break_start_dt = tick_start.replace(hour=bs_h, minute=bs_m, second=0, microsecond=0)
    break_end_dt = tick_start.replace(hour=be_h, minute=be_m, second=0, microsecond=0)
    return tick_start < break_end_dt and tick_end > break_start_dt


def _collect_activity(choice: str, last_activities: list[str]) -> str:
    normalized = choice.strip().lower()

    if normalized and normalized not in ("s", "b", "r") and not normalized.isdigit():
        return choice.strip() or DEFAULT_ACTIVITY

    picked = choose_activity(choice, last_activities)

    if normalized in ("s", "b"):
        return picked.strip() or DEFAULT_ACTIVITY

    if not picked and choice not in ("s", "b"):
        picked = prompt_multiline("Describe lo que hiciste (multilínea):")
    else:
        picked = maybe_edit(picked)

    return picked.strip() or DEFAULT_ACTIVITY


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
    logger.info("Saved entry: %s %s-%s (%s min)", entry.date, entry.start, entry.end, entry.minutes)


def _handle_tick(cfg: RunConfig, tz: ZoneInfo, state: RuntimeState) -> bool:
    tick_end = state.tick_start + timedelta(minutes=cfg.minutes)
    _notify_if_enabled(cfg, tz, state.tick_start, tick_end)

    if _is_break_block(state, state.tick_start, tick_end):
        entry = _build_entry(state.tick_start, tick_end, "(break / descanso)", "")
        _persist_and_export(state, entry)
        state.tick_start = tick_end
        state.next_tick = time.time()
        return True

    block_minutes = max(1, int((tick_end - state.tick_start).total_seconds() / 60))
    print("=" * 70)
    print(f"🕒 Bloque: {state.tick_start.strftime('%H:%M')}–{tick_end.strftime('%H:%M')} ({block_minutes} min)")
    print("Opciones: [Enter]=nuevo o escribe la actividad  /  (s)=skip  /  (b)=break  /  (q)=salir")
    sprint_menu(state.last_activities)

    choice_raw, timed_out = _input_with_timeout("> ", cfg.input_timeout_sec, default="")
    choice = choice_raw.strip().lower()

    if timed_out:
        print(f"⏰ Sin respuesta. Se registrará automáticamente como '{DEFAULT_ACTIVITY}'.")
        activity = DEFAULT_ACTIVITY
        tags = cfg.tags
        entry = _build_entry(state.tick_start, tick_end, activity, tags)
        _persist_and_export(state, entry)
        state.tick_start = tick_end
        state.next_tick = time.time()
        return True

    if choice == "q":
        export_markdown(state.paths["md"], storage.read_jsonl(state.paths["jsonl"]))
        print(f"👋 Cerrando. Markdown exportado: {state.paths['md']}")
        return False

    activity = _collect_activity(choice, state.last_activities)
    tags_raw, tags_timeout = _input_with_timeout(
        f"Tags (Enter para '{cfg.tags}'): ", cfg.input_timeout_sec, default=cfg.tags
    )
    tags = cfg.tags if tags_timeout else (tags_raw.strip() or cfg.tags)

    entry = _build_entry(state.tick_start, tick_end, activity, tags)

    state.last_activities = update_sprint(state.last_activities, activity)
    _persist_and_export(state, entry)

    # avanzar ventana
    state.tick_start = tick_end
    state.next_tick = time.time()
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

            if _should_tick(cfg, tz, state) and not _handle_tick(cfg, tz, state):
                return

            time.sleep(1)

    except KeyboardInterrupt:
        export_markdown(state.paths["md"], storage.read_jsonl(state.paths["jsonl"]))
        print(f"\n👋 Interrumpido. Markdown exportado: {state.paths['md']}")
