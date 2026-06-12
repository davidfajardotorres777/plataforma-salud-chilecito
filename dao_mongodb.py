"""
SaludDAO - Capa de acceso a datos para Plataforma Salud Chilecito (MongoDB)
=========================================================================
Concentra todas las operaciones contra MongoDB en una sola clase.
Accesible desde git y desde Jupyter Notebook.

Esta clase implementa el patrón DAO (Data Access Object) para abstraer
la complejidad de las operaciones de base de datos MongoDB y proporcionar una
interfaz limpia y consistente para el dominio de salud.

Características principales:
- Gestión de centros de salud, médicos, pacientes y turnos
- Selección por síntomas para derivación automática a especialidades
- Configuración personalizada por hospital (modelo single-hospital)
- Cálculo de precios estimados por especialidad y tipo de consulta
- Disponibilidad de turnos en tiempo real con horarios específicos
- Sistema de autenticación con registro de pacientes
- Verificación de email

Uso básico:
    from dao_mongodb import SaludDAO
    from db_models import Paciente, Usuario

    dao = SaludDAO()
    
    # Listar centros
    centros = dao.listar_centros()
    print(f"Centros: {len(centros)}")
    
    # Crear paciente
    paciente = Paciente(
        dni="12345678",
        nombre="Juan Pérez",
        telefono="3825-123456",
        distrito="Chilecito"
    )
    paciente_id = dao.crear_paciente(paciente)
    
    # Registrar usuario
    usuario = Usuario(
        email="juan@example.com",
        password_hash="hash_aqui",
        rol=Rol.PACIENTE,
        nombre="Juan Pérez",
        paciente_id=paciente_id
    )
    usuario_id = dao.registrar_usuario(usuario)
    
    dao.cerrar()

Autor: Alesandro David Fajardo / Kevin Facundo Nunez
Universidad: Universidad Nacional de Chilecito
Año: 2026
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import hashlib
import secrets
from bson import ObjectId

from config_vars import get_mongo_config
from db_models import (
    Paciente, CentroSalud, Medico, Turno, AgendaMedico,
    Especialidad, HistorialClinico, Sintoma, ConfiguracionHospital, Usuario, Rol,
    Receta, MedicamentoRecetado, EstudioMedico, TipoEstudio, EstadoEstudio,
    Notificacion, TipoNotificacion, EstadoNotificacion, Internacion, TipoInternacion, EstadoInternacion
)


class SaludDAO:
    """
    Interfaz principal contra MongoDB para el dominio de salud.
    
    Esta clase proporciona métodos para realizar todas las operaciones
    de base de datos necesarias para la plataforma Salud Chilecito,
    incluyendo gestión de centros, médicos, pacientes, turnos, síntomas,
    configuración del hospital, autenticación y más.
    """
    
    def __init__(self):
        """
        Inicializa una nueva instancia del DAO.
        
        Carga la configuración de la base de datos desde config_vars
        y prepara la conexión a MongoDB.
        """
        config = get_mongo_config()
        self._config = config
        self._client = None
        self._db = None
    
    def _get_client(self):
        """Obtiene el cliente de MongoDB (lazy loading)."""
        if self._client is None:
            try:
                from pymongo import MongoClient
                self._client = MongoClient(self._config["uri"])
                self._db = self._client[self._config["db_name"]]
            except ImportError:
                raise RuntimeError(
                    "Falta instalar pymongo. Ejecuta: pip install pymongo"
                )
        return self._client
    
    def _get_db(self):
        """Obtiene la base de datos MongoDB."""
        if self._db is None:
            self._get_client()
        return self._db
    
    def ping(self) -> str:
        """
        Verifica la conexión con la base de datos.
        
        Returns:
            str: "OK" si la conexión funciona, "SIN_RESPUESTA" en caso contrario
        """
        try:
            db = self._get_db()
            db.command('ping')
            return "OK"
        except Exception:
            return "SIN_RESPUESTA"
    
    def contar(self, coleccion: str) -> int:
        """
        Cuenta el número de documentos en una colección.
        
        Args:
            coleccion: Nombre de la colección a contar
        
        Returns:
            int: Número de documentos en la colección
        """
        db = self._get_db()
        return db[coleccion].count_documents({})
    
    def cerrar(self):
        """Cierra la conexión con MongoDB."""
        if self._client is not None:
            self._client.close()
            self._client = None
            self._db = None
    
    # ======================================================================
    # USUARIOS Y AUTENTICACIÓN
    # ======================================================================
    
    def registrar_usuario(self, usuario: Usuario) -> str:
        """
        Registra un nuevo usuario en el sistema.
        
        Args:
            usuario: Objeto Usuario con los datos del usuario
        
        Returns:
            str: ID del usuario creado (MongoDB ObjectId)
        """
        db = self._get_db()
        
        # Generar token de verificación
        verification_token = secrets.token_urlsafe(32)
        
        doc = {
            "email": usuario.email,
            "password_hash": usuario.password_hash,
            "rol": usuario.rol.value,
            "nombre": usuario.nombre,
            "activo": usuario.activo,
            "verificado": usuario.verificado,
            "fecha_registro": usuario.fecha_registro or datetime.now(),
            "verification_token": verification_token,
        }
        
        if usuario.paciente_id:
            doc["paciente_id"] = ObjectId(usuario.paciente_id)
        if usuario.medico_id:
            doc["medico_id"] = ObjectId(usuario.medico_id)
        
        result = db["usuarios"].insert_one(doc)
        return str(result.inserted_id)
    
    def verificar_email(self, token: str) -> bool:
        """
        Verifica el email de un usuario usando el token.
        
        Args:
            token: Token de verificación
        
        Returns:
            bool: True si la verificación fue exitosa
        """
        db = self._get_db()
        
        result = db["usuarios"].update_one(
            {"verification_token": token, "verificado": False},
            {
                "$set": {
                    "verificado": True,
                    "fecha_verificacion": datetime.now(),
                    "verification_token": None
                }
            }
        )
        
        return result.modified_count > 0
    
    def obtener_usuario_por_email(self, email: str) -> Optional[Dict]:
        """
        Obtiene un usuario por su email.
        
        Args:
            email: Email del usuario
        
        Returns:
            dict | None: Datos del usuario si existe
        """
        db = self._get_db()
        return db["usuarios"].find_one({"email": email})
    
    def obtener_usuario_por_id(self, usuario_id: str) -> Optional[Dict]:
        """
        Obtiene un usuario por su ID.
        
        Args:
            usuario_id: ID del usuario (MongoDB ObjectId)
        
        Returns:
            dict | None: Datos del usuario si existe
        """
        db = self._get_db()
        return db["usuarios"].find_one({"_id": ObjectId(usuario_id)})
    
    # ======================================================================
    # CENTROS DE SALUD
    # ======================================================================
    
    def listar_centros(self, distrito: Optional[str] = None) -> List[Dict]:
        """
        Lista todos los centros de salud.
        
        Args:
            distrito: Filtrar por distrito (opcional)
        
        Returns:
            list[dict]: Lista de centros de salud
        """
        db = self._get_db()
        
        query = {}
        if distrito:
            query["distrito"] = distrito
        
        return list(db["centros"].find(query))
    
    def crear_centro(self, centro: CentroSalud) -> str:
        """
        Crea un nuevo centro de salud.
        
        Args:
            centro: Objeto CentroSalud con los datos del centro
        
        Returns:
            str: ID del centro creado (MongoDB ObjectId)
        """
        db = self._get_db()
        
        doc = {
            "nombre": centro.nombre,
            "direccion": centro.direccion,
            "distrito": centro.distrito,
            "tipo": centro.tipo,
            "telefono": centro.telefono,
            "email": centro.email,
            "activo": centro.activo,
            "fecha_creacion": centro.fecha_creacion or datetime.now(),
            "slug": centro.slug,
        }
        
        result = db["centros"].insert_one(doc)
        return str(result.inserted_id)
    
    # ======================================================================
    # PACIENTES
    # ======================================================================
    
    def obtener_paciente_por_dni(self, dni: str) -> Optional[Dict]:
        """
        Obtiene un paciente por su DNI.
        
        Args:
            dni: DNI del paciente
        
        Returns:
            dict | None: Datos del paciente si existe
        """
        db = self._get_db()
        return db["pacientes"].find_one({"dni": dni}, {"_id": 0})
    
    def listar_pacientes(self) -> List[Dict]:
        """
        Lista todos los pacientes.
        
        Returns:
            list[dict]: Lista de pacientes
        """
        db = self._get_db()
        return list(db["pacientes"].find({}, {"_id": 0}))
    
    def crear_paciente(self, paciente: Paciente) -> str:
        """
        Crea un nuevo paciente.
        
        Args:
            paciente: Objeto Paciente con los datos del paciente
        
        Returns:
            str: ID del paciente creado (MongoDB ObjectId)
        """
        db = self._get_db()
        
        doc = {
            "dni": paciente.dni,
            "nombre": paciente.nombre,
            "email": paciente.email,
            "telefono": paciente.telefono,
            "fecha_nacimiento": paciente.fecha_nacimiento,
            "obra_social": paciente.obra_social,
            "distrito": paciente.distrito,
            "centro_id": ObjectId(paciente.centro_id) if paciente.centro_id else None,
            "fecha_alta": paciente.fecha_alta or datetime.now(),
            "activo": paciente.activo,
        }
        
        result = db["pacientes"].insert_one(doc)
        return str(result.inserted_id)
    
    # ======================================================================
    # MÉDICOS
    # ======================================================================
    
    def listar_medicos_por_centro(self, centro_id: str) -> List[Dict]:
        """
        Lista médicos por centro.
        
        Args:
            centro_id: ID del centro (MongoDB ObjectId)
        
        Returns:
            list[dict]: Lista de médicos del centro
        """
        db = self._get_db()
        return list(db["medicos"].find(
            {"centro_id": ObjectId(centro_id)},
            {"_id": 0}
        ))
    
    def crear_medico(self, medico: Medico) -> str:
        """
        Crea un nuevo médico.
        
        Args:
            medico: Objeto Medico con los datos del médico
        
        Returns:
            str: ID del médico creado (MongoDB ObjectId)
        """
        db = self._get_db()
        
        doc = {
            "nombre": medico.nombre,
            "matricula": medico.matricula,
            "especialidad_id": ObjectId(medico.especialidad_id),
            "centro_id": ObjectId(medico.centro_id),
            "telefono": medico.telefono,
            "email": medico.email,
            "activo": medico.activo,
            "fecha_creacion": medico.fecha_creacion or datetime.now(),
        }
        
        result = db["medicos"].insert_one(doc)
        return str(result.inserted_id)
    
    # ======================================================================
    # ESPECIALIDADES
    # ======================================================================
    
    def listar_especialidades(self) -> List[Dict]:
        """
        Lista todas las especialidades.
        
        Returns:
            list[dict]: Lista de especialidades
        """
        db = self._get_db()
        return list(db["especialidades"].find({}))
    
    def crear_especialidad(self, especialidad: Especialidad) -> str:
        """
        Crea una nueva especialidad.
        
        Args:
            especialidad: Objeto Especialidad con los datos
        
        Returns:
            str: ID de la especialidad creada (MongoDB ObjectId)
        """
        db = self._get_db()
        
        doc = {
            "nombre": especialidad.nombre,
            "descripcion": especialidad.descripcion,
            "activa": especialidad.activa,
            "fecha_creacion": especialidad.fecha_creacion or datetime.now(),
        }
        
        result = db["especialidades"].insert_one(doc)
        return str(result.inserted_id)
    
    # ======================================================================
    # TURNOS
    # ======================================================================
    
    def listar_turnos_proximos(self, limite: int = 20) -> List[Dict]:
        """
        Lista los turnos próximos.
        
        Args:
            limite: Número máximo de turnos a retornar
        
        Returns:
            list[dict]: Lista de turnos próximos
        """
        db = self._get_db()
        return list(db["turnos"].find(
            {"fecha_turno": {"$gte": datetime.now()}},
            {"_id": 0}
        ).sort("fecha_turno", 1).limit(limite))
    
    def reservar_turno(self, turno: Turno) -> str:
        """
        Reserva un nuevo turno.
        
        Args:
            turno: Objeto Turno con los datos del turno
        
        Returns:
            str: ID del turno creado (MongoDB ObjectId)
        """
        db = self._get_db()
        
        doc = {
            "paciente_id": ObjectId(turno.paciente_id),
            "medico_id": ObjectId(turno.medico_id),
            "centro_id": ObjectId(turno.centro_id),
            "fecha_turno": turno.fecha_turno,
            "estado": turno.estado,
            "precio_consulta": turno.precio_consulta,
            "observaciones": turno.observaciones,
            "fecha_creacion": turno.fecha_creacion or datetime.now(),
        }
        
        result = db["turnos"].insert_one(doc)
        return str(result.inserted_id)
    
    # ======================================================================
    # SÍNTOMAS
    # ======================================================================
    
    def listar_sintomas(self) -> List[Dict]:
        """
        Lista todos los síntomas.
        
        Returns:
            list[dict]: Lista de síntomas
        """
        db = self._get_db()
        return list(db["sintomas"].find(
            {"activo": True},
            {"_id": 0}
        ))
    
    def buscar_especialidad_por_sintoma(self, sintoma: str) -> Optional[Dict]:
        """
        Busca la especialidad recomendada según el síntoma.
        
        Args:
            sintoma: Descripción del síntoma
        
        Returns:
            dict | None: Información del síntoma y especialidad
        """
        db = self._get_db()
        
        # Buscar síntoma que coincida con la descripción
        sintoma_doc = db["sintomas"].find_one(
            {"descripcion": {"$regex": sintoma, "$options": "i"}, "activo": True},
            {"_id": 0}
        )
        
        if not sintoma_doc:
            return None
        
        # Obtener especialidad
        especialidad = db["especialidades"].find_one(
            {"_id": sintoma_doc["especialidad_id"]},
            {"_id": 0}
        )
        
        return {
            "sintoma": sintoma_doc,
            "especialidad": especialidad
        }
    
    # ======================================================================
    # RECETAS MÉDICAS
    # ======================================================================
    
    def crear_receta(self, receta: Receta) -> str:
        """
        Crea una nueva receta médica.
        
        Args:
            receta: Objeto Receta con los datos de la receta
        
        Returns:
            str: ID de la receta creada (MongoDB ObjectId)
        """
        db = self._get_db()
        
        # Convertir medicamentos a diccionarios
        medicamentos_list = []
        for med in receta.medicamentos:
            medicamentos_list.append({
                "nombre": med.nombre,
                "dosis": med.dosis,
                "frecuencia": med.frecuencia,
                "duracion": med.duracion,
                "instrucciones": med.instrucciones
            })
        
        doc = {
            "paciente_id": ObjectId(receta.paciente_id),
            "medico_id": ObjectId(receta.medico_id),
            "turno_id": ObjectId(receta.turno_id) if receta.turno_id else None,
            "medicamentos": medicamentos_list,
            "diagnostico": receta.diagnostico,
            "indicaciones": receta.indicaciones,
            "fecha_emision": receta.fecha_emision or datetime.now(),
            "activa": receta.activa,
        }
        
        result = db["recetas"].insert_one(doc)
        return str(result.inserted_id)
    
    def obtener_recetas_por_paciente(self, paciente_id: str) -> List[Dict]:
        """
        Obtiene todas las recetas de un paciente.
        
        Args:
            paciente_id: ID del paciente (MongoDB ObjectId)
        
        Returns:
            list[dict]: Lista de recetas del paciente
        """
        db = self._get_db()
        return list(db["recetas"].find(
            {"paciente_id": ObjectId(paciente_id)}
        ).sort("fecha_emision", -1))
    
    # ======================================================================
    # ESTUDIOS MÉDICOS
    # ======================================================================
    
    def crear_estudio_medico(self, estudio: EstudioMedico) -> str:
        """
        Crea un nuevo estudio médico.
        
        Args:
            estudio: Objeto EstudioMedico con los datos del estudio
        
        Returns:
            str: ID del estudio creado (MongoDB ObjectId)
        """
        db = self._get_db()
        
        doc = {
            "paciente_id": ObjectId(estudio.paciente_id),
            "medico_id": ObjectId(estudio.medico_id),
            "tipo_estudio": estudio.tipo_estudio.value,
            "descripcion": estudio.descripcion,
            "indicaciones": estudio.indicaciones,
            "fecha_solicitud": estudio.fecha_solicitud or datetime.now(),
            "fecha_realizacion": estudio.fecha_realizacion,
            "fecha_resultado": estudio.fecha_resultado,
            "resultado": estudio.resultado,
            "estado": estudio.estado.value,
            "archivo_url": estudio.archivo_url,
            "turno_id": ObjectId(estudio.turno_id) if estudio.turno_id else None,
        }
        
        result = db["estudios_medicos"].insert_one(doc)
        return str(result.inserted_id)
    
    def obtener_estudios_por_paciente(self, paciente_id: str) -> List[Dict]:
        """
        Obtiene todos los estudios de un paciente.
        
        Args:
            paciente_id: ID del paciente (MongoDB ObjectId)
        
        Returns:
            list[dict]: Lista de estudios del paciente
        """
        db = self._get_db()
        return list(db["estudios_medicos"].find(
            {"paciente_id": ObjectId(paciente_id)}
        ).sort("fecha_solicitud", -1))
    
    def actualizar_estado_estudio(self, estudio_id: str, estado: EstadoEstudio, resultado: Optional[str] = None) -> bool:
        """
        Actualiza el estado de un estudio médico.
        
        Args:
            estudio_id: ID del estudio (MongoDB ObjectId)
            estado: Nuevo estado del estudio
            resultado: Resultado del estudio (opcional)
        
        Returns:
            bool: True si se actualizó exitosamente
        """
        db = self._get_db()
        
        update_data = {
            "$set": {
                "estado": estado.value,
                "fecha_resultado": datetime.now() if estado == EstadoEstudio.COMPLETADO else None
            }
        }
        
        if resultado:
            update_data["$set"]["resultado"] = resultado
        
        result = db["estudios_medicos"].update_one(
            {"_id": ObjectId(estudio_id)},
            update_data
        )
        
        return result.modified_count > 0
    
    # ======================================================================
    # NOTIFICACIONES
    # ======================================================================
    
    def crear_notificacion(self, notificacion: Notificacion) -> str:
        """
        Crea una nueva notificación.
        
        Args:
            notificacion: Objeto Notificacion con los datos de la notificación
        
        Returns:
            str: ID de la notificación creada (MongoDB ObjectId)
        """
        db = self._get_db()
        
        doc = {
            "usuario_id": ObjectId(notificacion.usuario_id),
            "tipo": notificacion.tipo.value,
            "titulo": notificacion.titulo,
            "mensaje": notificacion.mensaje,
            "estado": notificacion.estado.value,
            "fecha_creacion": notificacion.fecha_creacion or datetime.now(),
            "fecha_envio": notificacion.fecha_envio,
            "fecha_lectura": notificacion.fecha_lectura,
            "metadata": notificacion.metadata,
        }
        
        result = db["notificaciones"].insert_one(doc)
        return str(result.inserted_id)
    
    def obtener_notificaciones_por_usuario(self, usuario_id: str, no_leidas: bool = False) -> List[Dict]:
        """
        Obtiene las notificaciones de un usuario.
        
        Args:
            usuario_id: ID del usuario (MongoDB ObjectId)
            no_leidas: Si es True, solo retorna notificaciones no leídas
        
        Returns:
            list[dict]: Lista de notificaciones del usuario
        """
        db = self._get_db()
        
        query = {"usuario_id": ObjectId(usuario_id)}
        if no_leidas:
            query["estado"] = EstadoNotificacion.PENDIENTE.value
        
        return list(db["notificaciones"].find(query).sort("fecha_creacion", -1))
    
    def marcar_notificacion_leida(self, notificacion_id: str) -> bool:
        """
        Marca una notificación como leída.
        
        Args:
            notificacion_id: ID de la notificación (MongoDB ObjectId)
        
        Returns:
            bool: True si se actualizó exitosamente
        """
        db = self._get_db()
        
        result = db["notificaciones"].update_one(
            {"_id": ObjectId(notificacion_id)},
            {
                "$set": {
                    "estado": EstadoNotificacion.LEIDA.value,
                    "fecha_lectura": datetime.now()
                }
            }
        )
        
        return result.modified_count > 0
    
    # ======================================================================
    # INTERNACIONES
    # ======================================================================
    
    def crear_internacion(self, internacion: Internacion) -> str:
        """
        Crea una nueva internación.
        
        Args:
            internacion: Objeto Internacion con los datos de la internación
        
        Returns:
            str: ID de la internación creada (MongoDB ObjectId)
        """
        db = self._get_db()
        
        doc = {
            "paciente_id": ObjectId(internacion.paciente_id),
            "medico_id": ObjectId(internacion.medico_id),
            "centro_id": ObjectId(internacion.centro_id),
            "tipo": internacion.tipo.value,
            "motivo_ingreso": internacion.motivo_ingreso,
            "diagnostico_ingreso": internacion.diagnostico_ingreso,
            "fecha_ingreso": internacion.fecha_ingreso or datetime.now(),
            "fecha_alta": internacion.fecha_alta,
            "estado": internacion.estado.value,
            "habitacion": internacion.habitacion,
            "cama": internacion.cama,
            "diagnostico_egreso": internacion.diagnostico_egreso,
            "resumen_clinico": internacion.resumen_clinico,
        }
        
        result = db["internaciones"].insert_one(doc)
        return str(result.inserted_id)
    
    def obtener_internaciones_por_paciente(self, paciente_id: str) -> List[Dict]:
        """
        Obtiene todas las internaciones de un paciente.
        
        Args:
            paciente_id: ID del paciente (MongoDB ObjectId)
        
        Returns:
            list[dict]: Lista de internaciones del paciente
        """
        db = self._get_db()
        return list(db["internaciones"].find(
            {"paciente_id": ObjectId(paciente_id)}
        ).sort("fecha_ingreso", -1))
    
    def obtener_internaciones_activas(self, centro_id: Optional[str] = None) -> List[Dict]:
        """
        Obtiene las internaciones activas.
        
        Args:
            centro_id: ID del centro (opcional)
        
        Returns:
            list[dict]: Lista de internaciones activas
        """
        db = self._get_db()
        
        query = {"estado": EstadoInternacion.ACTIVA.value}
        if centro_id:
            query["centro_id"] = ObjectId(centro_id)
        
        return list(db["internaciones"].find(query).sort("fecha_ingreso", -1))
    
    def dar_alta_internacion(self, internacion_id: str, diagnostico_egreso: Optional[str] = None, resumen_clinico: Optional[str] = None) -> bool:
        """
        Da de alta una internación.
        
        Args:
            internacion_id: ID de la internación (MongoDB ObjectId)
            diagnostico_egreso: Diagnóstico al egreso (opcional)
            resumen_clinico: Resumen clínico (opcional)
        
        Returns:
            bool: True si se actualizó exitosamente
        """
        db = self._get_db()
        
        update_data = {
            "$set": {
                "estado": EstadoInternacion.ALTA_MEDICA.value,
                "fecha_alta": datetime.now()
            }
        }
        
        if diagnostico_egreso:
            update_data["$set"]["diagnostico_egreso"] = diagnostico_egreso
        if resumen_clinico:
            update_data["$set"]["resumen_clinico"] = resumen_clinico
        
        result = db["internaciones"].update_one(
            {"_id": ObjectId(internacion_id)},
            update_data
        )
        
        return result.modified_count > 0
