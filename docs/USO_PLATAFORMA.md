# Uso de la plataforma (Modelo Single-Hospital)

La plataforma web permite operar Salud Chilecito como una aplicacion real desde
el navegador. Incluye dashboard, alta y edicion de pacientes, reserva de turnos,
cambio de estado, gestion de centros, consulta de medicos, carga de documentos
y vista previa de archivos adjuntos.

**Nuevo modelo Single-Hospital**: El sistema ahora incluye:
- Selección de especialidades por síntomas
- Configuración personalizada del hospital (logo, colores, mensaje de bienvenida)
- Precios por tipo de consulta y especialidad
- Disponibilidad mejorada con horarios específicos

## Modos de uso

| Modo | Cuando usarlo | Datos |
|---|---|---|
| Demo web JSON | Para usar la plataforma sin preparar Oracle | `runtime/salud_chilecito_data.json` |
| Oracle XE | Para usar la base relacional completa | Oracle XE en Docker |

El modo demo se inicia siempre. Oracle puede levantarse en paralelo para validar
la base y el DAO.

## Windows

Requisitos oficiales:

- Git for Windows: <https://gitforwindows.org/>
- Python 3.12+: <https://www.python.org/downloads/windows/>
- Docker Desktop: <https://www.docker.com/products/docker-desktop/>

Abrir PowerShell en la carpeta del repo:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\windows\01_instalar.ps1
.\scripts\windows\02_iniciar_plataforma.ps1
```

Ese script levanta Docker, intenta preparar Oracle automaticamente y abre la web.
Si Oracle no llega a iniciar, la plataforma igual queda usable en modo demo JSON.

Abrir en el navegador:

```text
http://localhost:8000
```

Para usar la plataforma conversacional:

```text
http://localhost:8000/bot
```

Para cargar Oracle:

```powershell
.\scripts\windows\03_cargar_oracle.ps1
```

## Ubuntu

Instalar dependencias del sistema:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip docker.io docker-compose-plugin
sudo usermod -aG docker $USER
```

Abrir una terminal en la carpeta del repo:

```bash
bash scripts/ubuntu/01_instalar.sh
```

Cerrar sesion y volver a entrar si el script agrego el usuario al grupo Docker.
Luego:

```bash
bash scripts/ubuntu/02_iniciar_plataforma.sh
```

Ese script levanta Docker, intenta preparar Oracle automaticamente y abre la web.
Si Oracle no llega a iniciar, la plataforma igual queda usable en modo demo JSON.

Abrir:

```text
http://localhost:8000
```

Para usar la plataforma conversacional:

```text
http://localhost:8000/bot
```

Para cargar Oracle:

```bash
bash scripts/ubuntu/03_cargar_oracle.sh
```

## Uso operativo

1. Entrar a `Turnos` para revisar disponibilidad por medico, dia, horario,
   cupos y precio estimado.
2. **NUEVO**: Al crear un turno, seleccionar un síntoma para autocompletar la
   especialidad y médico recomendado.
3. Crear reservas, editar horarios/datos, cambiar estados o eliminar un turno
   cargado por error.
4. Entrar a `Pacientes` para dar de alta un paciente nuevo o editar datos si se
   cargo mal DNI, telefono, obra social o distrito.
5. Entrar a `Centros` para crear o editar centros, distritos, telefonos y tipo
   de institucion.
6. Entrar a `Documentos` para adjuntar ordenes, estudios, recetas o imagenes y
   usar `Ver documento` para abrir su informacion, imagen, PDF o texto guardado.
7. Usar el buscador superior para filtrar registros por paciente, medico,
   centro, DNI, distrito o estado.

## Uso con Bot IA

La segunda plataforma esta en `http://localhost:8000/bot`. Permite operar el
sistema por chat sin recorrer formularios.

Ejemplos:

```text
listar pacientes
mostrar horarios disponibles y precios
listar sintomas
que especialidad para dolor de pecho
que doctor para fiebre
crear paciente nombre Ana Diaz dni 50111222 telefono 3825-111222 distrito Chilecito obra social APOS
editar paciente 1 telefono 3825-999000
crear turno paciente 1 medico 1 fecha 2026-06-20 hora 09:30 motivo dolor de pecho
editar turno 1 fecha 2026-06-21 hora 10:00 motivo control reprogramado
eliminar turno 2
crear documento paciente 1 tipo ESTUDIO archivo resultado.txt contenido Resultado normal
ver documento 1
```

Guia completa: [BOT_IA.md](BOT_IA.md).

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
python -m pytest -q
```

Abrir notebook de demostracion:

Windows:

```powershell
.\scripts\windows\04_abrir_notebook.ps1
```

Ubuntu:

```bash
bash scripts/ubuntu/04_abrir_notebook.sh
```
