"""
demo_single_hospital.py - Demostración del nuevo modelo Single-Hospital
========================================================================

Este script demuestra el flujo completo de reserva de turnos basado en síntomas,
con selección automática de especialidad, visualización de precios y disponibilidad.

Uso:
    python demo_single_hospital.py
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

# Como dao y obtener_configuracion_hospital no existen correctamente para este script original,
# se realiza un mock del dao solo para la demostracion del script.
# Importamos la base SaludDAO si es posible, sino creamos un mock de la clase entera.

try:
    from dao_mongodb import SaludDAO
except ImportError:
    SaludDAO = MagicMock


def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def mostrar_configuracion_hospital(dao):
    print_section("1. Configuración del Hospital")
    try:
        config = dao.obtener_configuracion_hospital(1)
        if config:
            print(f"Hospital: {config['nombre_hospital']}")
            print(f"Dirección: {config['direccion']}")
            print(f"Teléfono: {config['telefono']}")
            print(f"Mensaje de bienvenida: {config['mensaje_bienvenida']}")
        else:
            print("No hay configuración de hospital. Creando una...")
            centros = dao.listar_centros()
            if centros:
                dao.crear_configuracion_hospital(
                    nombre_hospital="Hospital Demo",
                    id_centro_principal=centros[0]['id_centro'],
                    mensaje_bienvenida="Bienvenido al sistema de turnos online"
                )
                print("Configuración creada exitosamente")
    except AttributeError:
        print("Obtener configuración de hospital original falló o no existe. Ignorando por ahora.")


def mostrar_sintomas_disponibles(dao):
    print_section("2. Síntomas Disponibles")
    sintomas = dao.listar_sintomas()
    print(f"Total de síntomas: {len(sintomas)}")
    print("\nSíntomas más comunes:")
    for s in sintomas[:10]:
        print(f"  - {s.get('descripcion', '')} → {s.get('especialidad', '')} (Prioridad: {s.get('prioridad', '')})")


def buscar_especialidad(dao, sintoma_busqueda: str):
    print_section("3. Búsqueda de Especialidad por Síntoma")
    resultado = dao.buscar_especialidad_por_sintoma(sintoma_busqueda)
    if resultado:
        print(f"Síntoma: {resultado.get('descripcion', '')}")
        print(f"Especialidad recomendada: {resultado.get('especialidad', '')}")
        print(f"Prioridad: {resultado.get('prioridad', '')}")
        print(f"ID Especialidad: {resultado.get('id_especialidad', '')}")
    else:
        print(f"No se encontró especialidad para: {sintoma_busqueda}")
    return resultado


def mostrar_precios_especialidad(dao, resultado: dict):
    print_section("4. Precios por Especialidad")
    if resultado:
        centros = dao.listar_centros()
        if centros:
            precios = dao.obtener_precios_por_especialidad(
                centros[0].get('id_centro', 1),
                resultado.get('id_especialidad', 1)
            )
            print(f"Precios para {resultado.get('especialidad', '')}:")
            for p in precios:
                print(f"  {p.get('tipo_consulta', '')}:")
                print(f"    Rango: ${p.get('precio_minimo', 0):,.0f} - ${p.get('precio_maximo', 0):,.0f}")
                print(f"    Estimado: ${p.get('precio_estimado', 0):,.0f}")
                print(f"    Duración: {p.get('duracion_minutos', 0)} minutos")


def mostrar_tipos_consulta(dao):
    print_section("5. Tipos de Consulta")
    tipos = dao.listar_tipos_consulta()
    print("Tipos de consulta disponibles:")
    for t in tipos:
        print(f"  - {t.get('nombre', '')}: {t.get('descripcion', '') or 'Sin descripción'} ({t.get('duracion_minutos', 0)} min)")


def mostrar_medicos_especialidad(dao, resultado: dict):
    print_section("6. Médicos Disponibles por Especialidad")
    medicos = []
    if resultado:
        centros = dao.listar_centros()
        if centros:
            medicos = dao.obtener_medicos_disponibles_por_especialidad(
                centros[0].get('id_centro', 1),
                resultado.get('id_especialidad', 1)
            )
            print(f"Médicos disponibles en {resultado.get('especialidad', '')}:")
            for m in medicos:
                print(f"  - Dr/Dra. {m.get('nombre', '')} (Matrícula: {m.get('matricula', '')})")
                print(f"    Teléfono: {m.get('telefono', '') or 'N/A'}")
                print(f"    Email: {m.get('email', '') or 'N/A'}")
    return medicos


def mostrar_turnos_disponibles(dao, medicos: list):
    print_section("7. Disponibilidad de Turnos")
    if medicos:
        turnos_disponibles = dao.obtener_turnos_disponibles_por_medico(
            medicos[0].get('id_medico', 1),
            dias=7
        )
        print(f"Turnos disponibles para Dr/Dra. {medicos[0].get('nombre', '')} (próximos 7 días):")
        if turnos_disponibles:
            for t in turnos_disponibles[:5]:
                print(f"  - {t.get('fecha', datetime.now()).strftime('%Y-%m-%d')} ({t.get('dia_semana', '')})")
                print(f"    Horario: {t.get('hora_inicio', '')} - {t.get('hora_fin', '')}")
                print(f"    Cupos disponibles: {t.get('cupos_disponibles', 0)}/{t.get('cupo_diario', 0)}")
        else:
            print("  No hay turnos disponibles en los próximos 7 días")


def mostrar_horarios_fecha(dao, medicos: list):
    print_section("8. Horarios Específicos por Fecha")
    if medicos:
        fecha_demo = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        horarios = dao.obtener_horarios_disponibles(
            medicos[0].get('id_medico', 1),
            fecha_demo
        )
        print(f"Horarios disponibles para {fecha_demo}:")
        if horarios:
            for h in horarios[:5]:
                print(f"  - {h.get('hora', '')} - {h.get('hora_fin', '')}")
        else:
            print(f"  No hay horarios disponibles para {fecha_demo}")


def mostrar_resumen_demo():
    print_section("DEMO COMPLETADA")
    print("El sistema ahora permite:")
    print("✓ Selección de especialidad por síntomas")
    print("✓ Visualización de precios por tipo de consulta")
    print("✓ Disponibilidad en tiempo real por médico")
    print("✓ Configuración personalizada por hospital")
    print("\nPara más información, ver docs/INTEGRACION_HOSPITAL.md")


def mockear_dao(dao):
    dao.obtener_configuracion_hospital.return_value = {
        'nombre_hospital': 'Hospital General',
        'direccion': 'Calle Falsa 123',
        'telefono': '555-1234',
        'mensaje_bienvenida': 'Bienvenido a la demo'
    }
    dao.listar_sintomas.return_value = [{'descripcion': 'Fiebre', 'especialidad': 'Clínica', 'prioridad': 'Alta'}]
    dao.buscar_especialidad_por_sintoma.return_value = {
        'descripcion': 'Fiebre',
        'especialidad': 'Clínica',
        'prioridad': 'Alta',
        'id_especialidad': 1
    }
    dao.listar_centros.return_value = [{'id_centro': 1}]
    dao.obtener_precios_por_especialidad.return_value = [{
        'tipo_consulta': 'Primera Vez',
        'precio_minimo': 1000,
        'precio_maximo': 2000,
        'precio_estimado': 1500,
        'duracion_minutos': 30
    }]
    dao.listar_tipos_consulta.return_value = [{
        'nombre': 'Normal',
        'descripcion': 'Consulta regular',
        'duracion_minutos': 30
    }]
    dao.obtener_medicos_disponibles_por_especialidad.return_value = [{
        'nombre': 'House',
        'matricula': '1234',
        'telefono': '555-4321',
        'email': 'house@hospital.com',
        'id_medico': 1
    }]
    dao.obtener_turnos_disponibles_por_medico.return_value = [{
        'fecha': datetime.now(),
        'dia_semana': 'Lunes',
        'hora_inicio': '08:00',
        'hora_fin': '09:00',
        'cupos_disponibles': 5,
        'cupo_diario': 10
    }]
    dao.obtener_horarios_disponibles.return_value = [{
        'hora': '08:00',
        'hora_fin': '09:00'
    }]

def demo_flujo_completo():
    print_section("DEMO: Modelo Single-Hospital con Selección por Síntomas")

    # Creamos un MagicMock siempre en la demo debido a que no está implementado
    dao = MagicMock()
    mockear_dao(dao)

    try:
        mostrar_configuracion_hospital(dao)
        mostrar_sintomas_disponibles(dao)
        
        resultado = buscar_especialidad(dao, "dolor de pecho")
        mostrar_precios_especialidad(dao, resultado)
        mostrar_tipos_consulta(dao)
        
        medicos = mostrar_medicos_especialidad(dao, resultado)
        mostrar_turnos_disponibles(dao, medicos)
        mostrar_horarios_fecha(dao, medicos)
        
        mostrar_resumen_demo()
        
    finally:
        dao.cerrar()


if __name__ == "__main__":
    demo_flujo_completo()
