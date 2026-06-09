"""
Adaptadores para integración con sistemas hospitalarios existentes (HIS).

Permite conectar Salud Chilecito con diferentes sistemas mediante una interfaz común.
"""

import json
import requests
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from datetime import datetime


class BaseAdapter(ABC):
    """Clase base para todos los adaptadores de HIS."""
    
    def __init__(self, config: Dict):
        """
        Inicializa el adaptador con configuración.
        
        Args:
            config: Diccionario de configuración del adaptador
        """
        self.config = config
        self.base_url = config.get("base_url", "")
        self.api_key = config.get("api_key", "")
        self.timeout = config.get("timeout", 30)
    
    @abstractmethod
    def sync_patients(self, patients: List[Dict]) -> List[Dict]:
        """
        Sincroniza pacientes con el HIS.
        
        Args:
            patients: Lista de pacientes a sincronizar
        
        Returns:
            Lista de pacientes sincronizados con IDs del HIS
        """
        pass
    
    @abstractmethod
    def sync_doctors(self, doctors: List[Dict]) -> List[Dict]:
        """
        Sincroniza médicos con el HIS.
        
        Args:
            doctors: Lista de médicos a sincronizar
        
        Returns:
            Lista de médicos sincronizados con IDs del HIS
        """
        pass
    
    @abstractmethod
    def sync_appointments(self, appointments: List[Dict]) -> List[Dict]:
        """
        Sincroniza turnos con el HIS.
        
        Args:
            appointments: Lista de turnos a sincronizar
        
        Returns:
            Lista de turnos sincronizados con IDs del HIS
        """
        pass
    
    @abstractmethod
    def sync_schedules(self, schedules: List[Dict]) -> List[Dict]:
        """
        Sincroniza agendas con el HIS.
        
        Args:
            schedules: Lista de agendas a sincronizar
        
        Returns:
            Lista de agendas sincronizadas con IDs del HIS
        """
        pass
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Realiza una solicitud HTTP al HIS.
        
        Args:
            method: Método HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint del HIS
            data: Datos a enviar (opcional)
        
        Returns:
            Respuesta del HIS
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=self.timeout)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=self.timeout)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=self.timeout)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error al conectar con HIS: {str(e)}")


class RESTAdapter(BaseAdapter):
    """Adaptador genérico para sistemas HIS con API REST."""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.endpoints = config.get("endpoints", {})
        self.field_mappings = config.get("field_mappings", {})
    
    def _map_fields(self, data: Dict, direction: str = "to_his") -> Dict:
        """
        Mapea campos entre formatos de Salud Chilecito y el HIS.
        
        Args:
            data: Datos a mapear
            direction: "to_his" o "from_his"
        
        Returns:
            Datos mapeados
        """
        mapped = {}
        mappings = self.field_mappings.get(direction, {})
        
        for sc_field, his_field in mappings.items():
            if sc_field in data:
                mapped[his_field] = data[sc_field]
        
        return mapped
    
    def sync_patients(self, patients: List[Dict]) -> List[Dict]:
        """Sincroniza pacientes con el HIS mediante API REST."""
        endpoint = self.endpoints.get("patients", "/api/patients")
        synced_patients = []
        
        for patient in patients:
            try:
                # Mapear campos
                mapped_patient = self._map_fields(patient, "to_his")
                
                # Enviar al HIS
                response = self._make_request("POST", endpoint, mapped_patient)
                
                # Guardar el ID del HIS
                synced_patient = patient.copy()
                synced_patient["his_id"] = response.get("id")
                synced_patients.append(synced_patient)
                
            except Exception as e:
                print(f"Error sincronizando paciente {patient.get('dni')}: {str(e)}")
                # Continuar con el siguiente paciente
        
        return synced_patients
    
    def sync_doctors(self, doctors: List[Dict]) -> List[Dict]:
        """Sincroniza médicos con el HIS mediante API REST."""
        endpoint = self.endpoints.get("doctors", "/api/doctors")
        synced_doctors = []
        
        for doctor in doctors:
            try:
                mapped_doctor = self._map_fields(doctor, "to_his")
                response = self._make_request("POST", endpoint, mapped_doctor)
                
                synced_doctor = doctor.copy()
                synced_doctor["his_id"] = response.get("id")
                synced_doctors.append(synced_doctor)
                
            except Exception as e:
                print(f"Error sincronizando médico {doctor.get('nombre')}: {str(e)}")
        
        return synced_doctors
    
    def sync_appointments(self, appointments: List[Dict]) -> List[Dict]:
        """Sincroniza turnos con el HIS mediante API REST."""
        endpoint = self.endpoints.get("appointments", "/api/appointments")
        synced_appointments = []
        
        for appointment in appointments:
            try:
                mapped_appointment = self._map_fields(appointment, "to_his")
                response = self._make_request("POST", endpoint, mapped_appointment)
                
                synced_appointment = appointment.copy()
                synced_appointment["his_id"] = response.get("id")
                synced_appointments.append(synced_appointment)
                
            except Exception as e:
                print(f"Error sincronizando turno {appointment.get('id')}: {str(e)}")
        
        return synced_appointments
    
    def sync_schedules(self, schedules: List[Dict]) -> List[Dict]:
        """Sincroniza agendas con el HIS mediante API REST."""
        endpoint = self.endpoints.get("schedules", "/api/schedules")
        synced_schedules = []
        
        for schedule in schedules:
            try:
                mapped_schedule = self._map_fields(schedule, "to_his")
                response = self._make_request("POST", endpoint, mapped_schedule)
                
                synced_schedule = schedule.copy()
                synced_schedule["his_id"] = response.get("id")
                synced_schedules.append(synced_schedule)
                
            except Exception as e:
                print(f"Error sincronizando agenda {schedule.get('id')}: {str(e)}")
        
        return synced_schedules


