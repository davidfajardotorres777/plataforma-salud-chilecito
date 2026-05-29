# Plataforma conversacional con Bot IA

El proyecto tiene dos formas de uso:

- Panel grafico: `http://localhost:8000`
- Bot IA conversacional: `http://localhost:8000/bot`

El bot trabaja sobre los mismos datos de la demo JSON. Si se crea un paciente,
se edita un turno o se adjunta un documento desde el chat, el cambio tambien se
ve en el panel grafico.

## Iniciar en Windows

Abrir PowerShell en la carpeta del repositorio:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
scripts\windows\02_iniciar_plataforma.ps1
```

Luego abrir:

```text
http://localhost:8000/bot
```

Tambien se puede iniciar manualmente:

```powershell
python -m src.webapp.server
```

## Iniciar en Ubuntu

Abrir una terminal en la carpeta del repositorio:

```bash
bash scripts/ubuntu/02_iniciar_plataforma.sh
```

Luego abrir:

```text
http://localhost:8000/bot
```

Tambien se puede iniciar manualmente:

```bash
python3 -m src.webapp.server
```

## Comandos que entiende

Resumen:

```text
resumen
```

Listar datos:

```text
listar pacientes
listar centros
listar medicos
listar turnos
listar documentos
```

Crear paciente:

```text
crear paciente nombre Ana Diaz dni 50111222 telefono 3825-111222 distrito Chilecito obra social APOS
```

Editar paciente:

```text
editar paciente 1 telefono 3825-999000 distrito Nonogasta
```

Crear centro:

```text
crear centro nombre Centro Demo direccion Calle 1 distrito Vichigasta telefono 3825-222333 tipo PUBLICO
```

Editar centro:

```text
editar centro 1 telefono 3825-000111
```

Crear turno:

```text
crear turno paciente 1 medico 1 fecha 2026-06-20 hora 09:30 motivo control
```

Editar turno:

```text
editar turno 1 fecha 2026-06-21 hora 10:00 motivo control reprogramado
```

Cambiar estado de turno:

```text
confirmar turno 1
cancelar turno 1
estado turno 1 atendido
```

Eliminar turno:

```text
eliminar turno 2
```

Crear documento de texto:

```text
crear documento paciente 1 tipo ESTUDIO archivo resultado.txt contenido Resultado normal
```

Ver documento:

```text
ver documento 1
```

## Notas importantes

- No hace falta instalar una API externa de IA.
- No hace falta una clave de OpenAI ni internet para usar el bot.
- El bot usa reglas locales para interpretar comandos frecuentes de la
  plataforma y ejecuta acciones reales contra `runtime/salud_chilecito_data.json`.
- Para cargar imagenes o PDF desde archivos locales, conviene usar el panel
  grafico en `http://localhost:8000`; despues se pueden consultar desde el bot
  con `ver documento ID`.
