"""Tests para el bot IA conversacional"""

import pytest
from src.bot import (
    ConversationalBot,
    ConversationContext,
    SimpleFallbackBackend,
    get_bot,
    reset_bot
)


class TestConversationContext:
    """Tests para el contexto de conversación"""
    
    def test_add_message(self):
        """Prueba agregar mensajes al contexto"""
        context = ConversationContext(max_history=10)
        
        context.add_message('user', 'Hola')
        context.add_message('assistant', '¡Hola! ¿Cómo te puedo ayudar?')
        
        assert len(context.history) == 2
        assert context.history[0].role == 'user'
        assert context.history[1].role == 'assistant'
    
    def test_history_limit(self):
        """Prueba que el historial respeta el límite"""
        context = ConversationContext(max_history=5)
        
        # Agregar más mensajes que el límite
        for i in range(15):
            context.add_message('user', f'Mensaje {i}')
            context.add_message('assistant', f'Respuesta {i}')
        
        # Debe mantener solo los últimos (max_history * 2) mensajes
        assert len(context.history) <= 10
    
    def test_get_history_text(self):
        """Prueba formatear el historial como texto"""
        context = ConversationContext()
        
        context.add_message('user', 'Hola')
        context.add_message('assistant', 'Hola!')
        
        text = context.get_history_text()
        assert 'USER: Hola' in text
        assert 'ASSISTANT: Hola!' in text
    
    def test_clear_history(self):
        """Prueba limpiar el historial"""
        context = ConversationContext()
        
        context.add_message('user', 'Test')
        assert len(context.history) > 0
        
        context.clear()
        assert len(context.history) == 0


class TestSimpleFallbackBackend:
    """Tests para el backend simple"""
    
    def test_backend_initialization(self):
        """Prueba inicializar el backend"""
        backend = SimpleFallbackBackend()
        assert backend is not None
        assert hasattr(backend, 'generate_response')
        assert hasattr(backend, 'extract_intent')
    
    def test_extract_intent_listar_pacientes(self):
        """Prueba extraer intención de listar pacientes"""
        backend = SimpleFallbackBackend()
        
        result = backend.extract_intent('listar pacientes')
        assert result['intent'] == 'listar_pacientes'
        
        result = backend.extract_intent('mostrar pacientes')
        assert result['intent'] == 'listar_pacientes'
    
    def test_extract_intent_listar_medicos(self):
        """Prueba extraer intención de listar médicos"""
        backend = SimpleFallbackBackend()
        
        result = backend.extract_intent('listar medicos')
        assert result['intent'] == 'listar_medicos'
        
        result = backend.extract_intent('mostrar doctores')
        assert result['intent'] == 'listar_medicos'
    
    def test_extract_intent_listar_centros(self):
        """Prueba extraer intención de listar centros"""
        backend = SimpleFallbackBackend()
        
        result = backend.extract_intent('listar centros')
        assert result['intent'] == 'listar_centros'
    
    def test_extract_intent_crear_turno(self):
        """Prueba extraer intención de crear turno"""
        backend = SimpleFallbackBackend()
        
        result = backend.extract_intent('crear turno')
        assert result['intent'] == 'crear_turno'
        
        result = backend.extract_intent('agendar cita')
        assert result['intent'] == 'crear_turno'
    
    def test_extract_intent_ayuda(self):
        """Prueba extraer intención de ayuda"""
        backend = SimpleFallbackBackend()
        
        result = backend.extract_intent('ayuda')
        assert result['intent'] == 'ayuda'
    
    def test_generate_response(self):
        """Prueba generar respuesta"""
        backend = SimpleFallbackBackend()
        context = ConversationContext()
        
        response = backend.generate_response('listar pacientes', context)
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_generate_response_for_different_intents(self):
        """Prueba que diferentes intenciones generan respuestas"""
        backend = SimpleFallbackBackend()
        context = ConversationContext()
        
        intents = [
            'listar pacientes',
            'listar medicos',
            'crear turno',
            'ayuda'
        ]
        
        responses = set()
        for intent in intents:
            response = backend.generate_response(intent, context)
            responses.add(response)
        
        # Debe haber respuestas diferentes
        assert len(responses) > 1