class FHIRAdapter(BaseAdapter):
    """Adaptador para sistemas que implementan el estándar HL7 FHIR."""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.fhir_version = config.get("fhir_version", "R4")
    
    def _to_fhir_resource(self, resource_type: str, data: Dict) -> Dict:
        """
        Convierte datos de Salud Chilecito a recurso FHIR.
        
        Args:
            resource_type: Tipo de recurso FHIR (Patient, Practitioner, Appointment, etc.)
            data: Datos a convertir
        
        Returns:
            Recurso FHIR
        """
        fhir_resource = {
            "resourceType": resource_type,
            "id": data.get("id"),
            "meta": {
                "created": datetime.now().isoformat()
            }
        }
        
        if resource_type == "Patient":
            fhir_resource["name"] = [{
                "family": data.get("nombre", "").split(" ")[-1] if data.get("nombre") else "",
                "given": data.get("nombre", "").split(" ")[:-1] if data.get("nombre") else []
            }]
            fhir_resource["identifier"] = [{
                "system": "http://hospital.gov.ar/dni",
                "value": data.get("dni", "")
            }]
            fhir_resource["telecom"] = []
            if data.get("telefono"):
                fhir_resource["telecom"].append({
                    "system": "phone",
                    "value": data.get("telefono")
                })
        
        elif resource_type == "Practitioner":
            fhir_resource["name"] = [{
                "family": data.get("nombre", "").split(" ")[-1] if data.get("nombre") else "",
                "given": data.get("nombre", "").split(" ")[:-1] if data.get("nombre") else []
            }]
        
        elif resource_type == "Appointment":
            fhir_resource["status"] = "booked"
            fhir_resource["start"] = f"{data.get('fecha')}T{data.get('hora')}:00"
            fhir_resource["participant"] = []
        
        return fhir_resource
    
    def sync_patients(self, patients: List[Dict]) -> List[Dict]:
        """Sincroniza pacientes con el HIS mediante FHIR."""
        endpoint = f"/fhir/{self.fhir_version}/Patient"
        synced_patients = []
        
        for patient in patients:
            try:
                fhir_patient = self._to_fhir_resource("Patient", patient)
                response = self._make_request("POST", endpoint, fhir_patient)
                
                synced_patient = patient.copy()
                synced_patient["his_id"] = response.get("id")
                synced_patients.append(synced_patient)
                
            except Exception as e:
                print(f"Error sincronizando paciente FHIR {patient.get('dni')}: {str(e)}")
        
        return synced_patients
    
    def sync_doctors(self, doctors: List[Dict]) -> List[Dict]:
        """Sincroniza médicos con el HIS mediante FHIR."""
        endpoint = f"/fhir/{self.fhir_version}/Practitioner"
        synced_doctors = []
        
        for doctor in doctors:
            try:
                fhir_doctor = self._to_fhir_resource("Practitioner", doctor)
                response = self._make_request("POST", endpoint, fhir_doctor)
                
                synced_doctor = doctor.copy()
                synced_doctor["his_id"] = response.get("id")
                synced_doctors.append(synced_doctor)
                
            except Exception as e:
                print(f"Error sincronizando médico FHIR {doctor.get('nombre')}: {str(e)}")
        
        return synced_doctors
    
    def sync_appointments(self, appointments: List[Dict]) -> List[Dict]:
        """Sincroniza turnos con el HIS mediante FHIR."""
        endpoint = f"/fhir/{self.fhir_version}/Appointment"
        synced_appointments = []
        
        for appointment in appointments:
            try:
                fhir_appointment = self._to_fhir_resource("Appointment", appointment)
                response = self._make_request("POST", endpoint, fhir_appointment)
                
                synced_appointment = appointment.copy()
                synced_appointment["his_id"] = response.get("id")
                synced_appointments.append(synced_appointment)
                
            except Exception as e:
                print(f"Error sincronizando turno FHIR {appointment.get('id')}: {str(e)}")
        
        return synced_appointments
    
    def sync_schedules(self, schedules: List[Dict]) -> List[Dict]:
        """Sincroniza agendas con el HIS mediante FHIR."""
        endpoint = f"/fhir/{self.fhir_version}/Schedule"
        synced_schedules = []
        
        for schedule in schedules:
            try:
                fhir_schedule = self._to_fhir_resource("Schedule", schedule)
                response = self._make_request("POST", endpoint, fhir_schedule)
                
                synced_schedule = schedule.copy()
                synced_schedule["his_id"] = response.get("id")
                synced_schedules.append(synced_schedule)
                
            except Exception as e:
                print(f"Error sincronizando agenda FHIR {schedule.get('id')}: {str(e)}")
        
        return synced_schedules


