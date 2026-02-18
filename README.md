
# worklog

Herramienta de consola para registrar actividades laborales por bloques de tiempo.
Pensada para uso diario y para facilitar el reporte de horas en **Azure DevOps**.

- 🕘 Jornada laboral por defecto: **L–V, 07:00–17:00**
- 🌎 Timezone por defecto: **America/Bogota**
- ⏱️ Registro por intervalos configurables
- 📤 Exporta: **JSONL (fuente), CSV (Excel), Markdown (copy/paste)**

---

## Requisitos

- Windows 10 / 11
- [`uv`](https://github.com/astral-sh/uv) instalado
- Python **3.12**

---

## Instalación (una sola vez)

Desde la carpeta raíz del proyecto (donde está `pyproject.toml`):

```bash
uv python install 3.12
uv venv --python 3.12
uv pip install -e .
````

Esto crea el entorno virtual y registra el comando `worklog`.

---

## Uso diario (flujo recomendado)

### 1. Abrir terminal

* Abre **Windows Terminal** o **PowerShell**
* Navega a la carpeta del proyecto `time-report/`

### 2. Iniciar la jornada laboral

Ejecuta este comando **al comenzar tu día (ej. lunes 7:00 a.m.)**:

```bash
uv run worklog run --minutes 60 --notify --immediate --tags "azure-devops"
```

### Qué hace este comando

* ⏱️ Registra actividades cada **60 minutos**
* 🔔 Muestra **notificación** en cada bloque
* ▶️ Pide el primer registro **de inmediato**
* 🗓️ Solo opera **lunes a viernes**
* 📁 Guarda los archivos del día en `logs/`

Déjalo ejecutándose durante el día.
Fuera del horario laboral, el programa se pausa automáticamente.

---

## Controles dentro del programa

En cada bloque de tiempo (tick) aparecerán estas opciones:

* **Enter** → Registrar una nueva actividad
  (permite texto multilínea; termina con una línea vacía)
* **s** → Skip (bloque sin actividad)
* **b** → Break (descanso)
* **q** → Salir guardando y exportando el reporte

### Sprint mode (atajos)

Si ya hay actividades registradas en el día:

* **r** → Repetir la última actividad (con opción de editar)
* **1..9** → Reutilizar una actividad reciente (con opción de editar)

---

## Archivos generados

Los archivos se crean automáticamente en la carpeta `logs/` con esta estructura:

* `logs/worklog_json/YYYY-MM-DD_worklog.jsonl`
  Fuente estructurada (historial completo).

* `logs/worklog_csv/YYYY-MM-DD_worklog.csv`
  Compatible con Excel.

* `logs/worklog_md/YYYY-MM-DD_worklog.md`
  Markdown listo para copiar y pegar en Azure DevOps.

El archivo Markdown diario incluye:

* Total de minutos y horas
* Resumen por tags
* Tabla cronológica de actividades

---

## Resumen semanal

El sistema puede generar un **reporte semanal consolidado**.

### Generar resumen de la semana actual

```bash
uv run worklog summary --week current
```

### Generar resumen de una semana específica

```bash
uv run worklog summary --week 2026-W06
```

### Incluir detalle completo (tabla por entrada)

```bash
uv run worklog summary --week current --details
```

El archivo se genera en:

```
logs/worklog_md/weekly/YYYY-Www_summary.md
```

Incluye:

* Total semanal de horas
* Totales por día
* Totales por tags
* (Opcional) detalle cronológico completo

---

## Configuración útil (flags)

Cambiar intervalo a 30 minutos:

```bash
uv run worklog run --minutes 30 --notify
```

Cambiar horario laboral:

```bash
uv run worklog run --start 08:00 --end 17:00 --minutes 60 --notify
```

Cambiar timezone:

```bash
uv run worklog run --tz America/Bogota
```

Cambiar carpeta de salida:

```bash
uv run worklog run --base-dir "C:\Users\TU_USUARIO\Documents\worklog-logs"
```

---

## Notificaciones en Windows

El programa intenta mostrar notificaciones tipo Toast de Windows en este orden:

1. **BurntToast** (si está instalado)
2. **Toast WinRT nativo** como fallback

### Instalar BurntToast (opcional, recomendado)

En PowerShell (una sola vez):

```powershell
Install-Module BurntToast -Scope CurrentUser
```

---

## Salir del programa

Presiona **Ctrl+C** en cualquier momento para salir de forma limpia.
El sistema exporta el Markdown antes de cerrarse, sin mostrar errores ni trazas.

---

## Troubleshooting

### El comando `worklog` no se reconoce

Asegúrate de:

* Estar en la carpeta raíz del proyecto
* Haber ejecutado `uv pip install -e .`

### No se generan archivos

Verifica permisos de escritura y que exista la carpeta `logs/`.

### Está “fuera de horario”

Es el comportamiento esperado fuera de lunes a viernes o fuera del rango configurado.
El programa se duerme hasta el siguiente inicio válido.

---

## Ejemplo completo de uso diario

Inicio de jornada (lunes 7:00 a.m.):

```bash
uv run worklog run --minutes 60 --notify --immediate --tags "azure-devops"
```

Fin de jornada:

* En el siguiente prompt escribe **q**
* Copia el contenido de `logs/worklog_md/YYYY-MM-DD_worklog.md` y pégalo en tu reporte