class TestConversationalBot:
    """Tests para el bot conversacional"""
    
    def test_bot_initialization(self):
        """Prueba inicializar el bot"""
        backend = SimpleFallbackBackend()
        bot = ConversationalBot(backend=backend)
        
        assert bot is not None
        assert bot.backend == backend
        assert bot.context is not None
    
    def test_bot_chat(self):
        """Prueba chatear con el bot"""
        backend = SimpleFallbackBackend()
        bot = ConversationalBot(backend=backend)
        
        response = bot.chat('listar pacientes')
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_bot_multiple_messages(self):
        """Prueba múltiples mensajes"""
        backend = SimpleFallbackBackend()
        bot = ConversationalBot(backend=backend)
        
        bot.chat('Hola')
        bot.chat('¿Qué puedo hacer?')
        bot.chat('listar pacientes')
        
        assert len(bot.get_history()) >= 6  # 3 user + 3 assistant
    
    def test_bot_get_history(self):
        """Prueba obtener el historial"""
        backend = SimpleFallbackBackend()
        bot = ConversationalBot(backend=backend)
        
        bot.chat('Hola')
        history = bot.get_history()
        
        assert len(history) >= 2
        assert history[0]['role'] == 'user'
        assert history[0]['content'] == 'Hola'
    
    def test_bot_clear_history(self):
        """Prueba limpiar el historial"""
        backend = SimpleFallbackBackend()
        bot = ConversationalBot(backend=backend)
        
        bot.chat('Test')
        assert len(bot.get_history()) > 0
        
        bot.clear_history()
        assert len(bot.get_history()) == 0
    
    def test_bot_get_system_info(self):
        """Prueba obtener información del sistema"""
        backend = SimpleFallbackBackend()
        bot = ConversationalBot(backend=backend)
        
        info = bot.get_system_info()
        assert 'backend_type' in info
        assert 'model_name' in info
        assert 'history_size' in info
        assert info['backend_type'] == 'SimpleFallbackBackend'


class TestBotSingleton:
    """Tests para el patrón singleton del bot"""
    
    def test_get_bot_singleton(self):
        """Prueba que get_bot retorna la misma instancia"""
        reset_bot()
        
        bot1 = get_bot()
        bot2 = get_bot()
        
        assert bot1 is bot2
    
    def test_reset_bot(self):
        """Prueba reiniciar el bot"""
        bot1 = get_bot()
        bot1.chat('Test')
        
        reset_bot()
        bot2 = get_bot()
        
        assert bot1 is not bot2
        assert len(bot2.get_history()) == 0


class TestBotConversationFlow:
    """Tests para flujos de conversación realistas"""
    
    def test_query_flow(self):
        """Prueba flujo de consulta"""
        bot = ConversationalBot()
        
        bot.chat('¿Qué es esta plataforma?')
        bot.chat('¿Qué puedo hacer?')
        bot.chat('Quiero listar pacientes')
        
        history = bot.get_history()
        assert len(history) >= 6
        
        for msg in history:
            assert 'role' in msg
            assert 'content' in msg
            assert 'timestamp' in msg
    
    def test_intent_recognition(self):
        """Prueba reconocimiento de intenciones"""
        backend = SimpleFallbackBackend()
        
        test_cases = {
            'listar pacientes': 'listar_pacientes',
            'mostrar medicos': 'listar_medicos',
            'ver centros': 'listar_centros',
            'crear nuevo turno': 'crear_turno',
            '¿me ayudas?': 'ayuda'
        }
        
        for text, expected_intent in test_cases.items():
            result = backend.extract_intent(text)
            assert result['intent'] == expected_intent, f"Failed for: {text}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
