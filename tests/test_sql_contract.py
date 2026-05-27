from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_sql(name: str) -> str:
    return (ROOT / "sql" / name).read_text(encoding="utf-8").upper()


def test_tablespaces_and_recovery_requirements_are_documented():
    sql = read_sql("01_tablespaces.sql")
    assert "DB_RECOVERY_FILE_DEST_SIZE = 3G" in sql
    assert "UNDO_RETENTION = 172800" in sql
    assert "ARCHIVELOG" in sql
    assert "TBS_SALUD_DATA" in sql
    assert "TBS_SALUD_IDX" in sql
    assert "MAXSIZE 3G" in sql


def test_users_roles_and_password_policy_exist():
    sql = read_sql("02_users_roles.sql")
    assert "CREATE PROFILE PF_SALUD_APP" in sql
    assert "PASSWORD_LIFE_TIME 15" in sql
    assert "CREATE ROLE RL_SALUD_ADMIN" in sql
    assert "CREATE ROLE RL_SALUD_CONSULTA" in sql
    assert sql.count("CREATE USER SALUD_CONSULTA_") == 3


def test_schema_contains_required_domain_tables_and_data_types():
    sql = read_sql("03_schema.sql")
    for table in [
        "ESPECIALIDAD",
        "CENTRO_SALUD",
        "MEDICO",
        "PACIENTE",
        "AGENDA_MEDICO",
        "TURNO",
        "HISTORIAL_CLINICO",
        "DOCUMENTO_PACIENTE",
    ]:
        assert f"CREATE TABLE {table}" in sql

    for data_type in ["NUMBER", "VARCHAR2", "DATE", "CLOB", "BLOB"]:
        assert data_type in sql

    assert "FOREIGN KEY" in sql
    assert "CHECK" in sql


def test_indexes_use_separate_tablespace():
    sql = read_sql("04_indexes.sql")
    assert sql.count("TABLESPACE TBS_SALUD_IDX") >= 5
    assert "IX_TURNO_MEDICO_FECHA" in sql
