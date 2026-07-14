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
