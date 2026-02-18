import logging
import shutil
import subprocess
import time

logger = logging.getLogger(__name__)

_last_notification_key: tuple[str, str] | None = None
_last_notification_ts: float = 0.0
_notifications_muted_until_ts: float = 0.0
_backend_preference: str = "burnttoast"


def _should_skip_duplicate(title: str, body: str, min_seconds: int = 20) -> bool:
    global _last_notification_key
    global _last_notification_ts

    key = (title, body)
    now_ts = time.time()
    if _last_notification_key == key and (now_ts - _last_notification_ts) < min_seconds:
        return True

    _last_notification_key = key
    _last_notification_ts = now_ts
    return False


def _is_muted() -> bool:
    return time.time() < _notifications_muted_until_ts


def _mute_notifications(minutes: int = 10) -> None:
    global _notifications_muted_until_ts
    _notifications_muted_until_ts = time.time() + (minutes * 60)


def _find_powershell() -> str | None:
    for exe in ("powershell", "powershell.exe", "pwsh", "pwsh.exe"):
        if shutil.which(exe):
            return exe
    return None


def _run_ps(ps_exe: str, script: str, timeout: int = 2) -> int:
    try:
        result = subprocess.run(
            [ps_exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode
    except subprocess.TimeoutExpired:
        return 124
    except Exception:
        return 125


def notify_windows(title: str, body: str) -> None:
    """
    Intenta notificación Toast en Windows evitando duplicados.
    1) BurntToast si está disponible.
    2) Toast WinRT nativo como fallback.
    """
    global _backend_preference

    if _is_muted():
        return

    if _should_skip_duplicate(title, body):
        logger.debug("Skipping duplicate notification: %s | %s", title, body)
        return

    ps_exe = _find_powershell()
    if not ps_exe:
        logger.warning("PowerShell no disponible; notificaciones desactivadas temporalmente.")
        _mute_notifications(minutes=60)
        return

    ps_toast = f"""
    try {{
      if (Get-Module -ListAvailable -Name BurntToast) {{
        Import-Module BurntToast -ErrorAction Stop
        New-BurntToastNotification -Text '{title.replace("'", "''")}', '{body.replace("'", "''")}' -AppLogo (Join-Path $env:WINDIR 'System32\\SHELL32.dll') | Out-Null
        exit 0
      }} else {{
        exit 2
      }}
    }} catch {{
      exit 1
    }}
    """.strip()

    if _backend_preference == "burnttoast":
        rc = _run_ps(ps_exe, ps_toast, timeout=2)
        if rc == 0:
            return
        if rc in (124, 125):
            logger.warning("Notificación BurntToast lenta o fallida; usando fallback WinRT.")
        _backend_preference = "winrt"

    ps_winrt = f"""
    try {{
      [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
      [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] > $null
      $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
      $xml.LoadXml("<toast><visual><binding template='ToastGeneric'><text>{title.replace("'", "''")}</text><text>{body.replace("'", "''")}</text></binding></visual></toast>")
      $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
      $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Worklog')
      $notifier.Show($toast)
      exit 0
    }} catch {{
      exit 1
    }}
    """.strip()

    rc = _run_ps(ps_exe, ps_winrt, timeout=2)
    if rc == 0:
        return

    logger.warning("No se pudo mostrar notificación; se pausarán por 10 minutos.")
    _mute_notifications(minutes=10)
