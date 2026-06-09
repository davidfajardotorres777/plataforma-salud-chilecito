"""
Ejemplos de integración con sistemas hospitalarios existentes (HIS).

Este script muestra cómo integrar Salud Chilecito con diferentes tipos de sistemas
hospitalarios mediante los adaptadores disponibles.
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from webapp.adapters import AdapterFactory, EXAMPLE_REST_CONFIG, EXAMPLE_FHIR_CONFIG
from webapp.auth import api_key_manager
from webapp.store import JsonStore


def ejemplo_api_keys():
    """Ejemplo de cómo generar y usar API Keys para integración."""
    print("=== Ejemplo: API Keys ===\n")
    
    # Generar una API Key para un hospital
    hospital_name = "Hospital Eleazar Herrera Motta"
    hospital_id = 1
    permissions = ["read", "write"]
    
    api_key = api_key_manager.generate_key(hospital_name, hospital_id, permissions)
    print(f"API Key generada: {api_key}")
    print(f"Guarda esta key de forma segura, no se volverá a mostrar\n")
    
    # Validar la API Key
    hospital_info = api_key_manager.validate_key(api_key)
    print(f"Validación: {hospital_info}")
    
    # Listar API Keys del hospital
    keys = api_key_manager.list_keys(hospital_id)
    print(f"\nAPI Keys del hospital: {len(keys)}")
    for key in keys:
        print(f"  - {key['key']}: {key['hospital_name']} (Activa: {key['is_active']})")
    
    return api_key


def ejemplo_adaptador_rest():
    """Ejemplo de integración con un sistema HIS mediante API REST."""
    print("\n=== Ejemplo: Adaptador REST ===\n")
    
    # Configuración del adaptador REST
    config = {
        "base_url": "https://api.hospital-ejemplo.com",
        "api_key": "tu-api-key-aqui",
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
    
    # Crear el adaptador
    adapter = AdapterFactory.create_adapter("rest", config)
    print(f"Adaptador REST creado para: {config['base_url']}")
    
    # Ejemplo de sincronización de pacientes
    pacientes = [
        {
            "id": 1,
            "dni": "12345678",
            "nombre": "Juan Pérez",
            "telefono": "3825-123456",
            "email": "juan.perez@email.com"
        },
        {
            "id": 2,
            "dni": "87654321",
            "nombre": "María García",
            "telefono": "3825-789012",
            "email": "maria.garcia@email.com"
        }
    ]
    
    print(f"\nSincronizando {len(pacientes)} pacientes...")
    # Nota: Esto fallará si no hay un servidor real, pero muestra el código
    # synced = adapter.sync_patients(pacientes)
    print("Código de sincronización preparado (requiere servidor real)")


def ejemplo_adaptador_fhir():
    """Ejemplo de integración con un sistema HIS mediante FHIR."""
    print("\n=== Ejemplo: Adaptador FHIR ===\n")
    
    # Configuración del adaptador FHIR
    config = {
        "base_url": "https://fhir.hospital-ejemplo.com",
        "api_key": "tu-api-key-aqui",
        "timeout": 30,
        "fhir_version": "R4"
    }
    
    # Crear el adaptador
    adapter = AdapterFactory.create_adapter("fhir", config)
    print(f"Adaptador FHIR creado para: {config['base_url']}")
    print(f"Versión FHIR: {config['fhir_version']}")
    
    # Ejemplo de sincronización de pacientes
    pacientes = [
        {
            "id": 1,
            "dni": "12345678",
            "nombre": "Juan Pérez",
            "telefono": "3825-123456"
        }
    ]
    
    print(f"\nSincronizando {len(pacientes)} pacientes con FHIR...")
    # Nota: Esto fallará si no hay un servidor real, pero muestra el código
    # synced = adapter.sync_patients(pacientes)
    print("Código de sincronización preparado (requiere servidor real)")


def ejemplo_sincronizacion_completa():
    """Ejemplo de sincronización completa entre Salud Chilecito y un HIS."""
    print("\n=== Ejemplo: Sincronización Completa ===\n")
    
    # Cargar datos de Salud Chilecito
    store = JsonStore()
    dashboard = store.dashboard()
    
    print(f"Datos de Salud Chilecito:")
    print(f"  - Pacientes: {len(dashboard['pacientes'])}")
    print(f"  - Médicos: {len(dashboard['medicos'])}")
    print(f"  - Turnos: {len(dashboard['turnos'])}")
    print(f"  - Agendas: {len(dashboard['agendas'])}")
    
    # Configurar adaptador
    config = EXAMPLE_REST_CONFIG.copy()
    config["base_url"] = "https://api.hospital-ejemplo.com"  # Cambiar por URL real
    config["api_key"] = "tu-api-key-aqui"  # Cambiar por API key real
    
    adapter = AdapterFactory.create_adapter("rest", config)
    
    print(f"\nSincronizando con HIS...")
    print("1. Sincronizar pacientes...")
    # synced_pacientes = adapter.sync_patients(dashboard['pacientes'])
    print("   Código preparado (requiere servidor real)")
    
    print("2. Sincronizar médicos...")
    # synced_doctors = adapter.sync_doctors(dashboard['medicos'])
    print("   Código preparado (requiere servidor real)")
    
    print("3. Sincronizar agendas...")
    # synced_schedules = adapter.sync_schedules(dashboard['agendas'])
    print("   Código preparado (requiere servidor real)")
    
    print("4. Sincronizar turnos...")
    # synced_appointments = adapter.sync_appointments(dashboard['turnos'])
    print("   Código preparado (requiere servidor real)")


def ejemplo_webhooks():
    """Ejemplo de cómo usar webhooks para sincronización bidireccional."""
    print("\n=== Ejemplo: Webhooks ===\n")
    
    from webapp.webhooks import webhook_manager, EventTypes
    
    # Registrar un webhook para recibir notificaciones
    hospital_id = 1
    webhook_url = "https://hospital-ejemplo.com/webhooks/salud-chilecito"
    events = [EventTypes.TURNO_CREATED, EventTypes.TURNO_CANCELLED, EventTypes.PACIENTE_UPDATED]
    
    webhook_id = webhook_manager.register_webhook(
        hospital_id=hospital_id,
        url=webhook_url,
        events=events,
        secret="secreto-para-firmar-payloads"
    )
    
    print(f"Webhook registrado: {webhook_id}")
    print(f"URL: {webhook_url}")
    print(f"Eventos suscritos: {events}")
    
    # Listar webhooks del hospital
    webhooks = webhook_manager.get_webhooks(hospital_id)
    print(f"\nWebhooks del hospital: {len(webhooks)}")
    for webhook in webhooks:
        print(f"  - ID: {webhook['id']}")
        print(f"    URL: {webhook['url']}")
        print(f"    Eventos: {webhook['events']}")
        print(f"    Activo: {webhook['is_active']}")
    
    # Disparar un evento de prueba
    print(f"\nDisparando evento de prueba...")
    webhook_manager.trigger_event(
        EventTypes.TURNO_CREATED,
        {
            "id": 1,
            "paciente_id": 1,
            "medico_id": 1,
            "fecha": "2026-06-20",
            "hora": "09:30",
            "estado": "CONFIRMADO"
        }
    )
    print("Evento disparado (el webhook recibirá la notificación)")


def ejemplo_flujo_completo():
    """Ejemplo del flujo completo de integración."""
    print("\n=== Ejemplo: Flujo Completo de Integración ===\n")
    
    print("Paso 1: Generar API Key para el hospital")
    api_key = ejemplo_api_keys()
    
    print("\nPaso 2: Configurar adaptador para el HIS del hospital")
    config = EXAMPLE_REST_CONFIG.copy()
    config["base_url"] = "https://api.hospital-ejemplo.com"
    config["api_key"] = api_key  # Usar la API Key generada
    
    print("\nPaso 3: Registrar webhooks para sincronización bidireccional")
    ejemplo_webhooks()
    
    print("\nPaso 4: Sincronizar datos maestros (pacientes, médicos, agendas)")
    ejemplo_sincronizacion_completa()
    
    print("\nPaso 5: A partir de ahora, los cambios se sincronizan automáticamente")
    print("  - Cuando un paciente reserva un turno en Salud Chilecito, se notifica al HIS")
    print("  - Cuando el hospital crea un turno en su HIS, se notifica a Salud Chilecito")
    print("  - Ambos sistemas permanecen sincronizados")


if __name__ == "__main__":
    print("=== Ejemplos de Integración con Sistemas Hospitalarios ===\n")
    print("Este script muestra cómo integrar Salud Chilecito con sistemas HIS existentes.\n")
    
    # Ejecutar ejemplos
    ejemplo_api_keys()
    ejemplo_adaptador_rest()
    ejemplo_adaptador_fhir()
    ejemplo_sincronizacion_completa()
    ejemplo_webhooks()
    
    print("\n=== Flujo Completo ===")
    ejemplo_flujo_completo()
    
    print("\n=== Notas Importantes ===")
    print("1. Los ejemplos de adaptadores requieren un servidor real del HIS")
    print("2. En producción, usa HTTPS y API Keys seguras")
    print("3. Implementa reintentos y manejo de errores en producción")
    print("4. Configura webhooks para sincronización bidireccional")
    print("5. Monitorea los logs de auditoría para detectar problemas")
    print("6. Para más información, ver docs/ARQUITECTURA_INTEGRACION.md")
