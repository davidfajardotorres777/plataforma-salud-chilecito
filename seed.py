"""
seed.py - Carga de datos de prueba para Salud Chilecito
========================================================
Inserta datos iniciales en la base Oracle para probar el DAO.

Uso:
    python seed.py
"""

import sys
from datetime import date, datetime

from dao import SaludDAO


def seed_especialidades(dao: SaludDAO):
    print("Insertando especialidades...")
    especialidades = [
        ("Clinica Medica", "Atencion primaria y seguimiento general"),
        ("Pediatria", "Atencion medica de ninos y adolescentes"),
        ("Cardiologia", "Diagnostico y control cardiovascular"),
        ("Odontologia", "Salud bucal y urgencias odontologicas"),
        ("Ginecologia", "Control y salud integral de la mujer"),
        ("Traumatologia", "Lesiones oseas, articulares y musculares"),
    ]
    for nombre, desc in especialidades:
        try:
            dao.crear_especialidad(nombre, desc)
            print(f"  OK - {nombre}")
        except Exception as e:
            print(f"  SKIP - {nombre}: {e}")


def seed_centros(dao: SaludDAO):
    print("Insertando centros de salud...")
    centros = [
        ("Hospital Eleazar Herrera Motta", "Av. La Mexicana 180", "Chilecito", "3825-422100", "PUBLICO", "hospital@saludchilecito.gob.ar"),
        ("Clinica San Nicolas", "Castro Barros 260", "Chilecito", "3825-430001", "PRIVADO", "turnos@clinicasannicolas.com"),
        ("Centro de Salud Nonogasta", "Ruta 40 y San Martin", "Nonogasta", "3825-490120", "PUBLICO", "nonogasta@saludchilecito.gob.ar"),
        ("Centro de Salud Sanogasta", "9 de Julio s/n", "Sanogasta", "3825-480010", "PUBLICO", "sanogasta@saludchilecito.gob.ar"),
    ]
    for nombre, direc, dist, tel, tipo, email in centros:
        try:
            dao.crear_centro(nombre, direc, dist, tipo, tel, email)
            print(f"  OK - {nombre}")
        except Exception as e:
            print(f"  SKIP - {nombre}: {e}")


def seed_pacientes(dao: SaludDAO):
    print("Insertando pacientes...")
    pacientes = [
        ("40111222", "Juan Perez", date(1998, 4, 12), "3825-600001", "juan.perez@mail.com", "OSDE", "Chilecito"),
        ("38222333", "Carla Mercado", date(1992, 9, 25), "3825-600002", "carla.mercado@mail.com", "APOS", "Nonogasta"),
        ("45123456", "Mateo Brizuela", date(2014, 6, 10), "3825-600003", "familia.brizuela@mail.com", "Sin obra social", "Sanogasta"),
    ]
    for dni, nombre, fnac, tel, email, obra, dist in pacientes:
        try:
            dao.crear_paciente(dni, nombre, fnac, tel, email, obra, dist)
            print(f"  OK - {nombre} (DNI {dni})")
        except Exception as e:
            print(f"  SKIP - {nombre}: {e}")


def seed_medicos(dao: SaludDAO):
    print("Insertando medicos...")
    medicos = [
        ("Dra. Maria Gonzalez", "LR-1001", "Cardiologia", "Hospital Eleazar Herrera Motta", "3825-500001", "mgonzalez@salud.local"),
        ("Dr. Lucas Ferreyra", "LR-1002", "Pediatria", "Centro de Salud Nonogasta", "3825-500002", "lferreyra@salud.local"),
        ("Dra. Ana Rojas", "LR-1003", "Clinica Medica", "Centro de Salud Sanogasta", "3825-500003", "arojas@salud.local"),
        ("Dr. Emiliano Vega", "LR-1004", "Odontologia", "Clinica San Nicolas", "3825-500004", "evega@salud.local"),
    ]
    for nombre, mat, esp, centro, tel, email in medicos:
        try:
            esp_row = dao.obtener_especialidad_por_nombre(esp)
            centro_rows = dao.listar_centros()
            centro_row = next((c for c in centro_rows if c["nombre"] == centro), None)
            if esp_row and centro_row:
                dao.crear_medico(nombre, mat, esp_row["id_especialidad"], centro_row["id_centro"], tel, email)
                print(f"  OK - {nombre}")
            else:
                print(f"  SKIP - {nombre}: especialidad o centro no encontrado")
        except Exception as e:
            print(f"  SKIP - {nombre}: {e}")


def main():
    print("=== Seed - Salud Chilecito ===\n")

    dao = SaludDAO()

    try:
        seed_especialidades(dao)
        seed_centros(dao)
        seed_pacientes(dao)
        seed_medicos(dao)
        print("\n=== Seed completado ===")
    finally:
        dao.cerrar()


if __name__ == "__main__":
    main()
