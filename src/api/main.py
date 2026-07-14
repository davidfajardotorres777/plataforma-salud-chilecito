from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dao_mongodb import SaludDAO
from src.api import auth as api_auth

app = FastAPI(title="Salud Chilecito API")

# Allow CORS for demo frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

dao = SaludDAO()

@app.get("/api/ping")
def ping():
    return {"status": dao.ping()}

@app.post('/api/auth/token')
def login_for_access_token(form_data: dict):
    """Accepts JSON {"email":..., "password":...} and returns access token."""
    email = form_data.get('email')
    password = form_data.get('password')
    user = api_auth.authenticate_user(email, password)
    if not user:
        raise HTTPException(status_code=401, detail='Incorrect email or password')
    access_token = api_auth.create_access_token({"sub": str(user.get('_id'))})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get('/api/auth/me')
def read_users_me(current_user=Depends(api_auth.get_current_user)):
    # hide password hash
    user = dict(current_user)
    user.pop('password_hash', None)
    return user

# ---------------------- Dashboard & catalog endpoints --------------------

@app.get('/api/dashboard')
def api_dashboard(centro_id: int = None, slug: str = None):
    """Aggregated dashboard response used by the static frontend."""
    # Basic aggregates from DAO
    centros = dao.listar_centros()
    pacientes = dao.listar_pacientes()
    medicos = []
    for c in centros:
        try:
            mids = dao.listar_medicos_por_centro(str(c.get('_id') or c.get('id')))
            # attach centro info to medicos
            for m in mids:
                m['centro'] = c
            medicos.extend(mids)
        except Exception:
            continue
    especialidades = dao.listar_especialidades()
    sintomas = dao.listar_sintomas()
    turnos = dao.listar_turnos_proximos(limit=200)

    # disponibilidad: naive view from medicos (placeholder)
    disponibilidad = []
    for m in medicos:
        disponibilidad.append({
            "medico": {"id": m.get('_id') or m.get('id'), "nombre": m.get('nombre'), "centro_id": m.get('centro', {}).get('_id') or m.get('centro', {}).get('id')},
            "precio_estimado": 0,
            "horarios": []
        })

    # metrics
    metricas = {
        "centros": len(centros),
        "pacientes": len(pacientes),
        "turnos_pendientes": sum(1 for t in turnos if t.get('estado') == 'PENDIENTE'),
        "turnos_confirmados": sum(1 for t in turnos if t.get('estado') == 'CONFIRMADO'),
        "documentos": 0,
    }

    dashboard = {
        "centros": centros,
        "pacientes": pacientes,
        "medicos": medicos,
        "especialidades": especialidades,
        "sintomas": sintomas,
        "turnos": turnos,
        "disponibilidad": disponibilidad,
        "metricas": metricas,
    }

    # Filter by centro_id if provided
    if centro_id:
        dashboard['centros'] = [c for c in dashboard['centros'] if int(c.get('id') or c.get('_id', 0)) == int(centre_id := centro_id)]
        dashboard['medicos'] = [m for m in dashboard['medicos'] if int(m.get('centro', {}).get('id') or m.get('centro', {}).get('_id', 0)) == int(centre_id)]
        dashboard['pacientes'] = [p for p in dashboard['pacientes'] if int(p.get('centro_id') or 0) == int(centre_id)]
        dashboard['turnos'] = [t for t in dashboard['turnos'] if int(t.get('centro_id') or 0) == int(centre_id)]
        dashboard['disponibilidad'] = [d for d in dashboard['disponibilidad'] if int(d.get('medico', {}).get('centro_id') or 0) == int(centre_id)]

    return dashboard

@app.get('/api/medicos')
def api_medicos():
    centros = dao.listar_centros()
    medicos = []
    for c in centros:
        mids = dao.listar_medicos_por_centro(str(c.get('_id') or c.get('id')))
        for m in mids:
            m['centro'] = c
            medicos.append(m)
    return medicos

@app.get('/api/medicos/disponibilidad')
def api_medico_disponibilidad(medico_id: int):
    # Placeholder: return empty horarios or compute from agendas if available
    return []

@app.get('/api/disponibilidad')
def api_disponibilidad(centro_id: int = None, especialidad_id: int = None, medico_id: int = None):
    # Placeholder implementation using medicos list
    medicos = []
    for c in dao.listar_centros():
        mids = dao.listar_medicos_por_centro(str(c.get('_id') or c.get('id')))
        for m in mids:
            m['centro'] = c
            medicos.append(m)
    results = []
    for m in medicos:
        if centro_id and int(m.get('centro', {}).get('id') or m.get('centro', {}).get('_id', 0)) != int(centre_id := centro_id):
            continue
        results.append({
            'medico': {'id': m.get('_id') or m.get('id'), 'nombre': m.get('nombre'), 'centro_id': m.get('centro', {}).get('id') or m.get('centro', {}).get('_id')},
            'precio_estimado': 0,
            'horarios': [],
        })
    return results

@app.get('/api/sintomas')
def api_sintomas():
    return dao.listar_sintomas()

@app.get('/api/buscar-especialidad-por-sintoma')
def api_buscar_especialidad_por_sintoma(sintoma: str):
    res = dao.buscar_especialidad_por_sintoma(sintoma)
    return res or {}

@app.get('/api/configuracion-hospital')
def api_config():
    try:
        return dao.obtener_configuracion_hospital()
    except Exception:
        return {}

@app.get('/api/precios-especialidad')
def api_precios_especialidad(centro_id: int, especialidad_id: int):
    try:
        return dao.obtener_precios_por_especialidad(int(centro_id), int(especialidad_id))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------------- Turnos CRUD --------------------

@app.get('/api/turnos')
def api_turnos(limit: int = 20):
    return dao.listar_turnos_proximos(limit=limit)

@app.post('/api/turnos')
def api_reservar_turno(turno: dict):
    from db_models import Turno
    t = Turno(**turno)
    return {"id": dao.reservar_turno(t)}

@app.post('/api/turnos/{turno_id}/estado')
def api_actualizar_estado_turno(turno_id: str, payload: dict):
    estado = payload.get('estado')
    if not estado:
        raise HTTPException(status_code=400, detail='estado requerido')
    # Use dao to update
    updated = dao.actualizar_estado_turno(turno_id, estado)
    return {"ok": bool(updated)}

@app.post('/api/turnos/{turno_id}/eliminar')
def api_eliminar_turno(turno_id: str):
    ok = dao.eliminar_turno(turno_id)
    return {"ok": bool(ok)}

# ---------------------- Documentos --------------------

@app.get('/api/documentos/{documento_id}')
def api_documento(documento_id: int):
    doc = dao.get_document(int(documento_id)) if hasattr(dao, 'get_document') else {}
    return doc or {}

@app.get("/api/centros")
def listar_centros(distrito: str = None):
    try:
        return dao.listar_centros(distrito=distrito)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/centros")
def crear_centro(centro: dict):
    try:
        from db_models import CentroSalud
        c = CentroSalud(**centro)
        return {"id": dao.crear_centro(c)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/pacientes")
def listar_pacientes():
    try:
        return dao.listar_pacientes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pacientes")
def crear_paciente(paciente: dict):
    try:
        from db_models import Paciente
        p = Paciente(**paciente)
        return {"id": dao.crear_paciente(p)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/turnos")
def listar_turnos(limit: int = 20):
    try:
        return dao.listar_turnos_proximos(limite=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/turnos")
def reservar_turno(turno: dict):
    try:
        from db_models import Turno
        t = Turno(**turno)
        return {"id": dao.reservar_turno(t)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
