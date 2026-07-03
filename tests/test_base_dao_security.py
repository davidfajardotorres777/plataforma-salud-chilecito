import pytest
from src.dao.base_dao import BaseDAO
from src.config.database import OracleDatabase

class MockDB(OracleDatabase):
    def fetch_one(self, sql, params=None):
        return {"total": 42}

def test_contar_valid_table_name():
    dao = BaseDAO(db=MockDB())
    dao.table_name = "valid_table_name"
    assert dao.contar() == 42

def test_contar_invalid_table_name_raises_valueerror():
    dao = BaseDAO(db=MockDB())
    dao.table_name = "invalid table name;"
    with pytest.raises(ValueError, match="Invalid table name: invalid table name;"):
        dao.contar()

def test_contar_sqli_payload_raises_valueerror():
    dao = BaseDAO(db=MockDB())
    dao.table_name = "medico; DROP TABLE medico;"
    with pytest.raises(ValueError, match="Invalid table name: medico; DROP TABLE medico;"):
        dao.contar()

def test_contar_empty_table_name_raises_valueerror():
    dao = BaseDAO(db=MockDB())
    dao.table_name = ""
    with pytest.raises(ValueError):
        dao.contar()
