"""
Tests para funcionalidades hospitalarias de Plataforma Salud Chilecito
===================================================================

Uso:
    pytest tests/test_hospitalarios.py
"""

import pytest
from datetime import datetime
from dao_mongodb import SaludDAO
from db_models import (
    Receta, MedicamentoRecetado, EstudioMedico, TipoEstudio, EstadoEstudio,
    Notificacion, TipoNotificacion, EstadoNotificacion, Internacion, TipoInternacion, EstadoInternacion
)


class TestRecetas:
    @pytest.mark.skip(reason="MongoDB required")
    def test_dummy(self):
        pass

class TestEstudiosMedicos:
    @pytest.mark.skip(reason="MongoDB required")
    def test_dummy(self):
        pass

class TestNotificaciones:
    @pytest.mark.skip(reason="MongoDB required")
    def test_dummy(self):
        pass

class TestInternaciones:
    @pytest.mark.skip(reason="MongoDB required")
    def test_dummy(self):
        pass

class TestSeguridad:
    """Tests para módulo de seguridad"""
    
    def test_validar_contrasena_fuerte(self):
        """Test validar contraseña fuerte"""
        from security import security_manager
        
        es_valida, errores = security_manager.validar_contrasena("MiPassword123!")
        assert es_valida is True
        assert len(errores) == 0
    
    def test_validar_contrasena_debil(self):
        """Test validar contraseña débil"""
        from security import security_manager
        
        es_valida, errores = security_manager.validar_contrasena("123")
        assert es_valida is False
        assert len(errores) > 0
    
    def test_sanitizar_input(self):
        """Test sanitizar input"""
        from security import security_manager
        
        input_malicioso = "<script>alert('xss')</script>"
        input_sanitizado = security_manager.sanitizar_input(input_malicioso)
        
        assert "<script>" not in input_sanitizado
        assert "&lt;script&gt;" in input_sanitizado
    
    def test_validar_email(self):
        """Test validar email"""
        from security import security_manager
        
        assert security_manager.validar_email("test@example.com") is True
        assert security_manager.validar_email("invalido") is False
    
    def test_validar_dni(self):
        """Test validar DNI"""
        from security import security_manager
        
        assert security_manager.validar_dni("12345678") is True
        assert security_manager.validar_dni("123") is False
    
    def test_generar_token_seguro(self):
        """Test generar token seguro"""
        from security import security_manager
        
        token = security_manager.generar_token_seguro()
        assert token is not None
        assert len(token) > 0






class TestAuditLogger:
    @pytest.fixture(autouse=True)
    def skip_if_no_file(self):
        import os
        if not os.path.exists("logs/audit.log"):
            pytest.skip("No logs folder available in CI")

    def test_log_action(self):
        from audit_logger import audit_logger
        resultado = audit_logger.log_action(
            usuario_id="test_user",
            accion="test_action",
            detalles={"key": "value"}
        )
        assert resultado is True

    def test_log_error(self):
        from audit_logger import audit_logger
        resultado = audit_logger.log_error(
            error="Test error",
            contexto={"operacion": "test"}
        )
        assert resultado is True

    def test_log_security(self):
        from audit_logger import audit_logger
        resultado = audit_logger.log_security(
            evento="login_attempt",
            usuario_id="test_user"
        )
        assert resultado is True

class TestReportGenerator:
    @pytest.fixture
    def generator(self):
        from report_generator import ReportGenerator
        from unittest.mock import patch, MagicMock
        with patch('report_generator.ReportGenerator.__init__', return_value=None):
            gen = ReportGenerator()
            gen.dao = MagicMock()
            mock_db = MagicMock()
            gen.dao._get_db.return_value = mock_db

            mock_db["turnos"].find.return_value = []
            mock_db["turnos"].count_documents.return_value = 0
            mock_db["pacientes"].find.return_value = []
            mock_db["medicos"].find.return_value = []

            yield gen

    def test_generar_reporte_turnos(self, generator):
        reporte = generator.generar_reporte_turnos()
        assert reporte is not None
        assert "tipo" in reporte
        assert reporte["tipo"] == "reporte_turnos"

    def test_generar_reporte_pacientes(self, generator):
        reporte = generator.generar_reporte_pacientes()
        assert reporte is not None
        assert "tipo" in reporte
        assert reporte["tipo"] == "reporte_pacientes"

    def test_generar_reporte_medicos(self, generator):
        reporte = generator.generar_reporte_medicos()
        assert reporte is not None
        assert "tipo" in reporte
        assert reporte["tipo"] == "reporte_medicos"

    def test_generar_reporte_financiero(self, generator):
        reporte = generator.generar_reporte_financiero()
        assert reporte is not None
        assert "tipo" in reporte
        assert reporte["tipo"] == "reporte_financiero"
