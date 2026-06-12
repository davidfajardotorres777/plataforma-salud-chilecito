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
    """Tests para gestión de recetas médicas"""
    
    @pytest.fixture
    def dao(self):
        """Fixture para DAO"""
        dao = SaludDAO()
        yield dao
        dao.cerrar()
    
    def test_crear_receta(self, dao):
        """Test crear receta médica"""
        medicamentos = [
            MedicamentoRecetado(
                nombre="Paracetamol",
                dosis="500mg",
                frecuencia="Cada 8 horas",
                duracion="5 días",
                instrucciones="Tomar con comida"
            )
        ]
        
        receta = Receta(
            paciente_id="test_paciente_id",
            medico_id="test_medico_id",
            medicamentos=medicamentos,
            diagnostico="Dolor de cabeza",
            indicaciones="Reposo y medicación"
        )
        
        receta_id = dao.crear_receta(receta)
        assert receta_id is not None
        assert len(receta_id) > 0
    
    def test_obtener_recetas_por_paciente(self, dao):
        """Test obtener recetas por paciente"""
        recetas = dao.obtener_recetas_por_paciente("test_paciente_id")
        assert isinstance(recetas, list)


class TestEstudiosMedicos:
    """Tests para gestión de estudios médicos"""
    
    @pytest.fixture
    def dao(self):
        """Fixture para DAO"""
        dao = SaludDAO()
        yield dao
        dao.cerrar()
    
    def test_crear_estudio_medico(self, dao):
        """Test crear estudio médico"""
        estudio = EstudioMedico(
            paciente_id="test_paciente_id",
            medico_id="test_medico_id",
            tipo_estudio=TipoEstudio.LABORATORIO,
            descripcion="Análisis de sangre completo",
            indicaciones="Ayuno de 12 horas"
        )
        
        estudio_id = dao.crear_estudio_medico(estudio)
        assert estudio_id is not None
        assert len(estudio_id) > 0
    
    def test_obtener_estudios_por_paciente(self, dao):
        """Test obtener estudios por paciente"""
        estudios = dao.obtener_estudios_por_paciente("test_paciente_id")
        assert isinstance(estudios, list)
    
    def test_actualizar_estado_estudio(self, dao):
        """Test actualizar estado de estudio"""
        # Primero crear un estudio
        estudio = EstudioMedico(
            paciente_id="test_paciente_id",
            medico_id="test_medico_id",
            tipo_estudio=TipoEstudio.RADIOLOGIA,
            descripcion="Radiografía de tórax"
        )
        
        estudio_id = dao.crear_estudio_medico(estudio)
        
        # Actualizar estado
        resultado = dao.actualizar_estado_estudio(
            estudio_id,
            EstadoEstudio.COMPLETADO,
            "Resultado normal"
        )
        assert resultado is True


class TestNotificaciones:
    """Tests para gestión de notificaciones"""
    
    @pytest.fixture
    def dao(self):
        """Fixture para DAO"""
        dao = SaludDAO()
        yield dao
        dao.cerrar()
    
    def test_crear_notificacion(self, dao):
        """Test crear notificación"""
        notificacion = Notificacion(
            usuario_id="test_usuario_id",
            tipo=TipoNotificacion.TURNO_CONFIRMADO,
            titulo="Turno Confirmado",
            mensaje="Tu turno ha sido confirmado para el día 15 de enero"
        )
        
        notificacion_id = dao.crear_notificacion(notificacion)
        assert notificacion_id is not None
        assert len(notificacion_id) > 0
    
    def test_obtener_notificaciones_por_usuario(self, dao):
        """Test obtener notificaciones por usuario"""
        notificaciones = dao.obtener_notificaciones_por_usuario("test_usuario_id")
        assert isinstance(notificaciones, list)
    
    def test_marcar_notificacion_leida(self, dao):
        """Test marcar notificación como leída"""
        # Primero crear una notificación
        notificacion = Notificacion(
            usuario_id="test_usuario_id",
            tipo=TipoNotificacion.SISTEMA,
            titulo="Test",
            mensaje="Mensaje de prueba"
        )
        
        notificacion_id = dao.crear_notificacion(notificacion)
        
        # Marcar como leída
        resultado = dao.marcar_notificacion_leida(notificacion_id)
        assert resultado is True


