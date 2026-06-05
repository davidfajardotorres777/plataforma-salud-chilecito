"""
Bot IA conversacional con capacidad de procesamiento de lenguaje natural.
Soporta conversaciones contextuales sobre la plataforma de salud.
"""

from datetime import datetime
from typing import Optional, Dict, List
import json
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import re

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False


@dataclass
class ConversationMessage:
    """Mensaje en el historial de conversación"""
    role: str  # 'user' o 'assistant'
    content: str
    timestamp: str


class ConversationContext:
    """Mantiene el contexto de la conversación"""
    
    def __init__(self, max_history: int = 10):
        self.history: List[ConversationMessage] = []
        self.max_history = max_history
        self.user_context = {
            'last_entity': None,
            'last_action': None,
            'filters': {}
        }
    
    def add_message(self, role: str, content: str):
        """Agrega un mensaje al historial"""
        msg = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat()
        )
        self.history.append(msg)
        
        # Mantener solo los últimos N mensajes
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-self.max_history * 2:]
    
    def get_history_text(self) -> str:
        """Retorna el historial formateado como texto"""
        return "\n".join(
            f"{msg.role.upper()}: {msg.content}"
            for msg in self.history[-10:]  # Últimos 10 mensajes
        )
    
    def clear(self):
        """Limpia el historial"""
        self.history = []
        self.user_context = {
            'last_entity': None,
            'last_action': None,
            'filters': {}
        }


class BaseAIBackend(ABC):
    """Interfaz base para backends de IA"""
    
    @abstractmethod
    def generate_response(self, prompt: str, context: ConversationContext) -> str:
        """Genera una respuesta basada en el prompt y contexto"""
        pass
    
    @abstractmethod
    def extract_intent(self, text: str) -> Dict[str, str]:
        """Extrae la intención del usuario"""
        pass


