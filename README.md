````md
# worklog

Herramienta de consola para registrar tus actividades por bloques de tiempo, pensada para el uso diario
y para facilitar el reporte de horas en Azure DevOps.

- Control de jornada: **L–V, 07:00–17:00** (por defecto)
- Timezone: **America/Bogota**
- Exporta: **JSONL (fuente), CSV (Excel), Markdown (copy/paste)**

---

## Requisitos

- Windows 10 / 11
- `uv` instalado
- Python **3.12**

---

## Instalación (una sola vez)

Desde la carpeta raíz del proyecto (donde está `pyproject.toml`):

```bash
uv python install 3.12
uv venv --python 3.12
````

Esto fija el proyecto a Python 3.12.

---

## Uso diario (flujo recomendado)

### 1. Abrir terminal

* Abre **Windows Terminal** o **PowerShell**
* Navega a la carpeta del proyecto `worklog/`

### 2. Ejecutar el worklog

Cada 60 minutos, con notificación:

```bash
uv run worklog --minutes 60 --notify --tags "azure-devops"
```

Para que pida registro inmediatamente al iniciar:

```bash
uv run worklog --minutes 60 --notify --immediate --tags "azure-devops"
```

**Recomendación:** ejecútalo alrededor de las **07:00 a.m.** y déjalo abierto.
Fuera del horario laboral el programa se pausa solo y se reactiva el siguiente día hábil.

---

## Controles dentro del programa

En cada bloque de tiempo aparecerán las siguientes opciones:

* **Enter** → Registrar actividad (permite texto multilínea; termina con una línea vacía)
* **s** → Skip (registra el bloque sin actividad)
* **b** → Break (descanso)
* **q** → Salir guardando y exportando Markdown

### Sprint mode (atajos)

Si ya hay actividades registradas en el día:

* **r** → Repetir la última actividad (con opción de editar)
* **1..9** → Elegir una actividad reciente y reutilizarla (con opción de editar)

---

## Archivos generados

Los archivos se crean automáticamente en la carpeta `logs/`:

* `logs/YYYY-MM-DD_worklog.jsonl`
  Fuente de verdad, estructurada (para futuros análisis).

* `logs/YYYY-MM-DD_worklog.csv`
  Compatible con Excel.

* `logs/YYYY-MM-DD_worklog.md`
  Markdown listo para copiar y pegar en Azure DevOps.

El archivo Markdown incluye:

* Total de minutos y horas trabajadas
* Resumen por tags
* Tabla cronológica con todas las actividades

---

## Configuración útil (flags)

Cambiar intervalo a 30 minutos:

```bash
uv run worklog --minutes 30 --notify
```

Cambiar horario laboral:

```bash
uv run worklog --start 07:00 --end 17:00 --minutes 60 --notify
```

Cambiar timezone:

```bash
uv run worklog --tz America/Bogota --minutes 60 --notify
```

Cambiar carpeta de salida:

```bash
uv run worklog --base-dir "C:\Users\TU_USUARIO\Documents\worklog-logs" --minutes 60 --notify
```

---

## Notificaciones en Windows

El programa intenta mostrar una notificación en este orden:

1. **Toast notification** usando el módulo de PowerShell `BurntToast` (si está instalado).
2. **MessageBox** como fallback.

### Instalar BurntToast (opcional, recomendado)

En PowerShell, una sola vez:

```powershell
Install-Module BurntToast -Scope CurrentUser
```

Si no se instala, el programa sigue funcionando normalmente.

---

## Troubleshooting

### El comando `worklog` no se reconoce

Asegúrate de ejecutar siempre usando `uv` y desde la carpeta del proyecto:

```bash
uv run worklog --minutes 60
```

### No se generan archivos

Verifica permisos de escritura en la carpeta del proyecto.
Por defecto, los logs se crean en `logs/`.

### Se cerró la terminal accidentalmente

El Markdown se exporta en cada bloque y al salir.
Revisa el archivo correspondiente en `logs/YYYY-MM-DD_worklog.md`.

---

## Ejemplo recomendado para el día a día

Inicio de jornada (07:00):

```bash
uv run worklog --minutes 60 --notify --immediate --tags "azure-devops"
```

Fin de jornada:

* En el siguiente bloque, presiona **q**
* Copia el contenido de `logs/YYYY-MM-DD_worklog.md` y pégalo en tu reporte

---

## Nota final

Este proyecto está pensado para ser:

* Simple de usar todos los días
* Predecible (sin automatismos peligrosos)
* Fácil de mantener y extender

Si más adelante necesitas exportes semanales o formatos específicos para Azure DevOps,
solo hay que extender el módulo `exporter.py`.

```
```