class TestInternaciones:
    """Tests para gestión de internaciones"""
    
    @pytest.fixture
    def dao(self):
        """Fixture para DAO"""
        dao = SaludDAO()
        yield dao
        dao.cerrar()
    
    def test_crear_internacion(self, dao):
        """Test crear internación"""
        internacion = Internacion(
            paciente_id="test_paciente_id",
            medico_id="test_medico_id",
            centro_id="test_centro_id",
            tipo=TipoInternacion.HOSPITALIZACION,
            motivo_ingreso="Dolor abdominal severo",
            diagnostico_ingreso="Apendicitis aguda"
        )
        
        internacion_id = dao.crear_internacion(internacion)
        assert internacion_id is not None
        assert len(internacion_id) > 0
    
    def test_obtener_internaciones_por_paciente(self, dao):
        """Test obtener internaciones por paciente"""
        internaciones = dao.obtener_internaciones_por_paciente("test_paciente_id")
        assert isinstance(internaciones, list)
    
    def test_obtener_internaciones_activas(self, dao):
        """Test obtener internaciones activas"""
        internaciones = dao.obtener_internaciones_activas()
        assert isinstance(internaciones, list)
    
    def test_dar_alta_internacion(self, dao):
        """Test dar alta a internación"""
        # Primero crear una internación
        internacion = Internacion(
            paciente_id="test_paciente_id",
            medico_id="test_medico_id",
            centro_id="test_centro_id",
            tipo=TipoInternacion.OBSERVACION,
            motivo_ingreso="Observación post-operatoria"
        )
        
        internacion_id = dao.crear_internacion(internacion)
        
        # Dar alta
        resultado = dao.dar_alta_internacion(
            internacion_id,
            diagnostico_egreso="Recuperación satisfactoria",
            resumen_clinico="Paciente dado de alta sin complicaciones"
        )
        assert resultado is True


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
    """Tests para módulo de auditoría"""
    
    def test_log_action(self):
        """Test log de acción"""
        from audit_logger import audit_logger
        
        resultado = audit_logger.log_action(
            usuario_id="test_user",
            accion="test_action",
            detalles={"key": "value"}
        )
        assert resultado is True
    
    def test_log_error(self):
        """Test log de error"""
        from audit_logger import audit_logger
        
        resultado = audit_logger.log_error(
            error="Test error",
            contexto={"operacion": "test"}
        )
        assert resultado is True
    
    def test_log_security(self):
        """Test log de seguridad"""
        from audit_logger import audit_logger
        
        resultado = audit_logger.log_security(
            evento="login_attempt",
            usuario_id="test_user"
        )
        assert resultado is True


class TestReportGenerator:
    """Tests para generador de reportes"""
    
    @pytest.fixture
    def generator(self):
        """Fixture para generador de reportes"""
        from report_generator import ReportGenerator
        gen = ReportGenerator()
        yield gen
        gen.cerrar()
    
    def test_generar_reporte_turnos(self, generator):
        """Test generar reporte de turnos"""
        reporte = generator.generar_reporte_turnos()
        assert reporte is not None
        assert "tipo" in reporte
        assert reporte["tipo"] == "reporte_turnos"
        assert "estadisticas" in reporte
    
    def test_generar_reporte_pacientes(self, generator):
        """Test generar reporte de pacientes"""
        reporte = generator.generar_reporte_pacientes()
        assert reporte is not None
        assert "tipo" in reporte
        assert reporte["tipo"] == "reporte_pacientes"
        assert "estadisticas" in reporte
    
    def test_generar_reporte_medicos(self, generator):
        """Test generar reporte de médicos"""
        reporte = generator.generar_reporte_medicos()
        assert reporte is not None
        assert "tipo" in reporte
        assert reporte["tipo"] == "reporte_medicos"
        assert "estadisticas" in reporte
    
    def test_generar_reporte_financiero(self, generator):
        """Test generar reporte financiero"""
        reporte = generator.generar_reporte_financiero()
        assert reporte is not None
        assert "tipo" in reporte
        assert reporte["tipo"] == "reporte_financiero"
        assert "estadisticas" in reporte
