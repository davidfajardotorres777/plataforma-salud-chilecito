"""
Módulo de generación de reportes para Plataforma Salud Chilecito
================================================================
Proporciona funcionalidad de generación de reportes y estadísticas.

Características:
- Reportes de turnos
- Reportes de pacientes
- Reportes de médicos
- Reportes financieros
- Exportación a CSV y JSON

Uso básico:
    from report_generator import ReportGenerator
    
    generator = ReportGenerator()
    
    # Generar reporte de turnos
    reporte = generator.generar_reporte_turnos(
        fecha_inicio="2024-01-01",
        fecha_fin="2024-01-31"
    )
    
    # Exportar a CSV
    generator.exportar_csv(reporte, "reporte_turnos.csv")
"""

import csv
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from collections import defaultdict


class ReportGenerator:
    """
    Generador de reportes para la plataforma.
    
    Proporciona métodos para generar reportes y estadísticas
    de las operaciones del hospital.
    """
    
    def __init__(self):
        """
        Inicializa una nueva instancia del generador de reportes.
        """
        from dao_mongodb import SaludDAO
        self.dao = SaludDAO()
    
    def generar_reporte_turnos(
        self,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
        centro_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Genera un reporte de turnos.
        
        Args:
            fecha_inicio: Fecha de inicio (YYYY-MM-DD)
            fecha_fin: Fecha de fin (YYYY-MM-DD)
            centro_id: ID del centro (opcional)
        
        Returns:
            dict: Reporte de turnos
        """
        db = self.dao._get_db()
        
        # Construir query
        query = {}
        if fecha_inicio or fecha_fin:
            query["fecha_turno"] = {}
            if fecha_inicio:
                query["fecha_turno"]["$gte"] = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            if fecha_fin:
                query["fecha_turno"]["$lte"] = datetime.strptime(fecha_fin, "%Y-%m-%d")
        
        if centro_id:
            query["centro_id"] = str(centro_id)
        
        # Obtener turnos
        turnos = list(db["turnos"].find(query))
        
        # Calcular estadísticas
        total_turnos = len(turnos)
        turnos_por_estado = defaultdict(int)
        turnos_por_especialidad = defaultdict(int)
        turnos_por_medico = defaultdict(int)
        
        for turno in turnos:
            turnos_por_estado[turno.get("estado", "desconocido")] += 1
            
            # Obtener especialidad del médico
            medico = db["medicos"].find_one({"_id": turno.get("medico_id")})
            if medico:
                especialidad = db["especialidades"].find_one({"_id": medico.get("especialidad_id")})
                if especialidad:
                    turnos_por_especialidad[especialidad.get("nombre", "desconocido")] += 1
                turnos_por_medico[medico.get("nombre", "desconocido")] += 1
        
        return {
            "tipo": "reporte_turnos",
            "fecha_generacion": datetime.now().isoformat(),
            "periodo": {
                "inicio": fecha_inicio,
                "fin": fecha_fin
            },
            "estadisticas": {
                "total_turnos": total_turnos,
                "turnos_por_estado": dict(turnos_por_estado),
                "turnos_por_especialidad": dict(turnos_por_especialidad),
                "turnos_por_medico": dict(turnos_por_medico)
            },
            "datos": turnos
        }
    
    def generar_reporte_pacientes(
        self,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
        centro_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Genera un reporte de pacientes.
        
        Args:
            fecha_inicio: Fecha de inicio (YYYY-MM-DD)
            fecha_fin: Fecha de fin (YYYY-MM-DD)
            centro_id: ID del centro (opcional)
        
        Returns:
            dict: Reporte de pacientes
        """
        db = self.dao._get_db()
        
        # Construir query
        query = {}
        if fecha_inicio or fecha_fin:
            query["fecha_alta"] = {}
            if fecha_inicio:
                query["fecha_alta"]["$gte"] = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            if fecha_fin:
                query["fecha_alta"]["$lte"] = datetime.strptime(fecha_fin, "%Y-%m-%d")
        
        if centro_id:
            query["centro_id"] = str(centro_id)
        
        # Obtener pacientes
        pacientes = list(db["pacientes"].find(query))
        
        # Calcular estadísticas
        total_pacientes = len(pacientes)
        pacientes_por_distrito = defaultdict(int)
        pacientes_por_obra_social = defaultdict(int)
        
        for paciente in pacientes:
            pacientes_por_distrito[paciente.get("distrito", "desconocido")] += 1
            pacientes_por_obra_social[paciente.get("obra_social", "sin_obra_social")] += 1
        
        return {
            "tipo": "reporte_pacientes",
            "fecha_generacion": datetime.now().isoformat(),
            "periodo": {
                "inicio": fecha_inicio,
                "fin": fecha_fin
            },
            "estadisticas": {
                "total_pacientes": total_pacientes,
                "pacientes_por_distrito": dict(pacientes_por_distrito),
                "pacientes_por_obra_social": dict(pacientes_por_obra_social)
            },
            "datos": pacientes
        }
    
    def generar_reporte_medicos(
        self,
        centro_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Genera un reporte de médicos.
        
        Args:
            centro_id: ID del centro (opcional)
        
        Returns:
            dict: Reporte de médicos
        """
        db = self.dao._get_db()
        
        # Construir query
        query = {}
        if centro_id:
            query["centro_id"] = str(centro_id)
        
        # Obtener médicos
        medicos = list(db["medicos"].find(query))
        
        # Calcular estadísticas
        total_medicos = len(medicos)
        medicos_por_especialidad = defaultdict(int)
        
        for medico in medicos:
            especialidad = db["especialidades"].find_one({"_id": medico.get("especialidad_id")})
            if especialidad:
                medicos_por_especialidad[especialidad.get("nombre", "desconocido")] += 1
        
        # Calcular turnos por médico
        turnos_por_medico = {}
        for medico in medicos:
            medico_id = str(medico["_id"])
            turnos_count = db["turnos"].count_documents({"medico_id": ObjectId(medico_id)})
            turnos_por_medico[medico.get("nombre", "desconocido")] = turnos_count
        
        return {
            "tipo": "reporte_medicos",
            "fecha_generacion": datetime.now().isoformat(),
            "estadisticas": {
                "total_medicos": total_medicos,
                "medicos_por_especialidad": dict(medicos_por_especialidad),
                "turnos_por_medico": turnos_por_medico
            },
            "datos": medicos
        }
    
    def generar_reporte_financiero(
        self,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Genera un reporte financiero.
        
        Args:
            fecha_inicio: Fecha de inicio (YYYY-MM-DD)
            fecha_fin: Fecha de fin (YYYY-MM-DD)
        
        Returns:
            dict: Reporte financiero
        """
        db = self.dao._get_db()
        
        # Construir query
        query = {}
        if fecha_inicio or fecha_fin:
            query["fecha_turno"] = {}
            if fecha_inicio:
                query["fecha_turno"]["$gte"] = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            if fecha_fin:
                query["fecha_turno"]["$lte"] = datetime.strptime(fecha_fin, "%Y-%m-%d")
        
        # Obtener turnos completados
        query["estado"] = "completado"
        turnos = list(db["turnos"].find(query))
        
        # Calcular estadísticas financieras
        total_ingresos = 0
        ingresos_por_especialidad = defaultdict(float)
        
        for turno in turnos:
            precio = turno.get("precio_consulta", 0)
            total_ingresos += precio
            
            # Obtener especialidad del médico
            medico = db["medicos"].find_one({"_id": turno.get("medico_id")})
            if medico:
                especialidad = db["especialidades"].find_one({"_id": medico.get("especialidad_id")})
                if especialidad:
                    ingresos_por_especialidad[especialidad.get("nombre", "desconocido")] += precio
        
        return {
            "tipo": "reporte_financiero",
            "fecha_generacion": datetime.now().isoformat(),
            "periodo": {
                "inicio": fecha_inicio,
                "fin": fecha_fin
            },
            "estadisticas": {
                "total_ingresos": total_ingresos,
                "total_turnos_completados": len(turnos),
                "promedio_por_turno": total_ingresos / len(turnos) if turnos else 0,
                "ingresos_por_especialidad": dict(ingresos_por_especialidad)
            },
            "datos": turnos
        }
    
    def exportar_csv(self, reporte: Dict[str, Any], nombre_archivo: str) -> bool:
        """
        Exporta un reporte a CSV.
        
        Args:
            reporte: Reporte a exportar
            nombre_archivo: Nombre del archivo CSV
        
        Returns:
            bool: True si se exportó exitosamente
        """
        try:
            datos = reporte.get("datos", [])
            if not datos:
                return False
            
            # Obtener claves del primer documento
            claves = list(datos[0].keys())
            
            with open(nombre_archivo, 'w', newline='', encoding='utf-8') as archivo:
                writer = csv.DictWriter(archivo, fieldnames=claves)
                writer.writeheader()
                writer.writerows(datos)
            
            return True
        except Exception as e:
            print(f"Error al exportar CSV: {e}")
            return False
    
    def exportar_json(self, reporte: Dict[str, Any], nombre_archivo: str) -> bool:
        """
        Exporta un reporte a JSON.
        
        Args:
            reporte: Reporte a exportar
            nombre_archivo: Nombre del archivo JSON
        
        Returns:
            bool: True si se exportó exitosamente
        """
        try:
            with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
                json.dump(reporte, archivo, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"Error al exportar JSON: {e}")
            return False
    
    def cerrar(self):
        """Cierra la conexión con la base de datos."""
        self.dao.cerrar()
