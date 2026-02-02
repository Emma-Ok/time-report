# Comandos disponibles

Este proyecto expone el ejecutable `worklog` (definido en `pyproject.toml`) y dos subcomandos: `run` y `summary`.

## 1) Ejecutar el worklog interactivo

**Comando:**

- `uv run worklog run`

**Descripción:**

Inicia el registro interactivo por bloques de tiempo. Cada intervalo solicita la actividad realizada y genera JSONL, CSV y Markdown en la carpeta de logs.

**Opciones disponibles:**

- `--minutes <int>`: Intervalo en minutos (default: 60)
- `--base-dir <path>`: Carpeta de salida para logs (default: `logs`)
- `--start <HH:MM>`: Inicio de jornada (default: `07:00`)
- `--end <HH:MM>`: Fin de jornada (default: `17:00`)
- `--tags <str>`: Tags por defecto (ej: `ado,backend,meetings`)
- `--notify`: Notificación en cada tick (default: activado)
- `--no-notify`: Desactiva notificaciones
- `--immediate`: Pide registro inmediatamente al iniciar
- `--tz <IANA>`: Timezone IANA (default: `America/Bogota`)
- `--break-start <HH:MM>`: Inicio de break automático (default: `13:00`)
- `--break-end <HH:MM>`: Fin de break automático (default: `14:00`)
- `--no-break`: Desactiva break automático

**Ejemplos:**

- `uv run worklog run --minutes 60 --immediate --tags "azure-devops"`
- `uv run worklog run --minutes 30 --start 08:00 --end 17:30`
- `uv run worklog run --minutes 45 --tz America/Mexico_City`
- `uv run worklog run --base-dir "C:\\Users\\TU_USUARIO\\Documents\\worklog-logs" --minutes 60`
- `uv run worklog run --tags "ado,backend,meetings" --immediate`
- `uv run worklog run --no-notify --minutes 60`
- `uv run worklog run --break-start 12:30 --break-end 13:30`
- `uv run worklog run --no-break`

---

## 2) Generar resumen semanal

**Comando:**

- `uv run worklog summary`

**Descripción:**

Genera un resumen semanal en Markdown con totales por día y por tags. El archivo se guarda en `logs/weekly/`.

**Opciones disponibles:**

- `--base-dir <path>`: Carpeta donde están los logs (default: `logs`)
- `--tz <IANA>`: Timezone IANA (default: `America/Bogota`)
- `--week <current|YYYY-Www>`: Semana ISO a resumir (default: `current`)
- `--details`: Incluye detalle con tabla por entradas

**Ejemplos:**

- `uv run worklog summary --week 2026-W05 --details`
- `uv run worklog summary --week current`
- `uv run worklog summary --base-dir logs --tz America/Bogota --details`

---

## Comportamiento al volver tarde

Si pasó más de un intervalo desde el último registro, el sistema ofrece:

- **1**: Un solo bloque con toda la duración
- **2**: Repetir la misma actividad en bloques del tamaño del intervalo

Esto evita perder horas si olvidaste registrar a tiempo.

---

## Alternativa con módulo Python

Si prefieres ejecutar el módulo directamente, los subcomandos y flags son los mismos:

- `python -m worklog run --minutes 60`
- `python -m worklog run --minutes 30 --immediate --tags "daily"`
- `python -m worklog summary --week current`
- `python -m worklog summary --week 2026-W05 --details`
