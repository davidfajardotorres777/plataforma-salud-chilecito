# Uso de la plataforma grafica

La plataforma web permite que el profesor use el proyecto como una aplicacion
real desde el navegador. Incluye dashboard, alta de pacientes, reserva de
turnos, cambio de estado, consulta de centros/medicos y carga de documentos.

## Modos de uso

| Modo | Cuando usarlo | Datos |
|---|---|---|
| Demo web JSON | Para mostrar la plataforma sin preparar Oracle | `runtime/salud_chilecito_data.json` |
| Oracle BD II | Para evaluar scripts, roles, tablespaces y DAOs | Oracle XE en Docker |

El modo demo se inicia siempre. Oracle puede levantarse en paralelo para validar
la parte de Base de Datos II.

## Windows

Abrir PowerShell en la carpeta del repo:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
scripts\windows\01_instalar.ps1
scripts\windows\02_iniciar_plataforma.ps1
```

Abrir en el navegador:

```text
http://localhost:8000
```

Para cargar Oracle con SQL*Plus:

```powershell
scripts\windows\03_cargar_oracle.ps1
```

Si no hay SQL*Plus, usar SQL Developer y ejecutar los archivos `sql/01` a
`sql/07` en orden.

## Ubuntu

Abrir una terminal en la carpeta del repo:

```bash
bash scripts/ubuntu/01_instalar.sh
```

Cerrar sesion y volver a entrar si el script agrego el usuario al grupo Docker.
Luego:

```bash
bash scripts/ubuntu/02_iniciar_plataforma.sh
```

Abrir:

```text
http://localhost:8000
```

Para cargar Oracle con SQL*Plus:

```bash
bash scripts/ubuntu/03_cargar_oracle.sh
```

## Uso operativo

1. Entrar a `Turnos` para crear reservas y cambiar estados.
2. Entrar a `Pacientes` para dar de alta un paciente nuevo.
3. Entrar a `Centros` para ver centros, distritos, medicos y especialidades.
4. Entrar a `Documentos` para adjuntar ordenes, estudios, recetas o imagenes.
5. Usar el buscador superior para filtrar registros por paciente, medico,
   centro, DNI, distrito o estado.

## Archivos que se modifican durante la demo

- `runtime/salud_chilecito_data.json`: datos editables de la demo.
- `runtime/uploads/`: documentos adjuntos desde la interfaz.

Ambas rutas estan ignoradas por Git para no subir datos sensibles.

## Comandos utiles

Iniciar solo la web:

```bash
python -m src.webapp.server
```

Reiniciar los datos demo desde la interfaz:

```text
Boton "Reiniciar demo"
```

Ejecutar tests:

```bash
pytest -q
```
