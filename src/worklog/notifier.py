import subprocess

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

    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_toast],
            capture_output=True,
            text=True,
            timeout=4
        )
        if r.returncode == 0:
            return
    except Exception:
        pass

    ps_msg = f"""
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show('{body.replace("'", "''")}', '{title.replace("'", "''")}') | Out-Null
    """.strip()

    try:
        subprocess.Popen(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_msg])
    except Exception:
        return