class AdapterFactory:
    """Fábrica para crear adaptadores según el tipo de sistema."""
    
    @staticmethod
    def create_adapter(adapter_type: str, config: Dict) -> BaseAdapter:
        """
        Crea un adaptador según el tipo.
        
        Args:
            adapter_type: Tipo de adaptador ("rest", "fhir", "custom")
            config: Configuración del adaptador
        
        Returns:
            Instancia del adaptador
        """
        if adapter_type == "rest":
            return RESTAdapter(config)
        elif adapter_type == "fhir":
            return FHIRAdapter(config)
        else:
            raise ValueError(f"Tipo de adaptador no soportado: {adapter_type}")


# Ejemplo de configuración para un adaptador REST
EXAMPLE_REST_CONFIG = {
    "base_url": "https://api.hospital-ejemplo.com",
    "api_key": "your-api-key-here",
    "timeout": 30,
    "endpoints": {
        "patients": "/api/v1/pacientes",
        "doctors": "/api/v1/medicos",
        "appointments": "/api/v1/turnos",
        "schedules": "/api/v1/agendas"
    },
    "field_mappings": {
        "to_his": {
            "dni": "documento",
            "nombre": "nombre_completo",
            "telefono": "telefono_contacto",
            "email": "correo_electronico"
        },
        "from_his": {
            "documento": "dni",
            "nombre_completo": "nombre",
            "telefono_contacto": "telefono",
            "correo_electronico": "email"
        }
    }
}

# Ejemplo de configuración para un adaptador FHIR
EXAMPLE_FHIR_CONFIG = {
    "base_url": "https://fhir.hospital-ejemplo.com",
    "api_key": "your-api-key-here",
    "timeout": 30,
    "fhir_version": "R4"
}