class HuggingFaceBackend(BaseAIBackend):
    """Backend usando Hugging Face transformers"""
    
    def __init__(self, model_name: str = "gpt2"):
        """
        Inicializa el backend de Hugging Face
        
        Args:
            model_name: Nombre del modelo (ej: 'gpt2', 'distilgpt2', 'tiiuae/falcon-7b-instruct')
        """
        if not HAS_TRANSFORMERS:
            raise RuntimeError(
                "Transformers no instalado. "
                "Ejecuta: pip install transformers torch"
            )
        
        self.model_name = model_name
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            self.generator = pipeline('text-generation', model=self.model, tokenizer=self.tokenizer)
        except Exception as e:
            raise RuntimeError(f"Error cargando modelo {model_name}: {e}")
    
    def generate_response(self, prompt: str, context: ConversationContext) -> str:
        """Genera respuesta usando el modelo"""
        try:
            # Limitar tamaño del prompt para evitar errores de token
            full_prompt = f"{context.get_history_text()}\nUSER: {prompt}\nASSISTANT:"
            
            response = self.generator(
                full_prompt,
                max_length=200,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
            
            generated = response[0]['generated_text']
            # Extraer solo la parte del asistente
            if 'ASSISTANT:' in generated:
                return generated.split('ASSISTANT:')[-1].strip()
            return generated.strip()
        except Exception as e:
            return f"Error generando respuesta: {str(e)}"
    
    def extract_intent(self, text: str) -> Dict[str, str]:
        """Extrae intención usando patrones"""
        text_lower = text.lower()
        
        intents = {
            'listar_pacientes': r'(listar|mostrar|ver)\s*(todos\s*)?(los\s*)?pacientes',
            'listar_medicos': r'(listar|mostrar|ver)\s*(todos\s*)?(los\s*)?medicos|doctores',
            'listar_centros': r'(listar|mostrar|ver)\s*(todos\s*)?(los\s*)?centros',
            'listar_turnos': r'(listar|mostrar|ver)\s*(todos\s*)?(los\s*)?turnos|citas',
            'crear_paciente': r'(crear|registrar|nuevo)\s*(paciente|patient)',
            'crear_turno': r'(crear|agendar|reservar)\s*(turno|cita|appointment)',
            'buscar': r'(buscar|search|find)\s+(.+)',
            'ayuda': r'(ayuda|help|que\s*puedo\s*hacer|como\s*funciona)',
            'informacion': r'(informaci[óo]n|info|details)\s+(?:sobre\s+)?(.+)',
        }
        
        for intent, pattern in intents.items():
            if re.search(pattern, text_lower):
                return {'intent': intent, 'text': text}
        
        return {'intent': 'general_query', 'text': text}


class SimpleFallbackBackend(BaseAIBackend):
    """Backend simple con respuestas predefinidas (fallback)"""
    
    def __init__(self):
        self.responses = {
            'listar_pacientes': 'Para listar pacientes, puedes decir: "listar pacientes" o "mostrar todos los pacientes"',
            'listar_medicos': 'Para ver médicos, prueba: "listar médicos" o "mostrar doctores disponibles"',
            'listar_centros': 'Para ver centros de salud, di: "listar centros" o "mostrar centros de salud"',
            'crear_paciente': 'Para crear un paciente, proporciona: nombre, DNI, teléfono, distrito y obra social',
            'crear_turno': 'Para agendar un turno, necesito: paciente, médico, fecha, hora y motivo',
            'ayuda': self._get_help_message(),
            'general_query': 'Soy un asistente para la plataforma de salud. ¿Qué necesitas? (listar, crear, buscar, editar)'
        }
    
    def _get_help_message(self) -> str:
        return """Puedo ayudarte con:
- **Listar**: pacientes, médicos, centros, turnos
- **Crear**: pacientes, turnos, documentos
- **Buscar**: por DNI, nombre, especialidad
- **Editar**: datos de pacientes o turnos
- **Ver**: historial, documentos
¿Qué necesitas?"""
    
    def generate_response(self, prompt: str, context: ConversationContext) -> str:
        intent_info = self.extract_intent(prompt)
        intent = intent_info.get('intent', 'general_query')
        return self.responses.get(intent, self.responses['general_query'])
    
    def extract_intent(self, text: str) -> Dict[str, str]:
        text_lower = text.lower()
        
        intents = {
            'listar_pacientes': r'(listar|mostrar|ver)\s*(todos\s*)?(los\s*)?pacientes',
            'listar_medicos': r'(listar|mostrar|ver)\s*(todos\s*)?(los\s*)?medicos|doctores',
            'listar_centros': r'(listar|mostrar|ver)\s*(todos\s*)?(los\s*)?centros',
            'listar_turnos': r'(listar|mostrar|ver)\s*(todos\s*)?(los\s*)?turnos|citas',
            'crear_paciente': r'(crear|registrar|nuevo)\s*(paciente|patient)',
            'crear_turno': r'(crear|agendar|reservar)\s*(turno|cita|appointment)',
            'ayuda': r'(ayuda|help|que\s*puedo\s*hacer|como\s*funciona)',
            'general_query': r'.*'
        }
        
        for intent, pattern in intents.items():
            if re.search(pattern, text_lower):
                return {'intent': intent, 'text': text}
        
        return {'intent': 'general_query', 'text': text}


class ConversationalBot:
    """Bot IA principal con conversación natural"""
    
    def __init__(self, backend: Optional[BaseAIBackend] = None, use_huggingface: bool = False):
        """
        Inicializa el bot
        
        Args:
            backend: Backend de IA personalizado
            use_huggingface: Si True, intenta usar Hugging Face (requiere instalación extra)
        """
        if backend:
            self.backend = backend
        elif use_huggingface and HAS_TRANSFORMERS:
            self.backend = HuggingFaceBackend()
        else:
            self.backend = SimpleFallbackBackend()
        
        self.context = ConversationContext()
    
    def chat(self, user_message: str) -> str:
        """
        Procesa un mensaje del usuario y retorna una respuesta
        
        Args:
            user_message: Mensaje del usuario
            
        Returns:
            Respuesta del bot
        """
        # Agregar mensaje del usuario al contexto
        self.context.add_message('user', user_message)
        
        # Extraer intención
        intent_info = self.backend.extract_intent(user_message)
        
        # Generar respuesta
        response = self.backend.generate_response(user_message, self.context)
        
        # Agregar respuesta al contexto
        self.context.add_message('assistant', response)
        
        return response
    
    def get_history(self) -> List[Dict]:
        """Retorna el historial de conversación"""
        return [
            {
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp
            }
            for msg in self.context.history
        ]
    
    def clear_history(self):
        """Limpia el historial de conversación"""
        self.context.clear()
    
    def get_system_info(self) -> Dict:
        """Retorna información del bot"""
        return {
            'backend_type': self.backend.__class__.__name__,
            'model_name': getattr(self.backend, 'model_name', 'simple'),
            'history_size': len(self.context.history),
            'has_transformers': HAS_TRANSFORMERS
        }


# Instancia global singleton
_bot_instance: Optional[ConversationalBot] = None


def get_bot(use_huggingface: bool = False) -> ConversationalBot:
    """
    Obtiene la instancia global del bot
    
    Args:
        use_huggingface: Si True, intenta usar Hugging Face
        
    Returns:
        Instancia del bot conversacional
    """
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = ConversationalBot(use_huggingface=use_huggingface)
    return _bot_instance


def reset_bot():
    """Reinicia la instancia global del bot"""
    global _bot_instance
    _bot_instance = None
