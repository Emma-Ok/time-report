from typing import List
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def prompt_multiline(msg: str) -> str:
    console.print(f"[bold cyan]{msg}[/bold cyan]")
    console.print("[dim](Termina con una línea vacía)[/dim]")
    lines: List[str] = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    return "\n".join(lines).strip()

def sprint_menu(last_activities: List[str]) -> None:
    if not last_activities:
        return
    console.print("[bold]Sprint:[/bold] (r)=repetir última, (1..9)=usar actividad reciente")
    recent = last_activities[-9:]
    for i, a in enumerate(recent, start=1):
        one_line = a.splitlines()[0]
        if len(one_line) > 60:
            one_line = one_line[:57] + "..."
        console.print(f"  {i}. {one_line}")

def choose_activity(choice: str, last_activities: List[str]) -> str:
    choice = choice.strip().lower()

    if choice == "s":
        return "(sin registro / skip)"
    if choice == "b":
        return "(break / descanso)"
    if choice == "r":
        return last_activities[-1] if last_activities else ""
    if choice.isdigit() and last_activities:
        idx = int(choice)
        recent = last_activities[-9:]
        if 1 <= idx <= len(recent):
            return recent[idx - 1]
    return ""

def maybe_edit(activity: str) -> str:
    if not activity:
        return activity
    console.print("\n[bold]Actividad seleccionada.[/bold] ¿Editar? (Enter=no / escribe algo=sí)")
    if Prompt.ask(">", default="").strip():
        return prompt_multiline("Nueva actividad (multilínea):")
    return activity

def ask_tags(default_tags: str) -> str:
    t = Prompt.ask(f"Tags (Enter para '{default_tags}')", default="").strip()
    return t if t else default_tags

def update_sprint(last_activities: List[str], activity: str) -> List[str]:
    skip_values = {"(sin detalle)", "(sin registro / skip)", "(break / descanso)"}
    if activity and activity not in last_activities and activity not in skip_values:
        last_activities.append(activity)
    if len(last_activities) > 9:
        last_activities = last_activities[-9:]
    return last_activities
