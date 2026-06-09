"""
demo_single_hospital.py - Demostración del nuevo modelo Single-Hospital
========================================================================

Este script demuestra el flujo completo de reserva de turnos basado en síntomas,
con selección automática de especialidad, visualización de precios y disponibilidad.

Uso:
    python demo_single_hospital.py
"""

from dao import SaludDAO


def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_flujo_completo():
    print_section("DEMO: Modelo Single-Hospital con Selección por Síntomas")
    
    dao = SaludDAO()
    
    try:
        # 1. Configuración del hospital
        print_section("1. Configuración del Hospital")
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
        
        # 2. Listar síntomas disponibles
        print_section("2. Síntomas Disponibles")
        sintomas = dao.listar_sintomas()
        print(f"Total de síntomas: {len(sintomas)}")
        print("\nSíntomas más comunes:")
        for s in sintomas[:10]:
            print(f"  - {s['descripcion']} → {s['especialidad']} (Prioridad: {s['prioridad']})")
        
        # 3. Buscar especialidad por síntoma
        print_section("3. Búsqueda de Especialidad por Síntoma")
        sintoma_busqueda = "dolor de pecho"
        resultado = dao.buscar_especialidad_por_sintoma(sintoma_busqueda)
        if resultado:
            print(f"Síntoma: {resultado['descripcion']}")
            print(f"Especialidad recomendada: {resultado['especialidad']}")
            print(f"Prioridad: {resultado['prioridad']}")
            print(f"ID Especialidad: {resultado['id_especialidad']}")
        else:
            print(f"No se encontró especialidad para: {sintoma_busqueda}")
        
        # 4. Obtener precios por especialidad
        print_section("4. Precios por Especialidad")
        if resultado:
            centros = dao.listar_centros()
            if centros:
                precios = dao.obtener_precios_por_especialidad(
                    centros[0]['id_centro'],
                    resultado['id_especialidad']
                )
                print(f"Precios para {resultado['especialidad']}:")
                for p in precios:
                    print(f"  {p['tipo_consulta']}:")
                    print(f"    Rango: ${p['precio_minimo']:,.0f} - ${p['precio_maximo']:,.0f}")
                    print(f"    Estimado: ${p['precio_estimado']:,.0f}")
                    print(f"    Duración: {p['duracion_minutos']} minutos")
        
        # 5. Tipos de consulta disponibles
        print_section("5. Tipos de Consulta")
        tipos = dao.listar_tipos_consulta()
        print("Tipos de consulta disponibles:")
        for t in tipos:
            print(f"  - {t['nombre']}: {t['descripcion'] or 'Sin descripción'} ({t['duracion_minutos']} min)")
        
        # 6. Médicos disponibles por especialidad
        print_section("6. Médicos Disponibles por Especialidad")
        if resultado:
            centros = dao.listar_centros()
            if centros:
                medicos = dao.obtener_medicos_disponibles_por_especialidad(
                    centros[0]['id_centro'],
                    resultado['id_especialidad']
                )
                print(f"Médicos disponibles en {resultado['especialidad']}:")
                for m in medicos:
                    print(f"  - Dr/Dra. {m['nombre']} (Matrícula: {m['matricula']})")
                    print(f"    Teléfono: {m['telefono'] or 'N/A'}")
                    print(f"    Email: {m['email'] or 'N/A'}")
        
        # 7. Disponibilidad de turnos por médico
        print_section("7. Disponibilidad de Turnos")
        if medicos:
            turnos_disponibles = dao.obtener_turnos_disponibles_por_medico(
                medicos[0]['id_medico'],
                dias=7
            )
            print(f"Turnos disponibles para Dr/Dra. {medicos[0]['nombre']} (próximos 7 días):")
            if turnos_disponibles:
                for t in turnos_disponibles[:5]:
                    print(f"  - {t['fecha'].strftime('%Y-%m-%d')} ({t['dia_semana']})")
                    print(f"    Horario: {t['hora_inicio']} - {t['hora_fin']}")
                    print(f"    Cupos disponibles: {t['cupos_disponibles']}/{t['cupo_diario']}")
            else:
                print("  No hay turnos disponibles en los próximos 7 días")
        
        # 8. Horarios específicos para una fecha
        print_section("8. Horarios Específicos por Fecha")
        if medicos:
            from datetime import datetime, timedelta
            fecha_demo = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            horarios = dao.obtener_horarios_disponibles(
                medicos[0]['id_medico'],
                fecha_demo
            )
            print(f"Horarios disponibles para {fecha_demo}:")
            if horarios:
                for h in horarios[:5]:
                    print(f"  - {h['hora']} - {h['hora_fin']}")
            else:
                print(f"  No hay horarios disponibles para {fecha_demo}")
        
        print_section("DEMO COMPLETADA")
        print("El sistema ahora permite:")
        print("✓ Selección de especialidad por síntomas")
        print("✓ Visualización de precios por tipo de consulta")
        print("✓ Disponibilidad en tiempo real por médico")
        print("✓ Configuración personalizada por hospital")
        print("\nPara más información, ver docs/INTEGRACION_HOSPITAL.md")
        
    finally:
        dao.cerrar()


if __name__ == "__main__":
    demo_flujo_completo()
