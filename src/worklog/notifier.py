import subprocess
import shutil
import logging

logger = logging.getLogger(__name__)

def _find_powershell() -> str | None:
    for exe in ("powershell", "powershell.exe", "pwsh", "pwsh.exe"):
        if shutil.which(exe):
            return exe
    return None

def notify_windows(title: str, body: str) -> None:
    """
    Intenta Toast con BurntToast (si existe). Si no, cae a MessageBox.
    No requiere dependencias Python externas.
    """
    ps_toast = f"""
    try {{
      if (Get-Module -ListAvailable -Name BurntToast) {{
        Import-Module BurntToast -ErrorAction Stop
        New-BurntToastNotification -Text '{title.replace("'", "''")}', '{body.replace("'", "''")}' | Out-Null
        exit 0
      }} else {{
        exit 2
      }}
    }} catch {{
      exit 1
    }}
    """.strip()

    ps_exe = _find_powershell()
    if not ps_exe:
      logger.warning("PowerShell not found; notifications disabled.")
        return

    try:
        r = subprocess.run(
            [ps_exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_toast],
            capture_output=True,
            text=True,
            timeout=4
        )
        if r.returncode == 0:
            return
    except Exception:
      logger.exception("Toast notification failed.")

    ps_msg = f"""
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show('{body.replace("'", "''")}', '{title.replace("'", "''")}') | Out-Null
    """.strip()

    try:
        subprocess.Popen([ps_exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-STA", "-Command", ps_msg])
    except Exception:
      logger.exception("Fallback MessageBox notification failed.")
      return
